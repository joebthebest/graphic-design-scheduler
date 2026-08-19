from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment, Service, Review, MEETING_TYPES, STATUS_CHOICES


class BookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'service',
            'appointment_date',
            'start_time',
            'client_name',
            'client_email',
            'client_phone',
            'company_or_brand',
            'design_brief',
            'brand_assets_link',
            'target_deadline',
            'meeting_type',
        ]
        widgets = {
            'service': forms.Select(attrs={'class': 'form-select', 'id': 'id_service'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_appointment_date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'id': 'id_start_time'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Alex Morgan'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. alex@brand.com'}),
            'client_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +234 812 345 6789'}),
            'company_or_brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Nova Aesthetics / Apex Labs'}),
            'design_brief': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about your brand vision, target audience, color palettes, or deliverables required...'}),
            'brand_assets_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://drive.google.com/... or https://figma.com/...'}),
            'target_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'meeting_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_appointment_date(self):
        appt_date = self.cleaned_data.get('appointment_date')
        if appt_date and appt_date < timezone.localdate():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return appt_date

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        appt_date = cleaned_data.get('appointment_date')
        start_time = cleaned_data.get('start_time')

        if service and appt_date and start_time:
            duration = timedelta(minutes=service.duration_minutes)
            start_dt = datetime.combine(appt_date, start_time)
            end_time = (start_dt + duration).time()

            # Double-booking check
            conflicts = Appointment.objects.filter(
                appointment_date=appt_date,
                status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS', 'RESCHEDULED']
            ).exclude(pk=self.instance.pk if self.instance else None)

            for conf in conflicts:
                if start_time < conf.end_time and end_time > conf.start_time:
                    raise forms.ValidationError("This time slot was just booked by another client. Please select an alternate slot.")

        return cleaned_data


class RescheduleForm(forms.Form):
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_reschedule_date'})
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'id': 'id_reschedule_time'})
    )

    def __init__(self, *args, appointment=None, **kwargs):
        self.appointment = appointment
        super().__init__(*args, **kwargs)

    def clean_appointment_date(self):
        appt_date = self.cleaned_data.get('appointment_date')
        if appt_date and appt_date < timezone.localdate():
            raise forms.ValidationError("Please pick a future date.")
        return appt_date

    def clean(self):
        cleaned_data = super().clean()
        appt_date = cleaned_data.get('appointment_date')
        start_time = cleaned_data.get('start_time')

        if self.appointment and appt_date and start_time:
            duration = timedelta(minutes=self.appointment.service.duration_minutes)
            start_dt = datetime.combine(appt_date, start_time)
            end_time = (start_dt + duration).time()

            conflicts = Appointment.objects.filter(
                appointment_date=appt_date,
                status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS', 'RESCHEDULED']
            ).exclude(pk=self.appointment.pk)

            for conf in conflicts:
                if start_time < conf.end_time and end_time > conf.start_time:
                    raise forms.ValidationError("The chosen slot conflicts with an existing booking. Please pick another time.")

        return cleaned_data


class BookingLookupForm(forms.Form):
    booking_reference = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. DES-849201', 'autocomplete': 'off'})
    )
    client_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. yourname@brand.com'})
    )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['client_name', 'client_role', 'service_name', 'rating', 'comment']
        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'client_role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Founder, NailedByDee'}),
            'service_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Brand Identity Suite'}),
            'rating': forms.Select(choices=[(5, '5 - Exceptional (⭐⭐⭐⭐⭐)'), (4, '4 - Great (⭐⭐⭐⭐)'), (3, '3 - Average (⭐⭐⭐)'), (2, '2 - Fair (⭐⭐)'), (1, '1 - Poor (⭐)')], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your experience working with James Design Studio...'}),
        }
