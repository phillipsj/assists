import os
from html.parser import HTMLParser
from pathlib import Path
from urllib import request

import hcl2
import typer
from semver import Version

from assists.base.tool import Tool

TERRAFORM_EXECUTABLE_NAME = (

)
TERRAFORM_EXECUTABLE = os.path.join(typer.get_app_dir(".assists"), f"lib/{TERRAFORM_EXECUTABLE_NAME}")


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
    def __init__(self, config_path: Path):
        super().__init__(config_path)
        self.version = None
        self.tool_name = "terraform"
        self.download_file_name = f"terraform_{self.version}_{self.platform_name}_{self.arch}.zip"
        self.download_url = f"https://releases.hashicorp.com/terraform/{self.version}/{self.download_file_name}"
        self.tool_executable_name = self.tool_name if self.platform_name != "Windows" else f"{self.tool_name}.exe"

    def find_terraform_tf(self) -> str:
        """Searches the current directory and any subdirectories for terraform.tf."""
        for root, dirs, files in os.walk("."):
            if "terraform.tf" in files:
                return os.path.join(root, "terraform.tf")


    def get_terraform_version(self, file: str) -> str:
        with open(file) as file:
            hcl = hcl2.load(file)
            return hcl["terraform"][0]["required_version"]


    def get_terraform_releases(self) -> list[Version]:
        url = "https://releases.hashicorp.com/terraform/"
        response = request.urlopen(url)
        html = response.read().decode("utf-8")
        parser = TerraformReleasesParser()
        parser.feed(html)
        return parser.versions





    def run(self, commands: list[str]):
        terraform_file = self.find_terraform_tf()
        terraform_version = self.get_terraform_version(terraform_file)
        if "," in terraform_version:
            raise ValueError(
                "Greater than, but less than constraints are not supported. See https://developer.hashicorp.com/terraform/tutorials/configuration-language/versions#terraform-version-constraints"
            )

        self.version = terraform_version.strip()

        versions = self.get_terraform_releases()

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

        self.download()
        print(TERRAFORM_EXECUTABLE)
        os.execv(TERRAFORM_EXECUTABLE, ["terraform"] + commands)
