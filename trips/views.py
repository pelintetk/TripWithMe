from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Trip , ChecklistItem , Expense , Place , SavedPlace
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Sum
import logging
from django.core.management import call_command
from django.views.decorators.http import require_POST
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from datetime import date

logger = logging.getLogger(__name__)

@login_required
def index(request):
    trips = Trip.objects.filter(user=request.user)
    return render(request , "trips/index.html" , {
        "trips" : trips
    })

@login_required
def create_trip(request):

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        city = request.POST.get("city", "").strip()
        country = request.POST.get("country", "").strip()
        start_date = request.POST.get("start_date", "").strip()
        end_date = request.POST.get("end_date", "").strip()
        trip_type = request.POST.get("trip_type", "").strip()
        budget = request.POST.get("budget", "").strip()
        budget_currency = request.POST.get("budget_currency", "").strip()

        # Check for missing or empty fields
        if not all([
            name, city, country, start_date,
            end_date, trip_type, budget, budget_currency
        ]):
            return render(request, "trips/create_trip.html", {
                "message": "Please fill in all required fields."
            })

        # Validate dates
        try:
            start_date = date.fromisoformat(start_date)
            end_date = date.fromisoformat(end_date)
        except ValueError:
            return render(request, "trips/create_trip.html", {
                "message": "Please enter valid dates."
            })

        if end_date < start_date:
            return render(request, "trips/create_trip.html", {
                "message": "End date cannot be before start date."
            })

        # Validate budget
        try:
            budget = Decimal(budget)

            if not budget.is_finite() or budget < 0:
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            return render(request, "trips/create_trip.html", {
                "message": "Budget must be a valid non-negative number."
            })

        trip = Trip.objects.create(
            name = name ,
            city = city ,
            country = country,
            start_date = start_date,
            end_date = end_date ,
            trip_type = trip_type,
            budget = budget,
            budget_currency = budget_currency,
            user = request.user
        )

        basic_items = [
            "Toothbrush",
            "Toothpaste",
            "Pajamas",
            "Underwear",
            "Socks",
            "Phone charger",
            "Medicine",
            "Face wash gel",
            "Brush",
            "Hair product",
            "Make up product",
            "Moisturizing cream",
            "Shoe/Slipper"
        ]

        for item in basic_items:
            ChecklistItem.objects.create(
                trip=trip,
                text=item
            )

        if trip.trip_type == "international":
            international_items = [
                "Passport",
                "eSIM",
                "Currency",
                "Departure fee for traveling abroad"
            ]

            for item in international_items:
                ChecklistItem.objects.create(
                    trip=trip,
                    text=item
                )

        if not Place.objects.filter(city__iexact=city).exists():
            try:
                call_command("import_places", city, country)
            except Exception:
                logger.exception(
                    "Could not import places for %s, %s",
                    city,
                    country
                )

        return redirect("index")

    return render(request , "trips/create_trip.html")

def login_view(request):
    if request.method =="POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request,user)
            return redirect("index")
        else:
            return render(request, "trips/login.html" , {
                "message": "Invalid username or password."
            })

    return render(request , "trips/login.html")

