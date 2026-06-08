# lawyer/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from .models import Lawyer, LawyerBooking

def lawyer_portal(request):
    """Main Lawyer Portal Page - No login required"""
    lawyers = Lawyer.objects.filter(is_verified=True).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    specialization = request.GET.get('specialization', '')
    
    if search_query:
        lawyers = lawyers.filter(
            models.Q(name__icontains=search_query) |
            models.Q(specialization__icontains=search_query) |
            models.Q(cases_handled__icontains=search_query)
        )
    
    if specialization:
        lawyers = lawyers.filter(specialization=specialization)
    
    context = {
        'lawyers': lawyers,
        'specializations': Lawyer.SPECIALIZATION_CHOICES,
        'search_query': search_query,
    }
    return render(request, 'lawyer/lawyer_portal.html', context)

def create_lawyer_profile(request):
    """Create Lawyer Profile - No login required"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        degree = request.POST.get('degree')
        specialization = request.POST.get('specialization')
        experience = request.POST.get('experience')
        bio = request.POST.get('bio')
        cases_handled = request.POST.get('cases_handled')
        bar_council_id = request.POST.get('bar_council_id')
        consultation_fee = request.POST.get('consultation_fee', 500)
        certificate = request.FILES.get('certificate')
        
        # Check if bar council ID exists
        if Lawyer.objects.filter(bar_council_id=bar_council_id).exists():
            messages.error(request, 'Bar Council ID already registered!')
            return redirect('create_lawyer_profile')
        
        lawyer = Lawyer.objects.create(
            name=name,
            email=email,
            phone=phone,
            degree=degree,
            specialization=specialization,
            experience=experience,
            bio=bio,
            cases_handled=cases_handled,
            bar_council_id=bar_council_id,
            consultation_fee=consultation_fee,
            is_verified=True  # Admin will verify
        )
        
        if certificate:
            lawyer.certificate = certificate
            lawyer.save()
        
        messages.success(request, f'Lawyer profile created for {name}! Admin will verify soon.')
        return redirect('lawyer_portal')
    
    return render(request, 'lawyer/create_lawyer_profile.html')

def lawyer_detail(request, lawyer_id):
    """Lawyer Detail Page with Booking - No login required"""
    lawyer = get_object_or_404(Lawyer, id=lawyer_id, is_verified=True)
    
    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')
        case_type = request.POST.get('case_type')
        case_description = request.POST.get('case_description')
        preferred_date = request.POST.get('preferred_date')
        
        booking = LawyerBooking.objects.create(
            lawyer=lawyer,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            case_type=case_type,
            case_description=case_description,
            preferred_date=preferred_date or None
        )
        
        messages.success(request, f'Booking request sent to {lawyer.name}!')
        return redirect('lawyer_detail', lawyer_id=lawyer_id)
    
    context = {
        'lawyer': lawyer,
        'specializations': Lawyer.SPECIALIZATION_CHOICES,
    }
    return render(request, 'lawyer/lawyer_detail.html', context)