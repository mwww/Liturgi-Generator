import os
from django.conf import settings

# static_file_timestamp is used to create STATIC_FILE_TIMESTAMP variable, used in modifying css filename (see base.html)
def static_file_timestamp(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'style.css')
    try:
        # Get the last modification time of the css file
        timestamp = int(os.path.getmtime(file_path))
        return {'STATIC_FILE_TIMESTAMP': timestamp}
    except OSError:
        return {'STATIC_FILE_TIMESTAMP': ''}
