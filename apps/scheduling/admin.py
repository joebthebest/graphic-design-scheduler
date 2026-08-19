from django.contrib import admin
from django.utils.html import format_html
from .models import Service, PortfolioItem, WorkingHours, BlackoutDate, Appointment, Review


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration_minutes', 'turnaround_time', 'is_active', 'order')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description', 'deliverables')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'is_active', 'order')


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'title', 'category', 'client_name', 'related_service', 'is_featured', 'order', 'created_at')
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('title', 'client_name', 'description', 'tools_used')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'order', 'category')
    readonly_fields = ('image_detail_preview', 'created_at')
    
    fieldsets = (
        ("🎨 Design & Artwork Upload", {
            'fields': ('title', 'slug', 'category', 'image', 'image_detail_preview', 'static_image_path'),
            'description': "Upload new high-resolution design image files (.png, .jpg, .webp). If uploaded, it takes precedence over static path."
        }),
        ("📌 Homepage & Gallery Visibility", {
            'fields': ('is_featured', 'order'),
            'description': "Check 'Is featured' to display this artwork directly on the Homepage Selected Works showcase. Use 'Order' (0, 1, 2...) to control display sequence."
        }),
        ("📝 Project Details & Case Study", {
            'fields': ('client_name', 'related_service', 'tools_used', 'description', 'created_at'),
            'description': "Details displayed in the interactive lightbox modal when visitors click on the design."
        }),
    )

    def thumbnail_preview(self, obj):
        url = obj.image_url
        if url:
            return format_html(
                '<img src="{}" style="width: 54px; height: 54px; object-fit: cover; border-radius: 6px; border: 1px solid #333;" />',
                url
            )
        return "No Image"
    thumbnail_preview.short_description = "Preview"

    def image_detail_preview(self, obj):
        url = obj.image_url
        if url:
            return format_html(
                '<div style="margin-top: 8px;"><img src="{}" style="max-height: 280px; max-width: 100%; border-radius: 8px; border: 1px solid #444;" /><br><small style="color: #888;">Current live image</small></div>',
                url
            )
        return "No Image Uploaded Yet"
    image_detail_preview.short_description = "Live Artwork Preview"


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'start_time', 'end_time', 'break_start', 'break_end', 'is_off')
    list_editable = ('start_time', 'end_time', 'break_start', 'break_end', 'is_off')
    ordering = ('day_of_week',)


@admin.register(BlackoutDate)
class BlackoutDateAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'reason')
    list_filter = ('start_date',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'client_name', 'service', 'appointment_date', 'start_time', 'status', 'meeting_type')
    list_filter = ('status', 'meeting_type', 'appointment_date', 'service')
    search_fields = ('booking_reference', 'client_name', 'client_email', 'company_or_brand')
    readonly_fields = ('booking_reference', 'created_at', 'updated_at')
    ordering = ('-appointment_date', '-start_time')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_role', 'service_name', 'rating', 'is_featured', 'created_at')
    list_filter = ('rating', 'is_featured')
    search_fields = ('client_name', 'comment')
    list_editable = ('is_featured',)
