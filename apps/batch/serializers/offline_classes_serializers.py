from rest_framework import serializers

from apps.batch.models import Schedule, TimeSlot, OfflineClass, Batch, BatchPurchaseOrder, Enrollment


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'start_time', 'end_time']  # Include only necessary fields


class TimeSlotSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True)  # Nested schedules

    class Meta:
        model = TimeSlot
        fields = ['id', 'day', 'schedules']  # Include necessary fields

    def create(self, validated_data):
        schedules_data = validated_data.pop('schedules')
        time_slot = TimeSlot.objects.create(**validated_data)
        for schedule_data in schedules_data:
            Schedule.objects.create(timeslot=time_slot, **schedule_data)
        return time_slot

    def update(self, instance, validated_data):
        schedules_data = validated_data.pop('schedules')
        instance.day = validated_data.get('day', instance.day)
        instance.save()

        # Update schedules
        for schedule_data in schedules_data:
            schedule_id = schedule_data.get('id', None)
            if schedule_id:
                schedule = Schedule.objects.get(id=schedule_id)
                schedule.start_time = schedule_data.get('start_time', schedule.start_time)
                schedule.end_time = schedule_data.get('end_time', schedule.end_time)
                schedule.save()
            else:
                Schedule.objects.create(timeslot=instance, **schedule_data)

        return instance


class OfflineClassSerializer(serializers.ModelSerializer):
    time_slots = TimeSlotSerializer(many=True)  # Nested time slots

    class Meta:
        model = OfflineClass
        fields = ['id', 'class_type', 'faculty', 'time_slots']

    def create(self, validated_data):
        time_slots_data = validated_data.pop('time_slots')
        offline_class = OfflineClass.objects.create(**validated_data)
        for time_slot_data in time_slots_data:
            schedules_data = time_slot_data.pop('schedules', [])
            time_slot = TimeSlot.objects.create(batch_class=offline_class, **time_slot_data)
            for schedule_data in schedules_data:
                Schedule.objects.create(timeslot=time_slot, **schedule_data)
        return offline_class

    def update(self, instance, validated_data):
        time_slots_data = validated_data.pop('time_slots', None)
        instance.class_type = validated_data.get('class_type', instance.class_type)
        instance.faculty = validated_data.get('faculty', instance.faculty)
        instance.save()

        if time_slots_data is not None:
            # Update time slots
            for time_slot_data in time_slots_data:
                time_slot_id = time_slot_data.get('id', None)
                if time_slot_id:
                    time_slot = TimeSlot.objects.get(id=time_slot_id)
                    time_slot.day = time_slot_data.get('day', time_slot.day)
                    time_slot.save()

                    # Update schedules
                    schedules_data = time_slot_data.get('schedules', [])
                    for schedule_data in schedules_data:
                        schedule_id = schedule_data.get('id', None)
                        if schedule_id:
                            schedule = Schedule.objects.get(id=schedule_id)
                            schedule.start_time = schedule_data.get('start_time', schedule.start_time)
                            schedule.end_time = schedule_data.get('end_time', schedule.end_time)
                            schedule.save()
                        else:
                            Schedule.objects.create(timeslot=time_slot, **schedule_data)
                else:
                    # Create new time slot if no ID is provided
                    schedules_data = time_slot_data.pop('schedules', [])
                    time_slot = TimeSlot.objects.create(batch_class=instance, **time_slot_data)
                    for schedule_data in schedules_data:
                        Schedule.objects.create(timeslot=time_slot, **schedule_data)

        return instance


class JoinBatchSerializer(serializers.Serializer):
    batch = serializers.IntegerField()

    def validate_batch(self, value):
        # Check if the batch exists
        try:
            batch = Batch.objects.get(id=value)
        except Batch.DoesNotExist:
            raise serializers.ValidationError("Batch does not exist.")
        return batch

    def validate(self, attrs):
        student = self.context['request'].user

        # Check if the student is already in the batch
        if BatchPurchaseOrder.objects.filter(batch=attrs['batch'], student=student).exists():
            raise serializers.ValidationError("Student is already added to this batch.")
        if Enrollment.objects.filter(batch=attrs['batch'], student=student).exists():
            raise serializers.ValidationError("Student is already in enrolled.")
        return attrs
