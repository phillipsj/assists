import os
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

    def download(self):
        download_directory = self.config_path / "downloads"
        tools_directory = self.config_path / "tools"
        if os.path.exists(download_directory):
            shutil.rmtree(
                download_directory,
            )

        os.makedirs(download_directory, exist_ok=True)
        os.makedirs(tools_directory, exist_ok=True)

        target_file = f"{download_directory}/{self.download_file_name}"
        request.urlretrieve(self.download_url, target_file)

        with zipfile.ZipFile(target_file) as archive:
            archive.extractall(tools_directory)

        shutil.rmtree(download_directory)
        self.executable_path = f"{tools_directory}/{self.tool_executable_name}"
        executable_stat = os.stat(self.executable_path)
        os.chmod(self.executable_path, executable_stat.st_mode | stat.S_IEXEC)

    @abstractmethod
    def run(self, commands: list[str]):
        pass
