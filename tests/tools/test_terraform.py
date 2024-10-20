from io import BytesIO
from pathlib import Path
from string import Template
from unittest.mock import patch
from urllib import request

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from semver import Version

from assists.tools import TerraformTool


def test_get_terraform_releases():
    data = get_release_html()
    version_to_find = Version(1, 9, 3)
    with patch.object(request, "urlopen", return_value=data):
        versions = TerraformTool.get_terraform_releases()
        assert len(versions) == 1
        assert version_to_find in versions


def test_get_terraform_version(fs):
    tf_path = create_terraform_tf(fs, "1.9.3")
    expected_version = "1.9.3"
    actual_version = TerraformTool.get_terraform_version(tf_path)
    assert actual_version == expected_version


def test_get_terraform_version_wrong(fs):
    tf_path = create_terraform_tf(fs, "1.9.3")
    expected_version = "1.9.2"
    actual_version = TerraformTool.get_terraform_version(tf_path)
    assert actual_version != expected_version


def test_get_terraform_version_should_throw_exception(fs):
    tf_path = create_terraform_tf(fs, ">= 1.2.0, < 2.0.0")
    with pytest.raises(ValueError, match="Greater than, but less than constraints are not supported"):
        TerraformTool.get_terraform_version(tf_path)


def test_find_terraform_tf(fs):
    expected = Path("/src/terraform.tf")
    fs.create_file("/src/terraform.tf")
    actual = TerraformTool.find_terraform_tf()
    assert actual == expected


def test_find_terraform_tf_nested(fs):
    expected = Path("/src/iac/terraform/terraform.tf")
    fs.create_file("/src/iac/terraform/terraform.tf")
    actual = TerraformTool.find_terraform_tf()
    assert actual == expected


def create_terraform_tf(fs: FakeFilesystem, version) -> Path:
    path = Path("/src/terraform.tf")
    terraform_tf = Template("""terraform {
                          required_version = "$version"
                      }
                   """)
    fs.create_file(path, contents=terraform_tf.substitute(version=version))
    return path


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
