import typer

from assists import aws
from assists import azure

app = typer.Typer()
app.add_typer(aws.app, name="aws", help="AWS related tasks.")
app.add_typer(azure.app, name="az", help="Azure related tasks.")
