from typing import List
from typing import Optional

import typer
from typing_extensions import Annotated

import assists
from assists import aws
from assists import azure
from assists.iac import terraform

app = typer.Typer()
app.add_typer(aws.app, name="aws", help="AWS related tasks.")
app.add_typer(azure.app, name="az", help="Azure related tasks.")


@app.command()
def terraform(commands: Annotated[Optional[List[str]], typer.Argument()] = None):
    assists.iac.terraform.run(commands)
