from django.urls import path 
from .views import login_view, signup_view,OwnerSignupView

urlpatterns = [
    path('login/', login_view.as_view(), name='login'),
    path('signup/', signup_view.as_view(), name='signup'),
    path('owner/signup/', OwnerSignupView.as_view(), name='owner_signup'),

]