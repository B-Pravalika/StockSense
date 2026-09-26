import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils import timezone


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('/')

        return render(
            request,
            'accounts/login.html',
            {
                'error': 'Invalid username or password.'
            }
        )

    return render(
        request,
        'accounts/login.html'
    )


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not email or not password:
            return render(
                request,
                'accounts/signup.html',
                {
                    'error': 'All fields are required.',
                    'username': username,
                    'email': email,
                }
            )

        if password != confirm_password:
            return render(
                request,
                'accounts/signup.html',
                {
                    'error': 'Passwords do not match.',
                    'username': username,
                    'email': email,
                }
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'accounts/signup.html',
                {
                    'error': 'Username already exists.',
                    'username': username,
                    'email': email,
                }
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                'accounts/signup.html',
                {
                    'error': 'An account with this email already exists.',
                    'username': username,
                    'email': email,
                }
            )

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('accounts:login')

    return render(
        request,
        'accounts/signup.html'
    )


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        user = User.objects.filter(
            email__iexact=email
        ).first()

        if user is None:
            return render(
                request,
                'accounts/forgot_password.html',
                {
                    'error': 'No account was found with this email.'
                }
            )

        # Generate a 6-digit OTP.
        otp = str(random.randint(100000, 999999))

        # Store OTP and expiry in the session.
        request.session['password_reset_user_id'] = user.id
        request.session['password_reset_otp'] = otp
        request.session['password_reset_otp_expires'] = (
            timezone.now().timestamp() + 300
        )

        send_mail(
            subject='StockSense Password Reset OTP',
            message=(
                f'Your StockSense password reset OTP is: {otp}\n\n'
                'This OTP is valid for 5 minutes.'
            ),
            from_email=None,
            recipient_list=[user.email],
        )

        return redirect('accounts:verify_otp')

    return render(
        request,
        'accounts/forgot_password.html'
    )


def verify_otp_view(request):
    if 'password_reset_user_id' not in request.session:
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()

        stored_otp = request.session.get(
            'password_reset_otp'
        )

        expiry = request.session.get(
            'password_reset_otp_expires'
        )

        if not stored_otp or not expiry:
            return render(
                request,
                'accounts/verify_otp.html',
                {
                    'error': 'OTP session expired. Please request a new OTP.'
                }
            )

        if timezone.now().timestamp() > float(expiry):
            return render(
                request,
                'accounts/verify_otp.html',
                {
                    'error': 'OTP has expired. Please request a new OTP.'
                }
            )

        if entered_otp != stored_otp:
            return render(
                request,
                'accounts/verify_otp.html',
                {
                    'error': 'Invalid OTP. Please try again.'
                }
            )

        request.session['password_reset_verified'] = True

        return redirect('accounts:reset_password')

    return render(
        request,
        'accounts/verify_otp.html'
    )


def reset_password_view(request):
    if not request.session.get('password_reset_verified'):
        return redirect('accounts:forgot_password')

    user_id = request.session.get(
        'password_reset_user_id'
    )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        request.session.flush()
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(
                request,
                'accounts/reset_password.html',
                {
                    'error': 'Passwords do not match.'
                }
            )

        try:
            validate_password(password, user)
        except Exception as error:
            return render(
                request,
                'accounts/reset_password.html',
                {
                    'error': ' '.join(error.messages)
                }
            )

        user.set_password(password)
        user.save()

        # Remove password-reset information from the session.
        request.session.flush()

        return redirect('accounts:login')

    return render(
        request,
        'accounts/reset_password.html'
    )