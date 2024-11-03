from unittest.mock import patch

from typer.testing import CliRunner

from assists.cloud.azure import USER_PLACEHOLDER
from assists.main import app

runner = CliRunner()


@patch("os.system")
def test_aws_cmd_podman(mock_system):
    region = "us-east-1"
    registry = f"00000000.dkr.ecr.{region}.amazonaws.com"
    expected = (
        f"aws ecr get-login-password --region {region} " f"| podman login --username AWS --password-stdin {registry}"
    )
    actual = runner.invoke(app, ["aws", "podman", registry])
    assert actual.exit_code == 0
    mock_system.assert_called_once_with(expected)


@patch("os.system")
def test_aws_cmd_podman_with_profile(mock_system):
    region = "us-east-1"
    profile = "my-profile"
    registry = f"00000000.dkr.ecr.{region}.amazonaws.com"
    expected = (
        f"aws ecr get-login-password --region {region} --profile {profile} "
        f"| podman login --username AWS --password-stdin {registry}"
    )
    actual = runner.invoke(app, ["aws", "podman", registry, "--profile", profile])
    assert actual.exit_code == 0
    mock_system.assert_called_once_with(expected)


@patch("os.system")
def test_aws_cmd_crane(mock_system):
    region = "us-east-1"
    registry = f"00000000.dkr.ecr.{region}.amazonaws.com"
    expected = (
        f"aws ecr get-login-password --region {region} "
        f"| crane auth login --username AWS --password-stdin {registry}"
    )
    actual = runner.invoke(app, ["aws", "crane", registry])
    assert actual.exit_code == 0
    mock_system.assert_called_once_with(expected)


@patch("os.system")
def test_aws_cmd_crane_with_profile(mock_system):
    region = "us-east-1"
    profile = "my-profile"
    registry = f"00000000.dkr.ecr.{region}.amazonaws.com"
    expected = (
        f"aws ecr get-login-password --region {region} --profile {profile} "
        f"| crane auth login --username AWS --password-stdin {registry}"
    )
    actual = runner.invoke(app, ["aws", "crane", registry, "--profile", profile])
    assert actual.exit_code == 0
    mock_system.assert_called_once_with(expected)


@patch("os.system")
def test_az_cmd_podman(mock_system):
    registry = "myregistry.azurecr.io"
    expected = (
        f'podman login {registry} -u {USER_PLACEHOLDER} -p "$(az acr login --name {registry} '
        f'--expose-token -o tsv --query accessToken)"'
    )
    actual = runner.invoke(app, ["az", "podman", registry])
    assert actual.exit_code == 0
    mock_system.assert_called_once_with(expected)


@patch("os.system")
def test_az_cmd_crane(mock_system):
    registry = "myregistry.azurecr.io"
    expected = (
        f'crane auth login {registry} -u {USER_PLACEHOLDER} -p "$(az acr login --name {registry} '
        f'--expose-token -o tsv --query accessToken)"'
    )
    actual = runner.invoke(app, ["az", "crane", registry])
    assert actual.exit_code == 0
    mock_system.assert_called_once_with(expected)
