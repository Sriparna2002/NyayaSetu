from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Complaint, PasswordReset
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('register')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'auth/register.html')

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('login')
    
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'dashboard.html')

@login_required(login_url='login')
def admin_dashboard_view(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('dashboard')
    return render(request, 'admin_dashboard.html')

# ==================== CITIZEN API VIEWS ====================

@login_required
def submit_complaint(request):
    if request.method == 'POST':
        try:
            category = request.POST.get('category')
            priority = request.POST.get('priority')
            description = request.POST.get('description')
            phone = request.POST.get('phone')
            evidence_data = request.POST.get('evidence_data')
            evidence_name = request.POST.get('evidence_name')
            nearest_police_station = request.POST.get('nearest_police_station', '')
            # Save phone to session
            if phone:
                request.session['user_phone'] = phone
            
            # Create complaint in database
            complaint = Complaint(
                user=request.user,
                category=category,
                priority=priority,
                description=description,
                nearest_police_station=nearest_police_station,
            )
            
            if evidence_data and evidence_name:
                complaint.evidence = evidence_data
                complaint.evidence_name = evidence_name
            
            complaint.save()
            
            return JsonResponse({
                'success': True,
                'complaint_id': complaint.complaint_id,
                'message': f'Complaint {complaint.complaint_id} submitted successfully!'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def get_complaints(request):
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    complaints_list = []
    for c in complaints:
        complaints_list.append({
            'id': c.complaint_id,
            'category': c.category,
            'priority': c.priority,
            'description': c.description,
            'date': c.created_at.strftime("%B %d, %Y at %I:%M %p"),
            'status': c.status,
            'has_evidence': bool(c.evidence),
            'evidence_name': c.evidence_name or ''
        })
    return JsonResponse({'complaints': complaints_list})

@login_required
def get_stats(request):
    complaints = Complaint.objects.filter(user=request.user)
    total = complaints.count()
    pending = complaints.filter(status__in=['Pending', 'Under Review', 'In Progress']).count()
    resolved = complaints.filter(status='Resolved').count()
    return JsonResponse({
        'total': total,
        'pending': pending,
        'resolved': resolved
    })

@login_required
def get_user_profile(request):
    phone = request.session.get('user_phone', '')
    return JsonResponse({
        'username': request.user.username,
        'email': request.user.email,
        'phone': phone,
        'member_since': request.user.date_joined.strftime("%B %d, %Y")
    })

@login_required
def update_phone(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        request.session['user_phone'] = phone
        return JsonResponse({'success': True, 'message': 'Phone updated successfully'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

# ==================== ADMIN API VIEWS ====================

@login_required
def admin_get_all_complaints(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    complaints = Complaint.objects.all().order_by('-created_at')
    complaints_list = []
    for c in complaints:
        complaints_list.append({
            'id': c.complaint_id,
            'user': c.user.username,
            'user_email': c.user.email,
            'category': c.category,
            'priority': c.priority,
            'description': c.description[:200],
            'date': c.created_at.strftime("%B %d, %Y at %I:%M %p"),
            'status': c.status,
            'has_evidence': bool(c.evidence),
            'assigned_to': c.assigned_to.username if c.assigned_to else 'Unassigned'
        })
    return JsonResponse({'complaints': complaints_list})

@login_required
def admin_update_status(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        new_status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')
        
        try:
            complaint = Complaint.objects.get(complaint_id=complaint_id)
            complaint.status = new_status
            if remarks:
                complaint.remarks = remarks
            complaint.save()
            return JsonResponse({'success': True, 'message': 'Status updated successfully'})
        except Complaint.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Complaint not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def admin_get_stats(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    total = Complaint.objects.count()
    pending = Complaint.objects.filter(status__in=['Pending', 'Under Review', 'In Progress']).count()
    resolved = Complaint.objects.filter(status='Resolved').count()
    urgent = Complaint.objects.filter(priority='Urgent', status__in=['Pending', 'Under Review', 'In Progress']).count()
    
    status_counts = {}
    for status in ['Pending', 'Under Review', 'In Progress', 'Resolved', 'Rejected']:
        status_counts[status] = Complaint.objects.filter(status=status).count()
    
    priority_counts = {}
    for priority in ['Low', 'Medium', 'Urgent']:
        priority_counts[priority] = Complaint.objects.filter(priority=priority).count()
    
    return JsonResponse({
        'total': total,
        'pending': pending,
        'resolved': resolved,
        'urgent': urgent,
        'status_counts': status_counts,
        'priority_counts': priority_counts
    })

@login_required
def admin_get_complaint_detail(request, complaint_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    try:
        complaint = Complaint.objects.get(complaint_id=complaint_id)
        data = {
            'id': complaint.complaint_id,
            'user': complaint.user.username,
            'user_email': complaint.user.email,
            'category': complaint.category,
            'priority': complaint.priority,
            'description': complaint.description,
            'date': complaint.created_at.strftime("%B %d, %Y at %I:%M %p"),
            'status': complaint.status,
            'has_evidence': bool(complaint.evidence),
            'evidence_name': complaint.evidence_name or '',
            'assigned_to': complaint.assigned_to.username if complaint.assigned_to else 'Unassigned',
            'remarks': complaint.remarks or ''
        }
        return JsonResponse({'success': True, 'complaint': data})
    except Complaint.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Complaint not found'})

@login_required
def admin_assign_officer(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        officer_name = request.POST.get('officer_name')
        
        try:
            complaint = Complaint.objects.get(complaint_id=complaint_id)
            officer = User.objects.filter(username=officer_name).first()
            if officer:
                complaint.assigned_to = officer
                complaint.save()
                return JsonResponse({'success': True, 'message': f'Case assigned to {officer_name}'})
            else:
                return JsonResponse({'success': False, 'message': 'Officer not found'})
        except Complaint.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Complaint not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def admin_get_officers(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    officers = User.objects.filter(is_staff=True) | User.objects.filter(is_superuser=True)
    officers_list = [{'username': o.username, 'email': o.email} for o in officers]
    return JsonResponse({'officers': officers_list})


# ==================== PASSWORD RESET VIEWS (Citizen) ====================

def forgot_password_view(request):
    """Citizen: Generate a one-time password reset link and show it on screen."""
    reset_link = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
            # Invalidate previous unused tokens
            PasswordReset.objects.filter(user=user, is_used=False).update(is_used=True)
            # Create a fresh token
            reset_obj = PasswordReset.objects.create(user=user)
            token = reset_obj.token
            reset_link = request.build_absolute_uri(f'/auth/reset-password/{token}/')
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address.')
    return render(request, 'auth/forgot_password.html', {'reset_link': reset_link})


def reset_password_view(request, token):
    """Citizen: Validate the token and allow the user to set a new password."""
    try:
        reset_obj = PasswordReset.objects.get(token=token, is_used=False)
    except PasswordReset.DoesNotExist:
        messages.error(request, 'This password reset link is invalid or has already been used.')
        return redirect('login')

    if reset_obj.is_expired():
        messages.error(request, 'This password reset link has expired. Please request a new one.')
        return redirect('forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            user = reset_obj.user
            user.set_password(new_password)
            user.save()
            reset_obj.is_used = True
            reset_obj.save()
            messages.success(request, 'Password reset successful! Please log in with your new password.')
            return redirect('login')

    return render(request, 'auth/reset_password.html', {'token': token})