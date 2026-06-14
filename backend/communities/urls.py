from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BillViewSet, BuildingViewSet, FeeTypeViewSet, PaymentViewSet, ReminderViewSet, RoomViewSet, dashboard


router = DefaultRouter()
router.register("buildings", BuildingViewSet)
router.register("rooms", RoomViewSet)
router.register("fee-types", FeeTypeViewSet)
router.register("bills", BillViewSet)
router.register("payments", PaymentViewSet)
router.register("reminders", ReminderViewSet)

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("", include(router.urls)),
]
