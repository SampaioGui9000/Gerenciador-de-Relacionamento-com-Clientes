from rest_framework.routers import DefaultRouter

from .views import ClienteViewSet, NotaViewSet

router = DefaultRouter()
router.register("clientes", ClienteViewSet, basename="cliente")
router.register("notas", NotaViewSet, basename="nota")

urlpatterns = router.urls
