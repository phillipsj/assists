from typing import Tuple

import boto3
import typer
from typing_extensions import Annotated

from assists.models.s3url import S3Url

app = typer.Typer()


# https://docs.aws.amazon.com/AmazonS3/latest/userguide/specify-batchjob-manifest-xaccount-csv.html
@app.command()
def copy(
    names: Annotated[Tuple[str, str], typer.Argument(help="S3Uri S3Uri")],
    role_arn: Annotated[str, typer.Argument(help("The role arn for the batch job to use."))],
    job_bucket: Annotated[str, typer.Option(help="The bucket for storing job manifests and reports")],
    profile: Annotated[str, typer.Option(help="The AWS profile to use.")] = "",
):
    """
    Creates a copy S3 Batch Job and returns the job id.
    """
    source = S3Url(names[0])
    destination = S3Url(names[1])

    session = boto3.session.Session(profile_name=profile)
    sts = session.client("sts")
    client = session.client("s3control")
    response = client.create_job(
        AccountId=sts.get_caller_identity()["Account"],
        ConfirmationRequired=False,
        Operation={
            "S3PutObjectCopy": {
                "TargetResource": destination.bucket,
                "TargetKeyPrefix": destination.key,
                "MetadataDirective": "COPY",
                "CannedAccessControlList": "bucket-owner-full-control",
            }
        },
        Report={
            "Bucket": job_bucket,
            "Format": "Report_CSV_20180820",
            "Enabled": True,
            "Prefix": "reports",
            "ReportScope": "FailedTasksOnly",
        },
        ManifestGenerator={
            "S3JobManifestGenerator": {
                "SourceBucket": source.bucket,
                "EnableManifestOutput": True,
                "ManifestOutputLocation": {
                    "Bucket": job_bucket,
                    "ManifestPrefix": "manifests",
                    "ManifestFormat": "S3InventoryReport_CSV_20211130",
                },
                "Filter": {
                    "KeyNameConstraint": {
                        "MatchAnyPrefix": [
                            source.key,
                        ]
                    }
                },
            }
        },
        Description=f"Copy batch job from {source.url} to {destination.url}.",
        Priority=3,
        RoleArn=role_arn,
    )

    return response["JobId"]
