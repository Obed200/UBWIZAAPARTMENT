from django.contrib import admin
from .models import Room, Gallery, Booking, ContactMessage, Apartment
from django.utils.html import format_html
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count, Sum
from datetime import datetime, timedelta

admin.site.site_header = "Ubwiza Apartment Administration"
admin.site.site_title = "Ubwiza Apartment Admin Portal"
admin.site.index_title = "Welcome to Ubwiza Apartment Admin Dashboard"

class RoomAdmin(admin.ModelAdmin):
    list_display = ['title', 'room_type', 'price', 'is_featured', 'image_preview']
    list_filter = ['room_type', 'is_featured', 'price']
    search_fields = ['title', 'description']
    list_editable = ['is_featured', 'price']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['title']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'room', 'check_in', 'check_out', 'guests', 'confirmed', 'created_at']
    list_filter = ['confirmed', 'check_in', 'check_out', 'room', 'created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at']
    list_editable = ['confirmed']
    actions = ['confirm_bookings', 'cancel_bookings']
    
    def confirm_bookings(self, request, queryset):
        queryset.update(confirmed=True)
        self.message_user(request, f"{queryset.count()} bookings confirmed successfully.")
    confirm_bookings.short_description = "Confirm selected bookings"
    
    def cancel_bookings(self, request, queryset):
        queryset.update(confirmed=False)
        self.message_user(request, f"{queryset.count()} bookings cancelled.")
    cancel_bookings.short_description = "Cancel selected bookings"

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'sent_at', 'message_preview']
    list_filter = ['sent_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['sent_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'

class ApartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'photo_preview', 'has_video', 'youtube_preview']
    search_fields = ['name', 'description']
    fields = ['name', 'description', 'photo', 'video_url']
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.photo.url)
        return "No Photo"
    photo_preview.short_description = 'Photo'
    
    def has_video(self, obj):
        return obj.has_video()
    has_video.boolean = True
    has_video.short_description = 'Has Video'
    
    def youtube_preview(self, obj):
        if obj.has_video():
            youtube_id = obj.get_youtube_id()
            return format_html(
                '<a href="{}" target="_blank" style="color: #ff0000; font-weight: bold;">▶ YouTube</a>',
                obj.video_url
            )
        return "No Video"
    youtube_preview.short_description = 'Video Link'

# Custom Admin Site
class CustomAdminSite(admin.AdminSite):
    site_header = "UBWIZA Apartment Administration"
    site_title = "UBWIZA Apartment Admin"
    index_title = "Welcome to UBWIZA Apartment Admin"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        # Dashboard statistics
        context = {
            **self.each_context(request),
            'total_bookings': Booking.objects.count(),
            'pending_bookings': Booking.objects.filter(confirmed=False).count(),
            'confirmed_bookings': Booking.objects.filter(confirmed=True).count(),
            'total_rooms': Room.objects.count(),
            'featured_rooms': Room.objects.filter(is_featured=True).count(),
            'total_messages': ContactMessage.objects.count(),
            'recent_messages': ContactMessage.objects.order_by('-sent_at')[:5],
            'recent_bookings': Booking.objects.order_by('-created_at')[:5],
        }
        return TemplateResponse(request, 'admin/dashboard.html', context)

# Register models with custom admin
admin_site = CustomAdminSite(name='custom_admin')

admin_site.register(Room, RoomAdmin)
admin_site.register(Gallery, GalleryAdmin)
admin_site.register(Booking, BookingAdmin)
admin_site.register(ContactMessage, ContactMessageAdmin)
admin_site.register(Apartment, ApartmentAdmin)

# Also register with default admin for backup
admin.site.register(Room, RoomAdmin)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(Apartment, ApartmentAdmin)