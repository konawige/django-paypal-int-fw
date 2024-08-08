from django.forms import ModelForm, TextInput, EmailInput, NumberInput

from donate.models import DonateClient


class DonateClientForm(ModelForm):
    """
    A form for payppal.
    """
    class Meta:
        model = DonateClient
        fields = ['name', 'email', 'amount']
        widgets = {
            'name': TextInput(attrs={
                'class': "form-control ",
            }),
            'email': EmailInput(attrs={
                'class': "form-control",
            }),
            'amount': NumberInput(attrs={
                'class': "form-control",
            }),
        }
