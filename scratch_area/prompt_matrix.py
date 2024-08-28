from typing import List
import re


def prompt_matrix(prompt: str) -> List[str]:
    matched_matrix = re.finditer(r"\{.+?\}", prompt, re.M)
    
    def generate_prompts(current_prompt: str, matches: List[str]) -> List[str]:
        if not matches:
            return [current_prompt]
        
        matched = matches[0]
        remaining_matches = matches[1:]
        
        # Strip brackets and split by '|'
        options = matched[1:-1].split("|")
        
        # Recursively generate all combinations
        generated_prompts = []
        for option in options:
            new_prompt = current_prompt.replace(matched, option, 1)
            generated_prompts.extend(generate_prompts(new_prompt, remaining_matches))
        
        return generated_prompts
    
    matches = [match.group() for match in matched_matrix]
    result_prompts = generate_prompts(prompt, matches)
    
    # If no valid combinations were generated, return the original prompt
    return result_prompts if result_prompts else [prompt]



if __name__ == "__main__":

    tests = """A green bus
    A {purple|orange} boat
    A {red|blue} {bicycle|car}
    A {scarlet|cerulean} {bus|cart|train}
    A {very|incredibly|stupidly} {long|girthy|deep} {negative prompt|neg prompt|pos prompt}"""
    test_cases = tests.split("\n")
    for test in test_cases:
        print(f'TESTING "{test}"')
        print("RESULT: " + str(prompt_matrix(test)))
