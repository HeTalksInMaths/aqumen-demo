import unittest
import os
from .orchestrator import Orchestrator

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        os.environ["AQU_MOCK_PIPELINE"] = "1"
        self.orchestrator = Orchestrator(db_path=":memory:")

    def test_run_full_pipeline_success(self):
        result = self.orchestrator.run_full_pipeline("Test Topic")
        self.assertTrue(result.final_success)
        self.assertEqual(result.stopped_at_step, 7)
        self.assertTrue(result.differentiation_achieved)
        self.assertTrue(result.student_assessment_created)

    def test_run_full_pipeline_step1_failure(self):
        # To simulate a failure, we can temporarily break the mock
        original_invoke = self.orchestrator.invoke_model_with_tools
        def mock_invoke_step1_fail(*args, **kwargs):
            if "difficulty_categories_tool" in str(args):
                return {"error": "Failed to generate categories"}
            return original_invoke(*args, **kwargs)

        self.orchestrator.invoke_model_with_tools = mock_invoke_step1_fail

        result = self.orchestrator.run_full_pipeline("Test Topic")

        self.assertFalse(result.final_success)
        self.assertEqual(result.stopped_at_step, 1)

        # Restore original method
        self.orchestrator.invoke_model_with_tools = original_invoke

if __name__ == '__main__':
    unittest.main()