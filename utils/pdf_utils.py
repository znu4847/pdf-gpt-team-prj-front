import os
import boto3


def read_file(file_path, embed_path):
    print(f"pdf_utils: file_path: {file_path}")
    print(f"pdf_utils: embed_path: {embed_path}")
    # check if file exists
    if not os.path.exists(file_path):
        print("pdf_utils: file NOT FOUND ")

    else:
        with open(file_path, "r") as f:
            print("pdf_utils: file exists")
            print(f)

    if not os.path.exists(embed_path):
        print("pdf_utils: embed NOT FOUND ")

    else:
        with open(embed_path, "r") as f:
            print("pdf_utils: embed exists")
            print(f)


# s3://pdf-gpt-files/cheatsheet.pdf


AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SCRET_KEY = os.environ.get("AWS_SCRET_KEY")
AWS_REGION = os.environ.get("AWS_REGION")
# print(f"AWS_BUCKET_NAME: {AWS_BUCKET_NAME}")
# print(f"AWS_ACCESS_KEY: {AWS_ACCESS_KEY}")
# print(f"AWS_SCRET_KEY: {AWS_SCRET_KEY}")


def upload_file(file_path, file_name, username):
    s3 = boto3.client(
        service_name="s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SCRET_KEY,
    )
    response = s3.upload_file(file_path, AWS_BUCKET_NAME, f"{username}/{file_name}")
    print(f"upload_log_to_aws response: {response}")

    # if not os.path.exists(file_path):
    #     print("pdf_utils: file NOT FOUND ")

    # else:
    #     with open(file_path, "r") as f:
    #         print("pdf_utils: file exists")
    #         s3_file_name = f"{username}/{file_path}"
    #         s3.upload_file(file_path, AWS_BUCKET_NAME, s3_file_name)
    #         print(f"Uploaded {file_path} to s3://{S3_BUCKET_NAME}/{s3_file_name}")
    #         print(f)
