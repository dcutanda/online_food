import os
from django.core.exceptions import ValidationError

def allow_only_images_validator(value):
    extension = os.path.splitext(value.name)[1] # cover-image.jpg the index 1 will extract the extension

    valid_extensions = ['jpg', 'png', 'jpeg']
    if extension.lower() not in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed extensions: ' + str(valid_extensions))
