from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div


class UploadDataForm(forms.Form):
    """
    Form untuk upload file data
    """
    file = forms.FileField(
        label='Pilih File',
        help_text='Format yang didukung: .xlsx, .xls, .csv (Maks. 100MB)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv'
        })
    )
    
    notes = forms.CharField(
        label='Catatan',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Tambahkan catatan untuk upload ini (opsional)'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            'file',
            'notes',
            Div(
                Submit('submit', 'Upload', css_class='btn btn-primary'),
                css_class='mt-3'
            )
        )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if file:
            # Validasi ukuran file (max 100MB)
            if file.size > 100 * 1024 * 1024:
                raise forms.ValidationError('Ukuran file terlalu besar. Maksimal 100MB.')
            
            # Validasi ekstensi file
            valid_extensions = ['.xlsx', '.xls', '.csv']
            ext = file.name.lower()[file.name.rfind('.'):]
            if ext not in valid_extensions:
                raise forms.ValidationError(f'Format file tidak valid. Gunakan: {", ".join(valid_extensions)}')
        
        return file


class KomitmenUploadForm(forms.Form):
    """
    Form untuk upload file komitmen
    """
    file = forms.FileField(
        label='Pilih File Komitmen',
        help_text='Format: KOMITMEN_NOV_2025.xlsx (Excel only, Maks. 50MB)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        })
    )
    
    notes = forms.CharField(
        label='Catatan',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Tambahkan catatan untuk upload ini (opsional)'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Div(
                Div('file', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('notes', css_class='col-12'),
                css_class='row mt-3'
            ),
            Div(
                Submit('submit', 'Validasi & Preview', css_class='btn btn-primary'),
                css_class='mt-3'
            )
        )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if file:
            # Validasi ukuran file (max 50MB)
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError('Ukuran file terlalu besar. Maksimal 50MB.')
            
            # Validasi ekstensi file (Excel only)
            valid_extensions = ['.xlsx', '.xls']
            ext = file.name.lower()[file.name.rfind('.'):]
            if ext not in valid_extensions:
                raise forms.ValidationError(f'Format file tidak valid. Hanya Excel (.xlsx, .xls) yang diperbolehkan.')
            
            # Validasi format nama file
            filename = file.name.upper()
            if 'KOMITMEN' not in filename:
                raise forms.ValidationError(
                    'Nama file harus mengandung kata "KOMITMEN". '
                    'Contoh: KOMITMEN_NOV_2025.xlsx'
                )
        
        return file
