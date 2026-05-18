from django.urls import path 
from .views import ResetPasswordView, login_view, signup_view,OwnerSignupView,GoogleLoginView,VerifyOTPView,sendotpView,KYCView,logout_view

urlpatterns = [
    path('login/', login_view.as_view(), name='login'),
    path('signup/', signup_view.as_view(), name='signup'),
    path('logout/', logout_view.as_view(), name='logout'),
    path('owner/signup/', OwnerSignupView.as_view(), name='owner_signup'),
    path('google/login/', GoogleLoginView.as_view(), name='google_login'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('send-otp/', sendotpView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('kyc/',KYCView.as_view(),name='kyc')
]
