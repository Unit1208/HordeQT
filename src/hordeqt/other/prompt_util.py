import random
import re
from typing import List, Optional, Tuple

from hordeqt.classes.Job import Job
from hordeqt.classes.LoRA import LoRA
from hordeqt.classes.Style import BaseStyle, Style
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
    lora_re = r"\s?\<lora:(?P<LoraID>\d+?) ((?:\:(?P<ModelStrength>-?\d+(\.\d+)?)?)?(?:\:(?P<CLIPStrength>-?\d+(\.\d+)?)?)?)(?:\:(?P<Comment>.+?))?>"

    matches = re.finditer(lora_re, prompt, re.VERBOSE | re.X)
    # Iterate through matches
    for match in matches:
        lora_id = int(match.group("LoraID"))
        lora_strength = float(match.group("ModelStrength") or 1)
        lora_clip_strength = float(match.group("CLIPStrength") or 1)
        lora_comment = str(match.group("Comment") or "")
        lora = LoRA(
            f"Prompt Lora: {lora_comment} ({lora_id})",
            lora_id,
            lora_strength,
            lora_clip_strength,
            None,
        )
        lora_list.append(lora)
    processed_prompt = re.sub(lora_re, "", prompt, 0, re.VERBOSE | re.X).strip()

    return (processed_prompt, lora_list)


def parse_job_styles(raw_prompt: str, prompt_format: str):
    if "###" in raw_prompt:

        prompt, neg_prompt = raw_prompt.split("###")
    else:
        prompt = raw_prompt
        neg_prompt = ""
    if "###" not in prompt_format:
        if len(neg_prompt.strip()) > 0:
            neg_prompt = "###" + neg_prompt
    else:
        if len(neg_prompt.strip()) == 0:
            prompt_format = prompt_format.replace("###", "")
    return prompt_format.replace("{p}", prompt).replace("{np}", neg_prompt)


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
    styles: List[Style],
    images: int,
) -> List[Job]:
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
        prompt = prompt + "###" + neg_prompt
    if len(styles) == 0:
        styles.append(BaseStyle)
    jobs = []
    prompts = prompt_matrix(prompt)
    prompts *= images

    for nprompt in prompts:
        parsed_loras = loras.copy()
        parsed_prompt, loras_gotten = parse_prompt_LoRAs(nprompt)
        parsed_loras.extend(loras_gotten)
        for style in styles:
            # if the user hasn't provided a seed, pick one. It must be under 2**31 so that we can display it on a spinbox eventually.
            # something something C++.
            if seed == 0:
                sj_seed = random.randint(0, 2**31 - 1)
            else:
                sj_seed = seed
            complete_loras = parsed_loras.copy()
            complete_loras.extend([s.to_lora() for s in (style.loras or [])])
            job = Job(
                prompt=parse_job_styles(parsed_prompt, style.prompt_format),
                sampler_name=style.sampler or sampler_name,
                cfg_scale=style.cfg_scale or cfg_scale,
                seed=str(sj_seed),
                width=style.width or width,
                height=style.height or height,
                clip_skip=style.clip_skip or clip_skip,
                steps=style.steps or steps,
                model=style.model or model,
                karras=style.karras or karras,
                hires_fix=style.hires_fix or hires_fix,
                allow_nsfw=allow_nsfw,
                share_image=share_image,
                upscale=upscale,
                loras=complete_loras,
            )
            jobs.append(job)
    LOGGER.info(f"Created {len(jobs)} jobs")
    return jobs
