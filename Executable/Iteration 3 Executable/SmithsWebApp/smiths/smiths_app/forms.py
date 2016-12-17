from django import forms


class SignInForm(forms.Form):
    cust_name = forms.CharField(required=True)
    cust_id = forms.IntegerField(min_value=0)
    new_cust = forms.CheckboxInput()