def register(request):

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if not username.strip() or not password.strip():
            return render(request, "trips/register.html", {
                "message": "Username and password cannot be empty."
            })

        if password != confirmation:
            return render(request, "trips/register.html" , {
                "message": "Passwords must match."
            })

        try:
            validate_password(password)
        except ValidationError as error:
            return render(request, "trips/register.html", {
                "message": " ".join(error.messages)
            })


        if User.objects.filter(username=username).exists():
            return render(request, "trips/register.html" , {
                "message": "Username already taken."
            })

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request,user)
        return redirect("index")

    return render(request, "trips/register.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def trip_detail(request,trip_id):
    trip = get_object_or_404(
        Trip,
        id=trip_id,
        user=request.user
    )

    if request.method=="POST":
        if "add_checklist" in request.POST:
            text = request.POST["text"]

            ChecklistItem.objects.create(
                trip=trip,
                text = text
            )

        if "add_expense" in request.POST:
            description = request.POST.get("description", "").strip()
            amount = request.POST.get("amount", "").strip()
            currency = request.POST.get("currency", "").strip()
            category = request.POST.get("category", "").strip()

            try:
                amount = Decimal(amount)

                if not amount.is_finite() or amount <= 0:
                    raise InvalidOperation

            except (InvalidOperation, ValueError):
                return redirect("trip_detail", trip_id=trip.id)

            if not description or not currency or not category:
                return redirect("trip_detail", trip_id=trip.id)

            Expense.objects.create(
                trip=trip,
                description=description,
                amount=amount,
                currency=currency,
                category=category
            )


        if "save_place" in request.POST:
            place_id = request.POST["place_id"]

            place = Place.objects.get(id = place_id)

            SavedPlace.objects.get_or_create(
                trip=trip,
                place=place
            )

        if "remove_place" in request.POST:
            saved_places_ids = request.POST["saved_places_ids"]

            saved_place = SavedPlace.objects.get(
                id=saved_places_ids ,
                trip=trip
            )

            saved_place.delete()

        if "save_review" in request.POST:
            saved_places_ids = request.POST["saved_places_ids"]

            saved_place = get_object_or_404(
                SavedPlace,
                id=saved_places_ids,
                trip=trip,
                visited=True
            )

            rating = request.POST.get("rating")
            review = request.POST.get("review", "")

            if rating == "":
                saved_place.rating = None
            elif rating in ["1","2","3","4","5"]:
                saved_place.rating = int(rating)
            else:
                return JsonResponse(
                    {"error": "Rating must be between 1 and 5"},
                    status=400
                )

            saved_place.review = review
            saved_place.save()
        return redirect("trip_detail", trip_id=trip.id)

    checklist_items = trip.checklist_items.all()
    expenses = trip.expenses.all()
    places = Place.objects.filter(city__iexact=trip.city)
    saved_places = trip.saved_places.all()
    saved_places_ids = list(
        saved_places.values_list("place_id", flat=True)
    )
    eur_expenses = expenses.filter(currency="EUR")
    usd_expenses = expenses.filter(currency="USD")
    try_expenses = expenses.filter(currency="TRY")

    eur_total = eur_expenses.aggregate(
        total=Sum("amount")
    )["total"] or 0

    usd_total = usd_expenses.aggregate(
        total=Sum("amount")
    )["total"] or 0

    try_total = try_expenses.aggregate(
        total=Sum("amount")
    )["total"] or 0

    if trip.budget_currency == "EUR":
        spent = eur_total
    elif trip.budget_currency == "USD":
        spent = usd_total
    elif trip.budget_currency == "TRY":
        spent = try_total
    else:
        spent = 0

    if trip.budget is not None:
        remaining = trip.budget - spent
    else:
        remaining = None

    category_totals = expenses.values(
        "category",
        "currency"
    ).annotate(
        total=Sum("amount")
    )

    return render(request , "trips/trip_detail.html" , {
        "trip":trip,
        "checklist_items": checklist_items,
        "expenses": expenses ,
        "eur_total" : eur_total,
        "usd_total": usd_total,
        "try_total": try_total,
        "spent" : spent,
        "remaining" : remaining,
        "category_totals": category_totals,
        "places" : places ,
        "saved_places" : saved_places,
        "saved_places_ids" : saved_places_ids
    })


@login_required
@require_POST
def delete_expense(request, expense_id):
    expense = get_object_or_404(
        Expense,
        id=expense_id,
        trip__user=request.user
    )

    trip_id = expense.trip.id
    expense.delete()

    return redirect("trip_detail", trip_id=trip_id)


@login_required
@require_POST
def toggle_checklist_item(request, item_id):
    item = get_object_or_404(
        ChecklistItem,
        id=item_id,
        trip__user=request.user
    )

    item.completed = not item.completed
    item.save()

    return JsonResponse({
        "success": True
    })



@login_required
@require_POST
def toggle_visited(request, saved_id):
    saved_place = get_object_or_404(
        SavedPlace,
        id=saved_id,
        trip__user=request.user
    )

    saved_place.visited = not saved_place.visited
    saved_place.save()

    return JsonResponse({
        "success": True,
        "visited": saved_place.visited
    })


@login_required
@require_POST
def delete_trip(request, trip_id):
    trip = get_object_or_404(
        Trip,
        id=trip_id,
        user=request.user
    )

    trip.delete()
    return redirect("index")
