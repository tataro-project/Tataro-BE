set -eo pipefail #명령어가 실패하면 그 밑으로 더이상 진행하지 않는다.
# 실패는 어떻게 알 수 있나? 명령어를 실행하면 모든 명령어는 exit code 를 리턴합니다. (리눅스 규칙)
# exit code 는 integer 인데 이게 0이면 성공, 0이 아닌 모든 값은 비정상 종료 (실패)

COLOR_GREEN=`tput setaf 2;`
COLOR_NC=`tput sgr0;` # No Color

echo "Starting black"
poetry run black .
echo "OK"

echo "Starting isort"
poetry run isort .
echo "OK"

echo "Starting mypy"
poetry run mypy .
echo "OK"

echo "Starting test with coverage"
poetry run coverage run manage.py test
poetry run coverage report -m

echo "${COLOR_GREEN}All tests passed successfully!${COLOR_NC}"
