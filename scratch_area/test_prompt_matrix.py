import unittest
from prompt_matrix import prompt_matrix
class TestPromptMatrix(unittest.TestCase):

    def test_single_placeholder_single_option(self):
        prompt = "Hello {world}"
        expected = ["Hello world"]
        result = prompt_matrix(prompt)
        self.assertEqual(result, expected)

    def test_single_placeholder_multiple_options(self):
        prompt = "Hello {world|universe}"
        expected = ["Hello world", "Hello universe"]
        result = prompt_matrix(prompt)
        self.assertEqual(result, expected)

    def test_multiple_placeholders_single_option_each(self):
        prompt = "Hello {world}, how are {you}?"
        expected = ["Hello world, how are you?"]
        result = prompt_matrix(prompt)
        self.assertEqual(result, expected)

    def test_multiple_placeholders_multiple_options_each(self):
        prompt = "Hello {world|universe}, how are {you|they}?"
        expected = [
            "Hello world, how are you?",
            "Hello world, how are they?",
            "Hello universe, how are you?",
            "Hello universe, how are they?",
        ]
        result = prompt_matrix(prompt)
        self.assertEqual(result, expected)

    def test_no_placeholders(self):
        prompt = "Hello world"
        expected = ["Hello world"]
        result = prompt_matrix(prompt)
        self.assertEqual(result, expected)

    def test_empty_string(self):
        prompt = ""
        expected = [""]
        result = prompt_matrix(prompt)
        self.assertEqual(result, expected)

    def test_unmatched_brackets(self):
        prompt = "Hello {world"
        expected = ["Hello {world"]
        result = prompt_matrix(prompt)
        self.assertEqual(result, expected)

    def test_placeholder_with_spaces(self):
        prompt = "Hello {world | universe}"
        expected = ["Hello world ", "Hello  universe"]
        result = prompt_matrix(prompt)
        self.assertEqual(result, expected)

    def test_nested_placeholders(self):
        prompt = "Hello {{world|universe}}"
        expected = ["Hello {world|universe}"]
        result = prompt_matrix(prompt)
        self.assertEqual(result, expected)

    def test_placeholder_with_empty_options(self):
        prompt = "Hello {world|}"
        expected = ["Hello world", "Hello "]
        result = prompt_matrix(prompt)
        self.assertEqual(result, expected)

    def test_duplicate_placeholders(self):
        prompt = "Hello {world|world}"
        expected = ["Hello world", "Hello world"]
        result = prompt_matrix(prompt)
        self.assertEqual(result, expected)

    def test_placeholder_with_multiple_braces(self):
        prompt = "Hello {{{world|earth}}}"
        expected = ["Hello {{world|earth}}"]
        result = prompt_matrix(prompt)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
