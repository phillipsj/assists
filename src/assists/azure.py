import os

import typer
from typing_extensions import Annotated

app = typer.Typer()

USER_PLACEHOLDER = "00000000-0000-0000-0000-000000000000"


@app.command()
def podman(registry: Annotated[str, typer.Argument(help="The registry to login to.")]):
    """
    Login in to ACR with Podman.
    """
    os.system(f'podman login {registry} -u {USER_PLACEHOLDER} -p "$({get_az_cmd(registry)})"')


@app.command()
def crane(registry: Annotated[str, typer.Argument(help="The registry to login to.")]):
    """
    Login in to ACR with Crane.
    """
    os.system(f'crane auth login {registry} -u {USER_PLACEHOLDER} -p "$({get_az_cmd(registry)})"')


def get_az_cmd(registry: str) -> str:
    return f"az acr login --name {registry} --expose-token -o tsv --query accessToken"
