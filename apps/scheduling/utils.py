from datetime import datetime, date, time, timedelta
from django.utils import timezone
from .models import WorkingHours, BlackoutDate, Appointment, Service


def get_available_slots(service, target_date):
    """
    Calculates dynamic real-time available time slots for a given service on a specific date.
    Accounts for designer working hours, lunch breaks, buffer periods, and existing active appointments.
    """
    if isinstance(target_date, str):
        try:
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            return []

    today = timezone.localdate()
    if target_date < today:
        return []

    # Check blackout dates
    if BlackoutDate.objects.filter(start_date__lte=target_date, end_date__gte=target_date).exists():
        return []

    # Check working hours for day of week (0=Mon, ..., 6=Sun)
    weekday = target_date.weekday()
    try:
        schedule = WorkingHours.objects.get(day_of_week=weekday)
    except WorkingHours.DoesNotExist:
        # Default fallback: Mon-Fri 9am-5pm, Sat 10am-2pm
        if weekday in [0, 1, 2, 3, 4]:
            schedule = WorkingHours(day_of_week=weekday, start_time=time(9, 0), end_time=time(17, 0), break_start=time(13, 0), break_end=time(14, 0), is_off=False)
        elif weekday == 5:
            schedule = WorkingHours(day_of_week=weekday, start_time=time(10, 0), end_time=time(14, 0), is_off=False)
        else:
            return []

    if schedule.is_off:
        return []

    # Existing active appointments on that day
    existing_appointments = Appointment.objects.filter(
        appointment_date=target_date,
        status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS', 'RESCHEDULED']
    ).values('start_time', 'end_time')

    duration = timedelta(minutes=service.duration_minutes)
    buffer = timedelta(minutes=service.buffer_minutes)
    step = timedelta(minutes=30)  # Check at 30 min increments

    now = timezone.localtime()
    current_time_threshold = (now + timedelta(minutes=45)).time() if target_date == today else None

    # Construct start & end datetimes for calculation
    dummy_date = date(2000, 1, 1)
    current_dt = datetime.combine(dummy_date, schedule.start_time)
    end_dt = datetime.combine(dummy_date, schedule.end_time)
    
    break_start_dt = datetime.combine(dummy_date, schedule.break_start) if schedule.break_start else None
    break_end_dt = datetime.combine(dummy_date, schedule.break_end) if schedule.break_end else None

    available_slots = []

    while current_dt + duration <= end_dt:
        slot_start_time = current_dt.time()
        slot_end_dt = current_dt + duration
        slot_end_time = slot_end_dt.time()

        # 1. Past time check for today
        if current_time_threshold and slot_start_time <= current_time_threshold:
            current_dt += step
            continue

        # 2. Lunch break overlap check
        if break_start_dt and break_end_dt:
            if not (slot_end_dt <= break_start_dt or current_dt >= break_end_dt):
                current_dt += step
                continue

        # 3. Existing appointment conflict check
        conflict = False
        for appt in existing_appointments:
            appt_start = appt['start_time']
            appt_end = appt['end_time']
            # Overlap condition: slot_start < appt_end and slot_end > appt_start
            if slot_start_time < appt_end and slot_end_time > appt_start:
                conflict = True
                break

        if not conflict:
            available_slots.append({
                'start_time': slot_start_time.strftime('%H:%M'),
                'start_formatted': slot_start_time.strftime('%I:%M %p').lstrip('0'),
                'end_time': slot_end_time.strftime('%H:%M'),
                'end_formatted': slot_end_time.strftime('%I:%M %p').lstrip('0'),
            })

        # Advance by duration + buffer or 30 min step
        current_dt += step

    return available_slots


def generate_ics_content(appointment):
    """
    Generates standard RFC 5545 iCalendar (.ics) content for the booked appointment.
    Can be opened directly in Apple Calendar, Google Calendar, Outlook, etc.
    """
    start_dt = datetime.combine(appointment.appointment_date, appointment.start_time)
    end_dt = datetime.combine(appointment.appointment_date, appointment.end_time)

    dtstamp = timezone.now().strftime('%Y%m%dT%H%M%SZ')
    dtstart = start_dt.strftime('%Y%m%dT%H%M%S')
    dtend = end_dt.strftime('%Y%m%dT%H%M%S')

    summary = f"Design Consultation: {appointment.service.name} ({appointment.booking_reference})"
    description = (
        f"Design Project Discovery & Consultation Session\\n\\n"
        f"Client: {appointment.client_name}\\n"
        f"Brand/Company: {appointment.company_or_brand or 'N/A'}\\n"
        f"Service: {appointment.service.name}\\n"
        f"Meeting Type: {appointment.get_meeting_type_display()}\\n"
        f"Meeting Link: {appointment.meeting_link}\\n"
        f"Booking Ref: {appointment.booking_reference}\\n\\n"
        f"Scope / Notes: {appointment.design_brief[:200]}"
    )
    location = appointment.meeting_link or "Google Meet Online Video"

    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//James Graphic Design Studio//Scheduling System//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:REQUEST",
        "BEGIN:VEVENT",
        f"UID:{appointment.booking_reference}@jamesdesignstudio.com",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{description}",
        f"LOCATION:{location}",
        f"ORGANIZER;CN=James Creative Studio:mailto:studio@jamescreative.design",
        f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=ACCEPTED;CN={appointment.client_name}:mailto:{appointment.client_email}",
        "STATUS:CONFIRMED",
        "SEQUENCE:0",
        "BEGIN:VALARM",
        "TRIGGER:-PT30M",
        "ACTION:DISPLAY",
        "DESCRIPTION:Reminder: Graphic Design Consultation in 30 minutes",
        "END:VALARM",
        "END:VEVENT",
        "END:VCALENDAR"
    ]

    return "\r\n".join(ics_lines)
