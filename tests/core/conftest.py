import pytest
import trio
from async_generator import asynccontextmanager

from tests.event_bus_spy import SpiedEventBus

# from parsec.signals import Namespace as SignalNamespace
from parsec.core.backend_cmds_sender import BackendCmdsSender
from parsec.core.encryption_manager import EncryptionManager
from parsec.core.fs import FS


@pytest.fixture
def encryption_manager_factory(alice, backend_cmds_sender_factory):
    @asynccontextmanager
    async def _encryption_manager_factory(device, backend_addr=None):
        async with backend_cmds_sender_factory(alice, backend_addr=backend_addr) as bcs:
            em = EncryptionManager(alice, bcs)
            async with trio.open_nursery() as nursery:
                await em.init(nursery)
                try:
                    yield em
                finally:
                    await em.teardown()

    return _encryption_manager_factory


@pytest.fixture
async def encryption_manager(encryption_manager_factory, alice):
    async with encryption_manager_factory(alice) as em:
        yield em


@pytest.fixture
def backend_cmds_sender_factory(running_backend):
    @asynccontextmanager
    async def _backend_cmds_sender_factory(device, backend_addr=None):
        if not backend_addr:
            backend_addr = running_backend.addr
        bcs = BackendCmdsSender(device, backend_addr)
        async with trio.open_nursery() as nursery:
            await bcs.init(nursery)
            try:
                yield bcs
            finally:
                await bcs.teardown()

    return _backend_cmds_sender_factory


@pytest.fixture
def fs_factory(backend_cmds_sender_factory, encryption_manager_factory, event_bus_factory):
    @asynccontextmanager
    async def _fs_factory(device, backend_addr=None, event_bus=None):
        if not event_bus:
            event_bus = event_bus_factory()

        async with encryption_manager_factory(
            device, backend_addr=backend_addr
        ) as encryption_manager, backend_cmds_sender_factory(
            device, backend_addr=backend_addr
        ) as backend_cmds_sender:
            fs = FS(device, backend_cmds_sender, encryption_manager, event_bus)
            yield fs

    return _fs_factory


@pytest.fixture
async def backend_cmds_sender(alice):
    return backend_cmds_sender_factory(alice)


@pytest.fixture
async def alice_fs(fs_factory, alice):
    async with fs_factory(alice) as fs:
        yield fs


@pytest.fixture
async def alice2_fs(fs_factory, alice2):
    async with fs_factory(alice2) as fs:
        yield fs


@pytest.fixture
def backend_addr_factory(running_backend, tcp_stream_spy):
    # Creating new addr for backend make it easy be selective on what to
    # turn offline
    counter = 0

    def _backend_addr_factory():
        nonlocal counter
        addr = f"tcp://backend-addr-{counter}.localhost:9999"
        tcp_stream_spy.push_hook(addr, running_backend.connection_factory)
        counter += 1
        return addr

    return _backend_addr_factory
