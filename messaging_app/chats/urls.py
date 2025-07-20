from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

#create a router for conversation
conversation_router = DefaultRouter()
conversation_router.register(r'conversation', ConversationViewSet, basename = 'conversation')

#create a nested router for messages within conversations
message_router  = DefaultRouter
message_router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    #include conversatiom routes
    path('', include(conversation_router.urls)),

    #include nested message routers under conversations
    path('conversations/<int:conversation_id>/', include(message_router.urls))
]