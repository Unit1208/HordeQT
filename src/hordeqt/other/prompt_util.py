import random
import re
from typing import List, Optional, Tuple

from hordeqt.classes.Job import Job
from hordeqt.classes.LoRA import LoRA
from hordeqt.other.consts import LOGGER


def prompt_matrix(prompt: str) -> List[str]:
    matched_matrix = re.finditer(r"\{[^\{]+?\}", prompt, re.M)

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

        a = []
        [
            a.extend(prompt_matrix(generated_prompt))
            for generated_prompt in generated_prompts
        ]
        a = list(set(a))
        return a

    matches = [match.group() for match in matched_matrix]

    result_prompts = generate_prompts(prompt, matches)

    # If no valid combinations were generated, return the original prompt
    return result_prompts if result_prompts else [prompt]


def parse_prompt_LoRAs(prompt: str) -> Tuple[str, List[LoRA]]:
    lora_list = []
    # \<lora:(?P<LoraID>\d+?) ((?:\:(?P<ModelStrength>-?\d+(\.\d+)?)?)?(?:\:(?P<CLIPStrength>-?\d+(\.\d+)?)?)?)(?:\:.+?)?>
    processed_prompt = prompt

    return (processed_prompt, lora_list)


def create_jobs(
    prompt: str,
    neg_prompt: Optional[str],
    sampler_name: str,
    cfg_scale: float,
    seed: int,
    width: int,
    height: int,
    clip_skip: int,
    steps: int,
    model: str,
    karras: bool,
    hires_fix: bool,
    allow_nsfw: bool,
    share_image: bool,
    upscale: str,
    loras: List[LoRA],
    images: int,
):
    if neg_prompt is not None and neg_prompt.strip() != "":
        """
        NOTE: the subsequent call to prompt matrix could do some *really* dumb stuff with this current implementation.
        Along the lines of:

        Prompt: This is a {test|
        Negative Prompt: negative test}
        new prompt: This is a {test| ### negative test}

        prompt matrix: [This is a test, this is a  ### negative test]
        "###" delineates prompt from negative prompt in the horde. i.e prompt ### negative prompt
        *To be fair*, you'd either be an idiot or know exactly what you're doing to encounter this. :shrug:
        """
        prompt = prompt + " ### " + neg_prompt
    jobs = []
    prompts = prompt_matrix(prompt)
    prompts *= images
    for nprompt in prompts:
        # if the user hasn't provided a seed, pick one. It must be under 2**31 so that we can display it on a spinbox eventually.
        # something something C++.
        if seed == 0:
            sj_seed = random.randint(0, 2**31 - 1)
        else:
            sj_seed = seed

        job = Job(
            prompt=nprompt,
            sampler_name=sampler_name,
            cfg_scale=cfg_scale,
            seed=str(sj_seed),
            width=width,
            height=height,
            clip_skip=clip_skip,
            steps=steps,
            model=model,
            karras=karras,
            hires_fix=hires_fix,
            allow_nsfw=allow_nsfw,
            share_image=share_image,
            upscale=upscale,
            loras=loras,
        )
        jobs.append(job)
    LOGGER.info(f"Created {len(jobs)} jobs")
    return jobs
