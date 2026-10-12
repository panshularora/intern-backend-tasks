from celery.result import AsyncResult
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsAgent, IsSupervisor, IsAdminUser
from .models import CallLog
from .serializers import CallLogSerializer
from .tasks import notify_call_completion


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

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.status == 'completed':
            notify_call_completion.delay(instance.id)

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'completed':
            notify_call_completion.delay(instance.id)


class TaskStatusViewSet(viewsets.ViewSet):
    permission_classes = [IsAgent]

    def retrieve(self, request, pk=None):
        result = AsyncResult(pk)
        payload = {
            'task_id': pk,
            'status': result.status,
            'result': None,
        }
        if result.successful():
            payload['result'] = result.result
        elif result.failed():
            payload['result'] = str(result.result)
        return Response(payload, status=status.HTTP_200_OK)
