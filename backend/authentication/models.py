from django.db import models
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import os

# Create your models here.

class UserAccountManager(BaseUserManager):
    """Manager for UserAccount"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
    
# def get_upload_path(instance, filename):
    # extension = os.path.splitext(filename)[1]
    # return f'{instance.id}{extension}'
    # return

class UserAccount(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50, default="")
    email = models.EmailField(validators=[EmailValidator()], unique=True) # add email to be unique
    password = models.CharField(max_length=128)
    verified_mail = models.BooleanField(default=True)
    # avatar = models.ImageField(upload_to=get_upload_path, default='user.svg')
    avatar = models.ImageField(upload_to='', default='user.svg') 
    user_state = models.CharField(max_length=50, default='offline')
    is_staff = models.BooleanField(default=False)  # Required for admin access
    secret_key = models.CharField(max_length=50, null=True, blank=True)
    is_2fa_verified = models.BooleanField(default=False)
    is_42 = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Leave empty to only require username and password
    objects = UserAccountManager()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        try :
            # print('*****self: ', self.id)
            # print('*****selfaa: ', self.avatar.url)
            # self.avatar.url = f'saaaalaam.png'
            # self.avatar = f'saaaalaam.png'
            if self.nickname == "":
                self.nickname = self.first_name + '_' + self.last_name
            super().save(*args, **kwargs)
            # print('aaaaa:::::: ', self.avatar)
        except Exception as e:
            print("exception raised")

   
    # def is_authenticated(self):
    #     """
    #     Always return True for instances of UserAccount.
    #     Mimics Django's behavior for authenticated user instances.
    #     """
    #     return True
    
    UNUSABLE_PASSWORD_PREFIX = '!UNUSABLE-'  # Prefix for unusable passwords

    def set_unusable_password(self):
        """
        Marks the password as unusable by setting it to a specific value.
        """
        import uuid
        # Generate a unique unusable password value
        self.password = make_password(f"{self.UNUSABLE_PASSWORD_PREFIX}{uuid.uuid4().hex}")

    def __str__(self) -> str:
        return f"{self.first_name.capitalize()} {self.last_name.upper()}"
    

# from django.db import models
# from django.contrib.auth.base_user import BaseUserManager
# from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin

# class CustomerUserManager(BaseUserManager):
#     def create_user(self, username, password=None, **extra_fields):
#         if not username:
#             raise ValueError("The Username field must be set")
#         user = self.model(username=username, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, username, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')

#         return self.create_user(username, password, **extra_fields)
