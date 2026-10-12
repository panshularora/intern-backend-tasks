import json
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CallLog

logger = logging.getLogger(__name__)

ALLOWED_EVENTS = {
    'call.completed': 'completed',
    'call.missed': 'missed',
    'call.dropped': 'dropped',
}


@csrf_exempt
def call_completed_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if payload.get('secret') != settings.WEBHOOK_SECRET:
        return JsonResponse({'error': 'Invalid secret'}, status=403)

    event = payload.get('event')
    if event not in ALLOWED_EVENTS:
        return JsonResponse({'error': 'Unknown event'}, status=400)

    data = payload.get('data') or {}
    log = CallLog.objects.create(
        agent_name=data.get('agent_name', ''),
        caller_number=data.get('caller_number', ''),
        duration_secs=data.get('duration_secs') or 0,
        status=data.get('status') or ALLOWED_EVENTS[event],
        notes=data.get('notes', ''),
    )
    logger.info("Webhook created call log %s", log.id)
    return JsonResponse({'status': 'ok', 'id': log.id}, status=201)
