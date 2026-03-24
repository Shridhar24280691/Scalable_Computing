from django.db import models
from django.contrib.auth.models import User
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    restaurant_id = models.CharField(max_length=50)
    restaurant_name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    cuisine = models.CharField(max_length=100)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    guests = models.PositiveIntegerField()
    card_image_data_url = models.TextField(blank=True)
    qr_code_data_url = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.restaurant_name}"