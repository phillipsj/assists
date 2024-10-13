from html.parser import HTMLParser
from pathlib import Path
from platform import machine
from platform import system
from urllib import request

import hcl2
from semver import Version

from assists.tools.tool import Tool
from assists.tools.tool_config import ToolConfig


class TerraformReleasesParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_tag = None
        self.versions = []

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag

    def handle_data(self, data):
        if self.current_tag == "a" and "terraform_" in data:
            clean_text = data.replace("terraform_", "")
            version = Version.parse(clean_text)
            if version.prerelease is None:
                self.versions.append(version)


class TerraformTool(Tool):
    def __init__(self, version: Version, config_path: Path):
        arch: str = "amd64" if machine().lower() == "x86_64" else machine().lower()
        platform_name: str = system().lower()
        download_file_name = f"terraform_{version}_{platform_name}_{arch}.zip"
        download_url = f"https://releases.hashicorp.com/terraform/{version}/{download_file_name}"
        tool_name = "terraform"
        tool_executable_name = tool_name if platform_name != "Windows" else f"{tool_name}.exe"

        config = ToolConfig(
            config_path=config_path,
            download_file_name=download_file_name,
            download_url=download_url,
            tool_executable_name=tool_executable_name,
            tool_name=tool_name,
            version=version,
        )

        super().__init__(config)

    @classmethod
    def find_terraform_tf(cls) -> Path:
        """Searches the current directory and any subdirectories for terraform.tf."""
        for root, _dirs, files in Path.cwd().walk():
            if "terraform.tf" in files:
                return root / "terraform.tf"

    @classmethod
    def get_terraform_version(cls, file: Path) -> str:
        with file.open() as f:
            hcl = hcl2.load(f)
            required_version = hcl["terraform"][0]["required_version"]
            if "," in required_version:
                raise ValueError(
                    "Greater than, but less than constraints are not supported. See https://developer.hashicorp.com/terraform/tutorials/configuration-language/versions#terraform-version-constraints"
                )
            return required_version

    @classmethod
    def get_terraform_releases(cls) -> list[Version]:
        url = "https://releases.hashicorp.com/terraform/"
        response = request.urlopen(url)
        html = response.read().decode("utf-8")
        parser = TerraformReleasesParser()
        parser.feed(html)
        return parser.versions

    @classmethod
    def from_terraform_config(cls, config_path: Path):
        terraform_file = cls.find_terraform_tf()
        terraform_version = cls.get_terraform_version(terraform_file)
        versions = cls.get_terraform_releases()
        version = cls.get_constrained_version(terraform_version, versions)
        return TerraformTool(version, config_path)

    @classmethod
    def get_constrained_version(cls, terraform_version, versions):
        version = terraform_version.strip()
        if "~>" in terraform_version:
            version = terraform_version.split("~>")[1].strip()
            parsed_version = Version.parse(version)
            matched_versions = []
            for v in versions:
                if v.is_compatible(parsed_version):
                    matched_versions.append(v)
            version = max(matched_versions)
            print(version)
        elif ">=" in terraform_version:
            max_version = max(versions)
            if max_version.match(terraform_version.replace(" ", "")):
                print(max_version)
                version = max_version
        return version
