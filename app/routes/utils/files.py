from typing import Annotated, Tuple

from fastapi import File, UploadFile


async def read_optional_file(file: UploadFile | None) -> Tuple[bytes | None, str | None]:
    if file is not None:
        try:
            content = await file.read()
            return content, file.filename
        except Exception:
            return None, None
    return None, None


async def get_optional_file(
    image: Annotated[str | UploadFile | None, File()] = None,
):
    if isinstance(image, UploadFile):
        return image
    return None
