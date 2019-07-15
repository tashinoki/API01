
from django.urls import path
from .views import (
  FitTokenUid, FitTokenId
)

urlpatterns = [
  path('user_uid', FitTokenUid.as_view(), name='fit-token-user-uid'),
  path('user_id', FitTokenId.as_view(), name='fit-token-user-id')
]
