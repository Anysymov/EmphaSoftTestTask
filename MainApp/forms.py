from django import forms

class FilterForm(forms.Form):
    spots_min = forms.IntegerField(label="Min spots:", required=False)
    spots_max = forms.IntegerField(label="Max spots:", required=False)
    price_min = forms.IntegerField(label="Min price:", required=False)
    price_max = forms.IntegerField(label="Max price:", required=False)

    vacant_from = forms.DateField(
        label="Vacant from:",
        required=False,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )

    vacant_untill = forms.DateField(
        label="untill:",
        required=False,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )

class LoginForm(forms.Form):
    login = forms.CharField()
    password = forms.CharField()

class OrderChoice(forms.Form):
    ORDER_CHOICES = (
        ('name_asc', 'Name ↑'),
        ('name_desc', 'Name ↓'),
        ('price_asc', 'Price ↑'),
        ('price_desc', 'Price ↓'),
        ('spots_asc', 'Spots ↑'),
        ('spots_desc', 'Spots ↓'),
    )

    orderchoice = forms.ChoiceField(choices=ORDER_CHOICES, label="Order by")

class RegistrationForm(forms.Form):
    username = forms.CharField(label="Username")
    full_name = forms.CharField(label="Full name")
    password1 = forms.CharField(label="Password")
    password2 = forms.CharField(label="Repeat password")

class ReservationForm(forms.Form):
    room = forms.ChoiceField(label="Room for reservation: ")

    date_from = forms.DateField(
        label="Reserve from:",
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )

    date_untill = forms.DateField(
        label="untill:",
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )