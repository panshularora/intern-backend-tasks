import logging
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg, Sum
from django.utils import timezone
from .models import CallLog

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_call_completion(self, call_log_id: int):
    """Email a supervisor when a call is marked completed."""
    try:
        call = CallLog.objects.get(id=call_log_id)
        send_mail(
            subject=f"Call Completed: {call.caller_number}",
            message=(
                f"Agent: {call.agent_name}\n"
                f"Duration: {call.duration_display()}\n"
                f"Notes: {call.notes or '-'}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.SUPERVISOR_EMAIL],
            fail_silently=False,
        )
        logger.info("Notification sent for call log %s", call_log_id)
        return {"status": "sent", "call_id": call_log_id}
    except CallLog.DoesNotExist:
        logger.error("CallLog %s not found", call_log_id)
        raise
    except Exception as exc:
        logger.error("Failed to send notification: %s", exc)
        raise self.retry(exc=exc)


@shared_task
def generate_call_report(agent_name: str, date_str: str):
    """Build a daily summary dict for one agent."""
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    logs = CallLog.objects.filter(agent_name=agent_name, timestamp__date=date)
    totals = logs.aggregate(avg=Avg('duration_secs'), total_dur=Sum('duration_secs'))
    return {
        'total_calls': logs.count(),
        'completed': logs.filter(status='completed').count(),
        'missed': logs.filter(status='missed').count(),
        'dropped': logs.filter(status='dropped').count(),
        'avg_duration_secs': totals['avg'] or 0,
        'total_duration_secs': totals['total_dur'] or 0,
    }


@shared_task
def send_daily_digest():
    """Log a same-day summary for every agent."""
    today = timezone.localdate()
    logs = CallLog.objects.filter(timestamp__date=today)
    agents = logs.values_list('agent_name', flat=True).distinct()
    lines = [f"Daily digest for {today}"]
    for agent in agents:
        report = generate_call_report(agent, today.isoformat())
        lines.append(
            f"{agent}: {report['total_calls']} calls, "
            f"{report['completed']} completed, avg {report['avg_duration_secs']}"
        )
    report_text = "\n".join(lines)
    logger.info(report_text)
    return report_text
