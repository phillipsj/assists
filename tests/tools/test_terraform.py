from io import BytesIO
from pathlib import Path
from string import Template
from unittest.mock import patch
from urllib import request

import pytest
from semver import Version

from assists.tools import TerraformTool


def test_get_terraform_releases():
    data = get_release_html()
    version_to_find = Version(1, 9, 3)
    with patch.object(request, "urlopen", return_value=data):
        versions = TerraformTool.get_terraform_releases()
        assert len(versions) == 1
        assert version_to_find in versions


def test_get_terraform_version(tmp_path):
    tf_path = create_terraform_tf("1.9.3", tmp_path / "src/terraform.tf")
    expected_version = "1.9.3"
    actual_version = TerraformTool.get_terraform_version(tf_path)
    assert actual_version == expected_version


def test_get_terraform_version_wrong(tmp_path: Path):
    tf_path = create_terraform_tf("1.9.3", tmp_path / "src/terraform.tf")
    expected_version = "1.9.2"
    actual_version = TerraformTool.get_terraform_version(tf_path)
    assert actual_version != expected_version


def test_get_terraform_version_should_throw_exception(tmp_path: Path):
    tf_path = create_terraform_tf(">= 1.2.0, < 2.0.0", tmp_path / "src/terraform.tf")
    with pytest.raises(ValueError, match="Greater than, but less than constraints are not supported"):
        TerraformTool.get_terraform_version(tf_path)


@pytest.mark.parametrize("path", ["src/terraform.tf", "src/iac/terraform/terraform.tf"])
def test_find_terraform_tf(path: str, tmp_path: Path):
    expected = tmp_path / path
    create_terraform_tf("1.9.3", expected)

    actual = TerraformTool.find_terraform_tf(tmp_path)
    assert actual == expected


def test_find_terraform_tf_should_throw_exception(tmp_path: Path):
    with pytest.raises(
        FileNotFoundError, match="Required file terraform.tf not found in current directory or any subdirectories."
    ):
        TerraformTool.find_terraform_tf(tmp_path)


@pytest.mark.parametrize(
    "version, expected", [("1.9.3", Version(1, 9, 3)), ("~>1.9.3", Version(1, 9, 4)), (">=1.9.3", Version(1, 9, 4))]
)
def test_get_constrained_version(version: str, expected: Version):
    versions = [Version(1, 9, 2), Version(1, 9, 3), Version(1, 9, 4)]
    actual = TerraformTool.get_constrained_version(version, versions)
    assert actual == expected


def test_from_terraform_config(tmp_path: Path):
    version = "1.9.3"
    file = tmp_path / "src/terraform.tf"
    create_terraform_tf(version, file)
    data = get_release_html()
    config_path = tmp_path / "app"
    with patch.object(request, "urlopen", return_value=data), patch.object(Path, "cwd", return_value=tmp_path):
        expected = TerraformTool(Version(1, 9, 3), config_path)
        actual = TerraformTool.from_terraform_config(config_path)
        assert actual == expected


def create_terraform_tf(version: str, terraform_file: Path) -> Path:
    terraform_tf = Template("""terraform {
                          required_version = "$version"
                      }
                   """)
    terraform_file.parent.mkdir(parents=True, exist_ok=True)
    terraform_file.touch()
    terraform_file.write_text(terraform_tf.substitute(version=version), encoding="utf-8")
    return terraform_file


def get_release_html() -> BytesIO:
    html = """<!DOCTYPE html>
            <html lang="us-en">
                <head>
                    <title>Terraform Versions | HashiCorp Releases</title>
                </head>
                <body>
                    <ul>
                        <li>
                        <a href="../">../</a>
                        </li>
                        <li>
                        <a href="/terraform/1.9.3/">terraform_1.9.3</a>
                        </li>
                    </ul>
                </body>
            </html>
            """
    return BytesIO(html.encode("utf-8"))
