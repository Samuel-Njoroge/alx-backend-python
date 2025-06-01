from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(allow_blank=True, required=False)
    
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'bio', 'profile_image', 'first_name', 'last_name']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField()  
    
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at', 'read']


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at', 'messages', 'message_count']

    def get_message_count(self, obj):
        return obj.messages.count()
    
    def validate(self, data):
        if not data.get('participants') and self.instance is None:
            raise serializers.ValidationError("A conversation must have participants.")
        return data
