# tests/test_job.py

import time

from hordeqt.civit.civit_api import BaseModel, ModelVersion, ModelVersionStats
from hordeqt.classes.Job import Job

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


def test_job_init():
    job = Job(
        prompt="test prompt",
        sampler_name="test sampler",
        cfg_scale=1.0,
        seed="123",
        width=512,
        height=512,
        clip_skip=1,
        steps=10,
        model="test model",
    )
    assert job.prompt == "test prompt"
    assert job.sampler_name == "test sampler"
    assert job.cfg_scale == 1.0
    assert job.seed == "123"
    assert job.width == 512
    assert job.height == 512
    assert job.clip_skip == 1
    assert job.steps == 10
    assert job.model == "test model"


def test_to_job_config():
    job = Job(
        prompt="test prompt",
        sampler_name="test sampler",
        cfg_scale=1.0,
        seed="123",
        width=512,
        height=512,
        clip_skip=1,
        steps=10,
        model="test model",
    )
    config = job.to_job_config()
    assert config["prompt"] == "test prompt"
    assert config["sampler_name"] == "test sampler"
    assert config["cfg_scale"] == 1.0
    assert config["seed"] == 123
    assert config["width"] == 512
    assert config["height"] == 512
    assert config["clip_skip"] == 1
    assert config["steps"] == 10
    assert config["model"] == "test model"


def test_to_json():
    job = Job(
        prompt="test prompt",
        sampler_name="test sampler",
        cfg_scale=1.0,
        seed="123",
        width=512,
        height=512,
        clip_skip=1,
        steps=10,
        model="test model",
    )
    json_data = job.to_json()
    assert json_data["prompt"] == "test prompt"
    assert json_data["params"]["sampler_name"] == "test sampler"
    assert json_data["params"]["cfg_scale"] == 1.0
    assert json_data["params"]["seed"] == "123"
    assert json_data["params"]["width"] == 512
    assert json_data["params"]["height"] == 512
    assert json_data["params"]["clip_skip"] == 1
    assert json_data["params"]["steps"] == 10
    assert json_data["models"] == ["test model"]


def test_from_json():
    json_data = {
        "prompt": "test prompt",
        "params": {
            "sampler_name": "test sampler",
            "cfg_scale": 1.0,
            "seed": "123",
            "width": 512,
            "height": 512,
            "clip_skip": 1,
            "steps": 10,
        },
        "models": ["test model"],
    }
    job = Job.from_json(json_data)
    assert job.prompt == "test prompt"
    assert job.sampler_name == "test sampler"
    assert job.cfg_scale == 1.0
    assert job.seed == "123"
    assert job.width == 512
    assert job.height == 512
    assert job.clip_skip == 1
    assert job.steps == 10
    assert job.model == "test model"


def test_serialize():
    job = Job(
        prompt="test prompt",
        sampler_name="test sampler",
        cfg_scale=1.0,
        seed="123",
        width=512,
        height=512,
        clip_skip=1,
        steps=10,
        model="test model",
    )
    serialized_data = job.serialize()
    assert serialized_data["prompt"] == "test prompt"
    assert serialized_data["params"]["sampler_name"] == "test sampler"
    assert serialized_data["params"]["cfg_scale"] == 1.0
    assert serialized_data["params"]["seed"] == "123"
    assert serialized_data["params"]["width"] == 512
    assert serialized_data["params"]["height"] == 512
    assert serialized_data["params"]["clip_skip"] == 1
    assert serialized_data["params"]["steps"] == 10
    assert serialized_data["models"] == ["test model"]
    assert "id" in serialized_data
    assert "horde_job_id" in serialized_data
    assert "queue_position" in serialized_data
    assert "wait_time" in serialized_data
    assert "mod_time" in serialized_data
    assert "creation_time" in serialized_data


def test_deserialize():
    serialized_data = {
        "prompt": "test prompt",
        "params": {
            "sampler_name": "test sampler",
            "cfg_scale": 1.0,
            "seed": "123",
            "width": 512,
            "height": 512,
            "clip_skip": 1,
            "steps": 10,
        },
        "models": ["test model"],
        "id": "test_id",
        "horde_job_id": "test_horde_id",
        "queue_position": 1,
        "wait_time": 10,
        "mod_time": 1234567,
        "creation_time": 1234560,
    }
    st = time.time()
    job = Job.deserialize(serialized_data)
    et = time.time()

    assert job.prompt == "test prompt"
    assert job.sampler_name == "test sampler"
    assert job.cfg_scale == 1.0
    assert job.seed == "123"
    assert job.width == 512
    assert job.height == 512
    assert job.clip_skip == 1
    assert job.steps == 10
    assert job.model == "test model"
    assert job.job_id == "test_id"
    assert job.horde_job_id == "test_horde_id"
    assert job.queue_position == 1
    assert job.wait_time == 10
    assert st < job.mod_time < et
    assert job.creation_time == 1234560


def test_update_status():
    job = Job(
        prompt="test prompt",
        sampler_name="test sampler",
        cfg_scale=1.0,
        seed="123",
        width=512,
        height=512,
        clip_skip=1,
        steps=10,
        model="test model",
    )
    status_data = {
        "done": True,
        "faulted": False,
        "kudos": 10,
        "queue_position": 2,
        "wait_time": 20,
    }
    job.update_status(status_data)
    assert job.done
    assert not job.faulted
    assert job.kudos == 10
    assert job.queue_position == 2
    assert job.wait_time == 20
    assert job.mod_time != job.creation_time
