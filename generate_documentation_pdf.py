import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# --- STEP 1: GENERATE DIAGRAMS ---

def draw_stick_figure(ax, x, y, label, scale=1.0):
    # Head
    head = patches.Circle((x, y + 0.35 * scale), 0.08 * scale, fill=False, color='#2c3e50', linewidth=1.5)
    ax.add_patch(head)
    # Body
    ax.plot([x, x], [y + 0.27 * scale, y + 0.05 * scale], color='#2c3e50', linewidth=1.5)
    # Arms
    ax.plot([x - 0.15 * scale, x + 0.15 * scale], [y + 0.20 * scale, y + 0.20 * scale], color='#2c3e50', linewidth=1.5)
    # Legs
    ax.plot([x, x - 0.12 * scale], [y + 0.05 * scale, y - 0.18 * scale], color='#2c3e50', linewidth=1.5)
    ax.plot([x, x + 0.12 * scale], [y + 0.05 * scale, y - 0.18 * scale], color='#2c3e50', linewidth=1.5)
    # Label
    ax.text(x, y - 0.26 * scale, label, ha='center', va='top', fontsize=9, fontweight='bold', color='#1a252f')

def draw_ellipse_uc(ax, x, y, width, height, text):
    ellipse = patches.Ellipse((x, y), width, height, facecolor='#f0f4f8', edgecolor='#3b82f6', linewidth=1.4)
    ax.add_patch(ellipse)
    ax.text(x, y, text, ha='center', va='center', fontsize=8, color='#1e293b', wrap=True)

