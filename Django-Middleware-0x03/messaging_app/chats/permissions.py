from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Only participants of a conversation can send, view, update, and delete messages.
    """

    def has_permission(self, request, view):
        # Only allow authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # For Conversation objects
        if hasattr(obj, 'participants'):
            return user in obj.participants.all()

        # For Message objects
        elif hasattr(obj, 'conversation'):
            # Check participant of the conversation
            if user not in obj.conversation.participants.all():
                return False

            # Only allow GET, PUT, PATCH, DELETE if the user is a participant
            if request.method in permissions.SAFE_METHODS:
                return True
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                return True

        return False
