from django.urls import path
from .views import CreateUserView, AuthTokenView

app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('token/', AuthTokenView.as_view(), name='token'),
]
