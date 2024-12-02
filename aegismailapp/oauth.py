import os
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import OAuthCredentials
from django.utils import timezone
import datetime

def get_google_flow():
    """
    Creates a new OAuth2 flow using the client secrets file.
    Returns the flow object.
    """
    credentials_path = os.path.join(settings.BASE_DIR, 'credentials.json')
    return Flow.from_client_secrets_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/userinfo.email'],
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )

def google_login(request):
    """
    Initiates the Google OAuth2 login process by generating an authorization URL
    and redirecting the user to Google's OAuth2 consent screen.
    """
    flow = get_google_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',  # Request offline access to refresh tokens
        include_granted_scopes='true'  # Request access to all authorized scopes
    )

    # Save the state in the session to verify the callback
    request.session['state'] = state
    return redirect(authorization_url)

def google_callback(request):
    """
    Handles the callback from Google's OAuth2 server after user consent.
    Retrieves the access token and stores it in the database.
    """
    state = request.session.get('state')  # Retrieve the state from the session
    if request.GET.get('state') != state:
        return JsonResponse({'error': 'Invalid state parameter'}, status=400)

    flow = get_google_flow()
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    if not flow.credentials:
        return JsonResponse({'error': 'Authentication failed'}, status=400)

    credentials = flow.credentials

    # Save or update the OAuth credentials in the database
    OAuthCredentials.objects.update_or_create(
        provider='google',
        defaults={
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token or '',
            'expires_at': credentials.expiry or (timezone.now() + datetime.timedelta(seconds=3600))
        }
    )

    return JsonResponse({'message': 'Authentication successful'})

def get_google_credentials():
    """
    Fetches Google user credentials by running a local server for OAuth2 flow.
    Returns the credentials object.
    """
    credentials_path = os.path.join(settings.BASE_DIR, 'credentials.json')
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/userinfo.profile']  # Scope for user profile
    )
    credentials = flow.run_local_server(port=0)
    return credentials
