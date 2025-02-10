from django.urls import path

from .auth.kakao import KakaoCallbackView, KakaoLoginView

# from .auth.naver import NaverSocialLoginView, NaverTokenReissueView
from .auth.views import LogoutView

# from .views import UserView

urlpatterns = [
    #    path("user/", UserView.as_view()),
    path("user/auth/logout/", LogoutView.as_view()),
    path("user/auth/kakao/", KakaoLoginView.as_view(), name="kakao-login"),
    path("user/auth/kakao/callback/", KakaoCallbackView.as_view(), name="kakao-callback"),
    # path("user/auth/naver/", NaverSocialLoginView.as_view()),
    # path("user/auth/naver/reissue/", NaverTokenReissueView.as_view()),
    # path("user/questionnaire/", QuestionnaireView.as_view()),
]
