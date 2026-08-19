import random
import string
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from datetime import time, datetime, timedelta

CATEGORY_CHOICES = [
    ('branding', 'Branding & Identity'),
    ('flyers', 'Flyers & Event Posters'),
    ('social', 'Social Media & Creatives'),
    ('infographics', 'Infographics & Corporate Visuals'),
    ('consultation', 'Design Consultation & Strategy'),
]

MEETING_TYPES = [
    ('GOOGLE_MEET', 'Google Meet (Video)'),
    ('ZOOM', 'Zoom Conference'),
    ('PHONE', 'Phone / WhatsApp Call'),
    ('STUDIO', 'In-Person Studio Meeting'),
]

STATUS_CHOICES = [
    ('PENDING', 'Pending Confirmation'),
    ('CONFIRMED', 'Confirmed'),
    ('IN_PROGRESS', 'In Progress / Designing'),
    ('COMPLETED', 'Completed'),
    ('CANCELLED', 'Cancelled'),
    ('RESCHEDULED', 'Rescheduled'),
]

DAYS_OF_WEEK = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
]


def generate_booking_reference():
    """Generates a clean, unique booking reference like DES-892174."""
    chars = ''.join(random.choices(string.digits, k=6))
    return f"DES-{chars}"


class Service(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='branding')
    tagline = models.CharField(max_length=200, blank=True, help_text="Short engaging summary")
    description = models.TextField()
    deliverables = models.TextField(help_text="Comma-separated or bullet list of deliverables")
    duration_minutes = models.PositiveIntegerField(default=60, help_text="Duration of initial briefing/consultation in minutes")
    buffer_minutes = models.PositiveIntegerField(default=15, help_text="Buffer time after appointment for notes/setup")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=150.00)
    currency = models.CharField(max_length=10, default='$')
    turnaround_time = models.CharField(max_length=50, default="3-5 Business Days", help_text="Estimated project delivery time")
    badge_text = models.CharField(max_length=50, blank=True, help_text="E.g. 'Most Popular', 'Fast Delivery'")
    icon = models.CharField(max_length=50, default='palette', help_text="Lucide/Feather icon name")
    gradient = models.CharField(max_length=100, default='linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'price']
        verbose_name = "Design Service"
        verbose_name_plural = "Design Services"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.currency}{self.price:.2f})"

    def get_deliverables_list(self):
        if not self.deliverables:
            return []
        return [item.strip() for item in self.deliverables.split('\n') if item.strip()]


class PortfolioItem(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='branding')
    client_name = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    static_image_path = models.CharField(max_length=255, blank=True, help_text="Static relative image path if image field is not set")
    related_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='portfolio_items')
    tools_used = models.CharField(max_length=200, default="Adobe Photoshop, Illustrator, Figma")
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Portfolio Item"
        verbose_name_plural = "Portfolio Items"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        if self.static_image_path:
            return f"/static/{self.static_image_path.lstrip('/')}"
        return "/static/images/portfolio/clash_of_crowns.png"


class WorkingHours(models.Model):
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, unique=True)
    start_time = models.TimeField(default=time(9, 0))
    end_time = models.TimeField(default=time(17, 0))
    break_start = models.TimeField(null=True, blank=True, default=time(13, 0))
    break_end = models.TimeField(null=True, blank=True, default=time(14, 0))
    is_off = models.BooleanField(default=False)

    class Meta:
        ordering = ['day_of_week']
        verbose_name = "Working Hours"
        verbose_name_plural = "Working Hours"

    def __str__(self):
        day_str = dict(DAYS_OF_WEEK).get(self.day_of_week, "Unknown")
        if self.is_off:
            return f"{day_str}: OFF"
        return f"{day_str}: {self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"


class BlackoutDate(models.Model):
    title = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['start_date']
        verbose_name = "Blackout / Holiday Date"
        verbose_name_plural = "Blackout / Holiday Dates"

    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date})"


class Appointment(models.Model):
    booking_reference = models.CharField(max_length=20, unique=True, db_index=True, default=generate_booking_reference)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='appointments')
    client_name = models.CharField(max_length=120)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=30)
    company_or_brand = models.CharField(max_length=150, blank=True, verbose_name="Company / Brand Name")
    design_brief = models.TextField(verbose_name="Design Brief / Scope", help_text="Describe your project, style, goals, or color preferences")
    brand_assets_link = models.URLField(blank=True, verbose_name="Brand Assets / Reference Link", help_text="Link to Google Drive, Dropbox, Figma, Pinterest board")
    target_deadline = models.DateField(null=True, blank=True, verbose_name="Target Project Deadline")
    appointment_date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    meeting_type = models.CharField(max_length=30, choices=MEETING_TYPES, default='GOOGLE_MEET')
    meeting_link = models.CharField(max_length=255, blank=True, default='https://meet.google.com/apx-dsgn-ses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED', db_index=True)
    designer_notes = models.TextField(blank=True, help_text="Private internal notes for the designer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-start_time']
        verbose_name = "Design Appointment"
        verbose_name_plural = "Design Appointments"

    def __str__(self):
        return f"{self.booking_reference} - {self.client_name} ({self.service.name})"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = generate_booking_reference()
            while Appointment.objects.filter(booking_reference=self.booking_reference).exists():
                self.booking_reference = generate_booking_reference()
        
        # Calculate end_time if not provided
        if not self.end_time and self.start_time and self.service:
            duration = timedelta(minutes=self.service.duration_minutes)
            dummy_dt = datetime.combine(datetime.today(), self.start_time) + duration
            self.end_time = dummy_dt.time()

        super().save(*args, **kwargs)

    @property
    def is_past(self):
        from django.utils import timezone
        today = timezone.localdate()
        return self.appointment_date < today

    @property
    def status_badge_class(self):
        mapping = {
            'PENDING': 'badge-warning',
            'CONFIRMED': 'badge-success',
            'IN_PROGRESS': 'badge-primary',
            'COMPLETED': 'badge-info',
            'CANCELLED': 'badge-danger',
            'RESCHEDULED': 'badge-secondary',
        }
        return mapping.get(self.status, 'badge-secondary')


class Review(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='review')
    client_name = models.CharField(max_length=100)
    client_role = models.CharField(max_length=100, default="Client & Brand Owner")
    service_name = models.CharField(max_length=100, blank=True)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Client Review"
        verbose_name_plural = "Client Reviews"

    def __str__(self):
        return f"Review by {self.client_name} - {self.rating} Stars"
