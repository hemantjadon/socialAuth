from django.conf import settings
import requests


def Verify_Google_User_Id_Token(id_token):#--Verifies Client ID And returns userID
    KEYS = settings.SOCIAL_DATA["KEYS"]
    CLIENT_ID = KEYS["google"]["SOCIAL_AUTH_GOOGLE_CLIENT_ID"]

    payload = {'id_token':id_token}
    url = "https://www.googleapis.com/oauth2/v3/tokeninfo"

    r = requests.get(url,params=payload)
    if r.status_code == 200:
        json_resp = r.json()
        try:
            if json_resp["aud"] != CLIENT_ID:
                raise ValueError("Unrecognized Client")
            if json_resp["iss"] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError("Wrong Issuer")
        except ValueError:
            print("Invalid Token")
            return False

        return json_resp

    else:
        print("Invalid Token")
        return False


def GetAccessToken(auth_code):
    KEYS = settings.SOCIAL_DATA["KEYS"]
    CLIENT_ID = KEYS["google"]["SOCIAL_AUTH_GOOGLE_CLIENT_ID"]
    CLIENT_SECRET = KEYS["google"]["SOCIAL_AUTH_GOOGLE_CLIENT_SECRET"]

    url = "https://www.googleapis.com/oauth2/v4/token"
    payload = {'code':auth_code,'client_id':CLIENT_ID,'client_secret':CLIENT_SECRET,'grant_type':'authorization_code','redirect_uri':'postmessage'}

    r = requests.post(url,data=payload)
    if r.status_code == 200:
        json_resp = r.json()
        return json_resp
    else:
        print ("Error in getting google access token")
        return False