def generate_use_case_diagram(output_path):
    fig, ax = plt.subplots(figsize=(8.5, 6.2), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.5)
    ax.axis('off')

    # System boundary box
    sys_box = patches.Rectangle((2.2, 0.4), 5.6, 6.7, fill=True, facecolor='#ffffff', edgecolor='#64748b', linewidth=1.5)
    ax.add_patch(sys_box)
    ax.text(5.0, 6.85, 'James Design Studio — Scheduling System', ha='center', va='center', fontsize=11, fontweight='bold', color='#0f172a')

    # Actors
    draw_stick_figure(ax, 1.0, 5.5, 'Client / Customer', scale=0.85)
    draw_stick_figure(ax, 1.0, 2.3, 'Visitor', scale=0.85)
    draw_stick_figure(ax, 9.0, 5.2, 'Designer (Staff)', scale=0.85)
    draw_stick_figure(ax, 9.0, 1.8, 'Studio Admin', scale=0.85)

    # Use cases
    ucs = {
        'browse': (3.6, 6.2, 1.8, 0.55, 'Browse Portfolio\n& Services'),
        'login': (3.6, 5.3, 1.8, 0.52, 'Sign Up / Log In'),
        'lookup': (3.6, 4.4, 1.8, 0.52, 'Find / Track\nBooking'),
        'book': (3.6, 3.4, 1.8, 0.52, 'Book Consultation\nSession'),
        'slots': (5.0, 4.0, 1.8, 0.52, 'Select Real-Time\nAvailable Slot'),
        'cancel': (3.6, 2.4, 1.8, 0.52, 'Cancel / Reschedule\nBooking'),
        'hours': (6.4, 6.2, 1.8, 0.55, 'Set Weekly\nWorking Hours'),
        'blackout': (6.4, 5.2, 1.8, 0.52, 'Manage Time Off\n& Blackout Dates'),
        'manage_appts': (6.4, 4.2, 1.8, 0.52, 'Manage Appointments\n& Status'),
        'export': (6.4, 3.2, 1.8, 0.52, 'Export CSV &\nCalendar Sync'),
        'catalog': (5.0, 1.8, 1.9, 0.55, 'Manage Services\n& Portfolio Items'),
        'users': (5.0, 0.9, 1.9, 0.52, 'Manage User Accounts\n(Django Admin)')
    }

    for k, (x, y, w, h, t) in ucs.items():
        draw_ellipse_uc(ax, x, y, w, h, t)

    # Lines from Visitor
    ax.plot([1.0, 2.7], [2.3, 6.2], color='#94a3b8', linestyle='-', linewidth=1)
    ax.plot([1.0, 2.7], [2.3, 5.3], color='#94a3b8', linestyle='-', linewidth=1)
    ax.plot([1.0, 2.7], [2.3, 4.4], color='#94a3b8', linestyle='-', linewidth=1)

    # Lines from Customer
    ax.plot([1.0, 2.7], [5.5, 6.2], color='#334155', linestyle='-', linewidth=1.2)
    ax.plot([1.0, 2.7], [5.5, 5.3], color='#334155', linestyle='-', linewidth=1.2)
    ax.plot([1.0, 2.7], [5.5, 4.4], color='#334155', linestyle='-', linewidth=1.2)
    ax.plot([1.0, 2.7], [5.5, 3.4], color='#334155', linestyle='-', linewidth=1.2)
    ax.plot([1.0, 2.7], [5.5, 2.4], color='#334155', linestyle='-', linewidth=1.2)

    # <<include>> line from Book to Slots
    ax.annotate('', xy=(4.1, 3.8), xytext=(4.5, 3.8),
                arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.2, ls='--'))
    ax.text(4.2, 3.85, '<<include>>', fontsize=7, color='#ef4444', ha='center')

    # Lines from Designer (Staff)
    ax.plot([9.0, 7.3], [5.2, 6.2], color='#334155', linestyle='-', linewidth=1.2)
    ax.plot([9.0, 7.3], [5.2, 5.2], color='#334155', linestyle='-', linewidth=1.2)
    ax.plot([9.0, 7.3], [5.2, 4.2], color='#334155', linestyle='-', linewidth=1.2)
    ax.plot([9.0, 7.3], [5.2, 3.2], color='#334155', linestyle='-', linewidth=1.2)

    # Lines from Admin
    ax.plot([9.0, 6.0], [1.8, 1.8], color='#334155', linestyle='-', linewidth=1.2)
    ax.plot([9.0, 6.0], [1.8, 0.9], color='#334155', linestyle='-', linewidth=1.2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def generate_sequence_diagram(output_path):
    fig, ax = plt.subplots(figsize=(8.5, 6.8), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10.5)
    ax.axis('off')

    # Lifeline entities
    entities = [
        ('Client\n(Browser)', 1.2),
        ('Booking View\n(Django View)', 3.2),
        ('API Slot Endpoint\n(/available-slots/)', 5.3),
        ('Slot Engine\n(utils.py)', 7.3),
        ('Database\n(SQLite / Models)', 9.0),
    ]

    for name, x in entities:
        # Box
        box = patches.Rectangle((x - 0.75, 9.6), 1.5, 0.75, facecolor='#e0f2fe', edgecolor='#0284c7', linewidth=1.3)
        ax.add_patch(box)
        ax.text(x, 9.97, name, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0369a1')
        # Dashed Lifeline
        ax.plot([x, x], [9.6, 0.6], color='#94a3b8', linestyle='--', linewidth=1)

    # Helper for messages
    def msg(y, x1, x2, text, is_async=False, is_return=False):
        style = '->' if not is_return else '--'
        ls = '-' if not is_return else '--'
        color = '#0284c7' if not is_return else '#64748b'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.2, ls=ls))
        mid_x = (x1 + x2) / 2
        ax.text(mid_x, y + 0.12, text, ha='center', va='bottom', fontsize=7, color='#1e293b', fontweight='500')

    # Sequence steps
    msg(9.1, 1.2, 3.2, '1. GET /schedule/book/ (open wizard)')
    msg(8.6, 3.2, 9.0, '2. Service.objects.filter(is_active=True)')
    msg(8.1, 9.0, 3.2, '3. Return active design services', is_return=True)
    msg(7.6, 3.2, 1.2, '4. Render wizard step 1 (Services)', is_return=True)

    msg(7.0, 1.2, 5.3, '5. GET /schedule/api/available-slots/?service_id=X&date=Y')
    msg(6.4, 5.3, 7.3, '6. get_available_slots(service, date)')
    msg(5.8, 7.3, 9.0, '7. Query WorkingHours, BlackoutDates, Appointments')
    msg(5.2, 9.0, 7.3, '8. Return booked slots & schedules', is_return=True)
    msg(4.6, 7.3, 5.3, '9. Calculate & filter conflict-free slots', is_return=True)
    msg(4.0, 5.3, 1.2, '10. JSON response: { slots: ["10:00", "11:00", ...] }', is_return=True)

    msg(3.3, 1.2, 3.2, '11. POST /schedule/book/ (client details & slot)')
    msg(2.7, 3.2, 7.3, '12. Re-verify slot availability (anti-collision)')
    msg(2.1, 3.2, 9.0, '13. Appointment.objects.create(...) + clean()')
    msg(1.5, 9.0, 3.2, '14. Booking confirmed & Reference ID generated', is_return=True)
    msg(0.9, 3.2, 1.2, '15. Redirect to booking confirmation / ICS calendar', is_return=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def generate_class_diagram(output_path):
    fig, ax = plt.subplots(figsize=(8.5, 7.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    def draw_uml_class(x, y, w, h, title, fields, methods):
        # Outer box
        box = patches.Rectangle((x, y), w, h, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.3)
        ax.add_patch(box)
        # Header
        header = patches.Rectangle((x, y + h - 0.45), w, 0.45, facecolor='#0284c7', edgecolor='#1e293b', linewidth=1.3)
        ax.add_patch(header)
        ax.text(x + w / 2, y + h - 0.23, title, ha='center', va='center', fontsize=8, fontweight='bold', color='#ffffff')

        # Fields
        cur_y = y + h - 0.6
        for f in fields:
            ax.text(x + 0.1, cur_y, f, ha='left', va='center', fontsize=6.2, color='#334155', fontfamily='monospace')
            cur_y -= 0.22

        # Separator
        ax.plot([x, x + w], [cur_y + 0.08, cur_y + 0.08], color='#cbd5e1', linewidth=0.8)
        cur_y -= 0.12

        # Methods
        for m in methods:
            ax.text(x + 0.1, cur_y, m, ha='left', va='center', fontsize=6.2, color='#0f172a', fontfamily='monospace', fontweight='600')
            cur_y -= 0.22

    # Classes
    draw_uml_class(0.4, 7.2, 2.4, 2.3, 'User (Django Built-in)',
                   ['+ id: Integer', '+ username: String', '+ email: String', '+ is_staff: Boolean'],
                   ['+ check_password()', '+ get_full_name()'])

    draw_uml_class(0.4, 4.4, 2.4, 2.3, 'Profile',
                   ['+ user: OneToOne(User)', '+ role: String (customer/staff)', '+ phone: String', '+ studio_bio: Text'],
                   ['+ is_designer()', '+ __str__()'])

    draw_uml_class(3.4, 6.8, 3.1, 2.8, 'Service',
                   ['+ id: Integer', '+ name: String', '+ slug: SlugField', '+ duration_minutes: Int', '+ buffer_minutes: Int', '+ price: Decimal', '+ currency: String (₦)', '+ is_active: Boolean'],
                   ['+ total_slot_duration()', '+ get_absolute_url()', '+ __str__()'])

    draw_uml_class(7.0, 4.8, 2.6, 4.8, 'Appointment',
                   ['+ booking_reference: String', '+ service: FK(Service)', '+ client_name: String', '+ client_email: String', '+ client_phone: String', '+ appointment_date: Date', '+ start_time: Time', '+ end_time: Time', '+ status: String', '+ meeting_type: String', '+ design_brief: Text'],
                   ['+ clean()', '+ is_upcoming()', '+ cancel_booking()', '+ __str__()'])

    draw_uml_class(3.4, 3.9, 3.1, 2.4, 'WorkingHours',
                   ['+ day_of_week: Integer (0-6)', '+ start_time: Time', '+ end_time: Time', '+ break_start: Time', '+ break_end: Time', '+ is_off: Boolean'],
                   ['+ get_day_of_week_display()', '+ __str__()'])

    draw_uml_class(0.4, 1.2, 2.4, 2.5, 'PortfolioItem',
                   ['+ title: String', '+ slug: SlugField', '+ category: String', '+ image: ImageField', '+ is_featured: Boolean', '+ order: Integer'],
                   ['+ image_url()', '+ __str__()'])

    draw_uml_class(3.4, 1.2, 3.1, 2.3, 'utils.py <<module>>',
                   ['(Availability Engine Logic)'],
                   ['+ get_available_slots()', '+ generate_ics_content()', '+ format_currency_naira()'])

    draw_uml_class(7.0, 1.2, 2.6, 2.8, 'Review',
                   ['+ client_name: String', '+ client_role: String', '+ service_name: String', '+ rating: Integer (1-5)', '+ comment: Text', '+ is_featured: Boolean'],
                   ['+ __str__()'])

    # Relationships Lines
    # User -> Profile
    ax.annotate('', xy=(1.6, 6.7), xytext=(1.6, 7.2), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.2))
    ax.text(1.7, 6.95, '1..1', fontsize=7, color='#334155')

    # Service -> Appointment
    ax.annotate('', xy=(7.0, 7.5), xytext=(6.5, 7.5), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.2))
    ax.text(6.65, 7.6, '1..*', fontsize=7, color='#334155')

    # WorkingHours -> utils.py
    ax.annotate('', xy=(4.95, 3.5), xytext=(4.95, 3.9), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.2, ls='--'))

    # utils.py -> Appointment
    ax.annotate('', xy=(7.0, 3.0), xytext=(6.5, 2.5), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.2, ls='--'))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


