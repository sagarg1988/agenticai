"""URL routing for the API application."""
from rest_framework.routers import DefaultRouter

from .views import AgentRunViewSet, AgentViewSet

router = DefaultRouter()
router.register(r"agents", AgentViewSet, basename="agent")
router.register(r"runs", AgentRunViewSet, basename="agentrun")

urlpatterns = router.urls
