from django.db import models
import chess

class GameRecord(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    fen = models.CharField(max_length=120, default=chess.STARTING_FEN)
    move_history = models.TextField(blank=True, default="")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    winner = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Game #{self.id} ({self.difficulty}) - {self.winner or 'In Progress'}"