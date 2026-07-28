import unittest

from code_reviewer import validate_code


class TestCodeValidation(unittest.TestCase):

    def test_accepts_python_code(self):
        language = validate_code(
            "example.py",
            "print('Hello')",
        )

        self.assertEqual(language, "python")

    def test_rejects_unsupported_file(self):
        with self.assertRaises(ValueError):
            validate_code(
                "notes.txt",
                "Hello",
            )

    def test_rejects_empty_code(self):
        with self.assertRaises(ValueError):
            validate_code(
                "example.py",
                "",
            )

    def test_rejects_large_code(self):
        large_code = "a" * 50001

        with self.assertRaises(ValueError):
            validate_code(
                "example.py",
                large_code,
            )


if __name__ == "__main__":
    unittest.main()