import os
import shutil
import stat
import zipfile
from abc import ABCMeta
from abc import abstractmethod
from urllib import request

from assists.tools.tool_config import ToolConfig


class Tool(metaclass=ABCMeta):
    """
    Base class for all tools.
    """

    def __init__(self, config: ToolConfig):
        self.config = config
        self.executable_path = ""

    def download(self):
        download_directory = self.config.download_path
        tool_directory = self.config.tool_path
        if download_directory.exists():
            shutil.rmtree(download_directory)

        download_directory.mkdir(parents=True, exist_ok=True)
        tool_directory.mkdir(parents=True, exist_ok=True)

        target_file = download_directory / self.config.download_file_name
        request.urlretrieve(self.config.download_url, target_file)

        with zipfile.ZipFile(target_file) as archive:
            archive.extractall(tool_directory)

        shutil.rmtree(download_directory)
        self.config.excutable_path.chmod(stat.S_IEXEC)

    @abstractmethod
    def run(self, commands: list[str]):
        self.download()
        print(self.config.executable_path)
        os.execv(self.config.executable_path, ["terraform"] + commands)
