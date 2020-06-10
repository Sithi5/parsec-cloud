# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import pytest
from uuid import uuid4

from tests.backend.common import realm_create, realm_stats
from tests.backend.common import vlob_create, block_create


@pytest.mark.trio
async def test_realm_stats_ok(backend, alice_backend_sock, realm):
    # Create new metadata
    await vlob_create(alice_backend_sock, realm_id=realm, vlob_id=uuid4(), blob=b"1234")
    rep = await realm_stats(alice_backend_sock, realm_id=realm)
    assert rep == {
        "status": "ok",
        "blocks_size": 0,
        "vlobs_size": 4,
    }

    # Create new data
    await block_create(
        alice_backend_sock, realm_id=realm, block_id=uuid4(), block=b"1234"
    )
    rep = await realm_stats(alice_backend_sock, realm_id=realm)
    assert rep == {
        "status": "ok",
        "blocks_size": 4,
        "vlobs_size": 4,
    }
