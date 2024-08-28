from typing import List
import uuid
import re
import re

tests = """A green bus
A {purple|orange} boat
A {red|blue} {bicycle|car}
A {scarlet|cerulean} {bus|cart|train}
A {very|incredibly|stupidly} {long|girthy|deep} {negative prompt|neg prompt|pos prompt}"""
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
    #This might be the most hacky solution I could find, but it "works"
    newer_prompts_array=[]
    for n in range(len(new_prompts_array)):
        p=new_prompts_array[n]
        if p.count("{")+p.count("}")==0:
            newer_prompts_array.append(p)


    if len(newer_prompts_array)==0:
        newer_prompts_array.append(prompt)
    
    
    return newer_prompts_array    
                

for test in test_cases:
    print(f"TESTING \"{test}\"")
    print("RESULT: "+str(prompt_matrix(test)))
