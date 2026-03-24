from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from .forms import RecommendationForm, BookingForm, SignUpForm, LoginForm
from .models import Booking
from .services import RecommendationAPIClient, BookingQueueProducer

import os
import boto3

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
booking_cards_table = dynamodb.Table("BookingCards")


@never_cache
def root_redirect_view(request):
    # Always clear any old logged-in session when opening "/"
    if request.user.is_authenticated:
        logout(request)
    return redirect("login")


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SignUpForm()

    return render(request, "bookings/signup.html", {"form": form})


@method_decorator(never_cache, name="dispatch")
class CustomLoginView(LoginView):
    template_name = "bookings/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = False


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url="/login/")
def home(request):
    form = RecommendationForm()
    return render(request, "bookings/home.html", {"form": form})


@login_required(login_url="/login/")
def recommendations(request):
    if request.method != "POST":
        return redirect("home")

    form = RecommendationForm(request.POST)
    if not form.is_valid():
        return redirect("home")

    payload = form.cleaned_data
    client = RecommendationAPIClient()
    data = client.get_recommendations(payload)

    restaurants = data.get("recommended_restaurants", [])

    context = {
        "restaurants": restaurants,
        "restaurants_data": restaurants,
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, "bookings/recommendations.html", context)


@login_required(login_url="/login/")
def booking_form(request):
    if request.method != "POST":
        return redirect("home")

    initial_data = {
        "restaurant_id": request.POST.get("restaurant_id"),
        "restaurant_name": request.POST.get("restaurant_name"),
        "location": request.POST.get("location"),
        "cuisine": request.POST.get("cuisine"),
    }

    form = BookingForm(initial=initial_data)
    return render(request, "bookings/booking_form.html", {"form": form})


@login_required(login_url="/login/")
def create_booking(request):
    if request.method != "POST":
        return redirect("home")

    form = BookingForm(request.POST)
    if not form.is_valid():
        return render(request, "bookings/booking_form.html", {"form": form})

    booking = form.save(commit=False)
    booking.user = request.user
    booking.save()

    card_payload = {
        "booking_id": str(booking.id),
        "firstName": booking.first_name,
        "lastName": booking.last_name,
        "email": booking.customer_email,
        "phone": booking.phone_number,
        "addressLine1": booking.restaurant_name,
        "booking_date": str(booking.booking_date),
        "booking_time": str(booking.booking_time),
        "guests": booking.guests,
        "theme": "default",
        "includeQr": True,
        "includeCardImage": True,
        "organizationName": booking.restaurant_name,
    }

    producer = BookingQueueProducer()
    producer.send_booking_job(card_payload)

    return redirect("booking_success", booking_id=booking.id)


@login_required(login_url="/login/")
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    response = booking_cards_table.get_item(Key={"booking_id": str(booking.id)})
    card_data = response.get("Item")

    return render(
        request,
        "bookings/booking_success.html",
        {
            "booking": booking,
            "card_data": card_data,
        },
    )


@login_required(login_url="/login/")
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "bookings/booking_history.html", {"bookings": bookings})