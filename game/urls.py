from django.urls import path
from . import views

urlpatterns = [
    path('', views.board_view, name='board'),
    path('terms/', views.terms_view, name='terms'),
    path('api/new-game/', views.api_new_game, name='api_new_game'),
    path('api/move/', views.api_player_move, name='api_player_move'),
    path('api/ai-move/', views.api_ai_move, name='api_ai_move'),
]