from django_filters import rest_framework as filters
from django.db.models import Subquery, OuterRef, Case, When, DecimalField, F
from django.db.models.functions import Coalesce

from .models import Course, CourseValidityPeriod

class CourseFilter(filters.FilterSet):
    ordering = filters.CharFilter(method='filter_sort_by')

    class Meta:
        model = Course
        fields = []

    def filter_sort_by(self, queryset, name, value):
        if value in ['lowToHigh', 'highToLow']:
            # Subquery for promoted price
            promoted_price = CourseValidityPeriod.objects.filter(
                course_id=OuterRef('pk'),
                is_promoted=True
            ).order_by('effective_price').values('effective_price')[:1]

            # Subquery for the first validity price
            first_price = CourseValidityPeriod.objects.filter(
                course_id=OuterRef('pk')
            ).order_by('effective_price').values('effective_price')[:1]

            # Annotate calculated price
            queryset = queryset.annotate(
                calculated_price=Case(
                    When(
                        validity_type='multiple',
                        then=Coalesce(
                            Subquery(promoted_price),  # Promoted price if exists
                            Subquery(first_price),    # Else first validity price
                            F('effective_price')      # Else course effective price
                        )
                    ),
                    default=F('effective_price'),  # For non-multiple validity
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )

            # Apply sorting based on calculated price
            if value == 'lowToHigh':
                return queryset.order_by('calculated_price')
            elif value == 'highToLow':
                return queryset.order_by('-calculated_price')

        # Default sorting for other cases
        if value == 'newest':
            return queryset.order_by('-created')
        elif value == 'oldest':
            return queryset.order_by('created')

        return queryset
