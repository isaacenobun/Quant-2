from django import forms

class MediaUploadForm(forms.Form):
    dxf_file = forms.FileField(label='Choose DXF File', widget=forms.FileInput(attrs={'accept': '.dxf'}))