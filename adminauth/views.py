# adminauth/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from userauth.models import Complaint, PasswordReset
from lawyer.models import Lawyer  # Lawyer model যোগ করুন
import json

def is_admin(user):
    return user.is_superuser or user.is_staff

def admin_login(request):
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and is_admin(user):
            login(request, user)
            messages.success(request, f'Welcome back, Admin {username}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or you are not authorized as admin!')
            return redirect('admin_login')
    
    return render(request, 'admin_auth/admin_login.html')

def admin_register(request):
    ADMIN_SECRET_KEY = 'NyayaSetu@2026'
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        admin_key = request.POST.get('admin_key', '')
        
        if admin_key != ADMIN_SECRET_KEY:
            messages.error(request, 'Invalid admin registration key!')
            return redirect('admin_register')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('admin_register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('admin_register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('admin_register')
        
        user = User.objects.create_superuser(username=username, email=email, password=password)
        user.save()
        
        messages.success(request, 'Admin account created successfully! Please login.')
        return redirect('admin_login')
    
    return render(request, 'admin_auth/admin_register.html')

def admin_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('admin_login')

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_dashboard(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    
    total_complaints = complaints.count()
    pending_complaints = complaints.filter(status__in=['Pending', 'Under Review', 'In Progress']).count()
    resolved_complaints = complaints.filter(status='Resolved').count()
    urgent_complaints = complaints.filter(priority='Urgent', status__in=['Pending', 'Under Review', 'In Progress']).count()
    
    status_counts = {
        'Pending': complaints.filter(status='Pending').count(),
        'Under Review': complaints.filter(status='Under Review').count(),
        'In Progress': complaints.filter(status='In Progress').count(),
        'Resolved': complaints.filter(status='Resolved').count(),
        'Rejected': complaints.filter(status='Rejected').count(),
    }
    
    priority_counts = {
        'Low': complaints.filter(priority='Low').count(),
        'Medium': complaints.filter(priority='Medium').count(),
        'Urgent': complaints.filter(priority='Urgent').count(),
    }
    
    officers = User.objects.filter(is_staff=True) | User.objects.filter(is_superuser=True)
    
    context = {
        'complaints': complaints,
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'urgent_complaints': urgent_complaints,
        'status_counts': status_counts,
        'priority_counts': priority_counts,
        'officers': officers,
    }
    
    return render(request, 'admin_dashboard.html', context)

# ==================== Admin Lawyer Views ====================

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_lawyer_list(request):
    """Admin can view all lawyers"""
    lawyers = Lawyer.objects.all().order_by('-created_at')
    return render(request, 'admin_lawyer_list.html', {'lawyers': lawyers})

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_lawyer_verify(request, lawyer_id):
    """Admin can verify lawyers"""
    if request.method == 'POST':
        lawyer = Lawyer.objects.get(id=lawyer_id)
        lawyer.is_verified = True
        lawyer.save()
        messages.success(request, f'Lawyer {lawyer.name} verified successfully!')
        return redirect('admin_lawyer_list')
    return redirect('admin_lawyer_list')

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_lawyer_delete(request, lawyer_id):
    """Admin can delete lawyers"""
    if request.method == 'POST':
        lawyer = Lawyer.objects.get(id=lawyer_id)
        lawyer_name = lawyer.name
        lawyer.delete()
        messages.success(request, f'Lawyer {lawyer_name} deleted successfully!')
        return redirect('admin_lawyer_list')
    return redirect('admin_lawyer_list')

# ==================== API Views ====================

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def get_all_complaints(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    complaints_list = []
    for c in complaints:
        complaints_list.append({
            'id': c.complaint_id,
            'user': c.user.username,
            'user_email': c.user.email,
            'category': c.category,
            'nearest_police_station': c.nearest_police_station if hasattr(c, 'nearest_police_station') and c.nearest_police_station else 'Not specified',
            'priority': c.priority,
            'description': c.description[:200] if len(c.description) > 200 else c.description,
            'date': c.created_at.strftime("%B %d, %Y at %I:%M %p"),
            'status': c.status,
            'assigned_to': c.assigned_to.username if c.assigned_to else 'Unassigned',
            'remarks': c.remarks if c.remarks else '',
        })
    return JsonResponse({'complaints': complaints_list})

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def update_complaint_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            complaint_id = data.get('complaint_id')
            new_status = data.get('status')
            remarks = data.get('remarks', '')
            
            complaint = Complaint.objects.get(complaint_id=complaint_id)
            complaint.status = new_status
            if remarks:
                complaint.remarks = remarks
            complaint.save()
            return JsonResponse({'success': True, 'message': 'Status updated successfully'})
        except Complaint.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Complaint not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def assign_officer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            complaint_id = data.get('complaint_id')
            officer_name = data.get('officer_name')
            
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

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def get_admin_stats(request):
    complaints = Complaint.objects.all()
    total = complaints.count()
    pending = complaints.filter(status__in=['Pending', 'Under Review', 'In Progress']).count()
    resolved = complaints.filter(status='Resolved').count()
    urgent = complaints.filter(priority='Urgent', status__in=['Pending', 'Under Review', 'In Progress']).count()
    
    status_counts = {}
    for status in ['Pending', 'Under Review', 'In Progress', 'Resolved', 'Rejected']:
        status_counts[status] = complaints.filter(status=status).count()
    
    priority_counts = {}
    for priority in ['Low', 'Medium', 'Urgent']:
        priority_counts[priority] = complaints.filter(priority=priority).count()
    
    return JsonResponse({
        'total': total,
        'pending': pending,
        'resolved': resolved,
        'urgent': urgent,
        'status_counts': status_counts,
        'priority_counts': priority_counts
    })

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def get_officers(request):
    officers = User.objects.filter(is_staff=True) | User.objects.filter(is_superuser=True)
    officers_list = [{'username': o.username, 'email': o.email} for o in officers]
    return JsonResponse({'officers': officers_list})

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def get_complaint_detail(request, complaint_id):
    try:
        complaint = Complaint.objects.get(complaint_id=complaint_id)
        data = {
            'id': complaint.complaint_id,
            'user': complaint.user.username,
            'user_email': complaint.user.email,
            'category': complaint.category,
            'nearest_police_station': complaint.nearest_police_station if hasattr(complaint, 'nearest_police_station') and complaint.nearest_police_station else 'Not specified',
            'priority': complaint.priority,
            'description': complaint.description,
            'date': complaint.created_at.strftime("%B %d, %Y at %I:%M %p"),
            'status': complaint.status,
            'assigned_to': complaint.assigned_to.username if complaint.assigned_to else 'Unassigned',
            'remarks': complaint.remarks if complaint.remarks else '',
        }
        return JsonResponse({'success': True, 'complaint': data})
    except Complaint.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Complaint not found'})


# ==================== PASSWORD RESET VIEWS (Admin) ====================

def admin_forgot_password(request):
    """Admin: Generate a one-time password reset link and show it on screen."""
    reset_link = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
            if not (user.is_superuser or user.is_staff):
                messages.error(request, 'No admin account found with that email address.')
            else:
                # Invalidate previous unused tokens
                PasswordReset.objects.filter(user=user, is_used=False).update(is_used=True)
                # Create a fresh token
                reset_obj = PasswordReset.objects.create(user=user)
                token = reset_obj.token
                reset_link = request.build_absolute_uri(f'/admin-dashboard/reset-password/{token}/')
        except User.DoesNotExist:
            messages.error(request, 'No admin account found with that email address.')
    return render(request, 'admin_auth/admin_forgot_password.html', {'reset_link': reset_link})


def admin_reset_password(request, token):
    """Admin: Validate the token and allow setting a new password."""
    try:
        reset_obj = PasswordReset.objects.get(token=token, is_used=False)
    except PasswordReset.DoesNotExist:
        messages.error(request, 'This password reset link is invalid or has already been used.')
        return redirect('admin_login')

    if reset_obj.is_expired():
        messages.error(request, 'This password reset link has expired. Please request a new one.')
        return redirect('admin_forgot_password')

    # Verify it belongs to an admin
    if not (reset_obj.user.is_superuser or reset_obj.user.is_staff):
        messages.error(request, 'Unauthorized reset attempt.')
        return redirect('admin_login')

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
            messages.success(request, 'Admin password reset successful! Please log in.')
            return redirect('admin_login')

    return render(request, 'admin_auth/admin_reset_password.html', {'token': token})