
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Trip , Expense , ChecklistItem , Place , SavedPlace
from unittest.mock import patch
from .models import ChecklistItem
from decimal import Decimal



class TripTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123"
        )

        self.trip = Trip.objects.create(
            user=self.user,
            name="Sevilla Adventure",
            city="Sevilla",
            country="Spain",
            start_date="2027-01-10",
            end_date="2027-01-15",
            trip_type="international",
            budget=500,
            budget_currency="EUR"
        )

    def test_trip_created(self):
        self.assertEqual(Trip.objects.count(), 1)
        self.assertEqual(self.trip.city, "Sevilla")

    def test_delete_trip(self):
        self.client.login(
            username="testuser",
            password="testpassword123"
        )

        response = self.client.post(
            reverse("delete_trip", args=[self.trip.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Trip.objects.count(), 0)

    def test_cannot_delete_trip_without_login(self):
        response = self.client.post(
            reverse("delete_trip", args=[self.trip.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Trip.objects.count(), 1)

    def test_delete_trip_requires_post(self):
        self.client.login(
            username="testuser",
            password="testpassword123"
        )

        response = self.client.get(
            reverse("delete_trip", args=[self.trip.id])
        )

        self.assertEqual(response.status_code, 405)
        self.assertEqual(Trip.objects.count(), 1)

    def test_cannot_delete_another_users_trip(self):
        another_user = User.objects.create_user(
            username="anotheruser",
            password="anotherpassword123"
        )

        self.client.force_login(another_user)

        response = self.client.post(
            reverse("delete_trip", args=[self.trip.id])
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Trip.objects.count(), 1)

    def test_other_user_cannot_view_trip(self):
        other_user = User.objects.create_user(
            username="anotheruser",
            password="SecurePass123!"
        )

        self.client.force_login(other_user)

        response = self.client.get(
            reverse("trip_detail", args=[self.trip.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_trip_detail_requires_login(self):
        response = self.client.get(
            reverse("trip_detail", args=[self.trip.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class AuthenticationTests(TestCase):

    def test_register_success(self):
        response = self.client.post(reverse("register"), {
            "username": "newtraveler",
            "password": "SecurePass123!",
            "confirmation": "SecurePass123!"
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            User.objects.filter(username="newtraveler").exists()
        )

        # Registration should automatically log the user in.
        self.assertEqual(
            str(self.client.session["_auth_user_id"]),
            str(User.objects.get(username="newtraveler").id)
        )

    def test_register_password_mismatch(self):
        response = self.client.post(reverse("register"), {
            "username": "newtraveler",
            "password": "SecurePass123!",
            "confirmation": "DifferentPass123!"
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords must match.")
        self.assertFalse(
            User.objects.filter(username="newtraveler").exists()
        )

    def test_register_duplicate_username(self):
        User.objects.create_user(
            username="existinguser",
            password="SecurePass123!"
        )

        response = self.client.post(reverse("register"), {
            "username": "existinguser",
            "password": "AnotherPass123!",
            "confirmation": "AnotherPass123!"
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username already taken.")
        self.assertEqual(
            User.objects.filter(username="existinguser").count(),
            1
        )

    def test_logout(self):
        user = User.objects.create_user(
            username="traveler",
            password="SecurePass123!"
        )

        self.client.force_login(user)

        response = self.client.get(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)


    def test_register_empty_password_rejected(self):
        response = self.client.post(reverse("register"), {
            "username": "emptytraveler",
            "password": "",
            "confirmation": ""
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(username="emptytraveler").exists()
        )

    def test_register_whitespace_username_rejected(self):
        response = self.client.post(reverse("register"), {
            "username": "   ",
            "password": "SecurePass123!",
            "confirmation": "SecurePass123!"
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Username and password cannot be empty."
        )
        self.assertFalse(
            User.objects.filter(username="   ").exists()
        )

    def test_register_whitespace_username_rejected(self):
        response = self.client.post(reverse("register"), {
            "username": "   ",
            "password": "SecurePass123!",
            "confirmation": "SecurePass123!"
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Username and password cannot be empty."
        )
        self.assertFalse(
            User.objects.filter(username="   ").exists()
        )

    def test_register_weak_password_rejected(self):
        response = self.client.post(reverse("register"), {
            "username": "weaktraveler",
            "password": "123",
            "confirmation": "123"
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(username="weaktraveler").exists()
        )


class LoginTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testtraveler",
            password="SecurePass123!"
        )

    def test_login_success(self):
        response = self.client.post(reverse("login"), {
            "username": "testtraveler",
            "password": "SecurePass123!"
        })

        self.assertRedirects(response, reverse("index"))
        self.assertEqual(
            str(self.client.session["_auth_user_id"]),
            str(self.user.id)
        )

    def test_login_wrong_password(self):
        response = self.client.post(reverse("login"), {
            "username": "testtraveler",
            "password": "WrongPassword123!"
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Invalid username or password."
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_nonexistent_user(self):
        response = self.client.post(reverse("login"), {
            "username": "unknownuser",
            "password": "SecurePass123!"
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Invalid username or password."
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/login.html")

class CreateTripTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="tripcreator",
            password="SecurePass123!"
        )

        self.trip_data = {
            "name": "Sevilla Holiday",
            "city": "Sevilla",
            "country": "Spain",
            "start_date": "2027-01-10",
            "end_date": "2027-01-15",
            "trip_type": "international",
            "budget": "500.00",
            "budget_currency": "EUR"
        }

    @patch("trips.views.call_command")
    def test_create_trip_success(self, mock_import):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("create_trip"),
            self.trip_data
        )

        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Trip.objects.count(), 1)

        trip = Trip.objects.first()
        self.assertEqual(trip.name, "Sevilla Holiday")
        self.assertEqual(trip.city, "Sevilla")
        self.assertEqual(trip.budget_currency, "EUR")

        mock_import.assert_called_once_with(
            "import_places", "Sevilla", "Spain"
        )

    @patch("trips.views.call_command")
    def test_trip_belongs_to_creator(self, mock_import):
        self.client.force_login(self.user)

        self.client.post(
            reverse("create_trip"),
            self.trip_data
        )

        trip = Trip.objects.first()
        self.assertEqual(trip.user, self.user)

    @patch("trips.views.call_command")
    def test_international_checklist(self, mock_import):
        self.client.force_login(self.user)

        self.client.post(
            reverse("create_trip"),
            self.trip_data
        )

        trip = Trip.objects.first()

        items = list(
            ChecklistItem.objects.filter(
                trip=trip
            ).values_list("text", flat=True)
        )

        self.assertIn("Toothbrush", items)
        self.assertIn("Passport", items)
        self.assertIn("eSIM", items)
        self.assertIn("Currency", items)
        self.assertIn(
            "Departure fee for traveling abroad",
            items
        )

        self.assertEqual(len(items), 17)

    @patch("trips.views.call_command")
    def test_create_trip_requires_login(self, mock_import):
        response = self.client.post(
            reverse("create_trip"),
            self.trip_data
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Trip.objects.count(), 0)
        mock_import.assert_not_called()


    @patch("trips.views.call_command")
    def test_end_date_before_start_date_rejected(self, mock_import):
        self.client.force_login(self.user)

        invalid_data = self.trip_data.copy()
        invalid_data["start_date"] = "2027-01-15"
        invalid_data["end_date"] = "2027-01-10"

        response = self.client.post(
            reverse("create_trip"),
            invalid_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Trip.objects.count(), 0)
        mock_import.assert_not_called()

    @patch("trips.views.call_command")
    def test_negative_budget_rejected(self, mock_import):
        self.client.force_login(self.user)

        invalid_data = self.trip_data.copy()
        invalid_data["budget"] = "-500.00"

        response = self.client.post(
            reverse("create_trip"),
            invalid_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Trip.objects.count(), 0)
        mock_import.assert_not_called()

    @patch("trips.views.call_command")
    def test_invalid_budget_rejected(self, mock_import):
        self.client.force_login(self.user)

        invalid_data = self.trip_data.copy()
        invalid_data["budget"] = "abc"

        response = self.client.post(
            reverse("create_trip"),
            invalid_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Budget must be a valid non-negative number."
        )
        self.assertEqual(Trip.objects.count(), 0)
        mock_import.assert_not_called()

    @patch("trips.views.call_command")
    def test_missing_trip_name_rejected(self, mock_import):
        self.client.force_login(self.user)

        invalid_data = self.trip_data.copy()
        invalid_data.pop("name")

        response = self.client.post(
            reverse("create_trip"),
            invalid_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Please fill in all required fields."
        )
        self.assertEqual(Trip.objects.count(), 0)
        mock_import.assert_not_called()


    @patch("trips.views.call_command")
    def test_domestic_trip_creates_basic_checklist(self, mock_import):
        self.client.force_login(self.user)

        domestic_data = self.trip_data.copy()
        domestic_data["trip_type"] = "domestic"

        response = self.client.post(
            reverse("create_trip"),
            domestic_data
        )

        self.assertEqual(response.status_code, 302)

        trip = Trip.objects.get(name="Sevilla Holiday")

        self.assertEqual(
            ChecklistItem.objects.filter(trip=trip).count(),
            13
        )

        self.assertFalse(
            ChecklistItem.objects.filter(
                trip=trip,
                text="Passport"
            ).exists()
        )

class ChecklistTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="checklistuser",
            password="SecurePass123!"
        )

        self.trip = Trip.objects.create(
            user=self.user,
            name="Paris Holiday",
            city="Paris",
            country="France",
            start_date="2027-01-10",
            end_date="2027-01-15",
            trip_type="international",
            budget=500,
            budget_currency="EUR"
        )

        self.item = ChecklistItem.objects.create(
            trip=self.trip,
            text="Passport",
            completed=False
        )

    def test_checklist_item_can_be_completed(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("toggle_checklist_item", args=[self.item.id])
        )

        self.item.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertTrue(self.item.completed)

    def test_other_user_cannot_toggle_checklist_item(self):
        other_user = User.objects.create_user(
            username="otherchecklistuser",
            password="SecurePass123!"
        )

        self.client.force_login(other_user)

        response = self.client.post(
            reverse("toggle_checklist_item", args=[self.item.id])
        )

        self.item.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.item.completed)

    def test_checklist_toggle_requires_post(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("toggle_checklist_item", args=[self.item.id])
        )

        self.item.refresh_from_db()

        self.assertEqual(response.status_code, 405)
        self.assertFalse(self.item.completed)

    def test_checklist_item_can_be_unchecked(self):
        self.client.force_login(self.user)

        url = reverse(
            "toggle_checklist_item",
            args=[self.item.id]
        )

        # First click: False -> True
        first_response = self.client.post(url)

        self.item.refresh_from_db()

        self.assertEqual(first_response.status_code, 200)
        self.assertTrue(self.item.completed)

        # Second click: True -> False
        second_response = self.client.post(url)

        self.item.refresh_from_db()

        self.assertEqual(second_response.status_code, 200)
        self.assertFalse(self.item.completed)


class ExpenseTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="expenseuser",
            password="SecurePass123!"
        )

        self.trip = Trip.objects.create(
            user=self.user,
            name="Paris Holiday",
            city="Paris",
            country="France",
            start_date="2027-01-10",
            end_date="2027-01-15",
            trip_type="international",
            budget=500,
            budget_currency="EUR"
        )

    def test_expense_can_be_added(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("trip_detail", args=[self.trip.id]),
            {
                "add_expense": "1",
                "description": "Lunch",
                "amount": "25.00",
                "currency": "EUR",
                "category": "food"
            }
        )

        self.assertEqual(Expense.objects.count(), 1)

        expense = Expense.objects.first()

        self.assertEqual(expense.trip, self.trip)
        self.assertEqual(expense.description, "Lunch")
        self.assertEqual(expense.amount, Decimal("25.00"))
        self.assertEqual(expense.currency, "EUR")
        self.assertEqual(expense.category, "food")

    def test_negative_expense_rejected(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("trip_detail", args=[self.trip.id]),
            {
                "add_expense": "1",
                "description": "Lunch",
                "amount": "-100.00",
                "currency": "EUR",
                "category": "food"
            }
        )

        self.assertEqual(Expense.objects.count(), 0)

    def test_invalid_expense_amount_rejected(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("trip_detail", args=[self.trip.id]),
            {
                "add_expense": "1",
                "description": "Lunch",
                "amount": "abc",
                "currency": "EUR",
                "category": "food"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.count(), 0)

    def test_other_user_cannot_delete_expense(self):
        expense = Expense.objects.create(
            trip=self.trip,
            description="Dinner",
            amount=50,
            currency="EUR",
            category="food"
        )

        other_user = User.objects.create_user(
            username="otherexpenseuser",
            password="SecurePass123!"
        )

        self.client.force_login(other_user)

        response = self.client.post(
            reverse("delete_expense", args=[expense.id])
        )

        expense.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Expense.objects.count(), 1)

    def test_delete_expense_requires_post(self):
        expense = Expense.objects.create(
            trip=self.trip,
            description="Coffee",
            amount=10,
            currency="EUR",
            category="food"
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse("delete_expense", args=[expense.id])
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(
            Expense.objects.filter(id=expense.id).exists()
        )

    def test_user_can_delete_own_expense(self):
        expense = Expense.objects.create(
            trip=self.trip,
            description="Dinner",
            amount=50,
            currency="EUR",
            category="food"
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse("delete_expense", args=[expense.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Expense.objects.filter(id=expense.id).exists()
        )
        self.assertRedirects(
            response,
            reverse("trip_detail", args=[self.trip.id])
        )

    def test_empty_expense_description_rejected(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("trip_detail", args=[self.trip.id]),
            {
                "add_expense": "1",
                "description": "   ",
                "amount": "25.00",
                "currency": "EUR",
                "category": "food"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.count(), 0)

    def test_zero_expense_amount_rejected(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("trip_detail", args=[self.trip.id]),
            {
                "add_expense": "1",
                "description": "Coffee",
                "amount": "0",
                "currency": "EUR",
                "category": "food"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.count(), 0)

    def test_delete_expense_requires_login(self):
        expense = Expense.objects.create(
            trip=self.trip,
            description="Coffee",
            amount=10,
            currency="EUR",
            category="food"
        )

        response = self.client.post(
            reverse("delete_expense", args=[expense.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

        self.assertTrue(
            Expense.objects.filter(id=expense.id).exists()
        )

class SavedPlaceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="placeuser",
            password="SecurePass123!"
        )

        self.trip = Trip.objects.create(
            user=self.user,
            name="Paris Holiday",
            city="Paris",
            country="France",
            start_date="2027-01-10",
            end_date="2027-01-15",
            trip_type="international",
            budget=500,
            budget_currency="EUR"
        )

        self.place = Place.objects.create(
            name="Cafe de Flore",
            city="Paris",
            category="cafe"
        )

    def test_place_can_be_saved(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("trip_detail", args=[self.trip.id]),
            {
                "save_place": "1",
                "place_id": str(self.place.id)
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            SavedPlace.objects.filter(
                trip=self.trip,
                place=self.place
            ).exists()
        )

    def test_same_place_cannot_be_saved_twice(self):
        self.client.force_login(self.user)

        url = reverse(
            "trip_detail",
            args=[self.trip.id]
        )

        data = {
            "save_place": "1",
            "place_id": str(self.place.id)
        }

        # Save the place for the first time
        first_response = self.client.post(url, data)

        # Try saving the same place again
        second_response = self.client.post(url, data)

        self.assertEqual(first_response.status_code, 302)
        self.assertEqual(second_response.status_code, 302)

        self.assertEqual(
            SavedPlace.objects.filter(
                trip=self.trip,
                place=self.place
            ).count(),
            1
        )

    def test_other_user_cannot_save_place_to_trip(self):
        other_user = User.objects.create_user(
            username="otherplaceuser",
            password="SecurePass123!"
        )

        self.client.force_login(other_user)

        response = self.client.post(
            reverse("trip_detail", args=[self.trip.id]),
            {
                "save_place": "1",
                "place_id": str(self.place.id)
            }
        )

        self.assertEqual(response.status_code, 404)

        self.assertFalse(
            SavedPlace.objects.filter(
                trip=self.trip,
                place=self.place
            ).exists()
        )

    def test_saved_place_can_be_marked_visited(self):
        saved_place = SavedPlace.objects.create(
            trip=self.trip,
            place=self.place,
            visited=False
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse("toggle-visited", args=[saved_place.id])
        )

        saved_place.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertTrue(response.json()["visited"])
        self.assertTrue(saved_place.visited)

    def test_other_user_cannot_toggle_visited(self):
        saved_place = SavedPlace.objects.create(
            trip=self.trip,
            place=self.place,
            visited=False
        )

        other_user = User.objects.create_user(
            username="othervisiteduser",
            password="SecurePass123!"
        )

        self.client.force_login(other_user)

        response = self.client.post(
            reverse("toggle-visited", args=[saved_place.id])
        )

        saved_place.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(saved_place.visited)

    def test_toggle_visited_requires_post(self):
        saved_place = SavedPlace.objects.create(
            trip=self.trip,
            place=self.place,
            visited=False
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse("toggle-visited", args=[saved_place.id])
        )

        saved_place.refresh_from_db()

        self.assertEqual(response.status_code, 405)
        self.assertFalse(saved_place.visited)

    def test_visited_place_can_be_reviewed(self):
        saved_place = SavedPlace.objects.create(
            trip=self.trip,
            place=self.place,
            visited=True
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse("trip_detail", args=[self.trip.id]),
            {
                "save_review": "1",
                "saved_places_ids": str(saved_place.id),
                "rating": "5",
                "review": "Amazing coffee!"
            }
        )

        saved_place.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(saved_place.rating, 5)
        self.assertEqual(
            saved_place.review,
            "Amazing coffee!"
        )

    def test_invalid_rating_is_rejected(self):
        saved_place = SavedPlace.objects.create(
            trip=self.trip,
            place=self.place,
            visited=True,
            rating=4,
            review="Good coffee!"
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse("trip_detail", args=[self.trip.id]),
            {
                "save_review": "1",
                "saved_places_ids": str(saved_place.id),
                "rating": "6",
                "review": "New review"
            }
        )

        saved_place.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(saved_place.rating, 4)
        self.assertEqual(saved_place.review, "Good coffee!")

    def test_unvisited_place_cannot_be_reviewed(self):
        saved_place = SavedPlace.objects.create(
            trip=self.trip,
            place=self.place,
            visited=False
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse("trip_detail", args=[self.trip.id]),
            {
                "save_review": "1",
                "saved_places_ids": str(saved_place.id),
                "rating": "5",
                "review": "Amazing place!"
            }
        )

        saved_place.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertIsNone(saved_place.rating)
        self.assertFalse(saved_place.review)
