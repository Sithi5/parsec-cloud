# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import pytest
from parsec.backend.http import http_router


@pytest.fixture
@pytest.mark.trio
async def router():
    router = http_router()
    return router


@pytest.mark.trio
async def test_is_route(router):
    # test is_method_name with existent route
    assert (
        await router.is_route(b"/api/invite?organization_id=thisistheorganizationid123456789")
        is not None
    )
    # test is_method_name with non existent route
    assert await router.is_route(b"fakeroute") is None


@pytest.mark.trio
async def test_get_method_name(router):
    # test get_method_name with existent route
    method_name = await router.get_method_name(b"/api/invite")
    assert method_name == "http_invite_redirect"
    # test get_method_name with non existent route
    method_name = await router.get_method_name(b"fakeroute")
    assert method_name == "http_404"


@pytest.mark.trio
async def test_get_404_method_name(router):
    # test get_404_method_name with existent route
    method_name = router.get_404_method_name()
    assert method_name == "http_404"


@pytest.mark.trio
async def test_get_regexs_from_method_name(router):
    # test get_regexs_from_method_name with existent method_name
    regexs = await router.get_regexs_from_method_name("http_invite_redirect")
    assert regexs == [b"^/api/invite(.*)$"]
    # test get_regexs_from_method_name with no input method_name
    regexs = await router.get_regexs_from_method_name()
    assert regexs == []
