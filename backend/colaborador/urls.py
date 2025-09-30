from rest_framework.routers import SimpleRouter
from .views import ColaboradorViewSet

router = SimpleRouter()
router.register(r'colaboradores', ColaboradorViewSet, basename='colaborador')
urlpatterns = router.urls