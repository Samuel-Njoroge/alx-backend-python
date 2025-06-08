from rest_framework import permissions

class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view or edit.
    """

    def has_object_permission(self, request, view, obj):
        # If this is a conversation
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        # If this is a message
        elif hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        return False
