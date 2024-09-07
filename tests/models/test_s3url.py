import pytest

from assists.models.s3url import S3Url


def test_create_s3url():
    parsed = S3Url("S3://mybucket.com/my/path")
    assert parsed.bucket == "mybucket.com"
    assert parsed.key == "my/path"


def test_create_s3url_with_empty_url():
    with pytest.raises(ValueError) as e:
        S3Url("")
    assert e.value.args[0] == "S3 URL must be provided."


def test_create_s3url_with_invalid_url():
    with pytest.raises(ValueError) as e:
        S3Url("S3://")
    assert e.value.args[0] == "S3 URL is not valid."
