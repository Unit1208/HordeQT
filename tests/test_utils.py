import pytest

from hordeqt.other.util import prompt_matrix


@pytest.mark.parametrize(
    "prompt, expected",
    [
        # Test case with no placeholders
        ("Simple prompt", ["Simple prompt"]),
        # Test case with a single placeholder
        ("This is a {test}", ["This is a test"]),
        # Test case with multiple options in a single placeholder
        (
            "This is a {test|sample|example}",
            ["This is a test", "This is a sample", "This is a example"],
        ),
        # Test case with multiple placeholders
        (
            "{Hello|Hi}, {world|everyone}",
            ["Hello, world", "Hello, everyone", "Hi, world", "Hi, everyone"],
        ),
        # Test case with nested placeholders
        (
            "{The {quick|slow}|A {large|small}} dog",
            ["The quick dog", "The slow dog", "A large dog", "A small dog"],
        ),
        # Test case with empty options (edge case)
        ("Empty option {}", ["Empty option {}"]),
    ],
)
def test_prompt_matrix(prompt, expected):
    result = prompt_matrix(prompt)
    assert sorted(result) == sorted(expected)
