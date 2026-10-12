from rest_framework.routers import DefaultRouter
from .api_views import CallLogViewSet, TaskStatusViewSet

router = DefaultRouter()
router.register(r'call-logs', CallLogViewSet, basename='calllog')
router.register(r'tasks', TaskStatusViewSet, basename='tasks')

urlpatterns = router.urls
