# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import pytest
from uuid import uuid4

from tests.backend.common import realm_create, realm_status, realm_stats
from tests.backend.common import vlob_create, block_create

@pytest.mark.trio
async def test_realm_stats_ok(backend, alice, alice_backend_sock, administration_backend_sock, realm):
	rep = await realm_stats(alice_backend_sock, realm)
	print("\n\ndata_size : ", end="")
	print(rep["data_size"])
	assert rep == {
		"status": "ok",
        "data_size": 48,
    }