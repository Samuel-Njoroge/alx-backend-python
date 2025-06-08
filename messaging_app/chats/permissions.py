from rest_framework import permissions


class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only participants to view/edit.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        elif hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        return False

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission:
    - Only authenticated users can access the API
    - Only participants in a conversation can view, send, update, or delete messages.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        # For Conversation objects
        if hasattr(obj, 'participants'):
            return user in obj.participants.all()
        
        # For Message objects
        elif hasattr(obj, 'conversation'):
            return user in obj.conversation.participants.all()
        
        return False