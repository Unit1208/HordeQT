import pytest

from hordeqt.classes.LoRA import LoRA
from hordeqt.classes.Style import Style, StyleLora
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
    styles = []
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
        styles,
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
    styles = []
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
        styles,
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
    styles = []
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
        styles,
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
    styles = []
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
        styles,
        images,
    )

    assert len(jobs) == 2
    for job in jobs:
        assert int(job.seed) != 0


# Sample data for testing
sample_style_data = {
    "name": "test_style",
    "prompt_format": "{p}### {np}",
    "model": "test_model",
    "width": 512,
    "height": 512,
    "cfg_scale": 7.5,
    "karras": True,
    "sampler": "test_sampler",
    "steps": 50,
    "clip_skip": 2,
    "hires_fix": False,
    "loras": [],
    "is_built_in": False,
}

sample_style_lora_data = {
    "name": "42",
    "is_version": False,
    "strength": 0.8,
    "clip_strength": 0.5,
}


@pytest.fixture
def style():
    return Style(**sample_style_data)


@pytest.fixture
def style_lora():
    return StyleLora.parse_from_json(sample_style_lora_data)


def test_style_serialization(style):
    serialized = style.serialize()
    assert serialized["name"] == style.name
    assert serialized["prompt_format"] == style.prompt_format
    assert serialized["model"] == style.model
    assert serialized["width"] == style.width
    assert serialized["height"] == style.height
    assert serialized["cfg_scale"] == style.cfg_scale
    assert serialized["karras"] == style.karras
    assert serialized["sampler"] == style.sampler
    assert serialized["steps"] == style.steps
    assert serialized["clip_skip"] == style.clip_skip
    assert serialized["hires_fix"] == style.hires_fix
    assert serialized["loras"] == []


def test_style_deserialization(style):
    serialized = style.serialize()
    deserialized = Style.deserialize(serialized)
    assert deserialized.name == style.name
    assert deserialized.prompt_format == style.prompt_format
    assert deserialized.model == style.model
    assert deserialized.width == style.width
    assert deserialized.height == style.height
    assert deserialized.cfg_scale == style.cfg_scale
    assert deserialized.karras == style.karras
    assert deserialized.sampler == style.sampler
    assert deserialized.steps == style.steps
    assert deserialized.clip_skip == style.clip_skip
    assert deserialized.hires_fix == style.hires_fix
    assert deserialized.loras == []


def test_style_lora_serialization(style_lora):
    serialized = style_lora.serialize()
    assert serialized["name"] == style_lora.name
    assert serialized["is_version"] == style_lora.is_version
    assert serialized["strength"] == style_lora.strength
    assert serialized["clip_strength"] == style_lora.clip_strength


def test_style_lora_deserialization(style_lora):
    serialized = style_lora.serialize()
    deserialized = StyleLora.deserialize(serialized)
    assert deserialized.name == style_lora.name
    assert deserialized.is_version == style_lora.is_version
    assert deserialized.strength == style_lora.strength
    assert deserialized.clip_strength == style_lora.clip_strength


def test_create_jobs_with_style(style):
    prompt = "This is a test prompt"
    neg_prompt = "This is a negative prompt"
    sampler_name = "default_sampler"
    cfg_scale = 7.0
    seed = 0
    width = 512
    height = 512
    clip_skip = 1
    steps = 20
    model = "model_v1"
    karras = False
    hires_fix = False
    allow_nsfw = False
    share_image = False
    upscale = "none"
    loras = []
    styles = [style]
    images = 1

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
        styles,
        images,
    )

    assert len(jobs) == 1
    job = jobs[0]
    assert job.prompt == "This is a test prompt### This is a negative prompt"
    assert job.sampler_name == "test_sampler"
    assert job.cfg_scale == 7.5
    assert job.seed != 0
    assert job.width == 512
    assert job.height == 512
    assert job.clip_skip == 2
    assert job.steps == 50
    assert job.model == "test_model"
    assert job.karras
    assert not job.hires_fix
    assert job.loras == []


def test_create_jobs_with_style_with_lora(style, style_lora):
    prompt = "This is a test prompt"
    neg_prompt = "This is a negative prompt"
    sampler_name = "default_sampler"
    cfg_scale = 7.0
    seed = 0
    width = 512
    height = 512
    clip_skip = 1
    steps = 20
    model = "model_v1"
    karras = False
    hires_fix = False
    allow_nsfw = False
    share_image = False
    upscale = "none"
    loras = []
    s = style
    s.loras = [style_lora]
    styles = [s]
    images = 1

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
        styles,
        images,
    )

    assert len(jobs) == 1
    job = jobs[0]
    assert job.prompt == "This is a test prompt### This is a negative prompt"
    assert job.sampler_name == "test_sampler"
    assert job.cfg_scale == 7.5
    assert job.seed != 0
    assert job.width == 512
    assert job.height == 512
    assert job.clip_skip == 2
    assert job.steps == 50
    assert job.model == "test_model"
    assert job.karras
    assert not job.hires_fix
    assert job.loras == [style_lora.to_lora()]
