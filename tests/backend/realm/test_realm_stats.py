# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import pytest
from uuid import UUID

from parsec.api.data import RealmRoleCertificateContent, UserProfile
from parsec.api.protocol import RealmRole

from uuid import uuid4
from tests.backend.common import realm_create
from tests.backend.common import vlob_create, block_create

async def realm_stats(sock, realm_id):
    return {"status": "ok", "data_size": 0}

@pytest.mark.trio
async def test_realm_stats_ok(backend, alice, alice_backend_sock, administration_backend_sock, realm):
	rep = await realm_stats(administration_backend_sock, realm)
	print("data_size : ", end="")
	print(rep["data_size"])
	assert rep == {
        "status": "ok",
        "data_size": 0,
    }

	#Create new metadata
	await vlob_create(alice_backend_sock, realm_id=realm, vlob_id=uuid4(), blob=b"1234")
	# Create new data
	await block_create(alice_backend_sock, realm_id=realm, block_id=uuid4(), block=b"1234")
	rep = await realm_stats(administration_backend_sock, realm)
	print("data_size : ", end="")
	print(rep["data_size"])
	assert rep == {
        "status": "ok",
        "data_size": 0,
    }