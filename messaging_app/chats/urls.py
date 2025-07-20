from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Create routers
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested router for messages
conversation_router = DefaultRouter()
conversation_router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('conversations/<int:conversation_id>/', include(conversation_router.urls)),
]