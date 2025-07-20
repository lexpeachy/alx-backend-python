from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from.models import Conversation, Message
from .serializers import (ConversationSerializer,
                          MessageSerializer,
                          MessageCreateSerializer
)
from django.contrib.auth import get_user_model
User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Conversation.objects.all()

    def get_queryset(self):
        # Only show conversations where the current user is a participant
        return self.queryset.filter(participants=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        conversation = serializer.save()
        # Always add the current user as a participant
        conversation.participants.add(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get participant IDs from request
        participant_ids = request.data.get('participants', [])
        participants = User.objects.filter(id__in=participant_ids)
        
        # Create conversation
        conversation = Conversation.objects.create(
            is_group_chat=serializer.validated_data.get('is_group_chat', False),
            group_name=serializer.validated_data.get('group_name', '')
        )
        
        # Add participants (including current user)
        conversation.participants.add(self.request.user)
        for participant in participants:
            conversation.participants.add(participant)
        
        return Response(
            ConversationSerializer(conversation).data,
            status=status.HTTP_201_CREATED
        )

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        # Only show messages from conversations the user is part of
        return self.queryset.filter(
            conversation__participants=self.request.user
        ).order_by('timestamp')

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_id')
        conversation = get_object_or_404(
            Conversation.objects.filter(participants=self.request.user),
            id=conversation_id
        )
        serializer.save(sender=self.request.user, conversation=conversation)

    def list(self, request, conversation_id=None):
        # Get messages for a specific conversation
        conversation = get_object_or_404(
            Conversation.objects.filter(participants=self.request.user),
            id=conversation_id
        )
        messages = self.get_queryset().filter(conversation=conversation)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)