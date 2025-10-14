#!/usr/bin/env python3
"""
Fix duplicate step IDs in demoData.dev.js
"""

import json
import re

def fix_demo_data():
    input_file = 'demoData.dev.js'
    output_file = 'demoData.dev.js'

    # Read the current file
    with open(input_file, 'r') as f:
        content = f.read()

    # Extract assessments array
    assessments_start = content.find('export const demoAssessments = ')
    if assessments_start == -1:
        print("Could not find assessments array")
        return

    assessments_start += len('export const demoAssessments = ')

    # Find the end of the assessments array
    bracket_count = 0
    assessments_end = assessments_start
    for i, char in enumerate(content[assessments_start:], start=assessments_start):
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0:
                assessments_end = i + 1
                break

    assessments_str = content[assessments_start:assessments_end]
    assessments = json.loads(assessments_str)

    # Extract pipeline steps array
    steps_start = content.find('export const demoPipelineSteps = ')
    if steps_start == -1:
        print("Could not find pipeline steps array")
        return

    steps_start += len('export const demoPipelineSteps = ')

    # Find the end of the steps array
    bracket_count = 0
    steps_end = steps_start
    for i, char in enumerate(content[steps_start:], start=steps_start):
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0:
                steps_end = i + 1
                break

    steps_str = content[steps_start:steps_end]
    pipeline_steps = json.loads(steps_str)

    # Remove duplicate pipeline steps by keeping only unique _id entries
    seen_ids = set()
    unique_pipeline_steps = []

    for step in pipeline_steps:
        if step['_id'] not in seen_ids:
            seen_ids.add(step['_id])
            unique_pipeline_steps.append(step)
        else:
            print(f"Removing duplicate step: {step['_id']}")

    print(f"Original steps: {len(pipeline_steps)}")
    print(f"Unique steps: {len(unique_pipeline_steps)}")

    # Rebuild the file content
    new_content = content[:assessments_start] + json.dumps(assessments, indent=2) + content[assessments_end:steps_start] + json.dumps(unique_pipeline_steps, indent=2) + content[steps_end:]

    # Write the fixed content
    with open(output_file, 'w') as f:
        f.write(new_content)

    print(f"✅ Fixed demo data by removing {len(pipeline_steps) - len(unique_pipeline_steps)} duplicate steps")

if __name__ == '__main__':
    fix_demo_data()