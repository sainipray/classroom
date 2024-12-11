from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from apps.batch.models import Batch, Subject, Folder, File, OfflineClass, BatchFaculty, BatchReview
from apps.batch.serializers.fee_serializers import FeeStructureSerializer
from apps.batch.serializers.liveclass_serializers import LiveClassSerializer
from apps.batch.serializers.offline_classes_serializers import RetrieveOfflineClassSerializer
from apps.user.serializers import CustomUserSerializer

User = get_user_model()


class FacultyBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', ]


class BatchFacultySerializer(serializers.ModelSerializer):
    faculty = FacultyBatchSerializer(read_only=True)

    class Meta:
        model = BatchFaculty
        fields = ['id', 'faculty', 'batch']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class BatchSerializer(serializers.ModelSerializer):
    # Make created_by read-only as it will be automatically set by the view
    created_by = serializers.ReadOnlyField()
    batch_code = serializers.ReadOnlyField()

    class Meta:
        model = Batch
        fields = ['name', 'start_date', 'subject', 'created_by', 'batch_code', 'fee_structure', 'thumbnail',
                  'param_duration', 'param_enrolled', 'param_chapters', 'param_videos', 'param_level',
                  'param_1', 'param_2', 'param_3', 'param_4', 'param_5']

    def create(self, validated_data):
        # The validated data doesn't contain `created_by` yet, so we add it manually.
        validated_data['created_by'] = self.context['request'].user
        # Now save the instance
        return super().create(validated_data)


class RetrieveBatchSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    created_by = serializers.ReadOnlyField(source='created_by.full_name')
    total_enrolled_students = serializers.ReadOnlyField()
    enrolled_students = serializers.ReadOnlyField()
    student_join_request = serializers.ReadOnlyField()
    fee_structure = FeeStructureSerializer(read_only=True)
    faculties = BatchFacultySerializer(source='batch_faculties', many=True, read_only=True)

    # TODO filter live class of past one day later
    # live_classes = LiveClassSerializer(read_only=True, many=True)

    live_classes = serializers.SerializerMethodField()
    offline_classes = serializers.SerializerMethodField()

    def get_live_classes(self, obj):
        # Filter live classes where `date + 1 hour` is in the future
        one_hour_ahead = timezone.now() - timedelta(hours=1)
        filtered_live_classes = obj.live_classes.filter(date__gt=one_hour_ahead)

        # Serialize the filtered queryset
        return LiveClassSerializer(filtered_live_classes, many=True).data

    def get_offline_classes(self, obj):
        # Get the current date
        current_date = timezone.now().date()

        # Fetch all related offline classes
        data = obj.offline_classes.all()

        # Filter and extend classes based on type
        result = []
        for offline_class in data:
            if offline_class.class_type == OfflineClass.ClassType.REGULAR:
                # Add schedules for the next 7 days
                for i in range(7):
                    next_day = current_date + timedelta(days=i)
                    # Filter time slots for the specific day
                    time_slots = offline_class.time_slots.filter(
                        day=next_day.strftime("%a"))  # Match the day's short name

                    # Append filtered time slots with schedules
                    for time_slot in time_slots:
                        result.append({
                            'id': offline_class.id,
                            'class': RetrieveOfflineClassSerializer(offline_class).data,
                            'time_slot': time_slot.day,
                            'schedules': [
                                {
                                    'id': schedule.id,
                                    'start_time': schedule.start_time,
                                    'end_time': schedule.end_time
                                }
                                for schedule in time_slot.schedules.all()
                            ]
                        })
            elif offline_class.class_type == OfflineClass.ClassType.ONE_TIME:
                # Add only one instance for one-time classes
                time_slots = offline_class.time_slots.all()
                for time_slot in time_slots:
                    result.append({
                        'id': offline_class.id,
                        'class': RetrieveOfflineClassSerializer(offline_class).data,
                        'time_slot': time_slot.day,
                        'schedules': [
                            {
                                'id': schedule.id,
                                'start_time': schedule.start_time,
                                'end_time': schedule.end_time
                            }
                            for schedule in time_slot.schedules.all()
                        ]
                    })

        return result

    class Meta:
        model = Batch
        fields = '__all__'


class ListBatchSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    created_by = CustomUserSerializer()
    faculties = BatchFacultySerializer(source='batch_faculties', many=True, read_only=True)

    class Meta:
        model = Batch
        fields = '__all__'


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'batch', 'title', 'parent', 'created', 'order']


class FileSerializer(serializers.ModelSerializer):
    title = serializers.CharField(read_only=True)

    class Meta:
        model = File
        fields = ['id', 'title', 'folder', 'url', 'created', 'is_locked', 'order']


class BatchReviewSerializer(serializers.ModelSerializer):
    student = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = BatchReview
        fields = ['id', 'batch', 'title', 'description', 'rating', 'student']
        read_only_fields = ['id', 'created']

    def validate(self, data):
        student = self.context['request'].user
        batch = data.get('batch')

        if BatchReview.objects.filter(batch=batch, student=student).exists():
            raise serializers.ValidationError("You have already submitted a review for this batch.")

        return data
