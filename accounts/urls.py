from django.urls import path
from .views import RegisterView, LoginView

app_name = 'api/accounts'

urlpatterns = [
    # URLs that do not require a valid token
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
]
