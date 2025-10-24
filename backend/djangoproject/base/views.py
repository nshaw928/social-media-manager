from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth.models import User
from .models import Note
from .serializer import NoteSerializer, UserRegistrationSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs) # Calls TokenObtainPairView
            tokens = response.data # Tokens from response saved
            
            access_token = tokens['access']
            refresh_token = tokens['refresh']

            res = Response()
            res.data = {'sucess': True}

            res.set_cookie(
                key = "access_token",
                value = access_token,
                httponly = True,
                secure = True,
                samesite = 'None',
                path = '/'
            )

            res.set_cookie(
                key = "refresh_token",
                value = refresh_token,
                httponly = True,
                secure = True,
                samesite = 'None',
                path = '/'
            )

            return res
        

        except:
            return Response({'success': False})
        
class CustomRefreshToken(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token') # Pull old refresh token

            request.data['refresh'] = refresh_token # Save old refresh token

            response = super().post(request, *args, **kwargs)

            tokens = response.data
            access_token = tokens['access']

            res = Response()

            res.data = {'refreshed': True}

            res.set_cookie(
                key = 'access_token',
                value = access_token,
                httponly = True,
                secure = True,
                samesite = 'None',
                path = '/'
            ) # Set new access token

            return res

        except:
            return Response({'refreshed': False})

@api_view(['POST'])
def logout(request):
    try:
        res = Response()
        res.data = {'success': True}
        res.delete_cookie('access_token', path='/', samesite='None')
        res.delete_cookie('refresh_token', path='/', samesite='None')
        return res
    
    except:
        return Response({'success': False})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def is_authenticated(request):
    return Response({'authenticated': True})

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data) # pass body of request to serializer
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_email(request):
    email = request.data.get('email')
    if not email:
        return Response({'message': 'Email is required'}, status=400)
    
    try:
        user = User.objects.get(email=email)
        current_site = get_current_site(request)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Construct verification URL
        verification_url = f"{request.build_absolute_uri('/verify-email/')}{uid}/{token}/"
        
        # Send email (configure your email settings)
        send_mail(
            'Verify your email',
            f'Click the link to verify your email: {verification_url}',
            'from@example.com',
            [email],
            fail_silently=False,
        )
        
        return Response({'message': 'Verification email sent'}, status=200)
    except User.DoesNotExist:
        return Response({'message': 'User not found'}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email_token(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64)).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return Response({'message': 'Email verified successfully'}, status=200)
    else:
        return Response({'message': 'Invalid verification link'}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notes(request):
    user = request.user # saves user from request as user
    notes = Note.objects.filter(owner=user) # pulls notes for that user
    serializer = NoteSerializer(notes, many=True) # puts the note data into json
    return Response(serializer.data) # returns the json to requester

