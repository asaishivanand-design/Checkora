import sys
import chess

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

def evaluate_board(board: chess.Board) -> int:
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            val = PIECE_VALUES.get(piece.piece_type, 0)
            score += val if piece.color == chess.WHITE else -val
    return score

def minimax(board: chess.Board, depth: int, alpha: int, beta: int, maximizing: bool) -> int:
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    if maximizing:
        max_eval = -10**9
        for move in board.legal_moves:
            board.push(move)
            ev = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, ev)
            alpha = max(alpha, ev)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = 10**9
        for move in board.legal_moves:
            board.push(move)
            ev = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, ev)
            beta = min(beta, ev)
            if beta <= alpha:
                break
        return min_eval

def best_move_from_fen(fen: str, depth: int = 2) -> str:
    board = chess.Board(fen)
    legal = list(board.legal_moves)
    if not legal:
        return "none"
    best_m = legal[0]
    maximizing = board.turn == chess.WHITE
    best_val = -10**9 if maximizing else 10**9
    for move in legal:
        board.push(move)
        val = minimax(board, depth - 1, -10**9, 10**9, not maximizing)
        board.pop()
        if (maximizing and val > best_val) or (not maximizing and val < best_val):
            best_val = val
            best_m = move
    return best_m.uci()

if __name__ == "__main__":
    data = sys.stdin.read().strip().split()
    if not data:
        sys.exit(0)
    fen = " ".join(data[:-1]) if len(data) > 2 else chess.STARTING_FEN
    depth = int(data[-1]) if data[-1].isdigit() else 2
    print(best_move_from_fen(fen, depth))