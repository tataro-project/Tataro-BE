import uuid

import boto3
from django.conf import settings


def upload_to_ncp(cate: str, file):  # type: ignore
    """NCP Object Storage에 파일을 업로드하고 URL을 반환"""
    ncp_config = settings.NCP_STORAGE
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=ncp_config["ACCESS_KEY"],
        aws_secret_access_key=ncp_config["SECRET_KEY"],
        endpoint_url=ncp_config["ENDPOINT_URL"],
    )
    file_extension = file.name.split(".")[-1]
    file_name = f"{cate}/{uuid.uuid4()}.{file_extension}"  # 고유한 파일명 생성

    s3_client.upload_fileobj(
        file,
        ncp_config["BUCKET_NAME"],
        file_name,
    )

    return f"{ncp_config['ENDPOINT_URL']}/{ncp_config['BUCKET_NAME']}/{file_name}"


def delete_from_ncp(file_url: str):  # type: ignore
    """NCP Object Storage에서 파일 삭제"""
    ncp_config = settings.NCP_STORAGE
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=ncp_config["ACCESS_KEY"],
        aws_secret_access_key=ncp_config["SECRET_KEY"],
        endpoint_url=ncp_config["ENDPOINT_URL"],
    )

    # URL에서 버킷 이름과 파일 경로 추출
    file_path = file_url.replace(f"{ncp_config['ENDPOINT_URL']}/{ncp_config['BUCKET_NAME']}/", "")

    try:
        s3_client.delete_object(
            Bucket=ncp_config["BUCKET_NAME"],
            Key=file_path,
        )
        print(f"파일 삭제 성공: {file_url}")
    except Exception as e:
        print(f"파일 삭제 실패: {e}")
