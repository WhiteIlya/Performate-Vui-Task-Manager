from typing import Optional
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser

from .utils.validators import validate_latin_characters


class UserManager(BaseUserManager):
    """Custom manager for user DB"""

    def create_user(self, email: str, first_name: Optional[str] = '', last_name: Optional[str] = '', password: Optional[str] = None) -> "User":
        """
        Creates and saves a User with the given email, first_name, last_name and password.
        """

        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)

        user = self.model(email=email, first_name=first_name, last_name=last_name)
        if password:
            user.set_password(password)  # Here the password automatically hashes before it loads to the db
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email: str, password: Optional[str] = None) -> "User":
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
    

class User(AbstractUser):
    username = None  # Get rid of the useless property
    first_name = models.CharField(
        max_length=50,
        blank=True,
        validators=[validate_latin_characters],
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
        validators=[validate_latin_characters],
    )
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,  # Validation of the email on db level
    )
    is_admin = models.BooleanField(default=False)
    vui_configured = models.BooleanField(default=False)
    assistant_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Unique Assistant ID from OpenAI for the user."
    )
    thread_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Unique Thread ID from OpenAI for the user."
    )
    ttm_stage = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="TTM stage of the user.",
        default="Precontemplation"
    )

    USERNAME_FIELD: str = "email"  # is used as the unique identifier
    EMAIL_FIELD: str = "email"
    REQUIRED_FIELDS = []

    objects: UserManager = UserManager()

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        """
        Text representation of user.

        Display its first name and last name.
        """
        return self.get_full_name()
    
    # it is also possible to configure has_perm has_module_perms or any other @property

    # Map unused properties to is_admin
    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"