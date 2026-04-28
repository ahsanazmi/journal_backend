import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from manuscripts.serializers import ManuscriptSerializer
from django.core.files.uploadedfile import SimpleUploadedFile

class DummyReq:
    def __init__(self, data):
        self.data = data

data = {
    'title': 'Test Script Title',
    'abstract': 'Test Abstract',
    'authorName': 'John Doe',
    'emailAddress': 'john@example.com',
    'mobileNumber': '1234567890',
    'file': SimpleUploadedFile("file.pdf", b"file_content", content_type="application/pdf")
}

req = DummyReq(data)
serializer = ManuscriptSerializer(data=data, context={'request': req})
print('Is Valid:', serializer.is_valid())
if serializer.is_valid():
    ms = serializer.save()
    print('MS ID:', ms.id)
    print('Authors:', list(ms.authors.all()))
else:
    print(serializer.errors)
