import os
from html.parser import HTMLParser
from pathlib import Path
from urllib import request

import hcl2
from semver import Version

from assists.base.tool import Tool


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
        super().__init__(config_path)
        self.version = version
        self.tool_name = "terraform"
        self.download_file_name = f"terraform_{self.version}_{self.platform_name}_{self.arch}.zip"
        self.download_url = f"https://releases.hashicorp.com/terraform/{self.version}/{self.download_file_name}"
        self.tool_executable_name = self.tool_name if self.platform_name != "Windows" else f"{self.tool_name}.exe"

    @classmethod
    def find_terraform_tf(cls) -> str:
        """Searches the current directory and any subdirectories for terraform.tf."""
        for root, _dirs, files in os.walk("."):
            if "terraform.tf" in files:
                return os.path.join(root, "terraform.tf")

    @classmethod
    def get_terraform_version(cls, file: str) -> str:
        with open(file) as file:
            hcl = hcl2.load(file)
            return hcl["terraform"][0]["required_version"]

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
        if "," in terraform_version:
            raise ValueError(
                "Greater than, but less than constraints are not supported. See https://developer.hashicorp.com/terraform/tutorials/configuration-language/versions#terraform-version-constraints"
            )

        version = terraform_version.strip()

        versions = cls.get_terraform_releases()

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
        return TerraformTool(version, config_path)

    def run(self, commands: list[str]):
        self.download()
        print(self.executable_path)
        os.execv(self.executable_path, ["terraform"] + commands)
