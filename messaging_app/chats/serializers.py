from models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'last_seen', 'profile_picture', 'online_status', 'birth_date']
        extra_kwargs = {
            'profile_picture': {'required': False},
            'bio': {'required': False},
            'birth_date': {'required': False},
        }

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    read_by = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'timestamp', 'read_by']
        read_only_fields = ['id', 'timestamp', 'sender', 'read_by']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True)
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at', 'updated_at', 'is_group_chat', 'group_name', 'messages', 'last_message']
        read_only_fields = ['id', 'created_at', 'updated_at', 'messages']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def create(self, validated_data):
        participants_data = validated_data.pop('participants', [])
        conversation = Conversation.objects.create(**validated_data)
        for participant in participants_data:
            conversation.participants.add(participant)
        return conversation

# For creating messages with minimal data
class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['conversation', 'content']