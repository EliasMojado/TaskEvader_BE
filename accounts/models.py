from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import os

def profile_pic_upload_to(instance, filename):
    """
    Store uploads under MEDIA_ROOT/profile_pics/
    and name the file <username>.<ext>
    """
    base, ext = os.path.splitext(filename)
    new_name = f"{instance.username}{ext.lower()}"
    return os.path.join('profile_pics', new_name)

class UserProfile(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128, default='',
                                help_text="Hashed password; use set_password() to assign.")
    display_name = models.CharField(max_length=150)
    
    # ← new field for uploaded files
    profile_pic = models.ImageField(
        upload_to=profile_pic_upload_to,
        blank=True,
        null=True,
        help_text="Upload a profile picture."
    )

    class Meta:
        db_table = 'accounts_user_profile'

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save(update_fields=['password'])

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
