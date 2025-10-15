import unittest
from . import builders

class TestPromptBuilders(unittest.TestCase):
    def test_build_step1_prompt(self):
        template = "Topic: {topic}"
        prompt = builders.build_step1_prompt("Test Topic", template)
        self.assertEqual(prompt, "Topic: Test Topic")

    def test_build_step2_prompt(self):
        template = "Topic: {topic}, Subtopic: {subtopic}, Difficulty: {difficulty}"
        prompt = builders.build_step2_prompt("T", "S", "D", template)
        self.assertEqual(prompt, "Topic: T, Subtopic: S, Difficulty: D")

    def test_build_step3_prompt(self):
        template = "Catalog: {catalog_names}, Feedback: {failure_feedback}"
        catalog = [{"mistake": "Mistake 1"}, {"mistake": "Mistake 2"}]
        failures = ["Failure 1"]
        prompt = builders.build_step3_prompt("T", "S", "D", catalog, template, failures)
        self.assertIn("- Mistake 1", prompt)
        self.assertIn("- Mistake 2", prompt)
        self.assertIn("- Failure 1", prompt)

    def test_build_step45_prompt(self):
        template = "Title: {title}, Requirements: {requirements}"
        question = {"title": "Q Title", "requirements": ["R1", "R2"]}
        prompt = builders.build_step45_prompt(question, template)
        self.assertIn("Title: Q Title", prompt)
        self.assertIn("- R1", prompt)

    def test_build_step6_prompt(self):
        template = "Question: {question_text}, Sonnet: {sonnet_response}"
        question = {"question_text": "The Question"}
        prompt = builders.build_step6_prompt(question, "Sonnet says hi", "Haiku says hi", [], template)
        self.assertIn("Question: The Question", prompt)
        self.assertIn("Sonnet: Sonnet says hi", prompt)

    def test_build_step7_prompt(self):
        template = "Failures: {haiku_failures}, Feedback: {validation_feedback}"
        failures = ["Failure 1", "Failure 2"]
        feedback = ["Feedback 1"]
        config = {"allowed_difficulties": ["Beginner"]}
        prompt = builders.build_step7_prompt("T", "S", failures, "Haiku", "Sonnet", template, config, feedback)
        self.assertIn("- Failure 1", prompt)
        self.assertIn("- Feedback 1", prompt)

if __name__ == '__main__':
    unittest.main()