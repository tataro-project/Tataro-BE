from django.urls import path

from .auth.kakao import KakaoCallbackView, KakaoLoginView, KakaoReissueView
from .auth.naver import NaverCallbackView, NaverLoginView, NaverReissueView
from .auth.views import LogoutView

# from .views import UserView

urlpatterns = [
    #    path("user/", UserView.as_view()),
    path("user/auth/logout/", LogoutView.as_view()),
    path("user/auth/kakao/", KakaoLoginView.as_view(), name="kakao-login"),
    path("user/auth/kakao/callback/", KakaoCallbackView.as_view(), name="kakao-callback"),
<<<<<<< HEAD
    # path("user/auth/naver/", NaverSocialLoginView.as_view()),
    # path("user/auth/naver/reissue/", NaverTokenReissueView.as_view()),
    # path("user/questionnaire/", QuestionnaireView.as_view()),
=======
    path("user/auth/kakao/reissue/", KakaoReissueView.as_view(), name="kakao-token-refresh"),
    path("user/auth/naver/", NaverLoginView.as_view(), name="naver-login"),
    path("user/auth/naver/callback/", NaverCallbackView.as_view(), name="naver-callback"),
    path("user/auth/naver/reissue/", NaverReissueView.as_view(), name="naver-token-refresh"),
    path("user/questionnaire/", QuestionnaireView.as_view()),
>>>>>>> develop
]
