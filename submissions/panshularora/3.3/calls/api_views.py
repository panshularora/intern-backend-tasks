from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsAgent, IsSupervisor, IsAdminUser
from .models import CallLog
from .serializers import CallLogSerializer


class CallLogViewSet(viewsets.ModelViewSet):
    queryset = CallLog.objects.all()
    serializer_class = CallLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'agent_name']
    search_fields = ['agent_name', 'caller_number', 'notes']
    ordering_fields = ['timestamp', 'duration_secs']
    ordering = ['-timestamp']

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdminUser()]
        if self.action in ('update', 'partial_update'):
            return [IsSupervisor()]
        return [IsAgent()]

    def get_queryset(self):
        qs = CallLog.objects.all()
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
        if user.is_supervisor_or_above():
            return qs
        return qs.filter(agent_name=user.username)
