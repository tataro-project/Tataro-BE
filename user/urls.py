from django.urls import path

from .auth.kakao import KakaoSocialLoginView, KakaoTokenReissueView
from .auth.naver import NaverSocialLoginView, NaverTokenReissueView
from .auth.views import LogoutView
from .questionnaire.views import QuestionnaireView
from .views import UserView

urlpatterns = [
    path("user/", UserView.as_view()),
    path("user/auth/logout/", LogoutView.as_view()),
    path("user/auth/kakao/", KakaoSocialLoginView.as_view()),
    path("user/auth/kakao/reissue/", KakaoTokenReissueView.as_view()),
    path("user/auth/naver/", NaverSocialLoginView.as_view()),
    path("user/auth/naver/reissue/", NaverTokenReissueView.as_view()),
    path("user/questionnaire/", QuestionnaireView.as_view()),
]
