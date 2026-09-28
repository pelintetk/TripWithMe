from django.urls import path
from . import views

urlpatterns = [
    path("" , views.index , name="index" ),
    path("create/" , views.create_trip , name="create_trip"),
    path("login/" , views.login_view , name="login"),
    path("register/" , views.register , name="register"),
    path("logout/" , views.logout_view , name = "logout"),
    path("trips/<int:trip_id>/" , views.trip_detail , name="trip_detail"),
    path("checklist/<int:item_id>/toggle/", views.toggle_checklist_item,name="toggle_checklist_item"),
    path("expense/<int:expense_id>/delete/",views.delete_expense,name="delete_expense")
]