# --- STEP 2: NUMBERED CANVAS FOR FOOTERS ---

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 9)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(54, 36, "SEN 310 — Project Documentation: Personal Scheduling Web Application")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(612 - 54, 36, page_text)
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 48, 612 - 54, 48)
            self.restoreState()


# --- STEP 3: BUILD THE PDF DOCUMENT ---

def generate_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        alignment=1, # Center
        textColor=colors.HexColor('#0f172a')
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=17,
        alignment=1,
        textColor=colors.HexColor('#334155')
    )

    author_style = ParagraphStyle(
        'CoverAuthor',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=18,
        alignment=1,
        textColor=colors.HexColor('#0f172a')
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=20,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'SectionH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#0369a1'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1e293b')
    )

    table_bold_style = ParagraphStyle(
        'TableBodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#0f172a')
    )

    caption_style = ParagraphStyle(
        'FigCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        alignment=1,
        textColor=colors.HexColor('#475569'),
        spaceBefore=4,
        spaceAfter=12
    )

    story = []

    # ================= PAGE 1: COVER =================
    story.append(Spacer(1, 1.8 * inch))
    story.append(Paragraph("JAMES DESIGN STUDIO", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("A Personal Scheduling &amp; Portfolio Web Application for Graphic Design Businesses<br/>Built using Python and Django Framework", subtitle_style))
    story.append(Spacer(1, 2.2 * inch))
    story.append(Paragraph("JAMES EMMA EDEH", author_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("20231411222", subtitle_style))
    story.append(Spacer(1, 1.8 * inch))
    story.append(Paragraph("Project Documentation<br/>Covering: User Story, Use Case Diagram, Sequence Diagram, Class Diagram, and Deployment", subtitle_style))
    story.append(Spacer(1, 0.8 * inch))
    story.append(Paragraph("Built with Python and the Django Framework", subtitle_style))
    story.append(PageBreak())

    # ================= PAGE 2: USER STORY =================
    story.append(Paragraph("1. User Story", h1_style))
    story.append(Paragraph(
        "<b>James Design Studio</b> is a full-featured web application that enables a freelance graphic design studio "
        "to showcase creative works, automate client consultation bookings, calculate conflict-free real-time calendar slots, and manage "
        "production workflows online instead of through manual back-and-forth phone calls or unorganized messaging apps. "
        "The system supports three primary roles: a <b>Customer / Client</b> who browses portfolio designs and books design consultation sessions, "
        "a <b>Designer / Staff Member</b> who manages availability, reviews design briefs, and updates project statuses, and a <b>Business Admin</b> "
        "who oversees the design service catalog, pricing in Naira (₦), and customer accounts. The user stories below describe the system from the "
        "perspective of each user role.",
        body_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1.1 Customer Stories", h2_style))
    story.append(Paragraph("• <b>As a customer</b>, I want to browse high-resolution portfolio designs (event flyers, brand identities, infographics, social packs) with uncropped previews, so that I can evaluate the designer's style and quality before committing.", bullet_style))
    story.append(Paragraph("• <b>As a customer</b>, I want to see the studio's curated service packages with transparent Naira (₦) pricing and durations, so that I know the financial investment upfront.", bullet_style))
    story.append(Paragraph("• <b>As a customer</b>, I want to choose a date and pick from real-time available time slots that automatically exclude booked sessions, so that I do not waste time selecting an unavailable slot.", bullet_style))
    story.append(Paragraph("• <b>As a customer</b>, I want to provide my design brief, reference links, and contact details in a guided 4-step wizard, so that the designer understands my project requirements beforehand.", bullet_style))
    story.append(Paragraph("• <b>As a customer</b>, I want to instantly receive a booking reference code and download an .ICS calendar invite, so that I can add the discovery meeting to Google Calendar or Apple Calendar.", bullet_style))
    story.append(Paragraph("• <b>As a customer</b>, I want to look up my booking status, reschedule, or cancel my appointment online, so that I have full control over my schedule without making phone calls.", bullet_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1.2 Staff / Designer Stories", h2_style))
    story.append(Paragraph("• <b>As a designer</b>, I want to configure my recurring weekly working hours and lunch break intervals (e.g., Monday–Friday 9:00 AM to 5:00 PM), so that clients can only book me during active working hours.", bullet_style))
    story.append(Paragraph("• <b>As a designer</b>, I want to add specific blackout dates (holidays, illness, or studio vacations), so that the slot calculation engine prevents bookings on those dates.", bullet_style))
    story.append(Paragraph("• <b>As a designer</b>, I want a centralized dashboard showing key metrics (total bookings, confirmed Naira revenue, pending reviews), so that I have full business clarity.", bullet_style))
    story.append(Paragraph("• <b>As a designer</b>, I want to view all appointments in an organized table and update statuses (Pending, Confirmed, In Progress, Completed, Cancelled), so that my client pipeline is accurate.", bullet_style))
    story.append(Paragraph("• <b>As a designer</b>, I want to export my appointments list to CSV, so that I can perform accounting and archive client records.", bullet_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1.3 Business Admin Stories", h2_style))
    story.append(Paragraph("• <b>As a business admin</b>, I want to add, edit, or deactivate service packages and adjust prices in Naira (₦), so that our public offerings remain up-to-date.", bullet_style))
    story.append(Paragraph("• <b>As a business admin</b>, I want to upload, reorder, and feature new graphic design artworks in the portfolio showcase, so that visitors always see recent high-impact works.", bullet_style))
    story.append(Paragraph("• <b>As a business admin</b>, I want to manage client reviews and testimonials from the Django administration panel, ensuring authentic client feedback is showcased.", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("1.4 Non-Functional Expectations", h2_style))
    story.append(Paragraph("• <b>Concurrency & Anti-Collision:</b> The system must strictly prohibit double-booking. The slot calculation engine and model-level validation must prevent two clients from reserving overlapping time slots.", bullet_style))
    story.append(Paragraph("• <b>Responsive & Editorial UI:</b> The interface must deliver a modern, high-contrast editorial aesthetic across mobile phones, tablets, and wide desktop screens.", bullet_style))
    story.append(Paragraph("• <b>Security & Access Control:</b> Administrative dashboards, appointment modifications, and working hours settings must require authentication, protecting sensitive client data.", bullet_style))
    story.append(Paragraph("• <b>Automated Calendar Sync:</b> The system must generate standard iCalendar (.ics) RFC-5545 payloads for universal cross-platform calendar integration.", bullet_style))
    story.append(PageBreak())

    # ================= PAGE 3 & 4: USE CASE DIAGRAM =================
    story.append(Paragraph("2. Use Case Diagram", h1_style))
    story.append(Paragraph(
        "The diagram below illustrates the interactions between the system actors (Visitor, Customer/Client, Designer, and Business Admin) "
        "and the primary functional capabilities of the web application.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Add Diagram Image
    story.append(RLImage("use_case_diagram.png", width=6.8 * inch, height=4.9 * inch))
    story.append(Paragraph("Figure 1: Use Case Diagram for James Design Studio Scheduling Web Application", caption_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("2.1 Actors", h2_style))
    story.append(Paragraph("• <b>Visitor:</b> An unauthenticated user browsing portfolio artworks, service catalog packages, and studio contact information.", bullet_style))
    story.append(Paragraph("• <b>Customer / Client:</b> A client who selects a design package, provides a design brief, selects a real-time calendar slot, and manages their appointment.", bullet_style))
    story.append(Paragraph("• <b>Designer (Staff):</b> The creative professional who defines working schedules, reviews client briefs, manages appointment lifecycle statuses, and exports scheduling data.", bullet_style))
    story.append(Paragraph("• <b>Business Admin:</b> The studio administrator with full access to the Django administration panel for managing services, portfolio items, testimonials, and user permissions.", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("2.2 Detailed Use Case Descriptions", h2_style))

    def make_uc_table(fields_data):
        table_rows = [
            [Paragraph("<b>Field</b>", table_header_style), Paragraph("<b>Description</b>", table_header_style)]
        ]
        for field, desc in fields_data:
            table_rows.append([Paragraph(field, table_bold_style), Paragraph(desc, table_body_style)])
        t = Table(table_rows, colWidths=[1.3 * inch, 5.5 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f8fafc')]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        return t

    # Use Case 1: Book Appointment
    story.append(Paragraph("Use Case: Book Design Consultation Session", h3_style))
    uc1_data = [
        ("Actor", "Customer / Client"),
        ("Description", "Enables a client to choose a design service, input project requirements, pick a conflict-free slot from the live calendar, and receive a confirmed booking reference."),
        ("Precondition", "At least one active design service and active working hours schedule exist in the database."),
        ("Main Flow", "1. Client opens booking wizard (/schedule/book/).<br/>"
                      "2. Client selects design service package (e.g., Brand Identity Suite).<br/>"
                      "3. Client selects desired date from interactive calendar.<br/>"
                      "4. System queries database via AJAX (/schedule/api/available-slots/) and dynamically renders available time slots.<br/>"
                      "5. Client selects a slot and fills in contact details, project deadline, meeting preference, and design brief.<br/>"
                      "6. Client submits the booking form.<br/>"
                      "7. System validates slot availability, generates unique booking reference (e.g. DES-102938), saves record as 'PENDING', and renders confirmation page with .ICS calendar download."),
        ("Alternate Flow", "If the selected time slot was taken concurrently by another user, the system rejects the submission with a clear collision warning and prompts the client to choose another time."),
        ("Postcondition", "A new Appointment record is created in the database and is immediately visible on the designer's dashboard."),
        ("Includes", "Select Real-Time Available Slot, Re-check Anti-Collision Validation.")
    ]
    story.append(make_uc_table(uc1_data))
    story.append(Spacer(1, 8))

    # Use Case 2: Set Weekly Availability
    story.append(Paragraph("Use Case: Set Weekly Working Hours & Blackout Dates", h3_style))
    uc2_data = [
        ("Actor", "Designer (Staff)"),
        ("Description", "Allows the designer to define recurring working hours per weekday, configure lunch breaks, and block out holiday dates."),
        ("Precondition", "The designer is authenticated with staff/designer credentials."),
        ("Main Flow", "1. Designer logs into dashboard and navigates to Availability Settings (/dashboard/settings/working-hours/).<br/>"
                      "2. Designer sets daily start time, end time, break intervals, and 'Day Off' toggle for Monday through Sunday.<br/>"
                      "3. Designer optionally adds blackout dates with reasons (e.g., Studio Vacation).<br/>"
                      "4. System validates time sequences (start < end) and commits configuration to database."),
        ("Postcondition", "Customer slot calculations immediately reflect the updated operating hours and blacked-out periods.")
    ]
    story.append(make_uc_table(uc2_data))
    story.append(Spacer(1, 8))

    # Use Case 3: Manage Service Catalog
    story.append(Paragraph("Use Case: Manage Service Catalog & Portfolio Works", h3_style))
    uc3_data = [
        ("Actor", "Business Admin"),
        ("Description", "Allows the studio administrator to add, edit, reorder, or deactivate design packages and portfolio showcase items."),
        ("Precondition", "User is authenticated with superuser / admin privileges."),
        ("Main Flow", "1. Admin opens Django admin (/admin/).<br/>"
                      "2. Admin creates/edits a Service with name, duration, buffer time, and price in Naira (₦).<br/>"
                      "3. Admin uploads portfolio images, configures categories, and sets featured display order.<br/>"
                      "4. System saves records and refreshes public catalog and portfolio grid immediately."),
        ("Postcondition", "Public website displays updated packages, Naira figures, and artwork showcase.")
    ]
    story.append(make_uc_table(uc3_data))
    story.append(PageBreak())

    # ================= PAGE 5 & 6: SEQUENCE DIAGRAM =================
    story.append(Paragraph("3. Sequence Diagram", h1_style))
    story.append(Paragraph(
        "The Book Consultation Session workflow represents the core interaction of the system. "
        "It coordinates client input across a multi-step interface, asynchronous JSON slot calculations, "
        "double-booking prevention, database transactions, and calendar file generation.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Add Sequence Diagram Image
    story.append(RLImage("sequence_diagram.png", width=6.8 * inch, height=5.4 * inch))
    story.append(Paragraph("Figure 2: Sequence Diagram for the Booking Workflow & Real-Time Slot Engine", caption_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3.1 Description of the Flow", h2_style))
    story.append(Paragraph("• <b>1–4. Service Package Selection:</b> The client navigates to the booking wizard (/schedule/book/). The Django view queries active services from the database and renders Step 1 with durations and Naira pricing.", bullet_style))
    story.append(Paragraph("• <b>5–6. Interactive Date Selection:</b> When the client selects a service and picks a calendar date, the front-end JavaScript issues an asynchronous HTTP GET request to /schedule/api/available-slots/?service_id=X&date=Y.", bullet_style))
    story.append(Paragraph("• <b>7–9. Slot Engine Calculation:</b> The API endpoint executes get_available_slots() in utils.py. The engine loads the designer's WorkingHours for that weekday, verifies that the date is not in BlackoutDates, and retrieves all existing appointments for that date.", bullet_style))
    story.append(Paragraph("• <b>10. Dynamic Slot Rendering:</b> The engine computes non-overlapping time slots (accounting for service duration and buffer time) and returns a JSON payload. The client UI renders selectable time pills.", bullet_style))
    story.append(Paragraph("• <b>11–13. Submission & Double-Booking Prevention:</b> The client enters their design brief, deadline, meeting type, and submits the form via HTTP POST. Before committing, the server re-runs the availability algorithm to prevent race conditions. The Appointment model clean() method executes to verify time boundaries.", bullet_style))
    story.append(Paragraph("• <b>14–15. Confirmation & Calendar Payload:</b> The record is saved with status 'PENDING', generating a reference ID (DES-XXXXXX). The user is redirected to the confirmation view where an RFC-5545 iCalendar (.ics) invite is generated for download.", bullet_style))
    story.append(PageBreak())

    # ================= PAGE 7 & 8: CLASS DIAGRAM =================
    story.append(Paragraph("4. Class Diagram", h1_style))
    story.append(Paragraph(
        "The diagram below depicts the data model architecture of James Design Studio, illustrating model fields, "
        "methods, and relationships spanning authentication, scheduling, portfolio presentation, and client reviews.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Add Class Diagram Image
    story.append(RLImage("class_diagram.png", width=6.8 * inch, height=5.9 * inch))
    story.append(Paragraph("Figure 3: Class Diagram of Models and Architecture", caption_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("4.1 Description of Classes & Modules", h2_style))
    story.append(Paragraph("• <b>User (Django Built-in):</b> Django's native authentication model storing username, hashed password, email, and staff authorization flags. Acts as the root anchor for account relationships.", bullet_style))
    story.append(Paragraph("• <b>Profile:</b> Extends User via a One-to-One relationship with role designations ('customer', 'staff', 'admin'), direct phone number, and studio biography. Created automatically via Django post_save signals.", bullet_style))
    story.append(Paragraph("• <b>Service:</b> Represents a design offering (e.g. Brand Identity Suite, Event Flyer Design). Stores service duration in minutes, buffer padding time, active boolean status, and price formatted in Naira (₦).", bullet_style))
    story.append(Paragraph("• <b>WorkingHours:</b> Encapsulates daily recurring schedule blocks (days 0–6 for Monday through Sunday), start time, end time, and break periods, defining the designer's weekly availability envelope.", bullet_style))
    story.append(Paragraph("• <b>BlackoutDate:</b> Represents specific single dates or multi-day leaves during which all slot generations are blocked (e.g., public holidays, studio retreats).", bullet_style))
    story.append(Paragraph("• <b>Appointment:</b> The core transactional entity linking a client, design service, chosen date, start/end time range, design brief text, brand asset URLs, and status ('PENDING', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'). Enforces strict overlapping validation in clean().", bullet_style))
    story.append(Paragraph("• <b>PortfolioItem:</b> Manages visual gallery works, categories (Branding, Flyers, Infographics, Social Media), image assets, client names, and display ordering on the homepage 4x2 grid.", bullet_style))
    story.append(Paragraph("• <b>Review:</b> Stores client testimonials, ratings (1–5 stars), feedback comments, and featured status displayed in the studio reviews section.", bullet_style))
    story.append(Paragraph("• <b>utils.py (Availability & Calendar Engine):</b> Contains business logic functions get_available_slots() and generate_ics_content() that process calendar availability and format iCalendar exports.", bullet_style))
    story.append(PageBreak())

    # ================= PAGE 9: HOSTED LINK & DEPLOYMENT =================
    story.append(Paragraph("5. Hosted Link & Deployment Details", h1_style))
    story.append(Paragraph(
        "James Design Studio is deployed to production using a modern serverless cloud architecture on <b>Vercel</b>, "
        "integrated with a continuous deployment pipeline tracking the <b>GitHub</b> repository.",
        body_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("5.1 Production Deployment Architecture", h2_style))
    story.append(Paragraph("• <b>Cloud Platform:</b> Vercel Serverless Python 3.12 Runtime.", bullet_style))
    story.append(Paragraph("• <b>Static Asset Handling:</b> WhiteNoise middleware (whitenoise.middleware.WhiteNoiseMiddleware) with gzip/brotli compression and cached header routing.", bullet_style))
    story.append(Paragraph("• <b>Continuous Deployment (CI/CD):</b> Every commit pushed to the GitHub main branch triggers an automatic build, dependency installation, static collection, and atomic zero-downtime deployment.", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("5.2 Project Links & Credentials", h2_style))

    links_table_data = [
        [Paragraph("<b>Resource</b>", table_header_style), Paragraph("<b>Link / Value</b>", table_header_style)],
        [Paragraph("<b>Live Production URL</b>", table_bold_style), Paragraph('<a href="https://graphic-design-scheduler-roan.vercel.app"><u>https://graphic-design-scheduler-roan.vercel.app</u></a>', table_body_style)],
        [Paragraph("<b>GitHub Repository</b>", table_bold_style), Paragraph('<a href="https://github.com/joebthebest/graphic-design-scheduler"><u>https://github.com/joebthebest/graphic-design-scheduler</u></a>', table_body_style)],
        [Paragraph("<b>Google Submission Form</b>", table_bold_style), Paragraph('<a href="https://forms.gle/peLot6q8PS8qUzGU7"><u>https://forms.gle/peLot6q8PS8qUzGU7</u></a>', table_body_style)],
        [Paragraph("<b>Designer / Admin Username</b>", table_bold_style), Paragraph('<b>admin</b>', table_body_style)],
        [Paragraph("<b>Designer / Admin Password</b>", table_bold_style), Paragraph('<b>admin123</b>', table_body_style)],
        [Paragraph("<b>Designer Portal URL</b>", table_bold_style), Paragraph('<a href="https://graphic-design-scheduler-roan.vercel.app/accounts/login/"><u>https://graphic-design-scheduler-roan.vercel.app/accounts/login/</u></a>', table_body_style)],
        [Paragraph("<b>Django Admin Panel</b>", table_bold_style), Paragraph('<a href="https://graphic-design-scheduler-roan.vercel.app/admin/"><u>https://graphic-design-scheduler-roan.vercel.app/admin/</u></a>', table_body_style)],
    ]

    t_links = Table(links_table_data, colWidths=[2.2 * inch, 4.6 * inch])
    t_links.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_links)
    story.append(Spacer(1, 14))

    story.append(Paragraph("5.3 Steps to Replicate / Deploy", h2_style))
    story.append(Paragraph("1. <b>Clone Repository:</b> git clone https://github.com/joebthebest/graphic-design-scheduler.git", bullet_style))
    story.append(Paragraph("2. <b>Install Dependencies:</b> pip install -r requirements.txt", bullet_style))
    story.append(Paragraph("3. <b>Run Database Migrations:</b> python manage.py migrate", bullet_style))
    story.append(Paragraph("4. <b>Seed Initial Data:</b> python manage.py seed_data (Initializes services in ₦, working hours, portfolio artworks, and admin user).", bullet_style))
    story.append(Paragraph("5. <b>Run Automated Tests:</b> python manage.py test (Executes 7 unit tests covering models, slot algorithms, views, and security).", bullet_style))
    story.append(Paragraph("6. <b>Start Local Server:</b> python manage.py runserver 127.0.0.1:8000", bullet_style))
    story.append(Paragraph("7. <b>Deploy on Vercel:</b> Connect repository on vercel.com/new and deploy with zero additional configuration.", bullet_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated documentation PDF: {filename}")

if __name__ == '__main__':
    generate_use_case_diagram("use_case_diagram.png")
    generate_sequence_diagram("sequence_diagram.png")
    generate_class_diagram("class_diagram.png")
    generate_pdf("SEN310_Project_Documentation_James_Design_Studio.pdf")
