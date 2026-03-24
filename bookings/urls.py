from django.urls import path
from . import views

urlpatterns = [
    path("", views.root_redirect_view, name="root"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    path("home/", views.home, name="home"),
    path("recommendations/", views.recommendations, name="recommendations"),
    path("booking-form/", views.booking_form, name="booking_form"),
    path("create-booking/", views.create_booking, name="create_booking"),
    path("booking-success/<int:booking_id>/", views.booking_success, name="booking_success"),
    path("booking-history/", views.booking_history, name="booking_history"),
]