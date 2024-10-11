import shutil
import stat
import zipfile
from abc import ABCMeta
from abc import abstractmethod
from pathlib import Path
from platform import machine
from platform import system
from urllib import request


class Tool(metaclass=ABCMeta):
    def __init__(self, config_path: Path):
        self.executable_path = ""
        self.platform_name = system().lower()
        architecture = machine().lower()
        self.arch = "amd64" if architecture == "x86_64" else architecture
        self.config_path = config_path
        self.download_file_name = ""
        self.download_url = ""
        self.tool_executable_name = ""
        self.tool_name = ""
        self.version = ""

    def download(self, tools_prefix: Path):
        download_directory = self.config_path / "downloads"
        tools_directory = self.config_path / "tools" / tools_prefix
        if download_directory.exists():
            shutil.rmtree(
                download_directory,
            )

        download_directory.mkdir(parents=True, exist_ok=True)
        tools_directory.mkdir(parents=True, exist_ok=True)

        target_file = download_directory / self.download_file_name
        request.urlretrieve(self.download_url, target_file)

        with zipfile.ZipFile(target_file) as archive:
            archive.extractall(tools_directory)

        shutil.rmtree(download_directory)
        self.executable_path = tools_directory / self.tool_executable_name
        self.executable_path.chmod(stat.S_IEXEC)

    @abstractmethod
    def run(self, commands: list[str]):
        pass
