from __future__ import annotations

import os
import posixpath
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import paramiko
import requests
from django.conf import settings

from .models import BackupDestination, BackupLog


class BackupError(Exception):
    """Raised when a backup operation fails."""


def _database_settings():
    return settings.DATABASES["default"]


def _timestamped_name(prefix: str) -> str:
    return f"{prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.sql"


def run_backup(destination: BackupDestination) -> str:
    db_settings = _database_settings()
    file_name = _timestamped_name("fbf_backup")
    with tempfile.TemporaryDirectory() as tmpdir:
        local_path = Path(tmpdir) / file_name
        command = [
            "pg_dump",
            f"--host={db_settings.get('HOST') or 'localhost'}",
            f"--port={db_settings.get('PORT') or '5432'}",
            f"--username={db_settings.get('USER')}",
            "--no-owner",
            db_settings.get("NAME"),
        ]
        env = os.environ.copy()
        env["PGPASSWORD"] = db_settings.get("PASSWORD", "")
        with local_path.open("wb") as outfile:
            completed = subprocess.run(
                command,
                stdout=outfile,
                stderr=subprocess.PIPE,
                env=env,
                check=False,
            )
        if completed.returncode != 0:
            raise BackupError(completed.stderr.decode("utf-8", errors="ignore"))

        if destination.destination_type == BackupDestination.WEB_DAV:
            _upload_via_webdav(destination, local_path)
        else:
            _upload_via_sftp(destination, local_path)

        return file_name


def _upload_via_webdav(destination: BackupDestination, local_path: Path) -> None:
    url_base = destination.endpoint
    if not url_base.endswith("/"):
        url_base += "/"
    remote_file = destination.remote_path.strip("/") if destination.remote_path else ""
    remote_url = urljoin(url_base, f"{remote_file}/{local_path.name}" if remote_file else local_path.name)
    auth = (destination.username, destination.password) if destination.username else None
    with local_path.open("rb") as stream:
        response = requests.put(
            remote_url,
            data=stream,
            auth=auth,
            verify=destination.verify_ssl,
        )
    if response.status_code not in (200, 201, 204):
        raise BackupError(f"WebDAV Upload fehlgeschlagen ({response.status_code}): {response.text}")


def _ensure_sftp_path(sftp: paramiko.SFTPClient, remote_path: str) -> None:
    segments = [segment for segment in remote_path.split("/") if segment]
    current = ""
    for segment in segments:
        current = f"{current}/{segment}" if current else f"/{segment}" if remote_path.startswith("/") else segment
        try:
            sftp.chdir(current)
        except IOError:
            sftp.mkdir(current)
            sftp.chdir(current)


def _upload_via_sftp(destination: BackupDestination, local_path: Path) -> None:
    port = destination.port or 22
    transport = paramiko.Transport((destination.endpoint, port))
    try:
        transport.connect(username=destination.username or None, password=destination.password or None)
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            remote_path = destination.remote_path or "."
            if remote_path not in ("", "."):
                _ensure_sftp_path(sftp, remote_path)
            target = posixpath.join(remote_path or ".", local_path.name)
            sftp.put(str(local_path), target)
        finally:
            sftp.close()
    finally:
        transport.close()


def restore_database_from_file(uploaded_file) -> None:
    db_settings = _database_settings()
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix or ".sql") as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        temp_path = Path(tmp.name)

    try:
        command = [
            "psql",
            f"--host={db_settings.get('HOST') or 'localhost'}",
            f"--port={db_settings.get('PORT') or '5432'}",
            f"--username={db_settings.get('USER')}",
            db_settings.get("NAME"),
        ]
        env = os.environ.copy()
        env["PGPASSWORD"] = db_settings.get("PASSWORD", "")
        with temp_path.open("rb") as infile:
            completed = subprocess.run(
                command,
                stdin=infile,
                stderr=subprocess.PIPE,
                env=env,
                check=False,
            )
        if completed.returncode != 0:
            raise BackupError(completed.stderr.decode("utf-8", errors="ignore"))
    finally:
        if temp_path.exists():
            temp_path.unlink()


def log_backup_event(destination: Optional[BackupDestination], action: str, status: str, message: str, file_name: str = ""):
    BackupLog.objects.create(
        destination=destination,
        action=action,
        status=status,
        message=message,
        file_name=file_name,
    )
