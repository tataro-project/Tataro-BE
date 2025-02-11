# import requests
# from django.conf import settings
# from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema
# from rest_framework.request import Request
# from rest_framework.response import Response
# from rest_framework.views import APIView
#
#
# class NaverSocialLoginView(APIView):
#     @swagger_auto_schema(operation_description="네이버 소셜 로그인 URL 반환", responses={200: "로그인 URL 반환 성공"})
#     def get(self, request: Request) -> Response:
#         # 네이버 로그인 인증 URL 생성
#         naver_auth_url = (
#             f"https://nid.naver.com/oauth2.0/authorize?"
#             f"response_type=code&client_id={settings.NAVER_CLIENT_ID}&"
#             f"redirect_uri={settings.NAVER_REDIRECT_URI}&state=RANDOM_STATE"
#         )
#         # 생성된 URL 반환
#         return Response({"auth_url": naver_auth_url})
#
#     @swagger_auto_schema(
#         operation_description="네이버 로그인 콜백 처리",
#         manual_parameters=[
#             openapi.Parameter("code", openapi.IN_QUERY, description="Authorization code", type=openapi.TYPE_STRING),
#             openapi.Parameter("state", openapi.IN_QUERY, description="State", type=openapi.TYPE_STRING),
#         ],
#         responses={200: "토큰 발급 성공", 400: "잘못된 요청", 401: "인증 실패"},
#     )
#     def post(self, request: Request) -> Response:
#         # 요청에서 code와 state 파라미터 추출
#         code = request.data.get("code")
#         state = request.data.get("state")
#
#         # code와 state가 없으면 에러 반환
#         if not code or not state:
#             return Response({"error": "Code and state are required"}, status=400)
#
#         # 네이버 토큰 발급 URL
#         token_url = "https://nid.naver.com/oauth2.0/token"
#         # 토큰 요청에 필요한 데이터
#         data = {
#             "grant_type": "authorization_code",
#             "client_id": settings.NAVER_CLIENT_ID,
#             "client_secret": settings.NAVER_CLIENT_SECRET,
#             "code": code,
#             "state": state,
#         }
#
#         # 네이버 서버에 토큰 요청
#         token_response = requests.post(token_url, data=data)
#
#         # 토큰 발급 실패 시 에러 반환
#         if token_response.status_code != 200:
#             return Response({"error": "Failed to obtain token"}, status=401)
#
#         # 발급받은 토큰 정보
#         tokens = token_response.json()
#
#         # TODO: 여기서 사용자 정보를 가져오고 데이터베이스에 저장하는 로직을 추가할 수 있습니다.
#
#         # 액세스 토큰과 리프레시 토큰 반환
#         return Response(
#             {"access_token": tokens.get("access_token"), "refresh_token": tokens.get("refresh_token")}, status=200
#         )
#
#
# class NaverTokenReissueView(APIView):
#     @swagger_auto_schema(
#         operation_description="네이버 토큰 재발급",
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             required=["refresh_token"],
#             properties={"refresh_token": openapi.Schema(type=openapi.TYPE_STRING)},
#         ),
#         responses={200: "토큰 재발급 성공", 401: "재발급 실패"},
#     )
#     def post(self, request: Request) -> Response:
#         # 요청에서 리프레시 토큰 추출
#         refresh_token = request.data.get("refresh_token")
#
#         # 리프레시 토큰이 없으면 에러 반환
#         if not refresh_token:
#             return Response({"error": "Refresh token is required"}, status=400)
#
#         # 네이버 토큰 재발급 URL
#         token_url = "https://nid.naver.com/oauth2.0/token"
#         # 토큰 재발급 요청에 필요한 데이터
#         data = {
#             "grant_type": "refresh_token",
#             "client_id": settings.NAVER_CLIENT_ID,
#             "client_secret": settings.NAVER_CLIENT_SECRET,
#             "refresh_token": refresh_token,
#         }
#
#         # 네이버 서버에 토큰 재발급 요청
#         token_response = requests.post(token_url, data=data)
#
#         # 토큰 재발급 실패 시 에러 반환
#         if token_response.status_code != 200:
#             return Response({"error": "Failed to refresh token"}, status=401)
#
#         # 새로 발급받은 토큰 정보
#         new_tokens = token_response.json()
#
#         # 새 액세스 토큰과 리프레시 토큰 반환 (새 리프레시 토큰이 없으면 기존 것 사용)
#         return Response(
#             {
#                 "access_token": new_tokens.get("access_token"),
#                 "refresh_token": new_tokens.get("refresh_token", refresh_token),
#             },
#             status=200,
#         )
