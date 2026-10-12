from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Trip(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    BUDGET_CURRENCY_CHOICES = [
        ("TRY", "₺ TRY"),
        ("USD", "$ USD"),
        ("EUR", "€ EUR")
    ]

    budget_currency = models.CharField(
        max_length=3,
        choices=BUDGET_CURRENCY_CHOICES,
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="trips"
    )

    TRIP_TYPES = [
        ("domestic" , "Domestic"),
        ("international" , "International")
    ]

    trip_type = models.CharField (
        max_length=15,
        choices = TRIP_TYPES
    )

    def __str__(self):
        return self.name

class ChecklistItem(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete= models.CASCADE,
        related_name="checklist_items"
    )

    text = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Expense(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="expenses"
    )

    description = models.CharField(max_length=200)

    amount = models.DecimalField( max_digits=10 , decimal_places=2)

    CURRENCY_CHOICES = [
        ("TRY" ,"₺ TRY" ),
        ("USD" , "$ USD"),
        ("EUR" , "€ EUR")
    ]

    CATEGORY_CHOICES = [
        ("food","Food"),
        ("transport","Transportation"),
        ("accommodation","Accommodation"),
        ("shopping","Shopping"),
        ("activity","Activities"),
        ("other","Other")
    ]
    currency = models.CharField(max_length=3,choices=CURRENCY_CHOICES)

    category = models.CharField(max_length=20 , choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.description

class Place(models.Model):
    name = models.CharField(max_length=200)

    city = models.CharField(max_length=100)

    CATEGORY_CHOICES = [
        ("food", "Food"),
        ("cafe", "Cafe"),
        ("attraction", "Attraction"),
        ("shopping", "Shopping"),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    photo_url = models.URLField(max_length=1000, blank=True)

    def __str__(self):
        return self.name

class SavedPlace(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="saved_places"
    )

    place= models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="saved_in_trips"
    )

    visited = models.BooleanField(default=False)
    rating = models.IntegerField(
        null=True, 
        blank=True,
        validators=[
            MaxValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    review = models.TextField(blank=True)

    def __str__(self):
        return f"{self.trip.name} - {self.place.name}"
