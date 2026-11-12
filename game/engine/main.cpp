#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <algorithm>
#include <climits>

using namespace std;

struct Move {
    int from_r, from_c, to_r, to_c;
    int score;
};

int piece_value(char p) {
    switch (tolower(p)) {
        case 'p': return 100;
        case 'n': return 320;
        case 'b': return 330;
        case 'r': return 500;
        case 'q': return 900;
        case 'k': return 20000;
        default: return 0;
    }
}

bool is_white(char p) { return p >= 'A' && p <= 'Z'; }
bool is_black(char p) { return p >= 'a' && p <= 'z'; }

int evaluate(const string& board) {
    int score = 0;
    for (int i = 0; i < 64; i++) {
        char p = board[i];
        if (p == '.') continue;
        int val = piece_value(p);
        int r = i / 8, c = i % 8;
        int center_bonus = (3 - abs(3 - r)) + (3 - abs(3 - c));
        if (is_white(p)) score += val + center_bonus * 5;
        else score -= (val + center_bonus * 5);
    }
    return score;
}

bool in_bounds(int r, int c) { return r >= 0 && r < 8 && c >= 0 && c < 8; }

vector<Move> generate_moves(const string& board, bool white_turn) {
    vector<Move> moves;
    for (int r = 0; r < 8; r++) {
        for (int c = 0; c < 8; c++) {
            char p = board[r * 8 + c];
            if (p == '.') continue;
            if (white_turn && !is_white(p)) continue;
            if (!white_turn && !is_black(p)) continue;

            char type = tolower(p);
            auto add_move = [&](int nr, int nc) {
                if (!in_bounds(nr, nc)) return false;
                char target = board[nr * 8 + nc];
                if (target == '.') {
                    moves.push_back({r, c, nr, nc, 0});
                    return true;
                }
                if ((white_turn && is_black(target)) || (!white_turn && is_white(target))) {
                    moves.push_back({r, c, nr, nc, piece_value(target)});
                }
                return false;
            };

            if (type == 'p') {
                int dir = white_turn ? -1 : 1;
                int start_r = white_turn ? 6 : 1;
                if (in_bounds(r + dir, c) && board[(r + dir) * 8 + c] == '.') {
                    moves.push_back({r, c, r + dir, c, 0});
                    if (r == start_r && board[(r + 2 * dir) * 8 + c] == '.')
                        moves.push_back({r, c, r + 2 * dir, c, 0});
                }
                for (int dc : {-1, 1}) {
                    if (in_bounds(r + dir, c + dc)) {
                        char t = board[(r + dir) * 8 + (c + dc)];
                        if (t != '.' && ((white_turn && is_black(t)) || (!white_turn && is_white(t))))
                            moves.push_back({r, c, r + dir, c + dc, piece_value(t)});
                    }
                }
            } else if (type == 'n') {
                int dr[] = {-2,-2,-1,-1,1,1,2,2}, dc[] = {-1,1,-2,2,-2,2,-1,1};
                for (int i = 0; i < 8; i++) add_move(r + dr[i], c + dc[i]);
            } else if (type == 'k') {
                int dr[] = {-1,-1,-1,0,0,1,1,1}, dc[] = {-1,0,1,-1,1,-1,0,1};
                for (int i = 0; i < 8; i++) add_move(r + dr[i], c + dc[i]);
            } else {
                int dr[] = {-1,1,0,0,-1,-1,1,1}, dc[] = {0,0,-1,1,-1,1,-1,1};
                int start = (type == 'b') ? 4 : 0;
                int end = (type == 'r') ? 4 : 8;
                for (int dir = start; dir < end; dir++) {
                    for (int step = 1; step < 8; step++) {
                        if (!add_move(r + dr[dir] * step, c + dc[dir] * step)) break;
                    }
                }
            }
        }
    }
    sort(moves.begin(), moves.end(), [](const Move& a, const Move& b) {
        return a.score > b.score;
    });
    return moves;
}

string apply_move(string board, const Move& m) {
    char p = board[m.from_r * 8 + m.from_c];
    board[m.from_r * 8 + m.from_c] = '.';
    if (p == 'P' && m.to_r == 0) p = 'Q';
    if (p == 'p' && m.to_r == 7) p = 'q';
    board[m.to_r * 8 + m.to_c] = p;
    return board;
}

int minimax(const string& board, int depth, int alpha, int beta, bool maximizing) {
    if (depth == 0) return evaluate(board);
    vector<Move> moves = generate_moves(board, maximizing);
    if (moves.empty()) return evaluate(board);

    if (maximizing) {
        int max_eval = INT_MIN;
        for (const auto& m : moves) {
            int eval = minimax(apply_move(board, m), depth - 1, alpha, beta, false);
            max_eval = max(max_eval, eval);
            alpha = max(alpha, eval);
            if (beta <= alpha) break;
        }
        return max_eval;
    } else {
        int min_eval = INT_MAX;
        for (const auto& m : moves) {
            int eval = minimax(apply_move(board, m), depth - 1, alpha, beta, true);
            min_eval = min(min_eval, eval);
            beta = min(beta, eval);
            if (beta <= alpha) break;
        }
        return min_eval;
    }
}

string to_uci(const Move& m) {
    string s = "";
    s += (char)('a' + m.from_c);
    s += (char)('8' - m.from_r);
    s += (char)('a' + m.to_c);
    s += (char)('8' - m.to_r);
    return s;
}

int main() {
    string board;
    char turn_char = 'b';
    int depth = 3;
    if (!(cin >> board)) return 0;
    if (cin >> turn_char) {
        if (!(cin >> depth)) depth = 3;
    }
    bool white_turn = (turn_char == 'w');
    vector<Move> moves = generate_moves(board, white_turn);
    if (moves.empty()) {
        cout << "none" << endl;
        return 0;
    }
    Move best = moves[0];
    int best_val = white_turn ? INT_MIN : INT_MAX;
    for (const auto& m : moves) {
        int val = minimax(apply_move(board, m), depth - 1, INT_MIN, INT_MAX, !white_turn);
        if (white_turn && val > best_val) { best_val = val; best = m; }
        if (!white_turn && val < best_val) { best_val = val; best = m; }
    }
    cout << to_uci(best) << endl;
    return 0;
}