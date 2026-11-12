import os
import sys
import subprocess
import chess
from django.conf import settings

DEPTH_MAP = {
    'easy': 1,
    'medium': 2,
    'hard': 3,
}

class ChessGame:
    def __init__(self, fen=None):
        self.board = chess.Board(fen) if fen else chess.Board()

    def to_flat_board(self):
        flat = []
        for rank in range(7, -1, -1):
            for file in range(8):
                sq = chess.square(file, rank)
                piece = self.board.piece_at(sq)
                flat.append(piece.symbol() if piece else '.')
        return "".join(flat)

    def make_move(self, uci_move: str):
        try:
            move = chess.Move.from_uci(uci_move)
            if move in self.board.legal_moves:
                san = self.board.san(move)
                self.board.push(move)
                return True, san
            if len(uci_move) == 4:
                promo = chess.Move.from_uci(uci_move + 'q')
                if promo in self.board.legal_moves:
                    san = self.board.san(promo)
                    self.board.push(promo)
                    return True, san
            return False, None
        except ValueError:
            return False, None

    def get_ai_move(self, difficulty='medium'):
        depth = DEPTH_MAP.get(difficulty, 2)
        timeout = getattr(settings, 'CHESS_ENGINE_TIMEOUT', 10)
        engine_dir = os.path.join(settings.BASE_DIR, 'game', 'engine')
        cpp_exe = os.path.join(engine_dir, 'main.exe' if os.name == 'nt' else 'main')
        py_script = os.path.join(engine_dir, 'main.py')

        # 1. Try Primary C++17 Binary first
        if os.path.exists(cpp_exe):
            try:
                turn_char = 'w' if self.board.turn == chess.WHITE else 'b'
                payload = f"{self.to_flat_board()} {turn_char} {depth}\n"
                res = subprocess.run(
                    [cpp_exe],
                    input=payload,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                candidate = res.stdout.strip()
                if candidate and candidate != "none":
                    move = chess.Move.from_uci(candidate)
                    if move in self.board.legal_moves:
                        return candidate, "cpp"
            except Exception:
                pass

        # 2. Automatic Fallback to Python Engine
        try:
            payload = f"{self.board.fen()} {depth}\n"
            res = subprocess.run(
                [sys.executable, py_script],
                input=payload,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            candidate = res.stdout.strip()
            if candidate and candidate != "none":
                move = chess.Move.from_uci(candidate)
                if move in self.board.legal_moves:
                    return candidate, "python"
        except Exception:
            pass

        # 3. Safe Legal Move Fallback
        legal = list(self.board.legal_moves)
        if legal:
            return legal[0].uci(), "fallback"
        return None, "none"

    def get_status(self):
        return {
            'fen': self.board.fen(),
            'turn': 'white' if self.board.turn == chess.WHITE else 'black',
            'is_check': self.board.is_check(),
            'is_checkmate': self.board.is_checkmate(),
            'is_stalemate': self.board.is_stalemate(),
            'is_game_over': self.board.is_game_over(),
            'legal_moves': [m.uci() for m in self.board.legal_moves],
        }