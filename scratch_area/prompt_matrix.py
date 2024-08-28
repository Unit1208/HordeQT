from typing import List
import uuid
import re
import re

tests = """A green bus
A {purple|orange} boat
A {red|blue} {bicycle|car}
A {scarlet|cerulean} {bus|cart|train}"""
test_cases = tests.split("\n")

## Logic adapted from Artbot's implementation


def prompt_matrix(prompt:str):
    matched_matrix=re.finditer(r"\{.+?\}",prompt,re.M)
    
    new_prompts_array:List[str]=[]
    def parse_prompt(matched:str):
        update_prompts:List[str]=[]
        strip_brackets=matched.replace("{","").replace("}","")
        matched_word_array=strip_brackets.split("|") or []
        if len(new_prompts_array)==0:
            for word in matched_word_array:
                s=prompt.replace(matched,word)
                update_prompts.append(s)
        else:
            for s in new_prompts_array:
                for word in matched_word_array:
                    new_string=s.replace(matched,word)
                    update_prompts.append(new_string)
        for x in update_prompts:
            new_prompts_array.append(x)
    for match in matched_matrix:
        parse_prompt(match.group())
    if len(new_prompts_array)==0:
        new_prompts_array.append(prompt)
    return new_prompts_array    
                

for test in test_cases:
    print(f"TESTING \"{test}\"")
    print("RESULT: "+str(prompt_matrix(test)))
