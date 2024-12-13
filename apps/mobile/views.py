from abstract.views import CustomResponseMixin, ReadOnlyCustomResponseMixin
from .models import Banner
from .serializers import BannerSerializer


class BannerViewSet(CustomResponseMixin):
    queryset = Banner.objects.all().order_by('-created')
    serializer_class = BannerSerializer


class StudentBannerViewSet(ReadOnlyCustomResponseMixin):
    queryset = Banner.objects.filter(is_active=True).order_by('-created')
    serializer_class = BannerSerializer
