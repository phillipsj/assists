from io import BytesIO
from unittest.mock import patch
from urllib import request

from semver import Version

from assists.tools import TerraformTool


def test_get_terraform_releases():
    data = get_test_html()
    version_to_find = Version(1, 9, 3)
    with patch.object(request, "urlopen", return_value=data):
        versions = TerraformTool.get_terraform_releases()
        assert len(versions) == 1
        assert version_to_find in versions


def get_test_html() -> BytesIO:
    html = """<!DOCTYPE html>
            <html lang="us-en">
                <head>
                    <title>Terraform Versions | HashiCorp Releases</title>
                </head>
                <body>
                    <ul>
                        <li>
                        <a href="../">../</a>
                        </li>
                        <li>
                        <a href="/terraform/1.9.3/">terraform_1.9.3</a>
                        </li>
                    </ul>
                </body>
            </html>
            """
    return BytesIO(html.encode("utf-8"))
