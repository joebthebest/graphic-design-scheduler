from django.shortcuts import render, redirect
from django.contrib import messages
from apps.scheduling.models import Service, PortfolioItem, Review, Appointment
from django.utils import timezone


def home_view(request):
    """
    Landing page showcasing the Graphic Design Studio:
    - Hero section with live booking CTA
    - Interactive Portfolio Grid with real designs
    - Service Packages
    - Workflow / Design Process
    - Client Testimonials & Stats
    """
    services = Service.objects.filter(is_active=True).order_by('order', 'price')
    portfolio_items = PortfolioItem.objects.filter(is_featured=True).order_by('order')
    reviews = Review.objects.filter(is_featured=True).order_by('-created_at')[:6]
    
    # Calculate studio metrics
    total_appointments_count = Appointment.objects.count()
    completed_projects_count = Appointment.objects.filter(status='COMPLETED').count() + 148 # baseline + dynamic

    context = {
        'services': services,
        'portfolio_items': portfolio_items,
        'reviews': reviews,
        'completed_projects_count': completed_projects_count,
        'services_count': services.count(),
    }
    return render(request, 'core/index.html', context)


def portfolio_view(request):
    """
    Comprehensive design showcase with interactive category filtering and lightbox modal.
    """
    category = request.GET.get('category', 'all')
    if category != 'all':
        portfolio_items = PortfolioItem.objects.filter(category=category).order_by('order')
    else:
        portfolio_items = PortfolioItem.objects.all().order_by('order')

    categories = [
        ('all', 'All Works'),
        ('branding', 'Brand Identity & Logos'),
        ('flyers', 'Flyers & Event Posters'),
        ('infographics', 'Infographics & Data'),
        ('social', 'Social Media & Creatives'),
    ]

    context = {
        'portfolio_items': portfolio_items,
        'selected_category': category,
        'categories': categories,
    }
    return render(request, 'core/portfolio.html', context)


def services_view(request):
    """
    Services and Pricing breakdown page.
    """
    services = Service.objects.filter(is_active=True).order_by('order', 'price')
    context = {'services': services}
    return render(request, 'core/services.html', context)


def about_view(request):
    """
    Designer bio, studio methodology, software stack, and credentials.
    """
    reviews = Review.objects.filter(is_featured=True)[:4]
    context = {'reviews': reviews}
    return render(request, 'core/about.html', context)


from .models import ContactInquiry


def contact_view(request):
    """
    Studio contact and general design inquiry page.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            inquiry = ContactInquiry.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject or 'General Design Inquiry',
                message=message
            )
            messages.success(request, f"🎉 Thank you {name}! Your inquiry has been received. James Design Studio will reply to {email} shortly.")
        else:
            messages.error(request, "Please fill in all required fields (Name, Email, Message).")

        return redirect('contact')

    return render(request, 'core/contact.html')
