from abstract.views import ReadOnlyCustomResponseMixin
from .models import Transaction
from .student_serializers import StudentTransactionSerializer


class StudentTransactionViewSet(ReadOnlyCustomResponseMixin):
    queryset = Transaction.objects.all()
    serializer_class = StudentTransactionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user, payment_status=Transaction.PaymentStatus.COMPLETED)
