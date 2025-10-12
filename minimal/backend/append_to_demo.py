#!/usr/bin/env python3
"""
Append pipeline results to dev mode demo assessments.

Creates a scrollable tab interface with multiple assessments.
"""

import json
import sys
from pathlib import Path


def load_pipeline_result(results_file: str) -> dict:
    """Load a pipeline result JSON file."""
    with open(results_file, 'r') as f:
        return json.load(f)


def create_demo_assessment(result: dict, index: int) -> dict:
    """Convert pipeline result to demo assessment format."""
    assessment = result.get('assessment', {})
    metadata = result.get('metadata', {})

    # Extract metadata from top level if not in metadata object
    if not metadata:
        metadata = {
            'topic': result.get('topic'),
            'subtopic': result.get('subtopic'),
            'difficulty': result.get('difficulty'),
            'run_timestamp': result.get('run_timestamp')
        }

    return {
        'id': f'demo-assessment-{index}',
        'title': assessment.get('title', 'Untitled Assessment'),
        'topic': metadata.get('topic', 'Unknown Topic'),
        'subtopic': metadata.get('subtopic', 'Unknown Subtopic'),
        'difficulty': assessment.get('difficulty', metadata.get('difficulty', 'Intermediate')),
        'content_type': assessment.get('content_type', 'code'),
        'content': assessment.get('content', assessment.get('code', [])),
        'errors': assessment.get('errors', []),
        'run_timestamp': metadata.get('run_timestamp', ''),
    }


def create_pipeline_steps(result: dict, index: int) -> list:
    """Convert pipeline result steps to demo pipeline steps format."""
    steps = result.get('steps', [])
    pipeline_steps = []

    for step in steps:
        pipeline_step = {
            '_id': f"demo-{index}-step-{step['step_number']}",
            'step_number': step['step_number'],
            'description': step.get('step_name', f"Step {step['step_number']}"),
            'model': step.get('model_used', 'Unknown'),
            'timestamp': step.get('timestamp', ''),
            'success': step.get('success', False),
            'response_full': step.get('response', '')
        }
        pipeline_steps.append(pipeline_step)

    return pipeline_steps


def append_assessments_to_demo(results_files: list[str], output_file: str):
    """
    Append multiple pipeline results to demoData.dev.js

    Args:
        results_files: List of pipeline result JSON files
        output_file: Path to demoData.dev.js
    """
    assessments = []
    all_pipeline_steps = []

    for idx, results_file in enumerate(results_files, start=1):
        print(f"Loading {results_file}...")
        result = load_pipeline_result(results_file)

        # Check if it's a frontend_demo_data format or raw results
        if 'assessment' in result:
            demo_assessment = create_demo_assessment(result, idx)
            assessments.append(demo_assessment)

            # Also collect pipeline steps
            pipeline_steps = create_pipeline_steps(result, idx)
            all_pipeline_steps.extend(pipeline_steps)

            print(f"  ✅ Added: {demo_assessment['title']} with {len(pipeline_steps)} pipeline steps")
        else:
            print(f"  ⚠️  Skipped: No assessment found in {results_file}")

    # Create the JavaScript export for demoData.dev.js
    js_content = "// demoData.dev.js\n"
    js_content += "// Dev mode demo assessments with full 7-step pipeline data\n"
    js_content += f"// Generated from {len(results_files)} recent pipeline runs\n\n"
    js_content += f"export const demoAssessments = {json.dumps(assessments, indent=2)};\n\n"
    js_content += f"export const demoPipelineSteps = {json.dumps(all_pipeline_steps, indent=2)};\n\n"
    js_content += "export default demoAssessments;\n"

    # Write to file
    with open(output_file, 'w') as f:
        f.write(js_content)

    print(f"\n✅ Wrote {len(assessments)} assessments and {len(all_pipeline_steps)} pipeline steps to {output_file}")
    print("   These will appear as tabs in Dev + Demo mode with full pipeline visualization")


def main():
    if len(sys.argv) < 2:
        print("Usage: python append_to_demo.py <result1.json> <result2.json> ...")
        print("\nExample:")
        print("  python append_to_demo.py frontend_demo_data_quadratic.json \\")
        print("                           frontend_demo_data_exec.json")
        sys.exit(1)

    results_files = sys.argv[1:]
    output_file = Path(__file__).parent.parent / 'frontend' / 'src' / 'demoData.dev.js'

    append_assessments_to_demo(results_files, str(output_file))


if __name__ == '__main__':
    main()
