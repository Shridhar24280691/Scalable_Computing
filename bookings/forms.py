from datetime import datetime, date, time, timedelta

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Booking


def generate_time_choices():
    choices = []
    current = datetime.combine(date.today(), time(10, 0))
    end = datetime.combine(date.today(), time(23, 30))  # last slot before 12:00 AM

    while current <= end:
        value = current.strftime("%H:%M")
        label = current.strftime("%I:%M %p")
        choices.append((value, label))
        current += timedelta(minutes=30)

    return choices


TIME_CHOICES = generate_time_choices()


class RecommendationForm(forms.Form):
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter location"
        })
    )

    cuisine = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter cuisine"
        })
    )

    budget = forms.IntegerField(
        min_value=1,
        max_value=3,
        help_text="1 = $, 2 = $$, 3 = $$$",
        widget=forms.NumberInput(attrs={
            "placeholder": "Enter budget",
            "min": 1,
            "max": 3
        })
    )

    min_rating = forms.FloatField(
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={
            "step": "0.1",
            "placeholder": "Enter minimum rating",
            "min": 0,
            "max": 5
        })
    )

    def clean_budget(self):
        budget = self.cleaned_data["budget"]
        if budget < 1 or budget > 3:
            raise ValidationError("Budget must be between 1 and 3 only.")
        return budget


class BookingForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter 10-digit phone number",
            "inputmode": "numeric",
            "maxlength": "10",
            "pattern": r"\d{10}"
        })
    )

    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date"
        })
    )

    booking_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select()
    )

    class Meta:
        model = Booking
        fields = [
            "first_name",
            "last_name",
            "customer_email",
            "phone_number",
            "restaurant_id",
            "restaurant_name",
            "location",
            "cuisine",
            "booking_date",
            "booking_time",
            "guests",
        ]
        widgets = {
            "restaurant_id": forms.HiddenInput(),
            "restaurant_name": forms.HiddenInput(),
            "location": forms.HiddenInput(),
            "cuisine": forms.HiddenInput(),
            "first_name": forms.TextInput(attrs={"placeholder": "Enter first name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Enter last name"}),
            "customer_email": forms.EmailInput(attrs={"placeholder": "Enter email address"}),
            "guests": forms.NumberInput(attrs={
                "min": 1,
                "placeholder": "Enter number of guests"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = timezone.localdate().isoformat()
        self.fields["booking_date"].widget.attrs["min"] = today

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"].strip()

        if not phone_number.isdigit():
            raise ValidationError("Phone number must contain digits only.")

        if len(phone_number) != 10:
            raise ValidationError("Phone number must be exactly 10 digits.")

        return phone_number

    def clean_booking_date(self):
        booking_date = self.cleaned_data["booking_date"]
        today = timezone.localdate()

        if booking_date < today:
            raise ValidationError("Booking date cannot be in the past.")

        return booking_date

    def clean_booking_time(self):
        booking_time = self.cleaned_data["booking_time"]

        try:
            parsed_time = datetime.strptime(booking_time, "%H:%M").time()
        except ValueError:
            raise ValidationError("Please select a valid booking time.")

        if parsed_time < time(10, 0) or parsed_time > time(23, 30):
            raise ValidationError("Booking time must be between 10:00 AM and 11:30 PM.")

        return parsed_time

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get("booking_date")
        booking_time = cleaned_data.get("booking_time")

        if booking_date and booking_time:
            today = timezone.localdate()
            now = timezone.localtime().time().replace(second=0, microsecond=0)

            if booking_date == today and booking_time <= now:
                self.add_error("booking_time", "Please select a future time for today.")

        return cleaned_data


class SignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)