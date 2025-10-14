# Debugging Guide: Automated Dataset Creation

## Goal

The goal of this work was to create a set of scripts to automate the creation of test datasets for the pipeline. The desired workflow is as follows:

1.  Run the pipeline with a new topic.
2.  The pipeline automatically detects that a new topic has been added to the database.
3.  A new, incrementally numbered dataset file is automatically created with the new topic.
4.  A test runner script can be used to run tests on any of the dataset files, including the newly created ones.

## Current State

The following scripts have been created to implement this workflow:

*   `minimal/backend/create_new_datasets.py`: This script is responsible for creating the new dataset files.
*   `minimal/backend/test_runner.py`: This script is used to run the tests on the datasets.
*   `minimal/backend/corrected_7step_pipeline.py`: This script has been modified to automatically call the `create_new_datasets.py` script after each pipeline run.
*   `minimal/backend/test_dataset_creation.py`: This script is used to test the dataset creation process.

The datasets are stored as JSON files in the `minimal/backend/datasets` directory.

## Issues Encountered

The `test_dataset_creation.py` script is currently failing. We have encountered a number of issues while trying to debug it, including:

*   **Pathing Issues:** The scripts have had trouble locating the database and the other scripts, due to the use of relative paths and the fact that the scripts are being run from different directories.
*   **Subprocess Issues:** The `test_dataset_creation.py` script calls the `create_new_datasets.py` script as a subprocess, which has caused issues with the working directory and the file paths.
*   **Race Conditions:** The test script and the dataset creation script have been interfering with each other, causing a race condition where the test script deletes the files that the dataset creation script has just created.

## Recommendations

While the current approach of using a collection of scripts is workable, it has proven to be fragile and difficult to debug. A more robust solution would be to use a dedicated testing framework, such as `pytest`.

A `pytest` solution would allow for:

*   **Fixtures:** Fixtures could be used to create a clean, isolated environment for each test, with a temporary database and temporary dataset files. This would eliminate the race conditions and the need for manual cleanup.
*   **Assertions:** `pytest` provides a rich set of assertion functions that would make it easier to verify the results of the tests.
*   **Test Discovery:** `pytest` can automatically discover and run tests, which would eliminate the need for the `test_runner.py` script.

I recommend that another developer take a look at this with a fresh pair of eyes and consider rewriting the testing logic using `pytest`.
