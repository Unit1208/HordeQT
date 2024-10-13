from typing import Any, Dict, List, Optional


def get_horde_metadata_pretty(val: Dict[str, Any]):
    prompt = val["prompt"]
    job_id = val["job_id"]
    warning_tokens = _get_job_metadata_tokens(val["generations"][0]["gen_metadata"])
    warning = " ".join(warning_tokens)
    return f"{warning} ({job_id}:{prompt})"


def _get_job_metadata_tokens(gen_metas: List[Dict[str, str]]) -> List[str]:
    all_tokens: List[str] = []
    for gen_meta in gen_metas:
        g_type = gen_meta["type"]
        g_value = gen_meta["value"]
        ref = gen_meta.get("ref", None)
        all_tokens.extend(_get_metadata_tokens(g_type, g_value, ref))
        all_tokens.append(";")
    if len(all_tokens) > 0:
        all_tokens.pop()
    return all_tokens


def _get_metadata_tokens(g_type: str, g_value: str, ref: Optional[str]) -> List[str]:
    tokens = []
    if g_type == "lora":
        tokens.append("LoRA(s)")
    elif g_type == "ti":
        tokens.append("TI(s)")
    elif (
        g_type == "source_image"
    ):  # img2img isn't actually implemented yet, but doesn't hurt to include code to handle it if I do implement it.
        tokens.append("img2img source image")
    elif g_type == "source_mask":  # ditto
        tokens.append("img2img mask image")
    elif g_type == "extra_source_images":  # ditto
        tokens.append("img2img extra source image(s)")
    elif g_type == "information":
        tokens.append("INFORMATION:")
    elif g_type == "censorship":
        tokens.append("Result")

    if g_value == "download_failed":
        tokens.append("failed to download")
    elif g_value == "parse_failed":
        tokens.append("failed to parse")
    elif g_value == "baseline_mismatch":
        tokens.append("were used on the wrong baseline")
    elif g_value == "csam":
        tokens.append("was censored due to the Horde's filtering")
    elif g_value == "nsfw":
        tokens.append("was censored due to user's request")
    if g_value == "see_ref" or ref is not None:
        tokens.append("Ref: ")
        tokens.append(ref)

    return tokens
