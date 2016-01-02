from django.shortcuts import render,redirect
from django.conf import settings
from django.http import HttpResponse,JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import requires_csrf_token,csrf_protect
from django.core.exceptions import SuspiciousOperation,ObjectDoesNotExist
from socialAuth.models import SocialUser
from django.contrib.auth import get_user_model
from django.contrib.auth import login,logout,authenticate
import uuid

from socialAuth.Verifications.googleVerifications import *
# Create your views here.


#-----------------------Generic Views------------------------#

@require_http_methods(["POST"])
@csrf_protect
def SocialAuthGetOrCreate(request):
    binary_post_data_str = request.body
    post_data_str = binary_post_data_str.decode('utf-8')
    post_array = post_data_str.split("&")
    post_dict = {}
    for data in post_array:
        token = data.split("=")
        post_dict[token[0]]=token[1]

    try:
        provider = post_dict["provider"]
    except KeyError:
        provider = ""
        raise SuspiciousOperation('Precondition Does Not Match')
        return JsonResponse({"status":"error",'code':400,'message':'BAD Request'})

    if provider == "google":
        status_dict = GetOrCreateGoogleUser(post_dict,request)

    return JsonResponse(status_dict)


#------------Google Specific Views and Functions-------------#

def GetOrCreateGoogleUser(post_dict,request):
    try:
        id_token = post_dict["id_token"]
    except KeyError:
        id_token=""
        raise SuspiciousOperation('Precondition Does Not Match')
        return JsonResponse({"status":"error",'code':400,'message':'BAD Request'})
    resp = Verify_Google_User_Id_Token(id_token)

    if resp != False:
        userID = resp['sub']
        email = resp['email']
        try:
            user = get_user_model().objects.get(email=email)
            try:
                social_user_of_user = user.social_relation

                if social_user_of_user.userID == userID:
                    if social_user_of_user.provider =="google":
                        if user.is_active == True:
                            user.backend='django.contrib.auth.backends.ModelBackend'
                            login(request,user)
                            social_user_of_user.times_logged_in = social_user_of_user.times_logged_in + 1
                            social_user_of_user.save()
                            return {"status":"success","code":200,"type":"get","message":"got user","first_time":"false","redirect":settings.SOCIAL_DATA["URLS"]["SOCIAL_AUTH_LOGIN_REDIRECT_URL"]}
                        else:
                            return {"status":"error","code":501,"type":"get","message":"inactive user","redirect":settings.SOCIAL_DATA["URLS"]["SOCIAL_AUTH_INACTIVE_USER_URL"]}
                    else:
                        return {"status":"error","code":401,"type":"get","message":"wrong provider","redirect":settings.SOCIAL_DATA["URLS"]["SOCIAL_AUTH_LOGIN_ERROR_URL"]}
                else:
                    return {"status":"error","code":402,"type":"get","message":"invalid user id","redirect":settings.SOCIAL_DATA["URLS"]["SOCIAL_AUTH_LOGIN_ERROR_URL"]}

            except ObjectDoesNotExist:
                return {"status":"error","code":403,"type":"get","message":"not social user","redirect":settings.SOCIAL_DATA["URLS"]["SOCIAL_AUTH_LOGIN_ERROR_URL"]}

        except get_user_model().DoesNotExist:
            user = None
            first_name = resp['given_name']
            last_name = resp['family_name']
            try:
                email_key = resp["email_verified"]
                if email_key == "true":
                    email_verified = True
                else:
                    email_verified = False
            except KeyError:
                email_verified = False

            uuid_username = uuid.uuid5(uuid.uuid1(), email)
            username = str(uuid_username).replace("-","")
            uuid_password = uuid.uuid5(uuid.uuid1(),userID)
            password = str(uuid_password).replace("=","")
            user = get_user_model().objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=email_verified
            )
            user.save()
            user.set_password(password)
            user.save()

            social_user = SocialUser.objects.create(
                user = user,
                userID = userID,
                provider = "google"
            )
            user.backend='django.contrib.auth.backends.ModelBackend'
            login(request,user)
            social_user.times_logged_in = social_user.times_logged_in + 1
            social_user.save()
            return {"status":"success","code":200,"type":"create","message":"created user","first_time":"true","redirect":settings.SOCIAL_DATA["URLS"]["SOCIAL_AUTH_FIRST_LOGIN_REDIRECT_URL"]}




@require_http_methods(["POST"])
@csrf_protect
def GoogleOfflineAccessAuthCode(request):
    try:
        PERM = settings.SOCIAL_DATA["PERMISSIONS"]["google"]["SOCIAL_AUTH_GET_OFFLINE_ACCESS"]
    except KeyError:
        raise SuspiciousOperation('Request Invalid : Setting Does Not Match')
        return JsonResponse({"status":"error",'code':400,'message':'BAD Request'})
    if PERM and PERM == "true":
        binary_post_data_str = request.body
        post_data_str = binary_post_data_str.decode('utf-8')
        post_array = post_data_str.split("&")
        post_dict = {}
        for data in post_array:
            token = data.split("=")
            post_dict[token[0]]=token[1]
        try:
            x = post_dict['auth_code'].split("%2F")
            post_dict['auth_code']=x[0]+str('/')+x[1]
            auth_code = post_dict["auth_code"]

        except KeyError:
            auth_code = ""
            raise SuspiciousOperation('Precondition Does Not Match')
            return JsonResponse({"status":"error",'code':400,'message':'BAD Request'})

        resp = GetAccessToken(auth_code)
        id_token = ""
        access_token = ""
        refresh_token = ""

        if resp != False:
            try:
                id_token = resp['id_token']
                access_token = resp['access_token']
                refresh_token = resp['refresh_token']
            except KeyError:
                pass

            id_resp = Verify_Google_User_Id_Token(id_token)
            if id_resp != False:
                try:
                    userID = id_resp['sub']
                except KeyError:
                    userID = ""

                try:
                    social_user = SocialUser.objects.get(userID = userID)
                except ObjectDoesNotExist:
                    social_user =None
                    raise SuspiciousOperation("Corresponding social user Does not exist in database")
                    return JsonResponse({"status":"error",'code':400,'message':'BAD Request'})

                if social_user is not None:
                    social_user.access_token = access_token
                    social_user.refresh_token = refresh_token
                    social_user.save()
                    status_dict = {"status":"success","code":200,"type":"create","message":"created user","first_time":"true","redirect":settings.SOCIAL_DATA["URLS"]["SOCIAL_AUTH_FIRST_LOGIN_REDIRECT_URL"]}
                    return JsonResponse(status_dict)
            else:
                raise SuspiciousOperation("id token not verified")
                return JsonResponse({"status":"error",'code':400,'message':'BAD Request'})
        else:
            raise SuspiciousOperation("Unable to process Auth Code")
            return JsonResponse({"status":"error",'code':400,'message':'BAD Request'})

    else:
        raise SuspiciousOperation('Request : Invalid Setting Does Not Match')
        return JsonResponse({"status":"error",'code':400,'message':'BAD Request'})
