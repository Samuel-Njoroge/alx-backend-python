from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth import get_user_model
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination
from .filters import MessageFilter
from django_filters.rest_framework import DjangoFilterBackend

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['participants__username']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return self.queryset.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        participant_ids = request.data.get('participants', [])
        if not participant_ids:
            return Response({'error': 'Participants are required.'}, status=status.HTTP_400_BAD_REQUEST)

        participants = User.objects.filter(user_id__in=participant_ids)
        conversation = Conversation.objects.create()
        conversation.participants.set(participants | User.objects.filter(user_id=request.user.user_id))
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    filter_class = MessageFilter

    def get_queryset(self):
        # Users can only see messages in conversations they participate in
        return Message.objects.filter(conversation__participants=self.request.user)

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation')
        content = request.data.get('content')

        if not conversation_id or not content:
            return Response({'error': 'Conversation ID and content are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id, participants=request.user)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found or you are not a participant.'}, status=status.HTTP_403_FORBIDDEN)

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=content
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
