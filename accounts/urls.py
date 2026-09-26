from django.urls import path

from .views import (
    login_view,
    signup_view,
    logout_view,
    forgot_password_view,
    verify_otp_view,
    reset_password_view,
)


app_name = 'accounts'


urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),

    path(
        'forgot-password/',
        forgot_password_view,
        name='forgot_password'
    ),

    path(
        'verify-otp/',
        verify_otp_view,
        name='verify_otp'
    ),

    path(
        'reset-password/',
        reset_password_view,
        name='reset_password'
    ),
]