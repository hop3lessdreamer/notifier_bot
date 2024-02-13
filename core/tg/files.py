from collections.abc import Iterator
from contextlib import contextmanager
from io import BytesIO

from aiogram.types import InputFile

from utils.transform_types import from_b64_to_bytes
from utils.types import b64


@contextmanager
def transferring_file(data: b64, file_name: str = 'default', file_ext: str = 'jpg') \
        -> Iterator[BytesIO]:
    bytes_io = BytesIO()
    try:
        bytes_io.write(from_b64_to_bytes(data))
        bytes_io.seek(0)
        yield InputFile(bytes_io, f'{file_name}.{file_ext}')
    finally:
        bytes_io.close()
