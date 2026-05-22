from django import forms


class ComplaintForm(forms.Form):
    complaint_text = forms.CharField(
        label='Describe your complaint',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
    )