from django.urls import path

from apps.widget.views import UserMetricsView, StudentMetricsView, GlobalMetricsView

urlpatterns = [
    path('metrics/user/', UserMetricsView.as_view(), name='user-metrics'),
    path('metrics/student/', StudentMetricsView.as_view(), name='student-metrics'),
    path('metrics/global/', GlobalMetricsView.as_view(), name='global-metrics'),
]
