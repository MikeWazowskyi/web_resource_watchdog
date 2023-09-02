from http import HTTPStatus

py_url = "https://www.python.org"


def test_add_resource(client):
    """Test adding a resource via a POST request."""
    got = client.post(
        "/api/v1/add_resource/",
        json={
            "full_url": py_url,
        },
    )
    assert (
        got.status_code == HTTPStatus.CREATED
    ), "POST to add_resource endpoint should return status code 201."
    assert list(got.json.keys()) == [
        "domain",
        "domain_zone",
        "fail_count",
        "full_url",
        "id",
        "protocol",
        "query_params",
        "screenshot",
        "url_path",
    ], (
        "POST request body to add_resource must contain "
        "`created, domain, domain_zone full_url, protocol, "
        "query_params, screenshot, url_path` keys"
    )
    assert got.json == {
        "id": 1,
        "domain": "www.python",
        "domain_zone": "org",
        "fail_count": 0,
        "full_url": py_url,
        "protocol": "https",
        "query_params": "",
        "screenshot": None,
        "url_path": "",
    }, "Response is different from expected"


def test_add_resource_empty_body(client):
    """Test adding a resource with an empty request body."""
    try:
        got = client.post("/api/v1/add_resource/")
    except Exception:
        raise AssertionError("If request body is empty - raise exception")
    assert got.status_code == HTTPStatus.BAD_REQUEST, (
        "Response on empty POST to `/api/v1/add_resource` "
        "must have status-code 400."
    )
    assert list(got.json.keys()) == ["error"], (
        "Response on empty POST to `/api/v1/add_resource` "
        "must have key `error`"
    )
    assert got.json == {"error": "Request body is empty"}, (
        "The response body message without a request "
        "body does not comply with the specification."
    )
