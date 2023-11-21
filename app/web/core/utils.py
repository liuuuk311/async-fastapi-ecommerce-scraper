import os
import uuid

from fastapi import UploadFile

from web.core.config import settings
from aioboto3 import Session as AsyncBotoSession


async def async_upload_to_do_spaces(file: UploadFile, prefix: str = "uploads") -> str:
    session = AsyncBotoSession()
    async with session.client(
        "s3",
        endpoint_url=settings.DO_SPACES_ENDPOINT_URL,
        aws_access_key_id=settings.DO_SPACES_ACCESS_KEY,
        aws_secret_access_key=settings.DO_SPACES_SECRET_KEY,
    ) as s3:
        _, file_extension = os.path.splitext(file.filename)
        key = f"{prefix}/{uuid.uuid4()}{file_extension}"

        await s3.upload_fileobj(
            file.file,
            settings.DO_SPACES_BUCKET_NAME,
            key,
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type},
        )

        public_url = (
            f"{settings.DO_SPACES_ENDPOINT_URL}/{settings.DO_SPACES_BUCKET_NAME}/{key}"
        )
        return public_url
