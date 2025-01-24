from django.urls import path

from .auth.kakao import KakaoTokenReissueView
from .auth.naver import NaverTokenReissueView
from .auth.views import LogoutView
from .questionnaire.views import QuestionnaireView
from .views import UserView

urlpatterns = [
    path("user/", UserView.as_view()),
    path("user/auth/logout/", LogoutView.as_view()),
    path("user/auth/kakao/reissue/", KakaoTokenReissueView.as_view()),
    path("user/auth/naver/reissue/", NaverTokenReissueView.as_view()),
    path("user/questionnaire/", QuestionnaireView.as_view()),
]
