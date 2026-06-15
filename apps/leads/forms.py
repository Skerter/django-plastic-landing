from django import forms
from .models import Lead


class LeadForm(forms.ModelForm):
    consent = forms.BooleanField(
        required=True,
        label='Я согласен на обработку персональных данных',
    )
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Lead
        fields = ['name', 'phone', 'email', 'comment', 'type', 'product']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Ваше имя'})
        self.fields['phone'].widget.attrs.update({'placeholder': '+7 (900) 000-00-00'})
        self.fields['email'].required = False
        self.fields['email'].widget.attrs.update({'placeholder': 'email@example.com'})
        self.fields['comment'].required = False
        self.fields['product'].required = False

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')
        return ''
