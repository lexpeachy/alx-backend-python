from django.urls import path, include
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet

# Initialize DefaultRouter
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Initialize another DefaultRouter for nested messages
message_router = routers.DefaultRouter()
message_router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('conversations/<int:conversation_id>/', include(message_router.urls)),
]