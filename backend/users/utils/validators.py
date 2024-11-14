from django.core.validators import RegexValidator

validate_latin_characters = RegexValidator(
    regex=r"^[A-Za-z0-9_\s-]*$",
    message="Only latin characters, numbers, underscores, spaces and hyphens are allowed.",
)