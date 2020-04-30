# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import trio
import unicodedata
from zlib import adler32
from pathlib import Path
from structlog import get_logger
from winfspy import FileSystem, enable_debug_log
from winfspy.plumbing.winstuff import filetime_now

from parsec.core.mountpoint.exceptions import MountpointDriverCrash
from parsec.core.mountpoint.winfsp_operations import WinfspOperations, winify_entry_name
from parsec.core.mountpoint.thread_fs_access import ThreadFSAccess
from parsec.core.mountpoint.winfsp_base_operations import WinfspBaseOperations

__all__ = ("winfsp_mountpoint_runner",)


logger = get_logger()


async def _get_available_drive() -> Path:
    for letter in "PQRSTUVWXYZ":
        if not await trio.Path(f"{letter}:").exists():
            return Path(f"{letter}:")
    return RuntimeError("No available drive")


def _generate_volume_serial_number(device):
    return adler32(f"{device.organization_id}-{device.device_id}".encode())


async def winfsp_mountpoint_runner(
    user_fs,
    base_mountpoint_path: Path,
    config: dict,
    event_bus,
    *,
    task_status=trio.TASK_STATUS_IGNORED,
):
    """
    Raises:
        MountpointDriverCrash
    """
    device = user_fs.device
    drive = await _get_available_drive()

    if config.get("debug", False):
        enable_debug_log()

    # Volume label is limited to 32 WCHAR characters, so force the label to
    # ascii to easily enforce the size.
    volume_label = (
        unicodedata.normalize("NFKD", f"{device.user_id}")
        .encode("ascii", "ignore")[:32]
        .decode("ascii")
    )
    volume_serial_number = _generate_volume_serial_number(device)
    base_operations = WinfspBaseOperations(event_bus, volume_label)

    # See https://docs.microsoft.com/en-us/windows/desktop/api/fileapi/nf-fileapi-getvolumeinformationa  # noqa
    fs = FileSystem(
        str(drive),
        base_operations,
        sector_size=512,
        sectors_per_allocation_unit=1,
        volume_creation_time=filetime_now(),
        volume_serial_number=volume_serial_number,
        file_info_timeout=1000,
        case_sensitive_search=1,
        case_preserved_names=1,
        unicode_on_disk=1,
        persistent_acls=0,
        reparse_points=0,
        reparse_points_access_check=0,
        named_streams=0,
        read_only_volume=0,
        post_cleanup_when_modified_only=1,
        device_control=0,
        um_file_context_is_user_context2=1,
        file_system_name="Parsec",
        prefix="",
        # The minimum value for IRP timeout is 1 minute (default is 5)
        irp_timeout=60000,
        # Work around the avast/winfsp incompatibility
        reject_irp_prior_to_transact0=True,
        # security_timeout_valid=1,
        # security_timeout=10000,
    )

    async def runner(
        workspace_fs,
        base_mountpoint_path: Path,
        config: dict,
        event_bus,
        *,
        task_status=trio.TASK_STATUS_IGNORED,
    ):
        name = winify_entry_name(workspace_fs.get_workspace_name())
        trio_token = trio.hazmat.current_trio_token()
        fs_access = ThreadFSAccess(trio_token, workspace_fs)
        operations = WinfspOperations(event_bus, volume_label, fs_access)
        base_operations.operations_mapping[name] = operations
        task_status.started(drive / name)
        try:
            await trio.sleep_forever()
        finally:
            del base_operations.operations_mapping[name]

    try:
        event_bus.send("mountpoint.starting", mountpoint=drive)

        # Run fs start in a thread, as a cancellable operation
        # This is because fs.start() might get stuck for while in case of an IRP timeout
        await trio.to_thread.run_sync(fs.start, cancellable=True)

        # Because of reject_irp_prior_to_transact0, the mountpoint isn't ready yet
        # We have to add a bit of delay here, the tests would fail otherwise
        # 10 ms is more than enough, although a strict process would be nicer
        # Still, this is only temporary as avast is working on a fix at the moment
        # Another way to address this problem would be to migrate to python 3.8,
        # then use `os.stat` to differentiate between a started and a non-started
        # file syste.
        await trio.sleep(0.01)

        event_bus.send("mountpoint.started", mountpoint=drive)
        task_status.started(runner)

        await trio.sleep_forever()

    except Exception as exc:
        raise MountpointDriverCrash(f"WinFSP has crashed on {drive}: {exc}") from exc

    finally:
        # Must run in thread given this call will wait for any winfsp operation
        # to finish so blocking the trio loop can produce a dead lock...
        with trio.CancelScope(shield=True):
            await trio.to_thread.run_sync(fs.stop)
        event_bus.send("mountpoint.stopped", mountpoint=drive)
