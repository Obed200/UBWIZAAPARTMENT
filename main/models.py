from django.db import models
import re

# --- Room model ---
class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('suite', 'Suite'),
    ]
    title = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='rooms/')
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# --- Gallery model ---
class Gallery(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# --- Booking model ---
class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.room.title}"


# --- Contact Message model ---
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# --- Apartment model ---
class Apartment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    photo = models.ImageField(upload_to='apartments/photos/')
    video_url = models.URLField(blank=True, null=True, help_text="Enter YouTube video URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)")

    def __str__(self):
        return self.name
    
    def get_youtube_id(self):
        """Extract YouTube video ID from URL"""
        if self.video_url:
            # Extract ID from various YouTube URL formats
            patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&]+)',
                r'youtube\.com\/embed\/([^?]+)',
                r'youtube\.com\/v\/([^?]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, self.video_url)
                if match:
                    return match.group(1)
        return None
    
    def has_video(self):
        return bool(self.video_url and self.get_youtube_id())