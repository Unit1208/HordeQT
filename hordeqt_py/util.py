
import json
import re
from typing import List
import uuid
from pathlib import Path



def create_uuid():
    return str(uuid.uuid4())


def get_headers(api_key: str):
    return {
        "apikey": api_key,
        "Client-Agent": "HordeQt:0.0.1:Unit1208",
        "accept": "application/json",
        "Content-Type": "application/json",
    }


def prompt_matrix(prompt: str) -> List[str]:
    # fails with nested brackets, but that shouldn't be an issue?
    # Writing this out, {{1|2}|{3|4}} would evalutate to e.g [1,2,3,4], and I doubt that anyone would the former. If they do, I'll fix it. Maybe.
    # {{1|2|3|4}} should evalutate to [1,2,3,4] as well.
    matched_matrix = re.finditer(r"\{.+?\}", prompt, re.M)

    def generate_prompts(current_prompt: str, matches: List[str]) -> List[str]:
        if not matches:
            return [current_prompt]

        matched = matches[0]
        remaining_matches = matches[1:]

        # Strip brackets and split by '|'
        options = matched[1:-1].split("|")

        # Recursively generate all combinations.
        # If you hit the stack limit, that's on you, it shouldn't happen.
        generated_prompts = []
        for option in options:
            new_prompt = current_prompt.replace(matched, option, 1)
            generated_prompts.extend(generate_prompts(new_prompt, remaining_matches))

        return generated_prompts

    matches = [match.group() for match in matched_matrix]
    result_prompts = generate_prompts(prompt, matches)

    # If no valid combinations were generated, return the original prompt
    return result_prompts if result_prompts else [prompt]
