import os
import shutil
import stat
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from platform import machine
from platform import system
from urllib import request

import hcl2
from semver import Version


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


class TerraformTool:
    def __init__(self, version: Version, config_path: Path):
        self.version: Version = version
        self.config_path: Path = config_path

        architecture = machine().lower()
        self.arch: str = "amd64" if architecture == "x86_64" else architecture
        self.platform_name: str = system().lower()
        self.download_file_name: str = f"terraform_{version}_{self.platform_name}_{self.arch}.zip"
        self.download_url: str = f"https://releases.hashicorp.com/terraform/{self.version}/{self.download_file_name}"
        self.tool_name: str = "terraform"
        self.tool_executable_name: str = self.tool_name if self.platform_name != "Windows" else f"{self.tool_name}.exe"

    @property
    def download_path(self) -> Path:
        return self.config_path / "downloads"

    @property
    def executable_path(self) -> Path:
        return self.tool_path / self.tool_executable_name

    @property
    def tool_path(self) -> Path:
        return self.config_path / "tools" / self.tool_name / str(self.version)

    def download(self):
        download_directory = self.download_path
        tool_directory = self.tool_path
        if download_directory.exists():
            shutil.rmtree(download_directory)

        download_directory.mkdir(parents=True, exist_ok=True)
        tool_directory.mkdir(parents=True, exist_ok=True)

        target_file = download_directory / self.download_file_name
        request.urlretrieve(self.download_url, target_file)

        with zipfile.ZipFile(target_file) as archive:
            archive.extractall(tool_directory)

        shutil.rmtree(download_directory)
        self.executable_path.chmod(stat.S_IEXEC)

    def run(self, commands: list[str]):
        if not self.executable_path.exists():
            self.download()
        print(self.executable_path)
        os.execv(self.executable_path, ["terraform"] + commands)

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
