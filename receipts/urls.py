from django.urls import path

from receipts import views

urlpatterns = [
    path("process", views.ProcessReceipts.as_view()),
    path("<int:id>/points", views.GetPoints.as_view())
]
