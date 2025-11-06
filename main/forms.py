from django import forms
from .models import Booking, ContactMessage, Room
from django.core.exceptions import ValidationError
from datetime import date

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'name', 'email', 'phone', 'check_in', 'check_out', 'guests']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+250 XXX XXX XXX'}),
            'guests': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
            'room': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        room = cleaned_data.get('room')
        guests = cleaned_data.get('guests')
        
        # Date validation
        if check_in and check_out:
            if check_in < date.today():
                raise ValidationError({'check_in': 'Check-in date cannot be in the past.'})
            
            if check_out <= check_in:
                raise ValidationError({'check_out': 'Check-out date must be after check-in date.'})
        
        # Room capacity validation
        if room and guests:
            max_guests = 2 if room.room_type == 'single' else 4
            if guests > max_guests:
                raise ValidationError({
                    'guests': f'This {room.room_type} room can accommodate maximum {max_guests} guests.'
                })
        
        return cleaned_data

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'your@email.com'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'How can we help you?',
                'rows': 5
            }),
        }