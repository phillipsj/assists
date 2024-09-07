from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class S3Url:
    """Class for parsing an S3 Url in the format S3://<bucket>/<key>"""

    bucket: str
    key: str
    url: str

    def __init__(self, s3_url: str):
        if not s3_url:
            raise ValueError("S3 URL must be provided.")

        parsed = urlparse(s3_url, allow_fragments=False)
        if not parsed.netloc and not parsed.path:
            raise ValueError("S3 URL is not valid.")

        self.url = parsed.geturl()
        self.bucket = parsed.netloc
        self.key = parsed.path.lstrip("/")
