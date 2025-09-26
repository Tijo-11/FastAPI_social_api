import logging
import tempfile

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status

from social_media_api.libs.b2 import b2_upload_file

logger = logging.getLogger(__name__)

router = APIRouter()


# client splits up file into  chunks 1 MB
# clients send chunks 1 at a time
# client sends the last chunk

CHUNK_SIZE = 1024 * 1024  # 1 MB


@router.post("/upload", status_code=201)
async def upload_file(file: UploadFile):
    # file.read(CHUNK_SIZE)
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            file_name = tmp.name
            logger.info(f"Saving uploaded file temporarily to {file_name}")

            # Open the temp file asynchronously for writing binary data
            async with aiofiles.open(file_name, "wb") as f:
                # Read chunks asynchronously and write them to the file
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)

            # Upload the completed temp file to Backblaze B2
            file_url = b2_upload_file(
                local_file=file_name,
                file_name=file.filename,  # original client file name
            )

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file.",
        )

    return {"message": "Upload successful", "file_url": file_url}
