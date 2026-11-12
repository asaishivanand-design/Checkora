import json
from django.test import TestCase, Client
from .engine import ChessGame

class CheckoraEngineTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_initial_board_state(self):
        game = ChessGame()
        status = game.get_status()
        self.assertEqual(status['turn'], 'white')
        self.assertFalse(status['is_game_over'])
        self.assertEqual(len(status['legal_moves']), 20)

    def test_valid_and_invalid_player_move(self):
        game = ChessGame()
        ok, san = game.make_move('e2e4')
        self.assertTrue(ok)
        self.assertEqual(san, 'e4')
        bad_ok, _ = game.make_move('e2e5')
        self.assertFalse(bad_ok)

    def test_ai_engine_returns_legal_move(self):
        game = ChessGame()
        game.make_move('e2e4')
        ai_move, source = game.get_ai_move(difficulty='easy')
        self.assertIsNotNone(ai_move)
        self.assertIn(ai_move, [m.uci() for m in game.board.legal_moves])

    def test_api_endpoints(self):
        res = self.client.post('/api/new-game/')
        self.assertEqual(res.status_code, 200)
        fen = res.json()['fen']

        move_res = self.client.post(
            '/api/move/',
            data=json.dumps({'fen': fen, 'move': 'e2e4'}),
            content_type='application/json'
        )
        self.assertEqual(move_res.status_code, 200)
        next_fen = move_res.json()['fen']

        ai_res = self.client.post(
            '/api/ai-move/',
            data=json.dumps({'fen': next_fen, 'difficulty': 'easy'}),
            content_type='application/json'
        )
        self.assertEqual(ai_res.status_code, 200)
        self.assertIn('ai_move', ai_res.json())