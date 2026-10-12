from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from .models import CallLog


class CallLogListView(ListView):
    model = CallLog
    template_name = 'calls/call_log_list.html'
    context_object_name = 'call_logs'

    def get_queryset(self):
        qs = CallLog.objects.all()
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs


class CallLogDetailView(DetailView):
    model = CallLog
    template_name = 'calls/call_log_detail.html'
    context_object_name = 'call_log'


class CallLogCreateView(CreateView):
    model = CallLog
    template_name = 'calls/call_log_form.html'
    fields = ['agent_name', 'caller_number', 'duration_secs', 'status', 'notes']
    success_url = reverse_lazy('calls:list')

    def form_valid(self, form):
        duration = form.cleaned_data.get('duration_secs')
        if duration is not None and duration < 0:
            form.add_error('duration_secs', 'Duration must be 0 or more.')
            return self.form_invalid(form)
        return super().form_valid(form)


class CallLogUpdateView(UpdateView):
    model = CallLog
    template_name = 'calls/call_log_form.html'
    fields = ['agent_name', 'caller_number', 'duration_secs', 'status', 'notes']
    success_url = reverse_lazy('calls:list')

    def form_valid(self, form):
        duration = form.cleaned_data.get('duration_secs')
        if duration is not None and duration < 0:
            form.add_error('duration_secs', 'Duration must be 0 or more.')
            return self.form_invalid(form)
        return super().form_valid(form)


class CallLogDeleteView(DeleteView):
    model = CallLog
    template_name = 'calls/call_log_confirm_delete.html'
    success_url = reverse_lazy('calls:list')
