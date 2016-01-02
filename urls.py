from django.conf.urls import url
from socialAuth.views import SocialAuthGetOrCreate,GoogleOfflineAccessAuthCode

urlpatterns = [
    url(r'^accounts/google-offline-auth-code/$',GoogleOfflineAccessAuthCode,name='google_offline_access_auth_code'),
    url(r'^accounts/get-or-create/$',SocialAuthGetOrCreate,name='social_auth_get_create'),
]
