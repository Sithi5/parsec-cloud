# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import pytest
import trio


@pytest.mark.trio
async def test_send_http_request(running_backend):
    stream = await trio.open_tcp_stream(running_backend.addr.hostname, running_backend.addr.port)
    await stream.send_all(
        b"GET / HTTP/1.1\r\n"
        b"Host: parsec.example.com\r\n"
        b"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0\r\n"
        b"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
        b"Accept-Language: fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3\r\n"
        b"Accept-Encoding: gzip, deflate\r\n"
        b"DNT: 1\r\n"
        b"Connection: keep-alive\r\n"
        b"Upgrade-Insecure-Requests: 1\r\n"
        b"Cache-Control: max-age=0\r\n"
        b"\r\n"
    )
    rep = await stream.receive_some()
    print(rep)

    # todo : the assert rep


@pytest.mark.trio
async def test_send_http_request_to_rest_invite_no_invitation_type(running_backend):
    stream = await trio.open_tcp_stream(running_backend.addr.hostname, running_backend.addr.port)
    await stream.send_all(
        b"GET /api/invite?organization_id=thisistheorganizationid123456789&token=S3CRET&no_ssl=true HTTP/1.0\r\n\r\n"
    )
    rep = await stream.receive_some()
    print(rep)
    # assert re.search(b"HTTP/1.1 400", rep) is not None


@pytest.mark.trio
async def test_send_http_request_to_rest_false_route(running_backend):
    stream = await trio.open_tcp_stream(running_backend.addr.hostname, running_backend.addr.port)
    await stream.send_all(b"GET /api/false HTTP/1.0\r\n\r\n")
    rep = await stream.receive_some()
    print(rep)
    # assert re.search(b"HTTP/1.1 400", rep) is not None


@pytest.mark.trio
async def test_send_http_request_to_rest_invite_valid(running_backend):
    stream = await trio.open_tcp_stream(running_backend.addr.hostname, running_backend.addr.port)
    await stream.send_all(
        b"GET /api/invite?organization_id=thisistheorganizationid123456789&invitation_type=invitation_type&token=S3CRET&no_ssl=true HTTP/1.0\r\n\r\n"
    )
    rep = await stream.receive_some()
    print(rep)
