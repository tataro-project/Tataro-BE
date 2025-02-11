from django.urls import path

from .auth.kakao import KakaoCallbackView, KakaoLoginView
from .auth.naver import NaverCallbackView, NaverLoginView
from .auth.views import LogoutView
from .questionnaire.views import QuestionnaireView
from .views import UserView

urlpatterns = [
    path("user/", UserView.as_view()),
    path("user/auth/logout/", LogoutView.as_view()),
    path("user/auth/kakao/", KakaoLoginView.as_view(), name="kakao-login"),
    path("user/auth/kakao/callback/", KakaoCallbackView.as_view(), name="kakao-callback"),
    path("user/auth/naver/", NaverLoginView.as_view()),
    path("user/auth/naver/callback/", NaverCallbackView.as_view(), name="naver-callback"),
    path("user/questionnaire/", QuestionnaireView.as_view()),
]
