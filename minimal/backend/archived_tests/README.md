# Archived Test Scripts

This directory contains experimental and debugging test scripts that are not part of the main test suite.

## Files

### test_content_marketing.py
- **Purpose**: One-off validation test for Step 7 improvements
- **Created**: October 11, 2025
- **Context**: Testing Step 7 retry rate reduction (50% → <5%) after auto-fix implementation
- **Topic**: "LLM Rubrics for Content Marketing Generation"
- **Status**: Experimental/debugging script - not for CI/CD

### test_step7_direct.py
- **Purpose**: Debug Step 7 directly using database data from previous runs
- **Dependencies**: Requires `pipeline_results.db` with specific topic data
- **Context**: Allows testing Step 7 without running expensive full pipeline
- **Status**: Development/debugging tool - not for CI/CD

## Why Archived?

These scripts were useful during development for validating specific fixes but are not essential for the core test suite. They:
- Test very specific scenarios (Step 7 validation fix)
- Depend on specific database state
- Were meant as one-off validation tools
- Are not part of automated testing

## Reference

For details on the Step 7 improvements these scripts tested, see:
- `STEP7_FIX_IMPLEMENTATION.md`

## Core Test Suite

For the main pytest test suite, see:
- `tests/integration/test_api_endpoints.py` - API endpoint tests
- `tests/integration/test_pipeline_flow.py` - Pipeline flow tests
