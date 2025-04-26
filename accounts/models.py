from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    username = models.CharField(max_length=150, unique=True, default='', blank=True)
    password = models.CharField(max_length=128, default='', blank=True,
                                help_text="Hashed password; use set_password() to assign.")
    name = models.CharField(max_length=150)
    
    # ← new field for uploaded files
    profile_pic = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text="Upload a profile picture."
    )

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save(update_fields=['password'])

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
