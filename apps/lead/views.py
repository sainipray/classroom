from rest_framework.permissions import AllowAny

from abstract.views import CustomResponseMixin
from .models import Lead
from .serializers import LeadSerializer, ListLeadSerializer


class LeadViewSet(CustomResponseMixin):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    list_serializer_class = ListLeadSerializer
