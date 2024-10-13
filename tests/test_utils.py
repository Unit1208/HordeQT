import pytest

from hordeqt.classes.LoRA import LoRA
from hordeqt.other.prompt_util import create_jobs, parse_prompt_LoRAs, prompt_matrix


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


def test_parse_prompt_LoRAs_no_lora():
    """Test parsing a prompt with no LoRA tags."""

    prompt = "This is a test prompt."
    expected_prompt = "This is a test prompt."
    expected_lora_list = []
    result = parse_prompt_LoRAs(prompt)
    result_prompt, result_lora_list = result
    assert result_prompt == expected_prompt
    assert result_lora_list == expected_lora_list


def test_parse_prompt_LoRAs_single_lora():
    """Test parsing a prompt with a single LoRA tag."""

    prompt = "This is a test prompt with <lora:1> tag."
    expected_prompt = "This is a test prompt with tag."
    expected_lora_list = [LoRA("Prompt Lora:  (1)", 1, 1.0, 1.0, None)]
    result = parse_prompt_LoRAs(prompt)
    result_prompt, result_lora_list = result
    assert result_prompt == expected_prompt
    assert result_lora_list == expected_lora_list


def test_parse_prompt_LoRAs_single_lora_with_strength():
    """Test parsing a prompt with a single LoRA tag and strength."""

    prompt = "This is a test prompt with <lora:1:0.5> tag."
    expected_prompt = "This is a test prompt with tag."
    expected_lora_list = [LoRA("Prompt Lora:  (1)", 1, 0.5, 1.0, None)]
    result = parse_prompt_LoRAs(prompt)
    result_prompt, result_lora_list = result
    assert result_prompt == expected_prompt
    assert result_lora_list == expected_lora_list


def test_parse_prompt_LoRAs_single_lora_with_clip_strength():
    """Test parsing a prompt with a single LoRA tag and clip strength."""

    prompt = "This is a test prompt with <lora:1::0.5> tag."
    expected_prompt = "This is a test prompt with tag."
    expected_lora_list = [LoRA("Prompt Lora:  (1)", 1, 1.0, 0.5, None)]
    result = parse_prompt_LoRAs(prompt)
    result_prompt, result_lora_list = result
    assert result_prompt == expected_prompt
    assert result_lora_list == expected_lora_list


def test_parse_prompt_LoRAs_single_lora_with_comment():
    """Test parsing a prompt with a single LoRA tag and comment."""
    prompt = "This is a test prompt with <lora:1:Comment> tag."
    expected_prompt = "This is a test prompt with tag."
    expected_lora_list = [LoRA("Prompt Lora: Comment (1)", 1, 1.0, 1.0, None)]
    result = parse_prompt_LoRAs(prompt)
    result_prompt, result_lora_list = result
    assert result_prompt == expected_prompt
    assert result_lora_list == expected_lora_list


def test_parse_prompt_LoRAs_multiple_lora():
    """Test parsing a prompt with multiple LoRA tags."""

    prompt = "This is a test prompt with <lora:1> and <lora:2:0.5:Comment> tags."
    expected_prompt = "This is a test prompt with and tags."
    expected_lora_list = [
        LoRA("Prompt Lora:  (1)", 1, 1.0, 1.0, None),
        LoRA("Prompt Lora: Comment (2)", 2, 0.5, 1.0, None),
    ]
    result = parse_prompt_LoRAs(prompt)
    result_prompt, result_lora_list = result
    assert result_prompt == expected_prompt
    assert result_lora_list == expected_lora_list


def test_parse_prompt_LoRAs_invalid_lora():
    """Test parsing a prompt with an invalid LoRA tag."""
    prompt = "This is a test prompt with <lora:invalid> tag."
    expected_prompt = "This is a test prompt with <lora:invalid> tag."
    expected_lora_list = []
    result = parse_prompt_LoRAs(prompt)
    result_prompt, result_lora_list = result
    assert result_prompt == expected_prompt
    assert result_lora_list == expected_lora_list


