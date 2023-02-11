"""
URL mappings for alert app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from alert import views

router = DefaultRouter()
router.register('alerts', views.AlertViewSet)
router.register('symbols', views.SymbolViewSet)

app_name = 'alert'

urlpatterns = [
    path('', include(router.urls)),
]
