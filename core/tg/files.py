from collections.abc import Iterator
from contextlib import contextmanager

from aiogram.types import BufferedInputFile

from utils.transform_types import from_b64_to_bytes
from utils.types import b64


@contextmanager
def transferring_file(
    data: b64, file_name: str = 'default', file_ext: str = 'jpg'
) -> Iterator[BufferedInputFile]:
    yield BufferedInputFile(
        from_b64_to_bytes(data),
        f'{file_name}.{file_ext}',
        chunk_size=4 * 1024 * 1024,  # 4 Mb
    )


@contextmanager
def transferring_file2(
    data: bytes, file_name: str = 'default', file_ext: str = 'jpg'
) -> Iterator[BufferedInputFile]:
    yield BufferedInputFile(
        data,
        f'{file_name}.{file_ext}',
        chunk_size=4 * 1024 * 1024,  # 4 Mb
    )
