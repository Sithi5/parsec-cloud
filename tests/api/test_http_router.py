# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import pytest
from parsec.backend.http import http_router
from parsec.backend.http.http_controller import http_invite_redirect, http_404


@pytest.fixture
@pytest.mark.trio
async def router():
    router = http_router()
    return router


@pytest.mark.trio
async def test_is_route(router):
    # test is_controller with existent route
    assert (
        await router.is_route(b"/api/invite?organization_id=thisistheorganizationid123456789")
        is not None
    )
    # test is_controller with non existent route
    assert await router.is_route(b"fakeroute") is None


@pytest.mark.trio
async def test_get_controller(router):
    # test get_controller with existent route
    controller = await router.get_controller(b"/api/invite")
    assert controller == http_invite_redirect
    # test get_controller with non existent route
    controller = await router.get_controller(b"fakeroute")
    assert controller == http_404


@pytest.mark.trio
async def test_get_404_controller(router):
    # test get_404_controller with existent route
    controller = router.get_404_controller()
    assert controller == http_404


@pytest.mark.trio
async def test_get_regexs_from_controller(router):
    # test get_regexs_from_controller with existent controller
    regexs = await router.get_regexs_from_controller(http_invite_redirect)
    assert regexs == [b"^/api/invite(.*)$", b"^/api/test(.*)$"]
    # test get_regexs_from_controller with no input controller
    regexs = await router.get_regexs_from_controller()
    assert regexs == []
