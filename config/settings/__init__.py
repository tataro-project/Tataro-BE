import os

from dotenv import load_dotenv

# 환경 변수 파일 로드
ENV_FILE = os.path.join(os.path.dirname(__file__), f".env.{os.getenv('DJANGO_ENV', 'dev')}")
load_dotenv(ENV_FILE)
