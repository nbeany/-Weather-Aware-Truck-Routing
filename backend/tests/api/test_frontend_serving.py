"""Single-service deploys: WhiteNoise serves the built frontend next to the API.

Each test builds a tiny fake `dist` folder; WhiteNoise reads its settings when the test
client's handler is created, so override_settings must wrap client creation.
"""

import pytest
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.fixture
def dist(tmp_path):
    (tmp_path / "index.html").write_text("<!doctype html><title>RouteCast</title>")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "index-abc123.js").write_text("console.log('app')")
    (tmp_path / "logo.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
    return tmp_path


@pytest.fixture
def client(dist):
    with override_settings(
        WHITENOISE_ROOT=dist,
        WHITENOISE_INDEX_FILE=True,
        WHITENOISE_IMMUTABLE_FILE_TEST=r"^/assets/",
    ):
        yield APIClient()


def _body(response):
    return b"".join(response.streaming_content) if response.streaming else response.content


def test_root_serves_the_frontend_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"RouteCast" in _body(response)


def test_fingerprinted_assets_are_cached_forever(client):
    response = client.get("/assets/index-abc123.js")
    assert response.status_code == 200
    assert "immutable" in response["Cache-Control"]


def test_unhashed_files_are_not_cached_forever(client):
    response = client.get("/logo.svg")
    assert response.status_code == 200
    assert "immutable" not in response.get("Cache-Control", "")


def test_api_still_answers_alongside_the_frontend(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_paths_keep_the_json_404(client):
    response = client.get("/no-such-page")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
