from dataclasses import dataclass
from pathlib import Path
from platform import system, machine

from semver import Version

@dataclass(frozen=True)
class ToolConfig():
    """
    Handles the necessary configuration for a Tool.
    """
    config_path: Path
    download_file_name: str
    download_url: str
    tool_executable_name: str
    tool_name: str
    version: Version
    arch: str = "amd64" if machine().lower() == "x86_64" else machine().lower()
    platform_name: str = system().lower()

    @property
    def download_path(self) -> Path:
        return self.config_path / "downloads"

    @property
    def executable_path(self) -> Path:
        return self.tool_path / self.tool_executable_name

    @property
    def tool_path(self) -> Path:
        return self.config_path / "tools" / self.tool_name / str(self.version)
