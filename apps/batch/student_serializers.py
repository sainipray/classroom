from datetime import datetime, timedelta

from rest_framework import serializers

from .models import Batch, LiveClass, Attendance, OfflineClass
from .serializers.fee_serializers import FeeStructureSerializer
from .serializers.offline_classes_serializers import RetrieveOfflineClassSerializer


def generate_offline_classes(obj):
    # Get today's date to begin the search
    current_date = datetime.now().date()

    result = []

    # Filter all offline classes (this can be adjusted based on need)
    data = obj.offline_classes.all()

    # Iterate over each offline class
    for offline_class in data:
        if offline_class.class_type == OfflineClass.ClassType.REGULAR:
            # Regular class: display schedules for the next 7 days
            for i in range(7):
                next_day = current_date + timedelta(days=i)
                # Filter time slots for the specific day (by short name e.g. Mon, Tue, etc.)
                time_slots = offline_class.time_slots.filter(day=next_day.strftime("%a"))

                # Append filtered time slots with schedules
                for time_slot in time_slots:
                    result.append({
                        'class': RetrieveOfflineClassSerializer(offline_class).data,
                        'time_slot': time_slot.day,
                        'date': next_day,  # Add the calculated date for regular classes
                        'schedules': [
                            {
                                'start_time': schedule.start_time,
                                'end_time': schedule.end_time
                            }
                            for schedule in time_slot.schedules.all()
                        ]
                    })

        elif offline_class.class_type == OfflineClass.ClassType.ONE_TIME:
            # One-time class: display schedule for a specific datetime (i.e., the actual schedule date)
            time_slots = offline_class.time_slots.all()
            for time_slot in time_slots:
                result.append({
                    'class': RetrieveOfflineClassSerializer(offline_class).data,
                    'time_slot': time_slot.day,
                    'date': time_slot.date,  # Use the specific date for one-time classes
                    'schedules': [
                        {
                            'start_time': schedule.start_time,
                            'end_time': schedule.end_time
                        }
                        for schedule in time_slot.schedules.all()
                    ]
                })

    return result


class StudentBatchSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.full_name')
    fee_structure = FeeStructureSerializer(read_only=True)
    subject = serializers.ReadOnlyField(source='subject.name')
    installment_details = serializers.SerializerMethodField()

    is_joining_request_sent = serializers.SerializerMethodField()

    def get_is_joining_request_sent(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            return obj.is_joining_request_sent(user)

    class Meta:
        model = Batch
        fields = ['id', 'name', 'batch_code', 'start_date', 'subject', 'live_class_link',
                  'created_by', 'fee_structure', 'installment_details', 'thumbnail', 'is_joining_request_sent']

    def get_installment_details(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            return obj.get_installment_details_for_user(user)
        return []


class StudentLiveClassSerializer(serializers.ModelSerializer):
    student_join_link = serializers.ReadOnlyField()

    class Meta:
        model = LiveClass
        fields = ('title', 'date', 'class_id', 'status', 'recording_url',
                  'duration', 'recording_status', 'student_join_link')


class StudentRetrieveBatchSerializer(StudentBatchSerializer):
    content = serializers.ReadOnlyField()
    offline_classes = serializers.SerializerMethodField()

    def get_offline_classes(self, obj):
        return generate_offline_classes(obj)

    class Meta:
        model = Batch
        fields = '__all__'


class StudentAttendanceSerializer(serializers.ModelSerializer):
    live_class = serializers.ReadOnlyField(source='live_class.title')

    class Meta:
        model = Attendance
        fields = '__all__'
