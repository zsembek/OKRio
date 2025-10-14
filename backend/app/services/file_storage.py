"""Local file storage service for attachments and exports."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable
from uuid import uuid4

from ..core.config import get_settings


@dataclass(frozen=True)
class StoredFile:
    """Metadata describing a stored file."""

    relative_path: str
    original_name: str
    size: int
    checksum: str


class LocalFileStorage:
    """Persist files on the application server filesystem."""

    def __init__(self, base_path: Path | None = None) -> None:
        settings = get_settings()
        self._base_path = (base_path or settings.storage_root).resolve()
        self._base_path.mkdir(parents=True, exist_ok=True)

    @property
    def base_path(self) -> Path:
        return self._base_path

    def _resolve(self, relative_path: Path) -> Path:
        full_path = (self._base_path / relative_path).resolve()
        if self._base_path not in full_path.parents and full_path != self._base_path:
            raise ValueError("Attempted path traversal outside of storage root")
        return full_path

    def _write_bytes(self, data: bytes, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as file_obj:
            file_obj.write(data)

    def _hash_bytes(self, data: bytes) -> str:
        digest = hashlib.sha256()
        digest.update(data)
        return digest.hexdigest()

    def save_bytes(self, data: bytes, *, original_name: str, subdirs: Iterable[str] | None = None) -> StoredFile:
        identifier = uuid4().hex
        extension = Path(original_name).suffix
        relative_dir = Path()
        for part in subdirs or []:
            relative_dir /= Path(part)
        relative_dir /= identifier[:2]
        filename = f"{identifier}{extension}"
        relative_path = relative_dir / filename
        destination = self._resolve(relative_path)
        checksum = self._hash_bytes(data)
        self._write_bytes(data, destination)
        return StoredFile(relative_path=str(relative_path), original_name=original_name, size=len(data), checksum=checksum)

    def save_fileobj(self, file_obj: BinaryIO, *, original_name: str, subdirs: Iterable[str] | None = None) -> StoredFile:
        data = file_obj.read()
        return self.save_bytes(data, original_name=original_name, subdirs=subdirs)

    def open(self, relative_path: str, mode: str = "rb") -> BinaryIO:
        path = self._resolve(Path(relative_path))
        return path.open(mode)

    def delete(self, relative_path: str) -> None:
        path = self._resolve(Path(relative_path))
        try:
            path.unlink()
        except FileNotFoundError:
            return
        self._cleanup_empty_parents(path.parent)

    def exists(self, relative_path: str) -> bool:
        path = self._resolve(Path(relative_path))
        return path.exists()

    def get_absolute_path(self, relative_path: str) -> Path:
        """Return the full filesystem path for the stored file."""

        return self._resolve(Path(relative_path))

    def _cleanup_empty_parents(self, directory: Path) -> None:
        while directory != self._base_path:
            try:
                directory.rmdir()
            except OSError:
                break
            directory = directory.parent


__all__ = ["LocalFileStorage", "StoredFile"]
