from pathlib import Path
from typing import List
from typing import Optional

import typer
from typing_extensions import Annotated

from assists import aws
from assists import azure
from assists.iac.terraform import TerraformTool

app = typer.Typer()
app.add_typer(aws.app, name="aws", help="AWS related tasks.")
app.add_typer(azure.app, name="az", help="Azure related tasks.")


@app.command()
def terraform(commands: Annotated[Optional[List[str]], typer.Argument()] = None):
    config_path = Path(typer.get_app_dir("assists"))
    tool = TerraformTool.from_terraform_config(config_path=config_path)
    tool.run(commands)
