#!/usr/bin/env python3
"""
Load pipeline results from database to dev mode demo assessments.

Extracts data by timestamp and topic combinations from the database.
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import List, Dict, Tuple


def connect_to_database(db_path: str) -> sqlite3.Connection:
    """Connect to the SQLite database."""
    return sqlite3.connect(db_path)


def get_pipeline_runs_by_topics(db_path: str, topics: List[str], run_timestamp: str = None) -> List[Dict]:
    """
    Get pipeline results from database for specific topics.

    Args:
        db_path: Path to SQLite database
        topics: List of topic names to extract
        run_timestamp: Optional specific timestamp to limit to

    Returns:
        List of pipeline results with assessments and steps
    """
    conn = connect_to_database(db_path)

    try:
        # Build query to get all relevant data for the topics
        if run_timestamp:
            timestamp_filter = f"AND run_timestamp = '{run_timestamp}'"
        else:
            timestamp_filter = ""

        query = f"""
        SELECT
            topic,
            run_timestamp,
            step_number,
            step_name,
            model_used,
            success,
            full_response,
            timestamp
        FROM enhanced_step_responses
        WHERE topic IN ({','.join(['?' for _ in topics])}) {timestamp_filter}
        ORDER BY run_timestamp DESC, step_number ASC
        """

        cursor = conn.execute(query, topics)
        rows = cursor.fetchall()

        # Group data by run_timestamp and topic
        runs = {}
        for row in rows:
            run_key = f"{row[0]}_{row[1]}"  # topic_run_timestamp
            if run_key not in runs:
                runs[run_key] = {
                    'topic': row[0],
                    'subtopic': 'Unknown',
                    'difficulty': 'Intermediate',
                    'run_timestamp': row[1],
                    'final_success': True,  # Assume successful if steps exist
                    'differentiation_achieved': True,
                    'student_assessment_created': True,
                    'total_attempts': 1,
                    'weak_model_failures': [],
                    'steps': []
                }

            # Add step data
            if row[2] is not None:  # step_number
                runs[run_key]['steps'].append({
                    'step_number': row[2],
                    'step_name': row[3] or f"Step {row[2]}",
                    'model_used': row[4] or 'Unknown',
                    'success': bool(row[5]),
                    'response': row[6] or '',
                    'timestamp': row[7] or ''
                })

        return list(runs.values())

    finally:
        conn.close()


def create_demo_assessment(run_data: Dict, index: int) -> Dict:
    """Convert database run data to demo assessment format."""
    # Find step 7 (student assessment creation) to extract actual content
    step_7_data = None
    for step in run_data.get('steps', []):
        if step['step_number'] == 7 and step['success']:
            try:
                # Parse the JSON response from step 7
                import re
                response_text = step['response']

                # Handle different response formats
                if response_text.startswith('{') and '"title":' in response_text:
                    # Direct JSON format
                    step_7_data = json.loads(response_text)
                elif '"title":' in response_text:
                    # Extract JSON from response text
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        step_7_data = json.loads(json_match.group())

                # Handle nested model_response format
                if step_7_data and 'model_response' in step_7_data:
                    step_7_data = step_7_data['model_response']

                break
            except (json.JSONDecodeError, KeyError, AttributeError) as e:
                print(f"  ⚠️  Could not parse step 7 response for {run_data['topic']}: {e}")
                continue

    if step_7_data:
        return {
            'id': f'demo-assessment-{index}',
            'title': step_7_data.get('title', f"{run_data['topic']} Assessment"),
            'topic': run_data['topic'],
            'subtopic': run_data['subtopic'],
            'difficulty': step_7_data.get('difficulty', run_data['difficulty']),
            'content_type': step_7_data.get('content_type', 'code'),
            'content': step_7_data.get('content', ['// Assessment content loaded from database']),
            'code': step_7_data.get('code', step_7_data.get('content', ['// Assessment content loaded from database'])),
            'errors': step_7_data.get('errors', []),
            'run_timestamp': run_data['run_timestamp'],
        }
    else:
        # Fallback if no step 7 data found
        return {
            'id': f'demo-assessment-{index}',
            'title': f"{run_data['topic']} Assessment",
            'topic': run_data['topic'],
            'subtopic': run_data['subtopic'],
            'difficulty': run_data['difficulty'],
            'content_type': 'code',
            'content': ['// Assessment content loaded from database'],
            'errors': [],
            'run_timestamp': run_data['run_timestamp'],
        }


def create_pipeline_steps(run_data: Dict, index: int) -> List[Dict]:
    """Convert database run steps to demo pipeline steps format."""
    pipeline_steps = []

    for step in run_data.get('steps', []):
        pipeline_step = {
            '_id': f"demo-{index}-step-{step['step_number']}",
            'step_number': step['step_number'],
            'description': step['step_name'],
            'model': step['model_used'],
            'timestamp': step['timestamp'],
            'success': step['success'],
            'response_full': step['response']
        }
        pipeline_steps.append(pipeline_step)

    return pipeline_steps


def load_assessments_from_database(topics: List[str], db_path: str = None, run_timestamp: str = None) -> Tuple[List[Dict], List[Dict]]:
    """
    Load assessments from database for specific topics.

    Args:
        topics: List of topic names to load
        db_path: Path to database (defaults to local pipeline_results.db)
        run_timestamp: Specific timestamp to limit to (optional)

    Returns:
        Tuple of (assessments, pipeline_steps)
    """
    if db_path is None:
        db_path = Path(__file__).parent / 'pipeline_results.db'

    runs = get_pipeline_runs_by_topics(db_path, topics, run_timestamp)

    assessments = []
    all_pipeline_steps = []

    for idx, run_data in enumerate(runs, start=1):
        if run_data['student_assessment_created'] and run_data['final_success']:
            demo_assessment = create_demo_assessment(run_data, idx)
            assessments.append(demo_assessment)

            # Collect pipeline steps
            pipeline_steps = create_pipeline_steps(run_data, idx)
            all_pipeline_steps.extend(pipeline_steps)

            print(f"  ✅ Added: {run_data['topic']} assessment with {len(pipeline_steps)} pipeline steps")
        else:
            print(f"  ⚠️  Skipped: {run_data['topic']} - no successful assessment found")

    return assessments, all_pipeline_steps


def load_existing_demo_data(output_file: str) -> Tuple[List[Dict], List[Dict]]:
    """Load existing demo data from file if it exists."""
    try:
        if not Path(output_file).exists():
            return [], []

        # Read the existing file and extract data
        with open(output_file, 'r') as f:
            content = f.read()

        # Simple parsing to extract existing assessments and pipeline steps
        existing_assessments = []
        existing_pipeline_steps = []

        # Look for existing assessments array
        if 'export const demoAssessments' in content:
            start_marker = 'export const demoAssessments = '
            start_idx = content.find(start_marker)
            if start_idx != -1:
                start_idx += len(start_marker)
                # Find the end of the array (next semicolon)
                bracket_count = 0
                end_idx = start_idx
                for i, char in enumerate(content[start_idx:], start_idx):
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_idx = i + 1
                            break

                assessments_str = content[start_idx:end_idx]
                existing_assessments = json.loads(assessments_str)

        # Look for existing pipeline steps array
        if 'export const demoPipelineSteps' in content:
            start_marker = 'export const demoPipelineSteps = '
            start_idx = content.find(start_marker)
            if start_idx != -1:
                start_idx += len(start_marker)
                # Find the end of the array (next semicolon)
                bracket_count = 0
                end_idx = start_idx
                for i, char in enumerate(content[start_idx:], start_idx):
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_idx = i + 1
                            break

                pipeline_steps_str = content[start_idx:end_idx]
                existing_pipeline_steps = json.loads(pipeline_steps_str)

        return existing_assessments, existing_pipeline_steps

    except Exception as e:
        print(f"  ⚠️  Could not read existing demo data: {e}")
        return [], []


def write_demo_data(assessments: List[Dict], pipeline_steps: List[Dict], output_file: str):
    """Append demo data to JavaScript file."""
    # Load existing data first
    existing_assessments, existing_pipeline_steps = load_existing_demo_data(output_file)

    # Get the next available IDs for new assessments
    next_assessment_id = len(existing_assessments) + 1
    next_step_id = len(existing_pipeline_steps) + 1

    # Update IDs for new assessments to avoid conflicts
    for assessment in assessments:
        # Update the ID to be unique
        old_id = assessment['id']
        new_id = f'demo-assessment-{next_assessment_id}'
        assessment['id'] = new_id
        next_assessment_id += 1

        # Update pipeline step IDs to reference the new assessment ID
        # Extract the original index from the old ID and use it to find matching steps
        old_index = old_id.replace('demo-assessment-', '')
        for step in pipeline_steps:
            if step['_id'].startswith(f'demo-{old_index}-step-'):
                step['_id'] = f'demo-{next_assessment_id - 1}-step-' + step['_id'].split('-')[-1]

    # Combine existing and new data
    all_assessments = existing_assessments + assessments
    all_pipeline_steps = existing_pipeline_steps + pipeline_steps

    # Write the combined data
    js_content = "// demoData.dev.js\n"
    js_content += "// Dev mode demo assessments with full 7-step pipeline data\n"
    js_content += f"// Generated from database: {len(all_assessments)} assessments (total)\n\n"
    js_content += f"export const demoAssessments = {json.dumps(all_assessments, indent=2)};\n\n"
    js_content += f"export const demoPipelineSteps = {json.dumps(all_pipeline_steps, indent=2)};\n\n"
    js_content += "export default demoAssessments;\n"

    with open(output_file, 'w') as f:
        f.write(js_content)

    print(f"\n✅ Appended {len(assessments)} new assessments and {len(pipeline_steps)} new pipeline steps to {output_file}")
    print(f"   Total assessments: {len(all_assessments)}, Total pipeline steps: {len(all_pipeline_steps)}")
    print("   These will appear as options in Dev + Demo mode with full pipeline visualization")


def main():
    if len(sys.argv) < 2:
        print("Usage: python load_from_database.py <topic1> <topic2> ... [--timestamp TIMESTAMP]")
        print("\nExamples:")
        print("  python load_from_database.py 'LangChain' 'Prompt Engineering'")
        print("  python load_from_database.py 'LangChain' 'Prompt Engineering' --timestamp 20251012_213045")
        sys.exit(1)

    # Parse arguments
    topics = []
    run_timestamp = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--timestamp' and i + 1 < len(sys.argv):
            run_timestamp = sys.argv[i + 1]
            i += 2
        else:
            topics.append(sys.argv[i])
            i += 1

    print(f"Loading assessments for topics: {', '.join(topics)}")
    if run_timestamp:
        print(f"Limiting to timestamp: {run_timestamp}")

    # Load data from database
    assessments, pipeline_steps = load_assessments_from_database(topics, run_timestamp=run_timestamp)

    # Write to frontend
    output_file = Path(__file__).parent.parent / 'frontend' / 'src' / 'demoData.dev.js'
    write_demo_data(assessments, pipeline_steps, str(output_file))


if __name__ == '__main__':
    main()