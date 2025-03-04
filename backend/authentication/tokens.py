import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import Token, RefreshToken
from datetime import timedelta
from django.contrib.sites.shortcuts import get_current_site
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid 

def send_email(user, request):
    token = get_tokens_for_user(user)
            
    # Get the current domain
    current_site = get_current_site(request)
    # print("SITEWEEB =>    ", current_site)
    activation_link = f'http://127.0.0.1:8000/api/activate/{token["access"]}'
  
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    text = f"Activate Your Account\n\nPlease click the activation link below to activate your account:\n\n{activation_link}"
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = [user.email]
    msg['Subject'] = 'Email Confirmation'
    msg.attach(MIMEText(text, 'plain'))
    
    server.sendmail(settings.EMAIL_HOST_USER, [user.email], text)

def get_tokens_for_user(user):
    refresh = CustomRefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def token_decoder(token):
    try:
        # Decode the token
        decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_data['user_id']  # Assuming 'user_id' is part of the token payload
    except jwt.ExpiredSignatureError:
        return -1
    except jwt.InvalidTokenError:
        # Token is invalid
        return None
    
class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token["email"] = user.email  # Add the email to the token payload
        token["user_id"] = user.id,
        token['jti'] = str(uuid.uuid4()) 
        return token


class AccountActivationToken(Token):
    token_type = "account-activation"
    lifetime = timedelta(minutes=15)
