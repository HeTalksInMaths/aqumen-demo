import unittest
from .assessment import AssessmentValidator

class TestAssessmentValidator(unittest.TestCase):
    def setUp(self):
        self.config = {
            "allowed_difficulties": {"Beginner", "Intermediate", "Advanced", "Expert"},
            "min_code_lines": 5,
            "max_code_lines": 50,
            "min_errors": 1,
            "max_errors": 3,
            "min_error_span": 10,
            "max_error_span": 100,
        }
        self.validator = AssessmentValidator(self.config)

    def test_valid_payload(self):
        payload = {
            "title": "Valid Title",
            "difficulty": "Intermediate",
            "content_type": "code",
            "content": [
                "line 1 <<error_id_1_long_enough>>",
                "line 2",
                "line 3",
                "line 4",
                "line 5"
            ],
            "errors": [
                {"id": "error_id_1_long_enough", "description": "A valid error description."}
            ]
        }
        is_valid, _, errors = self.validator.validate(payload)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_invalid_title(self):
        payload = {
            "title": "",
            "difficulty": "Intermediate",
            "content_type": "code",
            "content": ["line 1"] * 5,
            "errors": [{"id": "error_id_1_long_enough", "description": "desc"}]
        }
        is_valid, _, errors = self.validator.validate(payload)
        self.assertFalse(is_valid)
        self.assertIn("Title must be a non-empty string.", errors)

    def test_invalid_difficulty(self):
        payload = {
            "title": "Valid Title",
            "difficulty": "Super Hard",
            "content_type": "code",
            "content": ["line 1"] * 5,
            "errors": [{"id": "error_id_1_long_enough", "description": "desc"}]
        }
        is_valid, _, errors = self.validator.validate(payload)
        self.assertFalse(is_valid)
        self.assertIn("Difficulty must be one of ['Advanced', 'Beginner', 'Expert', 'Intermediate'].", errors)

    def test_content_too_short(self):
        payload = {
            "title": "Valid Title",
            "difficulty": "Intermediate",
            "content_type": "code",
            "content": ["line 1"],
            "errors": [{"id": "error_id_1_long_enough", "description": "desc"}]
        }
        is_valid, _, errors = self.validator.validate(payload)
        self.assertFalse(is_valid)
        self.assertIn("`content` must contain between 5 and 50 lines (found 1).", errors)

    def test_too_many_errors(self):
        payload = {
            "title": "Valid Title",
            "difficulty": "Intermediate",
            "content_type": "code",
            "content": ["line 1"] * 5,
            "errors": [
                {"id": "error_id_1_long_enough", "description": "desc"},
                {"id": "error_id_2_long_enough", "description": "desc"},
                {"id": "error_id_3_long_enough", "description": "desc"},
                {"id": "error_id_4_long_enough", "description": "desc"}
            ]
        }
        is_valid, _, errors = self.validator.validate(payload)
        self.assertFalse(is_valid)
        self.assertIn("`errors` array must contain between 1 and 3 entries (found 4).", errors)

    def test_mismatched_error_ids(self):
        payload = {
            "title": "Valid Title",
            "difficulty": "Intermediate",
            "content_type": "code",
            "content": ["line 1 <<error_id_1_long_enough>>"] * 5,
            "errors": [{"id": "a_different_error_id_long_enough", "description": "desc"}]
        }
        is_valid, _, errors = self.validator.validate(payload)
        self.assertFalse(is_valid)
        self.assertIn("Error id 'a_different_error_id_long_enough' is not wrapped in <<...>> within the `content`.", errors)

if __name__ == '__main__':
    unittest.main()