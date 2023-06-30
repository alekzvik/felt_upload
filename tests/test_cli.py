import pytest
from typer.testing import CliRunner

from felt_upload.cli import app
from responses import matchers

runner = CliRunner(env={"FELT_TOKEN": "123"})
URL = "https://felt.com/api/v1/"


@pytest.fixture
def file_creator(tmp_path):
    def create_file(filename, content):
        path = tmp_path / filename
        with path.open("w") as f:
            f.write(content)
        return path

    return create_file


@pytest.mark.parametrize("command", ["user", "map"])
def test_no_token_param(command):
    result = runner.invoke(app, [command], env={"FELT_TOKEN": None})

    assert result.exit_code == 2
    assert "Missing option '--token'" in result.stdout, result.stdout


@pytest.mark.parametrize("command", ["user", "map"])
def test_token_param_option(command):
    result = runner.invoke(app, [command, "--token", "123"], env={"FELT_TOKEN": None})

    assert "Missing option '--token'" not in result.stdout


def test_auth_headers(mocked_responses):
    mocked_responses.get(
        f"{URL}user",
        match=[matchers.header_matcher({"authorization": "Bearer TOKEN"})],
    )

    runner.invoke(app, ["user", "--token", "TOKEN"])


def test_user(mocked_responses):
    mocked_responses.get(
        f"{URL}user",
        json={
            "data": {
                "attributes": {"name": "Alice", "email": "alice@example.com"},
                "id": "lsaN9C9BxxRhO2uC0D0vBktC",
                "type": "user",
            }
        },
    )
    result = runner.invoke(app, ["user"])
    assert result.exit_code == 0
    assert "Alice <alice@example.com>" in result.stdout


def test_user_unauthorized(mocked_responses):
    mocked_responses.get(
        f"{URL}user",
        status=401,
    )
    result = runner.invoke(app, ["user"])
    assert result.exit_code == 2
    assert "401 Unauthorized" in result.stdout


def test_only_map(mocked_responses):
    map_id = "8URXebFKSDuq5PLFC29BB1A"
    map_url = "https://felt.com/map/Felt-map-YLYztqPrTG69C5vOJDHFXZC"
    mocked_responses.post(
        f"{URL}maps",
        json={
            "data": {
                "attributes": {
                    "title": "UPDATED again 7",
                    "url": map_url,
                },
                "id": map_id,
                "links": {"self": "/api/v1/maps/YLYztqPrTG69C5vOJDHFXZC"},
                "type": "map",
            }
        },
    )

    result = runner.invoke(app, ["map"])
    assert result.exit_code == 0
    assert map_id in result.stdout
    assert map_url in result.stdout


def test_create_layer(mocked_responses, file_creator):
    map_id = "123"

    paths = [
        file_creator(filename, "content") for filename in ["first.json", "second.txt"]
    ]
    layer_id = "o6ycrzuvS3mof0dkyurxlA"

    presigned_attrs = {
        "AWSAccessKeyId": "ASIA52BWAJR7Q6N4VCN2",
        "signature": "fhdEQ+JRGG3GEoPVAwqQmjy+R8I=",
    }

    upload_url = "https://felt-user-data-uploads.com/"

    mocked_responses.post(
        f"{URL}maps/{map_id}/layers",
        json={
            "data": {
                "type": "presigned_upload",
                "attributes": {
                    "presigned_attributes": presigned_attrs,
                    "url": upload_url,
                    "layer_id": layer_id,
                },
            }
        },
        match=[
            matchers.json_params_matcher(
                {
                    "file_names": [p.name for p in paths],
                    "name": "Layer name",
                }
            )
        ],
    )

    for path in paths:
        mocked_responses.post(upload_url)
        mocked_responses.post(
            f"{URL}maps/{map_id}/layers/{layer_id}/finish_upload",
            match=[matchers.json_params_matcher({"filename": path.name})],
            json={},
        )

    result = runner.invoke(
        app,
        ["layer", map_id, "--name", "Layer name", *(map(str, paths))],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result.stdout
    assert layer_id in result.stdout


def test_layer_import(mocked_responses):
    map_id = "123"
    urls = ["http://test.com/one.geojson", "http://test.com/two.geojson"]
    layer_id = "o6ycrzuvS3mof0dkyurxlA"

    for url in urls:
        mocked_responses.post(
            f"{URL}maps/{map_id}/layers/url_import",
            json={
                "data": {
                    "attributes": {"name": "geo.nls.uk.url"},
                    "id": layer_id,
                    "type": "layer",
                }
            },
            match=[
                matchers.json_params_matcher({"layer_url": url, "name": "Layer name"})
            ],
        )

    result = runner.invoke(app, ["layer-import", map_id, "--name", "Layer name", *urls])

    assert result.exit_code == 0
    assert layer_id in result.stdout
