import os
import platform
import shutil
import stat
import zipfile
from html.parser import HTMLParser
from urllib import request

import hcl2
import typer
from semver import Version

BASE_DIR = os.path.dirname(__file__)
TERRAFORM_EXECUTABLE_NAME_NIX = "terraform"
TERRAFORM_EXECUTABLE_NAME_WIN = "terraform.exe"
TERRAFORM_EXECUTABLE_NAME = (
    TERRAFORM_EXECUTABLE_NAME_NIX if platform.system().lower() != "Windows" else TERRAFORM_EXECUTABLE_NAME_WIN
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


def find_terraform_tf() -> str:
    """Searches the current directory and any subdirectories for terraform.tf."""
    for root, dirs, files in os.walk("."):
        if "terraform.tf" in files:
            return os.path.join(root, "terraform.tf")


def get_terraform_version(file: str) -> str:
    with open(file) as file:
        hcl = hcl2.load(file)
        return hcl["terraform"][0]["required_version"]


def get_terraform_releases() -> list[Version]:
    url = "https://releases.hashicorp.com/terraform/"
    response = request.urlopen(url)
    html = response.read().decode("utf-8")
    parser = TerraformReleasesParser()
    parser.feed(html)
    return parser.versions


def download(version: str):
    download_directory = f"{typer.get_app_dir(".assists")}/downloads"
    extract_directory = f"{typer.get_app_dir(".assists")}/lib"

    if os.path.exists(download_directory):
        shutil.rmtree(
            download_directory,
        )

    platform_name = platform.system().lower()
    architecture = platform.machine().lower()
    arch = "amd64" if architecture == "x86_64" else architecture
    file_name = f"terraform_{version}_{platform_name}_{arch}.zip"
    download_url = f"https://releases.hashicorp.com/terraform/{version}/{file_name}"

    os.makedirs(download_directory, exist_ok=True)
    os.makedirs(extract_directory, exist_ok=True)

    target_file = f"{download_directory}/{file_name}"
    request.urlretrieve(download_url, target_file)

    with zipfile.ZipFile(target_file) as archive:
        archive.extractall(extract_directory)

    shutil.rmtree(download_directory)
    executable_path = f"{extract_directory}/{TERRAFORM_EXECUTABLE_NAME}"
    executable_stat = os.stat(executable_path)
    os.chmod(executable_path, executable_stat.st_mode | stat.S_IEXEC)


def run(commands: list[str]):
    terraform_file = find_terraform_tf()
    terraform_version = get_terraform_version(terraform_file)
    if "," in terraform_version:
        raise ValueError(
            "Greater than, but less than constraints are not supported. See https://developer.hashicorp.com/terraform/tutorials/configuration-language/versions#terraform-version-constraints"
        )

    version = terraform_version.strip()

    versions = get_terraform_releases()

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

    download(version)
    print(TERRAFORM_EXECUTABLE)
    os.execv(TERRAFORM_EXECUTABLE, ["terraform"] + commands)
