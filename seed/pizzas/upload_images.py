import json
from pathlib import Path
from urllib.parse import urlparse

from config.settings import settings


def get_content_type(image: Path) -> str:
    if image.suffix.lower() in {".jpg", ".jpeg"}:
        return "image/jpeg"

    if image.suffix.lower() == ".png":
        return "image/png"

    return "application/octet-stream"


def get_minio_client():
    from minio import Minio

    endpoint = urlparse(settings.object_storage_endpoint)
    secure = endpoint.scheme == "https"
    netloc = endpoint.netloc or endpoint.path

    return Minio(
        netloc,
        access_key=settings.object_storage_access_key,
        secret_key=settings.object_storage_secret_key,
        secure=secure
    )


def upload_images():
    from minio.error import S3Error

    image_path = Path(
        "seed",
        "pizzas",
        "img"
    )

    client = get_minio_client()

    try:
        if client.bucket_exists(settings.object_storage_bucket):
            print(f"Cleaning bucket {settings.object_storage_bucket}")

            for item in client.list_objects(settings.object_storage_bucket, recursive=True):
                client.remove_object(
                    settings.object_storage_bucket,
                    item.object_name,
                )

            client.remove_bucket(settings.object_storage_bucket)

        client.make_bucket(settings.object_storage_bucket)
        client.set_bucket_policy(
            settings.object_storage_bucket,
            json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetObject"],
                            "Resource": [
                                f"arn:aws:s3:::{settings.object_storage_bucket}/*"
                            ],
                        }
                    ],
                }
            ),
        )

        print(f"Bucket {settings.object_storage_bucket} ready")

        for image in image_path.iterdir():
            if not image.is_file():
                continue

            client.fput_object(
                settings.object_storage_bucket,
                image.name,
                str(image),
                content_type=get_content_type(image),
            )

            print(f"Uploaded {image.name}")

        print("Images uploaded")
    except S3Error as exc:
        raise RuntimeError(
            f"Failed to upload images to {settings.object_storage_bucket}"
        ) from exc
