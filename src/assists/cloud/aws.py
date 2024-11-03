import os

import typer
from typing_extensions import Annotated

app = typer.Typer()


@app.command()
def podman(
    registry: Annotated[str, typer.Argument(help="The registry to login to.")],
    profile: Annotated[str, typer.Option(help="The AWS profile to use.")] = "",
):
    """
    Login in to ECR with Podman.
    """
    region = get_region(registry)
    if profile:
        profile = f"--profile {profile} "
    cmd = f"{get_aws_cmd(region)} {profile}| podman login --username AWS --password-stdin {registry}"
    os.system(cmd)


@app.command()
def crane(
    registry: Annotated[str, typer.Argument(help="The registry to login to.")],
    profile: Annotated[str, typer.Option(help="The AWS profile to use.")] = "",
):
    """
    Login in to ECR with Crane.
    """
    region = get_region(registry)
    if profile:
        profile = f"--profile {profile} "
    cmd = f"{get_aws_cmd(region)} {profile}| crane auth login --username AWS --password-stdin {registry}"
    os.system(cmd)


def get_aws_cmd(region: str) -> str:
    return f"aws ecr get-login-password --region {region}"


def get_region(registry: str) -> str:
    return registry.split(".")[-3]
