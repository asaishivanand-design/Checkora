import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .engine import ChessGame

def board_view(request):
    return render(request, 'game/board.html')

def terms_view(request):
    return render(request, 'game/terms.html')

@csrf_exempt
def api_new_game(request):
    game = ChessGame()
    return JsonResponse({'status': 'ok', **game.get_status()})

@csrf_exempt
def api_player_move(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    data = json.loads(request.body or '{}')
    fen = data.get('fen')
    move_uci = data.get('move', '')
    game = ChessGame(fen)
    ok, san = game.make_move(move_uci)
    if not ok:
        return JsonResponse({'status': 'illegal', 'error': 'Illegal move'}, status=400)
    return JsonResponse({'status': 'ok', 'move': move_uci, 'san': san, **game.get_status()})

@csrf_exempt
def api_ai_move(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    data = json.loads(request.body or '{}')
    fen = data.get('fen')
    difficulty = data.get('difficulty', 'medium')
    game = ChessGame(fen)
    if game.board.is_game_over():
        return JsonResponse({'status': 'game_over', **game.get_status()})
    ai_uci, source = game.get_ai_move(difficulty=difficulty)
    if not ai_uci:
        return JsonResponse({'status': 'no_move', **game.get_status()})
    ok, san = game.make_move(ai_uci)
    return JsonResponse({
        'status': 'ok',
        'ai_move': ai_uci,
        'san': san,
        'engine_source': source,
        **game.get_status()
    })