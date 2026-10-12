from rest_framework import serializers
from .models import CallLog


class CallLogSerializer(serializers.ModelSerializer):
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = CallLog
        fields = [
            'id', 'agent_name', 'caller_number', 'duration_secs',
            'status', 'timestamp', 'notes', 'duration_display',
        ]
        read_only_fields = ['id', 'timestamp', 'duration_display']

    def get_duration_display(self, obj):
        return obj.duration_display()

    def validate_duration_secs(self, value):
        if value < 0:
            raise serializers.ValidationError('Duration cannot be negative.')
        return value

    def validate_caller_number(self, value):
        cleaned = value.strip()
        if len(cleaned) < 7:
            raise serializers.ValidationError('Caller number must be at least 7 characters.')
        allowed = set('0123456789+- ')
        if any(ch not in allowed for ch in cleaned):
            raise serializers.ValidationError(
                'Caller number can only contain digits, +, - and spaces.'
            )
        return cleaned
