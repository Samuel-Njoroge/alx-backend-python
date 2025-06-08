import logging
import os
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from collections import defaultdict
import re


class RequestLoggingMiddleware:  
    def __init__(self, get_response):
        self.get_response = get_response
        
        log_file_path = os.path.join(settings.BASE_DIR, 'requests.log')
      
        self.logger = logging.getLogger('request_logger')
        self.logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
    
    def __call__(self, request):
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
    
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        current_hour = datetime.now().hour

        if current_hour < 6 or current_hour >= 21:
            return HttpResponseForbidden(
                "Access to the messaging app is restricted outside of 6 AM to 9 PM."
            )
        
        response = self.get_response(request)
        return response

class OffensiveLanguageMiddleware:
    """
    Middleware that limits the number of chat messages a user can send within a certain time window,
    based on their IP address. Limits to 5 messages per minute.
    """
    
    ip_message_counts = defaultdict(list)
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_messages = 5
        self.time_window = 60  
    
    def __call__(self, request):
        if request.method == 'POST':
            ip_address = self.get_client_ip(request)
            current_time = datetime.now()
            
            self.clean_old_entries(ip_address, current_time)
            
            message_count = len(self.ip_message_counts[ip_address])
            
            if message_count >= self.max_messages:
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded. You can only send 5 messages per minute.',
                        'retry_after': self.time_window
                    },
                    status=429 
                )
            
            self.ip_message_counts[ip_address].append(current_time)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Extract the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def clean_old_entries(self, ip_address, current_time):
        """Remove entries older than the time window."""
        cutoff_time = current_time - timedelta(seconds=self.time_window)
        self.ip_message_counts[ip_address] = [
            timestamp for timestamp in self.ip_message_counts[ip_address]
            if timestamp > cutoff_time
        ]

class RolepermissionMiddleware: 
    def __init__(self, get_response):
        self.get_response = get_response
        self.restricted_paths = [
            '/api/users/',
            '/api/conversations/',
            '/api/messages/',
            '/admin/',
        ]
    
    def __call__(self, request):
        if self.requires_role_check(request.path):
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required.")
            
            user = request.user
        
            is_admin = getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False)
            is_moderator = self.check_moderator_role(user)
            
            if not (is_admin or is_moderator):
                return HttpResponseForbidden(
                    "Access denied. This action requires admin or moderator privileges."
                )
        
        response = self.get_response(request)
        return response
    
    def requires_role_check(self, path):
        """Check if the given path requires role-based access control."""
        for restricted_path in self.restricted_paths:
            if path.startswith(restricted_path):
                return True
        return False
    
    def check_moderator_role(self, user):
        """
        Check if user has moderator role.
        This implementation checks for a 'moderator' group or a role field.
        """
    
        if hasattr(user, 'groups'):
            return user.groups.filter(name='moderator').exists()
        
        if hasattr(user, 'role'):
            return user.role in ['moderator', 'admin']
        
        if hasattr(user, 'is_moderator'):
            return user.is_moderator
        
        return False

class OffensiveLanguageDetectionMiddleware:
    """
    Bonus middleware that actually detects offensive language in message content.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.offensive_words = [
            'spam', 'hate', 'offensive', 'inappropriate', 'banned'
            
        ]
    
    def __call__(self, request):
        if request.method == 'POST' and 'message_body' in request.POST:
            message_content = request.POST.get('message_body', '').lower()
            
            if self.contains_offensive_language(message_content):
                return JsonResponse(
                    {
                        'error': 'Message contains inappropriate content and cannot be sent.',
                        'code': 'OFFENSIVE_CONTENT'
                    },
                    status=400
                )
        
        response = self.get_response(request)
        return response
    
    def contains_offensive_language(self, text):
        """Check if text contains offensive language."""
        text_words = re.findall(r'\b\w+\b', text.lower())
        return any(word in self.offensive_words for word in text_words)