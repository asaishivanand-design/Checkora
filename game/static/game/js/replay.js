document.addEventListener('DOMContentLoaded', function () {

    // ── State ──────────────────────────────────────────────────────────────
    let moves = [];          // array of SAN move strings
    let timestamps = [];     // array of clock seconds (or null)
    let currentMoveIndex = -1;
    let autoPlayTimer = null;
    let chessGame = new Chess();

    const PIECE_VALUES = { p: 1, n: 3, b: 3, r: 5, q: 9, k: 0 };

    // ── Board ──────────────────────────────────────────────────────────────
    var board = Chessboard('board', {
        position: 'start',
        showNotation: false,
        pieceTheme: piece =>
            `https://images.chesscomfiles.com/chess-themes/pieces/neo/150/${piece.toLowerCase()}.png`
    });

    // ── Theme toggles ──────────────────────────────────────────────────────
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.body.setAttribute('data-theme', this.dataset.theme);
            document.querySelectorAll('.theme-btn').forEach(b => b.style.border = 'none');
            this.style.border = '2px solid #fff';
        });
    });

    // ── PGN parsing ────────────────────────────────────────────────────────
    function loadPGN(pgn) {
        const tempGame = new Chess();
        if (!tempGame.load_pgn(pgn)) {
            setStatus("Invalid or unreadable PGN.");
            return false;
        }

        // Extract clock timestamps from comments like {[%clk 0:00:45]}
        const clkRegex = /\[%clk\s+(\d+):(\d+):(\d+)\]/g;
        const rawComments = pgn.match(/\{[^}]*\}/g) || [];
        timestamps = rawComments.map(comment => {
            const m = /\[%clk\s+(\d+):(\d+):(\d+)\]/.exec(comment);
            if (!m) return null;
            return parseInt(m[1]) * 3600 + parseInt(m[2]) * 60 + parseInt(m[3]);
        });

        moves = tempGame.history();   // SAN moves array
        currentMoveIndex = -1;
        chessGame = new Chess();
        board.position('start', false);
        clearHighlights();
        renderMoveHistory();
        updateCaptured();
        setStatus('');
        return true;
    }

    // ── Navigation ─────────────────────────────────────────────────────────
    function goToMove(index) {
        // Rebuild board state up to `index`
        chessGame = new Chess();
        for (let i = 0; i <= index; i++) {
            chessGame.move(moves[i]);
        }
        currentMoveIndex = index;
        board.position(chessGame.fen(), false);
        highlightLastMove(index);
        updateCaptured();
        highlightMoveInHistory(index);
    }

    function stepForward() {
        if (currentMoveIndex >= moves.length - 1) {
            stopAutoPlay();
            setStatus(moves.length ? 'End of game.' : '');
            return;
        }
        goToMove(currentMoveIndex + 1);
    }

    function stepBack() {
        stopAutoPlay();
        if (currentMoveIndex < 0) return;
        goToMove(currentMoveIndex - 1 >= 0 ? currentMoveIndex - 1 : -1);
        if (currentMoveIndex === -1) {
            chessGame = new Chess();
            board.position('start', false);
            clearHighlights();
            updateCaptured();
            highlightMoveInHistory(-1);
        }
    }

    // ── Auto-play ──────────────────────────────────────────────────────────
    function startAutoPlay() {
        if (autoPlayTimer) return;
        if (currentMoveIndex >= moves.length - 1) goToMove(-1); // restart

        function scheduleNext() {
            // Use timestamp delta for speed, fallback to 1s
            let delay = 1000;
            const nextIdx = currentMoveIndex + 1;
            if (
                nextIdx < timestamps.length &&
                timestamps[nextIdx] !== null &&
                nextIdx > 0 &&
                timestamps[nextIdx - 1] !== null
            ) {
                const delta = Math.abs(timestamps[nextIdx - 1] - timestamps[nextIdx]);
                delay = Math.max(300, Math.min(delta * 1000, 3000));
            }
            autoPlayTimer = setTimeout(() => {
                stepForward();
                if (currentMoveIndex < moves.length - 1) scheduleNext();
                else autoPlayTimer = null;
            }, delay);
        }

        scheduleNext();
    }

    function stopAutoPlay() {
        if (autoPlayTimer) {
            clearTimeout(autoPlayTimer);
            autoPlayTimer = null;
        }
    }

    // ── Highlights ─────────────────────────────────────────────────────────
    function highlightLastMove(index) {
        clearHighlights();
        if (index < 0) return;

        // Re-run the move on a temp board to get from/to squares
        const temp = new Chess();
        for (let i = 0; i < index; i++) temp.move(moves[i]);
        const result = temp.move(moves[index]);
        if (!result) return;

        [result.from, result.to].forEach(sq => {
            const el = document.querySelector(`.square-${sq}`);
            if (el) el.classList.add('highlight-move');
        });
    }

    function clearHighlights() {
        document.querySelectorAll('.highlight-move').forEach(el =>
            el.classList.remove('highlight-move')
        );
    }

    // ── Move history panel ─────────────────────────────────────────────────
    function renderMoveHistory() {
        const body = document.getElementById('moveHistoryBody');
        if (!moves.length) {
            body.innerHTML = '<p style="color:#666;text-align:center;margin-top:20px;">No moves to display.</p>';
            return;
        }

        let html = '<table style="width:100%;border-collapse:collapse;font-size:0.85em;">';
        html += '<colgroup><col style="width:32px"><col style="width:50%"><col style="width:50%"></colgroup>';

        for (let i = 0; i < moves.length; i += 2) {
            const moveNum = Math.floor(i / 2) + 1;
            const white = moves[i];
            const black = moves[i + 1] || '';
            html += `
                <tr class="move-row" style="border-bottom:1px solid #2a2a2a;">
                    <td style="color:#666;padding:4px 6px;user-select:none;">${moveNum}.</td>
                    <td class="move-cell" data-index="${i}"
                        style="padding:4px 6px;cursor:pointer;border-radius:3px;">${white}</td>
                    <td class="move-cell" data-index="${i + 1}"
                        style="padding:4px 6px;cursor:pointer;border-radius:3px;">${black}</td>
                </tr>`;
        }
        html += '</table>';
        body.innerHTML = html;

        body.querySelectorAll('.move-cell').forEach(cell => {
            const idx = parseInt(cell.dataset.index);
            if (isNaN(idx) || idx >= moves.length) return;
            cell.addEventListener('click', () => {
                stopAutoPlay();
                goToMove(idx);
            });
            cell.addEventListener('mouseenter', () => {
                if (!cell.classList.contains('active-move'))
                    cell.style.background = '#2a2a2a';
            });
            cell.addEventListener('mouseleave', () => {
                if (!cell.classList.contains('active-move'))
                    cell.style.background = '';
            });
        });
    }

    function highlightMoveInHistory(index) {
        document.querySelectorAll('.move-cell').forEach(cell => {
            cell.classList.remove('active-move');
            cell.style.background = '';
        });
        if (index < 0) return;
        const active = document.querySelector(`.move-cell[data-index="${index}"]`);
        if (active) {
            active.classList.add('active-move');
            active.style.background = '#f5a623';
            active.style.color = '#000';
            active.scrollIntoView({ block: 'nearest' });
        }
    }

    // ── Captured pieces ────────────────────────────────────────────────────
    const PIECE_UNICODE = {
        wq: '♕', wr: '♖', wb: '♗', wn: '♘', wp: '♙',
        bq: '♛', br: '♜', bb: '♝', bn: '♞', bp: '♟'
    };

    function updateCaptured() {
        const history = chessGame.history({ verbose: true });
        const whiteCap = [], blackCap = [];
        let whiteScore = 0, blackScore = 0;

        history.forEach(move => {
            if (move.captured) {
                const val = PIECE_VALUES[move.captured] || 0;
                if (move.color === 'w') {
                    whiteCap.push(move.captured);
                    whiteScore += val;
                } else {
                    blackCap.push(move.captured);
                    blackScore += val;
                }
            }
        });

        const render = (pieces, color) =>
            pieces.map(p => `<span style="font-size:1.2em;">${PIECE_UNICODE[color + p] || ''}</span>`).join(' ');

        document.getElementById('whiteCaptured').innerHTML = render(whiteCap, 'b'); // white captures black pieces
        document.getElementById('blackCaptured').innerHTML = render(blackCap, 'w');
        document.getElementById('whitePoints').textContent = `+${whiteScore}`;
        document.getElementById('blackPoints').textContent = `+${blackScore}`;
    }

    // ── Status message ─────────────────────────────────────────────────────
    function setStatus(msg) {
        document.getElementById('statusMsg').textContent = msg;
    }

    // ── Button controls ────────────────────────────────────────────────────
    document.getElementById('btnNext').addEventListener('click', () => {
        stopAutoPlay();
        stepForward();
    });

    document.getElementById('btnPrev').addEventListener('click', stepBack);

    document.getElementById('btnPlay').addEventListener('click', () => {
        if (!moves.length) { setStatus('Load a match first.'); return; }
        startAutoPlay();
    });

    document.getElementById('btnPause').addEventListener('click', stopAutoPlay);

    // ── "Watch Recent Match" — fetch from Django ───────────────────────────
    document.getElementById('btnFetchDB').addEventListener('click', async () => {
        setStatus('Loading match...');
        try {
            const res = await fetch('/api/recent-replay/', {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await res.json();

            if (!res.ok) {
                setStatus(data.error || 'Failed to load match.');
                return;
            }

            if (loadPGN(data.pgn)) {
                setStatus(`Loaded: ${data.mode.toUpperCase()} · ${data.winner} wins by ${data.end_reason.replace(/_/g, ' ')}`);
                setTimeout(() => setStatus(''), 4000);
            }
        } catch (e) {
            setStatus('Network error. Could not reach server.');
        }
    });

    // ── PGN file upload ────────────────────────────────────────────────────
    document.getElementById('pgnUpload').addEventListener('change', function () {
        const file = this.files[0];
        if (!file) return;
        if (!file.name.endsWith('.pgn')) {
            setStatus('Please upload a valid .pgn file.');
            return;
        }
        const reader = new FileReader();
        reader.onload = e => {
            if (loadPGN(e.target.result)) {
                setStatus(`File loaded: ${file.name}`);
                setTimeout(() => setStatus(''), 3000);
            }
        };
        reader.readAsText(file);
    });

    // ── CSS for move highlights ────────────────────────────────────────────
    const style = document.createElement('style');
    style.textContent = `
        .highlight-move { background: rgba(245, 166, 35, 0.45) !important; }
        .active-move { color: #000 !important; }
    `;
    document.head.appendChild(style);
});