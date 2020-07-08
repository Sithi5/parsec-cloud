# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import pytest
from parsec.backend.http.http_router import (
    http_get_method,
    http_get_404_method,
    http_get_regexs_from_method,
    http_is_route,
)
from parsec.backend.http.http_controller import http_404, http_invite_redirect


@pytest.mark.trio
async def test_is_route():
    # test is_method with existent route
    assert (
        http_is_route(b"/api/invite?organization_id=thisistheorganizationid123456789") is not None
    )
    # test is_method with non existent route
    assert http_is_route(b"fakeroute") is None


@pytest.mark.trio
async def test_get_method():
    # test get_method with existent route
    method = http_get_method(b"/api/invite")
    assert method == http_invite_redirect
    # test get_method with non existent route
    method = http_get_method(b"fakeroute")
    assert method == http_404


@pytest.mark.trio
async def test_get_404_method():
    # test get_404_method with existent route
    method = http_get_404_method()
    assert method == http_404


@pytest.mark.trio
async def test_get_regexs_from_method():
    # test get_regexs_from_method with existent method
    regexs = http_get_regexs_from_method(http_invite_redirect)
    assert regexs == [b"^/api/invite(.*)$"]
    # test get_regexs_from_method with no input method
    regexs = http_get_regexs_from_method()
    assert regexs == []
