from hordeqt.other.job_util import get_horde_metadata_pretty


def test_csam_failure():
    val = {
        "prompt": "A beautiful landscape",
        "job_id": "12345",
        "generations": [
            {
                "gen_metadata": [
                    {"type": "censorship", "value": "csam"},
                ]
            }
        ],
    }
    expected_output = (
        "Result was censored due to the Horde's filtering (12345:A beautiful landscape)"
    )
    assert get_horde_metadata_pretty(val) == expected_output


def test_nsfw_failure():
    val = {
        "prompt": "A beautiful landscape",
        "job_id": "12345",
        "generations": [
            {
                "gen_metadata": [
                    {"type": "censorship", "value": "csam"},
                ]
            }
        ],
    }
    expected_output = (
        "Result was censored due to the Horde's filtering (12345:A beautiful landscape)"
    )
    assert get_horde_metadata_pretty(val) == expected_output


def test_lora_failure():
    val = {
        "prompt": "A beautiful landscape",
        "job_id": "12345",
        "generations": [
            {
                "gen_metadata": [
                    {"type": "lora", "value": "download_failed"},
                ]
            }
        ],
    }
    expected_output = "LoRA(s) failed to download (12345:A beautiful landscape)"
    assert get_horde_metadata_pretty(val) == expected_output


def test_lora_baseline_failure():
    val = {
        "prompt": "A beautiful landscape",
        "job_id": "12345",
        "generations": [
            {
                "gen_metadata": [
                    {"type": "lora", "value": "baseline_mismatch"},
                ]
            }
        ],
    }
    expected_output = (
        "LoRA(s) were used on the wrong baseline (12345:A beautiful landscape)"
    )
    assert get_horde_metadata_pretty(val) == expected_output
