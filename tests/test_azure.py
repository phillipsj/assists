from assists.cloud.azure import get_az_cmd


def test_get_az_cmd():
    registry = "myregistry.azurecr.io"
    expected = f"az acr login --name {registry} --expose-token -o tsv --query accessToken"
    actual = get_az_cmd(registry)
    assert actual == expected
