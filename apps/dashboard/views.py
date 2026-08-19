import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime

from apps.scheduling.models import Appointment, Service, WorkingHours, BlackoutDate, Review, DAYS_OF_WEEK


@login_required
def designer_dashboard_view(request):
    """
    Designer & Studio Executive Dashboard:
    - KPI Metrics (Total Bookings, Revenue, Pending, Completed, Today's sessions)
    - Filterable Appointments Table
    - Fast status toggling
    - Working hours summary
    """
    today = timezone.localdate()
    
    # Query parameters
    status_filter = request.GET.get('status', 'ALL')
    search_query = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date', '')

    appointments = Appointment.objects.select_related('service').all()

    if status_filter != 'ALL':
        appointments = appointments.filter(status=status_filter)
    if search_query:
        appointments = appointments.filter(
            Q(booking_reference__icontains=search_query) |
            Q(client_name__icontains=search_query) |
            Q(client_email__icontains=search_query) |
            Q(company_or_brand__icontains=search_query)
        )
    if date_filter:
        try:
            parsed_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(appointment_date=parsed_date)
        except ValueError:
            pass

    # Calculate KPIs
    all_appointments = Appointment.objects.all()
    total_bookings = all_appointments.count()
    pending_count = all_appointments.filter(status='PENDING').count()
    confirmed_count = all_appointments.filter(status='CONFIRMED').count()
    in_progress_count = all_appointments.filter(status='IN_PROGRESS').count()
    completed_count = all_appointments.filter(status='COMPLETED').count()
    cancelled_count = all_appointments.filter(status='CANCELLED').count()

    today_sessions = all_appointments.filter(appointment_date=today).order_by('start_time')
    upcoming_sessions = all_appointments.filter(
        appointment_date__gte=today,
        status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS', 'RESCHEDULED']
    ).order_by('appointment_date', 'start_time')[:10]

    # Revenue calculation
    confirmed_revenue = all_appointments.filter(
        status__in=['CONFIRMED', 'IN_PROGRESS', 'COMPLETED']
    ).aggregate(total=Sum('service__price'))['total'] or 0

    working_hours = WorkingHours.objects.all().order_by('day_of_week')
    services = Service.objects.all()

    context = {
        'appointments': appointments,
        'today_sessions': today_sessions,
        'upcoming_sessions': upcoming_sessions,
        'total_bookings': total_bookings,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'confirmed_revenue': confirmed_revenue,
        'working_hours': working_hours,
        'services': services,
        'selected_status': status_filter,
        'search_query': search_query,
        'date_filter': date_filter,
        'today': today,
    }
    return render(request, 'dashboard/designer_dashboard.html', context)


@login_required
def update_appointment_status_view(request, booking_ref):
    """
    POST endpoint for changing appointment status from the dashboard.
    """
    appointment = get_object_or_404(Appointment, booking_reference=booking_ref)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        designer_notes = request.POST.get('designer_notes', '')

        if new_status in dict(Appointment._meta.get_field('status').choices):
            appointment.status = new_status
            if designer_notes:
                appointment.designer_notes = designer_notes
            appointment.save()
            messages.success(request, f"Appointment {appointment.booking_reference} status updated to {appointment.get_status_display()}.")
        else:
            messages.error(request, "Invalid status choice.")

    return redirect('designer_dashboard')


@login_required
def working_hours_settings_view(request):
    """
    Configure weekly working hours and break periods.
    """
    schedules = WorkingHours.objects.all().order_by('day_of_week')
    
    if request.method == 'POST':
        for schedule in schedules:
            day_prefix = f"day_{schedule.day_of_week}_"
            is_off = request.POST.get(f"{day_prefix}is_off") == 'on'
            start_time = request.POST.get(f"{day_prefix}start")
            end_time = request.POST.get(f"{day_prefix}end")
            break_start = request.POST.get(f"{day_prefix}break_start")
            break_end = request.POST.get(f"{day_prefix}break_end")

            schedule.is_off = is_off
            if start_time:
                schedule.start_time = datetime.strptime(start_time, '%H:%M').time()
            if end_time:
                schedule.end_time = datetime.strptime(end_time, '%H:%M').time()
            if break_start:
                schedule.break_start = datetime.strptime(break_start, '%H:%M').time()
            else:
                schedule.break_start = None
            if break_end:
                schedule.break_end = datetime.strptime(break_end, '%H:%M').time()
            else:
                schedule.break_end = None
            schedule.save()

        messages.success(request, "Weekly working hours updated successfully!")
        return redirect('working_hours_settings')

    context = {
        'schedules': schedules,
    }
    return render(request, 'dashboard/availability_settings.html', context)


@login_required
def export_appointments_csv_view(request):
    """
    Exports appointments dataset as a formatted CSV file.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="studio_appointments_{timezone.localdate().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Booking Ref',
        'Client Name',
        'Email',
        'Phone',
        'Company/Brand',
        'Service',
        'Price ($)',
        'Appointment Date',
        'Start Time',
        'End Time',
        'Meeting Type',
        'Status',
        'Design Brief',
        'Created At'
    ])

    appointments = Appointment.objects.select_related('service').all().order_by('-appointment_date')
    for appt in appointments:
        writer.writerow([
            appt.booking_reference,
            appt.client_name,
            appt.client_email,
            appt.client_phone,
            appt.company_or_brand or 'N/A',
            appt.service.name,
            appt.service.price,
            appt.appointment_date,
            appt.start_time.strftime('%H:%M'),
            appt.end_time.strftime('%H:%M'),
            appt.get_meeting_type_display(),
            appt.get_status_display(),
            appt.design_brief.replace('\n', ' ')[:250],
            appt.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response
