# diagrama/urls.py
from rest_framework.routers import DefaultRouter
from .views import DiagramaViewSet

router = DefaultRouter()
router.register(r'diagramas', DiagramaViewSet, basename='diagramas')

urlpatterns = router.urls
