from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Room, Gallery, Apartment, Booking, ContactMessage
from .forms import BookingForm, ContactForm

def home(request):
    featured_rooms = Room.objects.filter(is_featured=True)[:6]
    gallery_images = Gallery.objects.all()[:8]
    apartments = Apartment.objects.all()
    
    # Statistics for home page
    total_rooms = Room.objects.count()
    featured_count = featured_rooms.count()
    
    context = {
        'featured_rooms': featured_rooms,
        'gallery_images': gallery_images,
        'apartments': apartments,
        'total_rooms': total_rooms,
        'featured_count': featured_count,
        'today': timezone.now().date().isoformat(),
        'tomorrow': (timezone.now() + timedelta(days=1)).date().isoformat(),
    }
    return render(request, 'main/home.html', context)

def rooms(request):
    all_rooms = Room.objects.all().order_by('-is_featured', 'price')
    
    # Get filter parameters
    room_type = request.GET.get('type', '')
    price_range = request.GET.get('price', '')
    
    # Apply filters
    if room_type:
        all_rooms = all_rooms.filter(room_type=room_type)
    if price_range:
        if price_range == 'budget':
            all_rooms = all_rooms.filter(price__lt=50000)
        elif price_range == 'medium':
            all_rooms = all_rooms.filter(price__range=(50000, 100000))
        elif price_range == 'premium':
            all_rooms = all_rooms.filter(price__gt=100000)
    
    context = {
        'rooms': all_rooms,
        'room_types': Room.ROOM_TYPES,
        'current_filters': {
            'type': room_type,
            'price': price_range,
        }
    }
    return render(request, 'main/rooms.html', context)

def gallery(request):
    photos = Gallery.objects.all().order_by('-uploaded_at')
    context = {'photos': photos}
    return render(request, 'main/gallery.html', context)

def about(request):
    gallery_images = Gallery.objects.all()[:8]
    total_rooms = Room.objects.count()
    total_bookings = Booking.objects.filter(confirmed=True).count()
    
    context = {
        'gallery_images': gallery_images,
        'total_rooms': total_rooms,
        'total_bookings': total_bookings,
    }
    return render(request, 'main/about.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            
            # Send email notification (optional)
            try:
                send_mail(
                    f'New Contact Message from {contact_message.name}',
                    f'Name: {contact_message.name}\nEmail: {contact_message.email}\nMessage: {contact_message.message}',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=True,
                )
            except:
                pass  # Email sending is optional
            
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {'form': form}
    return render(request, 'main/contact.html', context)

def booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            
            # Calculate total cost based on duration
            check_in = booking.check_in
            check_out = booking.check_out
            duration = (check_out - check_in).days
            months = max(1, duration // 30)  # Minimum 1 month
            total_cost = booking.room.price * months
            
            # Send confirmation email (optional)
            try:
                send_mail(
                    f'Booking Request - {booking.room.title}',
                    f'Hello {booking.name},\n\n'
                    f'Thank you for your booking request at UBWIZA Apartment!\n\n'
                    f'Booking Details:\n'
                    f'Room: {booking.room.title}\n'
                    f'Check-in: {booking.check_in}\n'
                    f'Check-out: {booking.check_out}\n'
                    f'Guests: {booking.guests}\n'
                    f'Estimated Cost: {total_cost} RWF\n\n'
                    f'We will review your request and contact you within 24 hours to confirm your booking.\n\n'
                    f'Best regards,\n'
                    f'UBWIZA Apartment Team\n'
                    f'Phone: +250 791 010 558\n'
                    f'Email: tuyambazesylvain5@gmail.com',
                    settings.DEFAULT_FROM_EMAIL,
                    [booking.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email sending failed: {e}")  # For debugging
            
            messages.success(request, 
                f'Booking request submitted successfully! '
                f'We will contact you at {booking.email} within 24 hours to confirm.'
            )
            return redirect('booking')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm()
        # Pre-select room if coming from rooms page
        room_id = request.GET.get('room')
        if room_id:
            try:
                form.initial['room'] = room_id
            except:
                pass
    
    # Get available rooms for the form
    rooms = Room.objects.all()
    
    context = {
        'form': form,
        'rooms': rooms,
        'today': timezone.now().date().isoformat(),
        'tomorrow': (timezone.now() + timedelta(days=1)).date().isoformat(),
    }
    return render(request, 'main/booking.html', context)

def room_detail(request, room_id):
    """Detailed view for individual room"""
    room = get_object_or_404(Room, id=room_id)
    similar_rooms = Room.objects.filter(room_type=room.room_type).exclude(id=room_id)[:3]
    
    context = {
        'room': room,
        'similar_rooms': similar_rooms,
    }
    return render(request, 'main/room_detail.html', context)

def check_availability(request):
    """AJAX view to check room availability"""
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        check_in_str = request.GET.get('check_in')
        check_out_str = request.GET.get('check_out')
        room_id = request.GET.get('room_id')
        
        try:
            if check_in_str and check_out_str and room_id:
                check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
                
                # Check for conflicting bookings
                conflicting_bookings = Booking.objects.filter(
                    room_id=room_id,
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                    confirmed=True
                )
                
                available = not conflicting_bookings.exists()
                return JsonResponse({
                    'available': available,
                    'message': 'Room is available for these dates.' if available else 'Room is not available for the selected dates.'
                })
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def booking_success(request, booking_id):
    """Success page after booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    context = {'booking': booking}
    return render(request, 'main/booking_success.html', context)

# Dashboard and reporting views (for admin or internal use)
def booking_report(request):
    """Simple booking report - you can enhance this later"""
    if not request.user.is_staff:
        return redirect('home')
    
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    recent_bookings = Booking.objects.filter(created_at__date__gte=last_week)
    monthly_bookings = Booking.objects.filter(created_at__date__gte=last_month)
    
    context = {
        'recent_bookings': recent_bookings,
        'monthly_bookings': monthly_bookings,
        'total_bookings': Booking.objects.count(),
        'confirmed_bookings': Booking.objects.filter(confirmed=True).count(),
    }
    return render(request, 'main/booking_report.html', context)