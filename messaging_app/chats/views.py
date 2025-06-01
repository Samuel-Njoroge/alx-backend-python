from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, and viewing conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with participants.
        Expects a list of user IDs.
        """
        participant_ids = request.data.get('participants', [])
        if not participant_ids:
            return Response({'error': 'Participants are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Include the creator in the conversation
        participants = User.objects.filter(id__in=participant_ids)
        conversation = Conversation.objects.create()
        conversation.participants.set(participants | User.objects.filter(id=request.user.id))
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and sending messages in conversations.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(conversation__participants=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Send a new message to an existing conversation.
        Expects: conversation (ID), content (string)
        """
        conversation_id = request.data.get('conversation')
        content = request.data.get('content')

        if not conversation_id or not content:
            return Response({'error': 'Conversation ID and content are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found or you are not a participant.'},
                            status=status.HTTP_404_NOT_FOUND)

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            content=content
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
