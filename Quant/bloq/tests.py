from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import *
import os
from django.conf import settings

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.unit = units_model.objects.create(unit='mm')
        self.dxf_file_path = os.path.join(settings.MEDIA_ROOT, 'sample.dxf')
        with open(self.dxf_file_path, 'rb') as f:
            file_content = f.read()

        self.dxf_file = SimpleUploadedFile("sample.dxf", file_content, content_type="application/dxf")

    def test_home_post(self):
        
        response = self.client.post(reverse('home'), {'unit': 'mm', 'dxf_file': self.dxf_file})
        self.assertEqual(response.status_code, 200)

    def test_home_post(self):
        response = self.client.post(reverse('home'), {'unit': 'mm', 'dxf_file': self.dxf_file})
        self.assertEqual(response.status_code, 200)  # Assuming it redirects to another page
        # Add more assertions as needed

    def test_params1_view(self):
        response = self.client.get(reverse('block-params'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'block-params.html')

    # Add tests for other views similarly

    def test_cancel_view(self):
        # Set up data
        block_model.objects.create(width=10, height=10, length=10, layer='Layer1', unit=self.unit)
        door_model.objects.create(width=20, height=20, quantity=2, unit=self.unit)
        window_model.objects.create(width=30, height=30, quantity=3, unit=self.unit)
        opening_model.objects.create(area=100, quantity=4, unit=self.unit)

        # Make request to cancel view
        response = self.client.get(reverse('cancel'))

        # Assert that all records associated with the selected unit are deleted
        self.assertEqual(block_model.objects.count(), 0)
        self.assertEqual(door_model.objects.count(), 0)
        self.assertEqual(window_model.objects.count(), 0)
        self.assertEqual(opening_model.objects.count(), 0)

        # Assert that the selected unit is deleted
        self.assertFalse(units_model.objects.filter(unit='mm').exists())

    # Add tests for other views similarly