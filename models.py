from django.db import models

# Create your models here.

try:
    from django.conf import settings
    USER = settings.AUTH_USER_MODEL
except:
    from django.contrib.auth.models import User
    USER = User

class SocialUser(models.Model):
    user = models.OneToOneField(USER,related_name='social_relation')
    userID = models.TextField(blank=False,null=True)
    provider = models.CharField(max_length=15,blank=False,null=True)
    access_token = models.TextField(blank=False,null=True)
    refresh_token = models.TextField(blank=False,null=True)
    times_logged_in = models.IntegerField(default=0)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.provider + " / " +self.userID
