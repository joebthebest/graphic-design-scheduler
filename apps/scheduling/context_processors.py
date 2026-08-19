def business_info(request):
    """
    Supplies consistent studio branding, contact info, and theme defaults across templates.
    """
    return {
        'STUDIO_NAME': 'James Design Studio',
        'STUDIO_TAGLINE': 'Visual identity, flyers & art direction for ambitious brands',
        'STUDIO_EMAIL': 'jamesemmaedeh@gmail.com',
        'STUDIO_PHONE': '+234 810 940 8368',
        'STUDIO_LOCATION': 'Remote Worldwide',
        'STUDIO_EXPERIENCE': '6+ Years Experience',
        'STUDIO_PROJECTS_COUNT': '150+ Projects Completed',
        'STUDIO_RATING': '4.9/5.0 Client Satisfaction',
    }
