import json

from PIL import ExifTags, Image

from hordeqt.classes.Job import Job
from hordeqt.classes.LocalJob import LocalJob, apply_metadata_to_image


def test_LocalJob_init():
    job = Job(
        prompt="test prompt",
        model="test model",
        steps=10,
        sampler_name="test sampler",
        cfg_scale=1.0,
        clip_skip=True,
        width=512,
        height=512,
        seed="",
    )
    job.job_id = "test_id"
    lj = LocalJob(job)
    assert lj.id == "test_id"
    assert lj.original == job
    assert lj.file_type == "webp"
    assert lj.path.suffix == ".webp"


def test_LocalJob_load_from_metadata():
    metadata = {
        "job": {
            "id": "test_id",
            "prompt": "test prompt",
            "model": "test model",
            "steps": 10,
            "sampler_name": "test sampler",
            "cfg_scale": 1.0,
            "clip_skip": True,
            "width": 512,
            "height": 512,
        }
    }
    lj = LocalJob.load_from_metadata(metadata)

    assert lj.original.prompt == "test prompt"
    assert lj.file_type == "webp"


def test_LocalJob_convert_to_metadata():
    job = Job(
        prompt="test prompt",
        model="test model",
        steps=10,
        sampler_name="test sampler",
        cfg_scale=1.0,
        clip_skip=True,
        width=512,
        height=512,
        seed="",
    )
    job.job_id = "test_id"
    lj = LocalJob(job)
    metadata = lj.convert_to_metadata()
    assert metadata["Application"] == "HordeQT"
    assert metadata["job"] == job.serialize()
    assert metadata["id"] == "test_id"
    assert metadata["worker"] == "Unknown (00000000-0000-0000-0000-000000000000)"


def test_LocalJob_pretty_format():
    job = Job(
        prompt="test prompt",
        model="test model",
        steps=10,
        sampler_name="test sampler",
        cfg_scale=1.0,
        clip_skip=True,
        width=512,
        height=512,
        seed="",
    )
    job.job_id = "test_id"
    lj = LocalJob(job)
    pretty_format = lj.pretty_format()
    assert "Prompt: test prompt" in pretty_format
    assert "Model: test model" in pretty_format
    assert "Steps: 10" in pretty_format
    assert "Sampler: test sampler" in pretty_format
    assert "Guidence: 1.0" in pretty_format
    assert "CLIP Skip: True" in pretty_format
    assert "Size: 512 x 512 (WxH)" in pretty_format


def test_LocalJob_serialize():
    job = Job(
        prompt="test prompt",
        model="test model",
        steps=10,
        sampler_name="test sampler",
        cfg_scale=1.0,
        clip_skip=True,
        width=512,
        height=512,
        seed="",
    )
    job.job_id = "test_id"
    lj = LocalJob(job)
    serialized = lj.serialize()
    assert serialized["id"] == "test_id"
    assert serialized["original"] == job.serialize()
    assert serialized["fileType"] == "webp"
    assert serialized["path"] == str(lj.path)
    assert serialized["completed_at"] > 0
    assert serialized["worker_id"] == "00000000-0000-0000-0000-000000000000"
    assert serialized["worker_name"] == "Unknown"


def test_LocalJob_deserialize():
    serialized = {
        "id": "test_id",
        "original": {
            "id": "test_id",
            "prompt": "test prompt",
            "model": "test model",
            "steps": 10,
            "sampler_name": "test sampler",
            "cfg_scale": 1.0,
            "clip_skip": True,
            "width": 512,
            "height": 512,
        },
        "fileType": "webp",
        "path": "path/to/image.webp",
        "completed_at": 1643723400,
        "worker_id": "00000000-0000-0000-0000-000000000000",
        "worker_name": "Unknown",
    }
    lj = LocalJob.deserialize(serialized)
    assert lj.original.prompt == "test prompt"
    assert lj.file_type == "webp"
    assert lj.path.suffix == ".webp"


def test_apply_metadata_to_image(tmp_path):
    image_path = tmp_path / "image.webp"
    Image.new("RGB", (512, 512)).save(image_path)
    job = Job(
        prompt="test prompt",
        model="test model",
        steps=10,
        sampler_name="test sampler",
        cfg_scale=1.0,
        clip_skip=True,
        width=512,
        height=512,
        seed="",
    )
    job.job_id = "test_id"
    lj = LocalJob(job)
    new_path = apply_metadata_to_image(image_path, lj)
    assert new_path == lj.path
    im = Image.open(new_path)
    exif = im.getexif()
    assert exif[ExifTags.Base.Software] == "HordeQT"
    assert json.loads(exif[ExifTags.Base.ImageDescription]) == lj.convert_to_metadata()
    assert exif[ExifTags.Base.UserComment] == lj.pretty_format()
