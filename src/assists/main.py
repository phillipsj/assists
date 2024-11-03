from pathlib import Path

import typer

from assists.cloud import aws
from assists.cloud import azure
from assists.tools import TerraformTool

app = typer.Typer()
app.add_typer(aws.app, name="aws", help="AWS related tasks.")
app.add_typer(azure.app, name="az", help="Azure related tasks.")


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
    help="Detects, installs, and executes Terraform.",
)
def terraform(ctx: typer.Context):
    config_path = Path(typer.get_app_dir("assists"))
    tool = TerraformTool.from_terraform_config(config_path=config_path)
    tool.run(ctx.args)
