from copy import copy

from hordeqt.civit.civit_api import ModelVersion, ModelVersionStats
from hordeqt.civit.civit_enums import BaseModel
from hordeqt.classes.LoRA import LoRA

test_model_version = ModelVersion(
    10,
    "Foo_version",
    "foo_status",
    BaseModel.StableDiffusion2_1,
    "",
    ModelVersionStats(1, 1, 1),
    [],
    [],
    "https://example.com",
)


def test_init():
    lora = LoRA("test_name", 1, 0.5, 0.5, copy(test_model_version))
    assert lora.name == "test_name"
    assert lora.version_id == 1
    assert lora.strength == 0.5
    assert lora.clip_strength == 0.5
    assert isinstance(lora.model_version, ModelVersion)
    assert lora.inject_trigger is None


def test_from_ModelVersion():
    model_version = copy(test_model_version)
    lora = LoRA.from_ModelVersion("test_name", model_version)
    assert lora.name == "test_name"
    assert lora.version_id == model_version.id
    assert lora.strength == 1
    assert lora.clip_strength == 1
    assert lora.model_version == model_version
    assert lora.inject_trigger is None


def test_to_job_format():
    lora = LoRA("test_name", 1, 0.5, 0.5, copy(test_model_version))
    job_format = lora.to_job_format()
    assert job_format["name"] == "1"
    assert job_format["model"] == 0.5
    assert job_format["clip"] == 0.5
    assert job_format["is_version"] is True
    assert "inject_trigger" not in job_format

    lora.inject_trigger = "  test_trigger  "
    job_format = lora.to_job_format()
    assert job_format["inject_trigger"] == "test_trigger"


def test_serialize():
    lora = LoRA("test_name", 1, 0.5, 0.5, copy(test_model_version))
    serialized = lora.serialize()
    assert serialized["name"] == "test_name"
    assert serialized["id"] == 1
    assert serialized["strength"] == 0.5
    assert serialized["clip_strength"] == 0.5
    assert serialized["inject_trigger"] is None
    assert isinstance(serialized["model_version"], dict)


def test_deserialize():
    serialized = {
        "name": "test_name",
        "id": 1,
        "strength": 0.5,
        "clip_strength": 0.5,
        "inject_trigger": "test_trigger",
        "model_version": {"id": 1, "name": "test_model_version"},
    }
    lora = LoRA.deserialize(serialized)
    assert lora.name == "test_name"
    assert lora.version_id == 1
    assert lora.strength == 0.5
    assert lora.clip_strength == 0.5
    assert lora.inject_trigger == "test_trigger"
    assert isinstance(lora.model_version, ModelVersion)
