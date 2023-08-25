from .views import CreateUserView, VerifyAPIView, GetNewVerificationCode, ChangeUserInformationView, UserLoginView, \
    LoginRefreshView, UserLogoutView, ForgotPasswordView, ResetPasswordView
from django.urls import path

urlpatterns = [
    path('signup/', CreateUserView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('login/refresh/', LoginRefreshView.as_view()),
    path('logout/', UserLogoutView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('new-verify/', GetNewVerificationCode.as_view()),
    path('change-user-info/', ChangeUserInformationView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),

]
