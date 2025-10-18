"""
Test Step 7 directly with outputs from the Content Marketing run
This allows us to test the Step 7 improvements without running the full pipeline
"""

import json
import logging
import sqlite3

from corrected_7step_pipeline import CorrectedSevenStepPipeline

# Set up logging to see auto-fix messages
logging.basicConfig(
    level=logging.WARNING,  # Show WARNING level to see auto-fix messages
    format='%(levelname)s - %(message)s'
)

def get_latest_pipeline_data(topic_pattern="LLM Rubrics"):
    """Get the latest Step 4-6 data for a topic from database"""
    conn = sqlite3.connect('pipeline_results.db')
    cursor = conn.cursor()

    # Get Steps 1-6 for the topic
    cursor.execute('''
        SELECT step_number, step_name, full_response
        FROM enhanced_step_responses
        WHERE topic LIKE ?
        ORDER BY created_at DESC, step_number ASC
        LIMIT 6
    ''', (f'%{topic_pattern}%',))

    steps = cursor.fetchall()
    conn.close()

    if not steps or len(steps) < 6:
        return None

    # Extract the data we need
    step4_response = next((s[2] for s in steps if s[0] == 4), None)
    step5_response = next((s[2] for s in steps if s[0] == 5), None)
    step6_response = next((s[2] for s in steps if s[0] == 6), None)

    # Parse haiku failures from step 6
    haiku_failures = []
    if step6_response and "HAIKU_FAILURES:" in step6_response:
        try:
            failures_section = step6_response.split("HAIKU_FAILURES:")[1].split("REASONING:")[0].strip()
            import re
            failure_items = re.findall(r'[•\-\*\d\.]\s*([^\n\r]+)', failures_section)
            haiku_failures = [item.strip() for item in failure_items if item.strip()]
        except Exception:
            haiku_failures = [
                "Subjective descriptors without behavioral anchors",
                "Incomplete scoring scale",
                "Less format-specific criteria",
            ]

    # Create mock question dict
    question = {
        "context": "LLM Rubrics for Content Marketing Generation",
        "title": "Content Quality Evaluation Rubrics",
        "question_text": "Create evaluation rubrics for LinkedIn posts, blog posts, and case studies",
        "requirements": [
            "5-point scale for each criterion",
            "Format-specific criteria",
            "Behavioral anchors for consistency"
        ]
    }

    return {
        "question": question,
        "sonnet_response": step4_response,
        "haiku_response": step5_response,
        "judge_response": step6_response,
        "haiku_failures": haiku_failures
    }

def test_step7_direct():
    """Test Step 7 with real data from Content Marketing run"""
    print("🧪 Testing Step 7 Directly with Content Marketing Data")
    print("="*70)

    # Get data from database
    data = get_latest_pipeline_data("LLM Rubrics")

    if not data:
        print("❌ No data found for LLM Rubrics topic")
        print("   Make sure the pipeline ran at least through Step 6")
        return

    print("✅ Found pipeline data in database")
    print(f"   Haiku failures identified: {len(data['haiku_failures'])}")
    for i, failure in enumerate(data['haiku_failures'][:3], 1):
        print(f"   {i}. {failure[:80]}...")
    print()

    # Initialize pipeline
    pipeline = CorrectedSevenStepPipeline()

    print("🎯 Running Step 7 with improved schema + auto-fix...")
    print("-"*70)

    # Run Step 7
    success, assessment, step7 = pipeline.step7_create_student_assessment(
        question=data["question"],
        sonnet_response=data["sonnet_response"],
        haiku_response=data["haiku_response"],
        haiku_failures=data["haiku_failures"]
    )

    print()
    print("="*70)
    print("📊 STEP 7 RESULTS")
    print("="*70)

    if success:
        print("✅ SUCCESS! Assessment generated")
        print(f"   Title: {assessment.get('title', 'N/A')}")
        print(f"   Difficulty: {assessment.get('difficulty', 'N/A')}")
        print(f"   Content type: {assessment.get('content_type', 'N/A')}")
        print(f"   Lines: {len(assessment.get('content', assessment.get('code', [])))}")
        print(f"   Errors: {len(assessment.get('errors', []))}")

        # Check if auto-fix was used (look in logs or step response)
        step_response_data = json.loads(step7.response) if isinstance(step7.response, str) else step7.response
        print(f"\n   Step name: {step7.step_name}")
        if "attempt 1" in step7.step_name:
            print("   🎉 SUCCESS ON FIRST ATTEMPT! (No retries needed)")
        else:
            print("   ⚠️  Required retries")

        # Show error examples
        if assessment.get('errors'):
            print("\n   Error examples:")
            for i, error in enumerate(assessment['errors'][:2], 1):
                print(f"   {i}. ID: {error['id'][:50]}...")
                print(f"      Desc: {error['description'][:70]}...")
    else:
        print("❌ FAILED after all attempts")
        # Try to parse the response to see validation errors
        try:
            step_response_data = json.loads(step7.response) if isinstance(step7.response, str) else step7.response
            if 'validation_errors' in step_response_data:
                print("\n   Validation errors:")
                for error in step_response_data['validation_errors'][:5]:
                    print(f"   - {error}")
        except Exception:
            print(f"   Response: {step7.response[:200]}...")

    print("="*70)

    # Save to database
    print("\n💾 Saving Step 7 result to database...")
    pipeline.current_topic = data["question"]["context"]
    pipeline._save_step_to_database(step7)
    print("✅ Saved!")

    return success, assessment

if __name__ == "__main__":
    test_step7_direct()
