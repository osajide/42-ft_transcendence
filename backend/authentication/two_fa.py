from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from .middlewares import CookieJWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from io import BytesIO
import pyotp, qrcode, base64
from PIL import Image
from rest_framework.views import APIView
from .models import *
from .serializers import *

# i will give the user an access token when he logged in with a short time lived
# this is will help me to check if its authenticated or not

class SetupTwoFa(APIView):
    
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def generate_qr_code(provisioning_uri):
        """
        Generate a base64-encoded QR code image from a provisioning URI.
        """
        qr = qrcode.make(provisioning_uri)
        qr_bytes = BytesIO()
        qr.save(qr_bytes, 'PNG')
        return base64.b64encode(qr_bytes.getvalue()).decode()

    def get(self, request):

       
        request.user.is_2fa_verified = False
        request.user.save()

         # Generate a TOTP secret key
        secret_key = pyotp.random_base32()
        request.user.secret_key = secret_key
        request.user.save()
        # Create a TOTP provisioning URI
        uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=request.user.first_name + ' ' + request.user.last_name,  
            issuer_name='42_pingpong'
        )

        # Generate the QR code as a base64 string
        qr_b64 = self.generate_qr_code(uri)

        return Response({'qrcode': "data:image/png;base64," + qr_b64}, status=200)


# class VerifyCode(APIView):

#     authentication_classes = [CookieJWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
        
#         code = request.data.get('code')
#         if not code:
#             return Response({"error": "2FA code is required"}, status=400)

#         # code = "620376"
#         totp = pyotp.TOTP(request.user.secret_key)

#         if totp.verify(code):

#             request.user.is_2fa_verified = True
#             request.user.save()
#             response = Response({
#                 'message': '2FA code verification successful',
#             }, status=status.HTTP_200_OK)

#             return response
        
#         else:
#             return Response({"message": "Invalid 2FA code"}, status=400)

class VerifyCode(APIView):

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        code = request.data.get('code')
        if not code:
            return Response({"error": "2FA code is required"}, status=200)

        # code = "620376"
        totp = pyotp.TOTP(request.user.secret_key)

        print('code', code)
        if totp.verify(code):

            request.user.is_2fa_verified = True
            request.user.save()

            # user = UserAccount.objects.filter(email = request.user.email).first()

            serializer = UserSerializer(request.user)
            response =  Response({
                'message': 'successfully Logged',
                'user': serializer.data
                } , status=status.HTTP_200_OK)
            # response = Response({
            #     'message': '2FA code verification successful',
            # }, status=status.HTTP_200_OK)

            return response
        
        else:
            return Response({"error": "Invalid 2FA code"}, status=200)