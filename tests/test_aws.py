from assists.cloud.aws import get_aws_cmd
from assists.cloud.aws import get_region


def test_get_aws_cmd():
    expected = "aws ecr get-login-password --region us-east-1"
    actual = get_aws_cmd("us-east-1")
    assert actual == expected


def test_get_region():
    expected = "us-east-1"
    ecr_name = "00000000.dkr.ecr.us-east-1.amazonaws.com"
    actual = get_region(ecr_name)
    assert actual == expected
