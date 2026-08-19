from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from datetime import datetime

from .models import Service, Appointment, Review, PortfolioItem
from .forms import BookingForm, RescheduleForm, BookingLookupForm, ReviewForm
from .utils import get_available_slots, generate_ics_content


def book_wizard_view(request, service_slug=None):
    """
    Renders and handles the 4-step interactive graphic design booking wizard.
    """
    services = Service.objects.filter(is_active=True).order_by('order', 'price')
    selected_service = None
    if service_slug:
        selected_service = get_object_or_404(Service, slug=service_slug, is_active=True)
    elif services.exists():
        selected_service = services.first()

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(request, f"🎉 Booking created successfully! Your reference code is {appointment.booking_reference}.")
            return redirect('booking_success', booking_ref=appointment.booking_reference)
        else:
            messages.error(request, "Please check the form for errors and select a valid time slot.")
    else:
        initial_data = {}
        if selected_service:
            initial_data['service'] = selected_service
        form = BookingForm(initial=initial_data)

    context = {
        'services': services,
        'selected_service': selected_service,
        'form': form,
        'today_date': timezone.localdate().strftime('%Y-%m-%d'),
    }
    return render(request, 'scheduling/book_wizard.html', context)


@require_GET
def available_slots_api_view(request):
    """
    AJAX endpoint: returns JSON of available slots for a given service and date.
    Query params: service_id, date (YYYY-MM-DD)
    """
    service_id = request.GET.get('service_id')
    date_str = request.GET.get('date')

    if not service_id or not date_str:
        return JsonResponse({'status': 'error', 'message': 'Missing service_id or date parameter.'}, status=400)

    try:
        service = Service.objects.get(id=service_id, is_active=True)
    except Service.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Service not found.'}, status=404)

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    slots = get_available_slots(service, target_date)

    return JsonResponse({
        'status': 'success',
        'service': {
            'id': service.id,
            'name': service.name,
            'duration': service.duration_minutes,
            'price': str(service.price),
            'currency': service.currency,
        },
        'date': date_str,
        'slots_count': len(slots),
        'slots': slots,
    })


def booking_success_view(request, booking_ref):
    """
    Displays the confirmation page for a newly created booking.
    """
    appointment = get_object_or_404(Appointment, booking_reference=booking_ref)
    context = {
        'appointment': appointment,
    }
    return render(request, 'scheduling/booking_success.html', context)


def download_ics_view(request, booking_ref):
    """
    Generates and returns the downloadable .ics calendar file.
    """
    appointment = get_object_or_404(Appointment, booking_reference=booking_ref)
    ics_text = generate_ics_content(appointment)
    
    response = HttpResponse(ics_text, content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="Design_Consultation_{appointment.booking_reference}.ics"'
    return response


def lookup_booking_view(request):
    """
    Allows clients to lookup their booking by reference and email.
    """
    form = BookingLookupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ref = form.cleaned_data['booking_reference'].strip().upper()
        email = form.cleaned_data['client_email'].strip().lower()

        appointment = Appointment.objects.filter(booking_reference__iexact=ref, client_email__iexact=email).first()
        if appointment:
            return redirect('booking_detail', booking_ref=appointment.booking_reference)
        else:
            messages.error(request, "No booking found matching that reference code and email. Please check your credentials.")

    context = {'form': form}
    return render(request, 'scheduling/lookup_booking.html', context)


def booking_detail_view(request, booking_ref):
    """
    Displays comprehensive booking details with self-service actions.
    """
    appointment = get_object_or_404(Appointment, booking_reference=booking_ref)
    review_form = ReviewForm(initial={
        'client_name': appointment.client_name,
        'service_name': appointment.service.name,
    })
    
    context = {
        'appointment': appointment,
        'review_form': review_form,
    }
    return render(request, 'scheduling/booking_detail.html', context)


def reschedule_booking_view(request, booking_ref):
    """
    Allows the client or designer to reschedule an existing appointment to a new date/time slot.
    """
    appointment = get_object_or_404(Appointment, booking_reference=booking_ref)
    
    if appointment.status in ['CANCELLED', 'COMPLETED']:
        messages.error(request, f"Cannot reschedule a booking that is already {appointment.get_status_display().lower()}.")
        return redirect('booking_detail', booking_ref=appointment.booking_reference)

    if request.method == 'POST':
        form = RescheduleForm(request.POST, appointment=appointment)
        if form.is_valid():
            appointment.appointment_date = form.cleaned_data['appointment_date']
            appointment.start_time = form.cleaned_data['start_time']
            appointment.status = 'RESCHEDULED'
            appointment.save()
            messages.success(request, f"Your consultation has been rescheduled to {appointment.appointment_date} at {appointment.start_time.strftime('%I:%M %p')}.")
            return redirect('booking_detail', booking_ref=appointment.booking_reference)
        else:
            messages.error(request, "Selected slot is unavailable. Please pick a different slot.")
    else:
        form = RescheduleForm(appointment=appointment, initial={
            'appointment_date': appointment.appointment_date,
            'start_time': appointment.start_time,
        })

    context = {
        'appointment': appointment,
        'form': form,
        'today_date': timezone.localdate().strftime('%Y-%m-%d'),
    }
    return render(request, 'scheduling/reschedule.html', context)


def cancel_booking_view(request, booking_ref):
    """
    Cancels an active appointment.
    """
    appointment = get_object_or_404(Appointment, booking_reference=booking_ref)
    if appointment.status in ['CANCELLED', 'COMPLETED']:
        messages.info(request, "This appointment is already cancelled or completed.")
        return redirect('booking_detail', booking_ref=appointment.booking_reference)

    if request.method == 'POST':
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.warning(request, f"Appointment {appointment.booking_reference} has been cancelled.")
        return redirect('booking_detail', booking_ref=appointment.booking_reference)

    return render(request, 'scheduling/cancel_confirm.html', {'appointment': appointment})


@require_POST
def add_review_view(request, booking_ref):
    """
    Submits client review for an appointment.
    """
    appointment = get_object_or_404(Appointment, booking_reference=booking_ref)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.appointment = appointment
        review.save()
        messages.success(request, "Thank you for submitting your review!")
    else:
        messages.error(request, "Failed to submit review. Please ensure all fields are filled.")

    return redirect('booking_detail', booking_ref=appointment.booking_reference)
