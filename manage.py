#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import environ

# 환경변수 로딩을 위해 manage.py 에 아래의 변수 추가 및 env 파일 로딩
env = environ.Env()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


def main():
    """Run administrative tasks."""
    environment = os.getenv("DJANGO_ENV", "dev")  # 기본값은 dev
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{environment}")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
