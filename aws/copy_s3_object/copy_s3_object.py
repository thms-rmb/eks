import concurrent.futures
from contextvars import ContextVar
import logging
import re
from typing import NamedTuple
from urllib.parse import urlparse
from operator import attrgetter

import boto3

logging.basicConfig(level=logging.INFO)

_BYTES_RE = r"bytes (\d+)-(\d+)"
_ETAG_MULTIPART_RE = r"-(\d+)\"$"


class LocalS3Client:
    """
    Holds S3 clients as local context variables.
    """

    _s3 = ContextVar("_s3")

    @classmethod
    def get(cls):
        """
        Gets the actual client.
        """

        try:
            return cls._s3.get()
        except LookupError:
            cls._s3.set(boto3.client("s3"))

        return cls._s3.get()


class S3ObjectReference(NamedTuple):
    Bucket: str
    Key: str

    @classmethod
    def from_url(cls, url: str):
        obj = urlparse(url, allow_fragments=False)

        if obj.scheme != "s3":
            raise ValueError(f"Argument url is not an S3 URL: {repr(url)}")

        return cls(Bucket=obj.netloc, Key=obj.path[1:])


class PartCompleteHandle(NamedTuple):
    ETag: str
    PartNumber: int


def copy_object(source: str, target: str):
    logger = logging.getLogger()
    s3 = LocalS3Client.get()

    source_ref = S3ObjectReference.from_url(source)
    target_ref = S3ObjectReference.from_url(target)

    info = s3.head_object(
        Bucket=source_ref.Bucket,
        Key=source_ref.Key,
    )

    etag_multipart_match = re.search(_ETAG_MULTIPART_RE, info["ETag"])

    if etag_multipart_match is None:
        s3.copy_object(
            Bucket=target_ref.Bucket,
            Key=target_ref.Key,
            CopySource={
                "Bucket": source_ref.Bucket,
                "Key": source_ref.Key,
            },
        )

    else:
        parts_count = int(etag_multipart_match.group(1))

        create_multipart_response = s3.create_multipart_upload(
            Bucket=target_ref.Bucket,
            Key=target_ref.Key,
        )

        parts = set()

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = []

            for part_number in range(1, parts_count + 1):
                futures.append(executor.submit(
                    copy_object_part,
                    source,
                    target,
                    create_multipart_response["UploadId"],
                    part_number,
                ))

            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                part = future.result()
                parts.add(PartCompleteHandle(
                    ETag=part["UploadPartCopy"]["CopyPartResult"]["ETag"],
                    PartNumber=part["PartNumber"],
                ))
                logger.info("Task %d / %d done.", i, len(futures))

        s3.complete_multipart_upload(
            Bucket=target_ref.Bucket,
            Key=target_ref.Key,
            UploadId=create_multipart_response["UploadId"],
            MultipartUpload={
                "Parts": [part._asdict() for part in sorted(
                    parts, key=attrgetter("PartNumber"),
                )],
            }
        )


def copy_object_part(source: str, target: str, upload_id: str, part_number: int):
    s3 = LocalS3Client.get()

    source_ref = S3ObjectReference.from_url(source)
    target_ref = S3ObjectReference.from_url(target)

    info = s3.head_object(
        Bucket=source_ref.Bucket,
        Key=source_ref.Key,
        PartNumber=part_number,
    )

    bytes_match = re.match(_BYTES_RE, info["ContentRange"])

    if bytes_match is None:
        raise ValueError(f"ContentRange does not match the expected pattern: {info['ContentRange']}")

    result = s3.upload_part_copy(
        Bucket=target_ref.Bucket,
        Key=target_ref.Key,
        PartNumber=part_number,
        UploadId=upload_id,
        CopySource={
            "Bucket": source_ref.Bucket,
            "Key": source_ref.Key,
        },
        CopySourceRange=f"bytes={bytes_match.group(1)}-{bytes_match.group(2)}",
    )

    return {
        "PartNumber": part_number,
        "UploadPartCopy": result,
    }


def main():
    copy_object(
        "s3://tind-dev-cicero/f1faad3f-ed06-40e4-8bbf-68f62d53f900",
        "s3://tind-dev-cicero/7425ad44-a272-4616-ab4d-9302aaa4a516",
    )


if __name__ == "__main__":
    main()
