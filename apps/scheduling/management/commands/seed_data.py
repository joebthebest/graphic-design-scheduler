from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, time, timedelta
from apps.scheduling.models import Service, PortfolioItem, WorkingHours, Appointment, Review, BlackoutDate


class Command(BaseCommand):
    help = "Seeds initial graphic design services, user portfolio samples, working hours, and demonstration appointments"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("[+] Seeding Graphic Design Scheduling Database..."))

        # 1. Create Superuser / Studio Owner
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "jamesemmaedeh@gmail.com", "admin123")
            self.stdout.write(self.style.SUCCESS("[OK] Created Superuser: admin (Password: admin123)"))
        else:
            User.objects.filter(username="admin").update(email="jamesemmaedeh@gmail.com")
            self.stdout.write(self.style.WARNING("[!] Superuser 'admin' email updated to jamesemmaedeh@gmail.com."))

        # 2. Setup Working Hours
        WorkingHours.objects.all().delete()
        default_hours = [
            (0, time(9, 0), time(18, 0), time(13, 0), time(14, 0), False),  # Monday
            (1, time(9, 0), time(18, 0), time(13, 0), time(14, 0), False),  # Tuesday
            (2, time(9, 0), time(18, 0), time(13, 0), time(14, 0), False),  # Wednesday
            (3, time(9, 0), time(18, 0), time(13, 0), time(14, 0), False),  # Thursday
            (4, time(9, 0), time(18, 0), time(13, 0), time(14, 0), False),  # Friday
            (5, time(10, 0), time(15, 0), None, None, False),                # Saturday
            (6, time(9, 0), time(17, 0), None, None, True),                 # Sunday (OFF)
        ]
        for day, start, end, b_start, b_end, is_off in default_hours:
            WorkingHours.objects.create(
                day_of_week=day,
                start_time=start,
                end_time=end,
                break_start=b_start,
                break_end=b_end,
                is_off=is_off
            )
        self.stdout.write(self.style.SUCCESS("[OK] Initialized weekly working hours (Mon-Sat)."))

        # 3. Setup Graphic Design Services
        services_data = [
            {
                'name': 'Brand Identity & Logo Suite',
                'slug': 'brand-identity-logo-suite',
                'category': 'branding',
                'tagline': 'Distinctive, memorable visual identity designed to scale your business.',
                'description': 'Complete brand identity including primary logos, color palette, typography guidelines, and vector source files.',
                'deliverables': 'Primary, Secondary & Sub-mark Logo Variations\nVector Master Files (.AI, .EPS, .SVG, .PDF, .PNG)\nColor Palette & Typography Styling Guide\nBrand Style Guide Book (PDF)\nSocial Media Favicon & Avatar Pack\n3 Revision Rounds & Full Commercial Copyright Ownership',
                'duration_minutes': 60,
                'buffer_minutes': 15,
                'price': 150000.00,
                'currency': '₦',
                'turnaround_time': '5-7 Business Days',
                'badge_text': 'Most Popular',
                'icon': 'sparkles',
                'gradient': 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                'order': 1,
            },
            {
                'name': 'High-Impact Event Flyer & Poster',
                'slug': 'event-flyer-poster-design',
                'category': 'flyers',
                'tagline': 'Eye-catching, crowd-pulling event, club, food, and corporate flyers.',
                'description': 'Striking event, club, food, and corporate promotional flyers optimized for print and social feeds.',
                'deliverables': 'High-Resolution 300 DPI CMYK Print-Ready PDF\nOptimized RGB Digital Versions (Instagram Post & Story sizes)\nEditable Source File (.PSD with organized layers)\n3D Realistic Mockup Preview\n2 Custom Concept Directions\nFast 48-Hour Turnaround',
                'duration_minutes': 45,
                'buffer_minutes': 15,
                'price': 45000.00,
                'currency': '₦',
                'turnaround_time': '2-3 Business Days',
                'badge_text': 'Fast Turnaround',
                'icon': 'layers',
                'gradient': 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
                'order': 2,
            },
            {
                'name': 'Social Media & Content Growth Pack',
                'slug': 'social-media-content-pack',
                'category': 'social',
                'tagline': 'Consistent, cohesive graphic assets for Instagram, LinkedIn, and X.',
                'description': 'Custom feed posts, matching story templates, and editable assets to elevate your brand presence.',
                'deliverables': '10 Custom Designed Feed Posts & Carousels\n5 Matching Story Templates\nCustom Highlight Icons & Banner\nEditable Photoshop / Canva Templates\nCopy & Visual Layout Optimization Guide',
                'duration_minutes': 45,
                'buffer_minutes': 15,
                'price': 75000.00,
                'currency': '₦',
                'turnaround_time': '3-5 Business Days',
                'badge_text': 'High Engagement',
                'icon': 'share-2',
                'gradient': 'linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)',
                'order': 3,
            },
            {
                'name': 'Infographics & Corporate Deck Design',
                'slug': 'infographics-corporate-deck',
                'category': 'infographics',
                'tagline': 'Turn complex data and business insights into clear, compelling visuals.',
                'description': 'Clear data visualizations, reports, and pitch deck presentations crafted from complex insights.',
                'deliverables': 'Custom Vector Data Visualizations & Charts\nStructured Information Hierarchy & Flow\nHigh-Resolution Print & Web Export Formats\nPowerPoint / Keynote / PDF Slide Deck Integration\nVector Icon Set & Source Files Included',
                'duration_minutes': 60,
                'buffer_minutes': 15,
                'price': 95000.00,
                'currency': '₦',
                'turnaround_time': '4-6 Business Days',
                'badge_text': 'Executive Standard',
                'icon': 'bar-chart-3',
                'gradient': 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
                'order': 4,
            },
            {
                'name': 'Political & Campaign Publicity Suite',
                'slug': 'political-campaign-publicity',
                'category': 'flyers',
                'tagline': 'Inspiring, authoritative campaign materials that resonate with voters.',
                'description': 'Posters, billboards, and social campaign banners engineered for high-visibility public elections.',
                'deliverables': 'Candidate Posters (A1, A2, A3 Print formats)\nDigital Campaign Banners (WhatsApp / Twitter / Meta)\nBillboard & Rollup Banner Layouts\nEndorsement & Manifesto Graphics\nUrgent 24-48 Hour Turnaround Available',
                'duration_minutes': 45,
                'buffer_minutes': 15,
                'price': 80000.00,
                'currency': '₦',
                'turnaround_time': '2-3 Business Days',
                'badge_text': 'High Impact',
                'icon': 'award',
                'gradient': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                'order': 5,
            },
            {
                'name': '1-on-1 Design Consultation & Visual Audit',
                'slug': 'design-consultation-visual-audit',
                'category': 'consultation',
                'tagline': 'Direct strategic consultation, screen-share audit, and creative roadmap.',
                'description': 'Live 45-minute video consultation, design critique, and strategic visual action plan.',
                'deliverables': '45-Minute Live Interactive Video Consultation\nLive Screen-Share Brand & Portfolio Audit\nColor Harmony & Typography Critique\nActionable 5-Point Design Roadmap (PDF Summary)\nSession Video Recording & Resource Links',
                'duration_minutes': 45,
                'buffer_minutes': 15,
                'price': 35000.00,
                'currency': '₦',
                'turnaround_time': 'Immediate Session',
                'badge_text': 'Quick Advice',
                'icon': 'video',
                'gradient': 'linear-gradient(135deg, #f43f5e 0%, #fb923c 100%)',
                'order': 6,
            }
        ]

        services_dict = {}
        for s_data in services_data:
            s_obj, created = Service.objects.update_or_create(slug=s_data['slug'], defaults=s_data)
            services_dict[s_data['slug']] = s_obj

        self.stdout.write(self.style.SUCCESS(f"[OK] Created {len(services_data)} graphic design services."))

        # 4. Setup Portfolio Items (Linking to copied user designs!)
        PortfolioItem.objects.all().delete()
        portfolio_data = [
            {
                'title': 'Clash of Crowns - Gaming & Event Poster',
                'slug': 'clash-of-crowns-event',
                'category': 'flyers',
                'client_name': 'Royale Esports & Events',
                'description': 'A vibrant, cinematic event poster designed for a premiere competitive gaming championship.',
                'static_image_path': 'images/portfolio/clash_of_crowns.png',
                'related_service': services_dict.get('event-flyer-poster-design'),
                'tools_used': 'Adobe Photoshop, Adobe Illustrator',
                'is_featured': True,
                'order': 1,
            },
            {
                'title': 'DAWN Infographic - Data & Health Visuals',
                'slug': 'dawn-infographic-report',
                'category': 'infographics',
                'client_name': 'DAWN Healthcare Research',
                'description': 'A comprehensive data infographic breaking down complex health metrics and patient outcomes.',
                'static_image_path': 'images/portfolio/dawn_infographic.png',
                'related_service': services_dict.get('infographics-corporate-deck'),
                'tools_used': 'Adobe Illustrator, Figma',
                'is_featured': True,
                'order': 2,
            },
            {
                'title': 'Grill & Groove - Food & Music Flyer',
                'slug': 'grill-and-groove-flyer',
                'category': 'flyers',
                'client_name': 'The Backyard Bistro & Lounge',
                'description': 'Dynamic promotional graphics blending seafood photography and sizzling grill aesthetics.',
                'static_image_path': 'images/portfolio/grill_and_groove.png',
                'related_service': services_dict.get('event-flyer-poster-design'),
                'tools_used': 'Adobe Photoshop, Lightroom',
                'is_featured': True,
                'order': 3,
            },
            {
                'title': 'NailedByDee - Luxury Brand Identity',
                'slug': 'nailedbydee-brand-identity',
                'category': 'branding',
                'client_name': 'NailedByDee Luxury Studio',
                'description': 'Minimalist, high-end branding for an upscale beauty and nail boutique.',
                'static_image_path': 'images/portfolio/nailedbydee_brand.png',
                'related_service': services_dict.get('brand-identity-logo-suite'),
                'tools_used': 'Adobe Illustrator, Figma',
                'is_featured': True,
                'order': 4,
            },
            {
                'title': 'NailedByDee - Promo & Price Menu',
                'slug': 'nailedbydee-promo-menu',
                'category': 'social',
                'client_name': 'NailedByDee Studio',
                'description': 'Sophisticated promotional social flyer and service menu cards with clean typography.',
                'static_image_path': 'images/portfolio/nailedbydee_promo.jpg',
                'related_service': services_dict.get('social-media-content-pack'),
                'tools_used': 'Adobe Photoshop, Illustrator',
                'is_featured': True,
                'order': 5,
            },
            {
                'title': 'ORJI BOND - Civic Campaign Poster',
                'slug': 'orji-bond-campaign',
                'category': 'flyers',
                'client_name': 'Orji Bond Campaign Organization',
                'description': 'Authoritative campaign publicity poster featuring dynamic lighting and bold messaging.',
                'static_image_path': 'images/portfolio/orji_bond_vote.png',
                'related_service': services_dict.get('political-campaign-publicity'),
                'tools_used': 'Adobe Photoshop, CorelDRAW',
                'is_featured': True,
                'order': 6,
            },
            {
                'title': 'Exam Prep - Academic Bootcamp Flyer',
                'slug': 'exam-prep-bootcamp-flyer',
                'category': 'flyers',
                'client_name': 'Apex Academic Academy',
                'description': 'High-clarity educational flyer structured with clear dates, course highlights, and instructor credentials.',
                'static_image_path': 'images/portfolio/exam_prep.jpg',
                'related_service': services_dict.get('event-flyer-poster-design'),
                'tools_used': 'Adobe Photoshop, InDesign',
                'is_featured': True,
                'order': 7,
            },
            {
                'title': 'Welcome to November - Creative Promo',
                'slug': 'welcome-november-creative',
                'category': 'social',
                'client_name': 'James Creative Studio',
                'description': 'Artistic monthly kickoff visual with autumn color palettes and custom 3D typography.',
                'static_image_path': 'images/portfolio/welcome_november.png',
                'related_service': services_dict.get('social-media-content-pack'),
                'tools_used': 'Photoshop Digital Painting',
                'is_featured': True,
                'order': 8,
            },
        ]

        for p_data in portfolio_data:
            PortfolioItem.objects.create(**p_data)

        self.stdout.write(self.style.SUCCESS(f"[OK] Linked {len(portfolio_data)} sample portfolio items with real images."))

        # 5. Create Sample Appointments & Reviews
        today = timezone.localdate()
        
        sample_appointments = [
            {
                'booking_reference': 'DES-102938',
                'service': services_dict.get('brand-identity-logo-suite'),
                'client_name': 'Dee Adebayo',
                'client_email': 'dee@nailedbydee.com',
                'client_phone': '+234 802 918 2736',
                'company_or_brand': 'NailedByDee Luxury Beauty',
                'design_brief': 'We need a luxury rebranding with nude and rose-gold palettes, minimalist sub-marks, and price lists.',
                'brand_assets_link': 'https://pinterest.com/nailedbydee/luxury-aesthetic',
                'target_deadline': today - timedelta(days=5),
                'appointment_date': today - timedelta(days=12),
                'start_time': time(10, 0),
                'end_time': time(11, 0),
                'meeting_type': 'GOOGLE_MEET',
                'meeting_link': 'https://meet.google.com/apx-dsgn-ses',
                'status': 'COMPLETED',
                'designer_notes': 'Delivered full logo suite and social templates. Client was thrilled with the nude color palette.',
            },
            {
                'booking_reference': 'DES-482910',
                'service': services_dict.get('event-flyer-poster-design'),
                'client_name': 'Chef Tunde',
                'client_email': 'tunde@backyardgrill.ng',
                'client_phone': '+234 813 456 7890',
                'company_or_brand': 'Backyard Grill & Lounge',
                'design_brief': 'Need an appetizing, high-energy flyer for our Grill & Groove weekend party featuring catfish and DJ lineup.',
                'brand_assets_link': 'https://drive.google.com/drive/folders/sample-food-photos',
                'target_deadline': today - timedelta(days=2),
                'appointment_date': today - timedelta(days=6),
                'start_time': time(14, 0),
                'end_time': time(14, 45),
                'meeting_type': 'ZOOM',
                'meeting_link': 'https://zoom.us/j/9823748291',
                'status': 'COMPLETED',
                'designer_notes': 'Delivered 300DPI print and Instagram sizes in 24 hours.',
            },
            {
                'booking_reference': 'DES-772914',
                'service': services_dict.get('infographics-corporate-deck'),
                'client_name': 'Dr. Kemi Balogun',
                'client_email': 'kemi@dawnresearch.org',
                'client_phone': '+234 809 112 2334',
                'company_or_brand': 'DAWN Health Research',
                'design_brief': 'We need a 5-page clinical data infographic explaining healthcare accessibility metrics for publication.',
                'brand_assets_link': 'https://drive.google.com/file/d/dawn-report-draft',
                'target_deadline': today + timedelta(days=8),
                'appointment_date': today + timedelta(days=1),
                'start_time': time(11, 0),
                'end_time': time(12, 0),
                'meeting_type': 'GOOGLE_MEET',
                'meeting_link': 'https://meet.google.com/apx-dsgn-ses',
                'status': 'CONFIRMED',
                'designer_notes': 'Prepare medical vector charts and palette suggestions.',
            },
            {
                'booking_reference': 'DES-892104',
                'service': services_dict.get('political-campaign-publicity'),
                'client_name': 'Hon. Orji Bond Committee',
                'client_email': 'campaign@orjibond.org',
                'client_phone': '+234 803 999 8888',
                'company_or_brand': 'Orji Bond for Council',
                'design_brief': 'Campaign billboard artwork and digital flyers with high contrast portrait retouching.',
                'brand_assets_link': 'https://drive.google.com/drive/folders/candidate-portraits',
                'target_deadline': today + timedelta(days=4),
                'appointment_date': today + timedelta(days=2),
                'start_time': time(15, 0),
                'end_time': time(15, 45),
                'meeting_type': 'STUDIO',
                'meeting_link': 'James Studio - Suite 4B Victoria Island, Lagos',
                'status': 'IN_PROGRESS',
                'designer_notes': 'Candidate portrait retouched; working on typography options.',
            },
            {
                'booking_reference': 'DES-339201',
                'service': services_dict.get('social-media-content-pack'),
                'client_name': 'Samuel Croft',
                'client_email': 'sam@royaleesports.gg',
                'client_phone': '+1 415 555 0192',
                'company_or_brand': 'Clash of Crowns Esports',
                'design_brief': 'Clash tournament announcement graphics and bracket templates for Discord and Twitter.',
                'brand_assets_link': 'https://figma.com/@royale-tournament',
                'target_deadline': today + timedelta(days=10),
                'appointment_date': today + timedelta(days=3),
                'start_time': time(16, 0),
                'end_time': time(16, 45),
                'meeting_type': 'GOOGLE_MEET',
                'meeting_link': 'https://meet.google.com/apx-dsgn-ses',
                'status': 'PENDING',
                'designer_notes': 'Pending initial brief discussion.',
            }
        ]

        for a_data in sample_appointments:
            appt, _ = Appointment.objects.update_or_create(
                booking_reference=a_data['booking_reference'],
                defaults=a_data
            )

        # 6. Add Reviews
        Review.objects.all().delete()
        reviews_data = [
            {
                'client_name': 'Orji Bond',
                'client_role': 'Campaign Organization',
                'service_name': 'Campaign Publicity Suite',
                'rating': 5,
                'comment': 'Top-notch turn-around time. The billboard posters and digital campaign materials gave our candidate an undeniable presence across all media channels.',
                'is_featured': True,
            },
            {
                'client_name': 'DAWN',
                'client_role': 'Healthcare Research',
                'service_name': 'Infographics & Corporate Visuals',
                'rating': 5,
                'comment': 'Extremely professional and punctual. The infographic communicated dense epidemiological data in such an intuitive, beautiful format for our board presentation.',
                'is_featured': True,
            },
            {
                'client_name': "Kala's Kitchen",
                'client_role': 'The Backyard Grill',
                'service_name': 'Event Flyer & Poster Design',
                'rating': 5,
                'comment': 'The Grill & Groove flyer had everyone talking! We sold out our event within 48 hours of posting. James’ attention to detail and color mastery is unmatched.',
                'is_featured': True,
            }
        ]

        for r_data in reviews_data:
            Review.objects.create(**r_data)

        self.stdout.write(self.style.SUCCESS("[OK] Seeded realistic client appointments and reviews."))
        self.stdout.write(self.style.SUCCESS("[OK] Graphic Design Scheduling Database seeding completed successfully!"))