def test_create_jobs_no_negative_prompt():
    prompt = "This is a test prompt"
    sampler_name = "sampler"
    cfg_scale = 1.0
    seed = 1
    width = 512
    height = 512
    clip_skip = 1
    steps = 20
    model = "model"
    karras = False
    hires_fix = False
    allow_nsfw = False
    share_image = False
    upscale = "upscale"
    loras = []
    images = 2

    jobs = create_jobs(
        prompt,
        None,
        sampler_name,
        cfg_scale,
        seed,
        width,
        height,
        clip_skip,
        steps,
        model,
        karras,
        hires_fix,
        allow_nsfw,
        share_image,
        upscale,
        loras,
        images,
    )

    assert len(jobs) == 2
    for job in jobs:
        assert job.prompt == prompt
        assert job.sampler_name == sampler_name
        assert job.cfg_scale == cfg_scale
        assert job.seed == "1"
        assert job.width == width
        assert job.height == height
        assert job.clip_skip == clip_skip
        assert job.steps == steps
        assert job.model == model
        assert job.karras == karras
        assert job.hires_fix == hires_fix
        assert job.allow_nsfw == allow_nsfw
        assert job.share_image == share_image
        assert job.upscale == upscale
        assert job.loras == []


def test_create_jobs_with_negative_prompt():
    prompt = "This is a test prompt"
    neg_prompt = "This is a negative test prompt"
    sampler_name = "sampler"
    cfg_scale = 1.0
    seed = 1
    width = 512
    height = 512
    clip_skip = 1
    steps = 20
    model = "model"
    karras = False
    hires_fix = False
    allow_nsfw = False
    share_image = False
    upscale = "upscale"
    loras = []
    images = 2

    jobs = create_jobs(
        prompt,
        neg_prompt,
        sampler_name,
        cfg_scale,
        seed,
        width,
        height,
        clip_skip,
        steps,
        model,
        karras,
        hires_fix,
        allow_nsfw,
        share_image,
        upscale,
        loras,
        images,
    )

    assert len(jobs) == 2
    for job in jobs:
        assert job.prompt.startswith(prompt) and job.prompt.endswith(neg_prompt)
        assert job.sampler_name == sampler_name
        assert job.cfg_scale == cfg_scale
        assert job.seed == "1"
        assert job.width == width
        assert job.height == height
        assert job.clip_skip == clip_skip
        assert job.steps == steps
        assert job.model == model
        assert job.karras == karras
        assert job.hires_fix == hires_fix
        assert job.allow_nsfw == allow_nsfw
        assert job.share_image == share_image
        assert job.upscale == upscale
        assert job.loras == []


def test_create_jobs_with_loras():
    prompt = "This is a test prompt with <lora:1:0.5:0.5:comment>"
    sampler_name = "sampler"
    cfg_scale = 1.0
    seed = 1
    width = 512
    height = 512
    clip_skip = 1
    steps = 20
    model = "model"
    karras = False
    hires_fix = False
    allow_nsfw = False
    share_image = False
    upscale = "upscale"
    loras = []
    images = 2

    jobs = create_jobs(
        prompt,
        None,
        sampler_name,
        cfg_scale,
        seed,
        width,
        height,
        clip_skip,
        steps,
        model,
        karras,
        hires_fix,
        allow_nsfw,
        share_image,
        upscale,
        loras,
        images,
    )

    assert len(jobs) == 2
    for job in jobs:
        assert job.prompt == "This is a test prompt with"
        assert job.loras == [LoRA("Prompt Lora: comment (1)", 1, 0.5, 0.5, None)]


def test_create_jobs_with_zero_seed():
    prompt = "This is a test prompt"
    sampler_name = "sampler"
    cfg_scale = 1.0
    seed = 0
    width = 512
    height = 512
    clip_skip = 1
    steps = 20
    model = "model"
    karras = False
    hires_fix = False
    allow_nsfw = False
    share_image = False
    upscale = "upscale"
    loras = []
    images = 2

    jobs = create_jobs(
        prompt,
        None,
        sampler_name,
        cfg_scale,
        seed,
        width,
        height,
        clip_skip,
        steps,
        model,
        karras,
        hires_fix,
        allow_nsfw,
        share_image,
        upscale,
        loras,
        images,
    )

    assert len(jobs) == 2
    for job in jobs:
        assert int(job.seed) != 0
