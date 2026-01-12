import streamlit as st
from typing import List, Optional, Tuple
import random

ROWS = 6
COLS = 7
EMPTY = 0
P1 = 1
P2 = 2

st.set_page_config(page_title="Connect Four", page_icon="🟡", layout="centered")


# ---------- Styling ----------
st.markdown(
    """
<style>
.block-container { padding-top: 3.8rem !important; padding-bottom: 2.6rem !important; }
header[data-testid="stHeader"] { background: rgba(0,0,0,.35) !important; backdrop-filter: blur(8px); }

.title {
  font-size: 2.0rem;
  font-weight: 900;
  margin: 0.2rem 0 0.1rem 0;
}
.subtle { color: rgba(255,255,255,.72); margin-bottom: .8rem; }

.board-card {
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.05);
  border-radius: 18px;
  padding: 14px;
  box-shadow: 0 16px 50px rgba(0,0,0,.45);
}

.cell {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 5px;
  border: 2px solid rgba(255,255,255,.10);
  background: rgba(0,0,0,.18);
  font-size: 22px;
}
.row { white-space: nowrap; }
.legend { font-size: .95rem; }
</style>
""",
    unsafe_allow_html=True,
)


# ---------- Game logic ----------
def new_board() -> List[List[int]]:
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def valid_moves(board: List[List[int]]) -> List[int]:
    return [c for c in range(COLS) if board[0][c] == EMPTY]

def drop_piece(board: List[List[int]], col: int, player: int) -> Optional[int]:
    """Drop a piece into a column. Returns row index where it lands, or None if column full."""
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            board[r][col] = player
            return r
    return None

def check_winner(board: List[List[int]]) -> int:
    """Return winner player (1/2) or 0 if none."""
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            line = board[r][c:c+4]
            if line[0] != EMPTY and all(x == line[0] for x in line):
                return line[0]

    # Vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            p = board[r][c]
            if p != EMPTY and all(board[r+i][c] == p for i in range(4)):
                return p

    # Diagonal down-right
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            p = board[r][c]
            if p != EMPTY and all(board[r+i][c+i] == p for i in range(4)):
                return p

    # Diagonal up-right
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            p = board[r][c]
            if p != EMPTY and all(board[r-i][c+i] == p for i in range(4)):
                return p

    return EMPTY

def is_draw(board: List[List[int]]) -> bool:
    return all(board[0][c] != EMPTY for c in range(COLS)) and check_winner(board) == EMPTY

def emoji_cell(val: int) -> str:
    # Use colored discs
    if val == P1:
        return "🟡"
    if val == P2:
        return "🔴"
    return "⚫"

def simulate_move_and_check(board: List[List[int]], col: int, player: int) -> bool:
    """Try a move on a copy; return True if it wins."""
    b = [row[:] for row in board]
    if drop_piece(b, col, player) is None:
        return False
    return check_winner(b) == player

def cpu_pick_move(board: List[List[int]]) -> int:
    """Simple CPU: win if possible, else block opponent, else center preference, else random."""
    moves = valid_moves(board)
    if not moves:
        return 0

    # 1) Win now
    for c in moves:
        if simulate_move_and_check(board, c, P2):
            return c

    # 2) Block player 1
    for c in moves:
        if simulate_move_and_check(board, c, P1):
            return c

    # 3) Prefer center columns
    center_order = sorted(moves, key=lambda x: abs(x - (COLS // 2)))
    top = center_order[:3] if len(center_order) >= 3 else center_order
    return random.choice(top)


# ---------- Session state ----------
if "board" not in st.session_state:
    st.session_state.board = new_board()
if "turn" not in st.session_state:
    st.session_state.turn = P1
if "winner" not in st.session_state:
    st.session_state.winner = EMPTY
if "mode" not in st.session_state:
    st.session_state.mode = "2 Players"  # or "Vs Computer"


def reset_game():
    st.session_state.board = new_board()
    st.session_state.turn = P1
    st.session_state.winner = EMPTY


# ---------- UI ----------
st.markdown('<div class="title">Connect Four</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">Drop discs, connect four in a row — horizontal, vertical, or diagonal.</div>', unsafe_allow_html=True)

top1, top2, top3 = st.columns([0.44, 0.33, 0.23])
with top1:
    st.session_state.mode = st.selectbox("Mode", ["2 Players", "Vs Computer"], index=0 if st.session_state.mode == "2 Players" else 1)
with top2:
    st.button("🔄 Reset", use_container_width=True, on_click=reset_game)
with top3:
    st.caption("P1 🟡  |  P2 🔴")

board = st.session_state.board

# Status
if st.session_state.winner != EMPTY:
    msg = "🟡 Player 1 wins!" if st.session_state.winner == P1 else "🔴 Player 2 wins!"
    st.success(msg)
elif is_draw(board):
    st.info("It's a draw 🤝")
else:
    who = "🟡 Player 1" if st.session_state.turn == P1 else "🔴 Player 2"
    if st.session_state.mode == "Vs Computer" and st.session_state.turn == P2:
        who = "🔴 Computer"
    st.write(f"**Turn:** {who}")

# Move buttons (columns)
moves_disabled = st.session_state.winner != EMPTY or is_draw(board)

cols = st.columns(COLS, gap="small")
for c in range(COLS):
    with cols[c]:
        label = f"⬇️ {c+1}"
        can_play = (not moves_disabled) and (board[0][c] == EMPTY)
        if st.button(label, key=f"col_{c}", use_container_width=True, disabled=not can_play):
            # Human move
            drop_piece(board, c, st.session_state.turn)
            w = check_winner(board)
            if w != EMPTY:
                st.session_state.winner = w
            else:
                if is_draw(board):
                    pass
                else:
                    st.session_state.turn = P2 if st.session_state.turn == P1 else P1

            # CPU move if enabled
            if (st.session_state.mode == "Vs Computer"
                and st.session_state.winner == EMPTY
                and not is_draw(board)
                and st.session_state.turn == P2):
                cpu_col = cpu_pick_move(board)
                drop_piece(board, cpu_col, P2)
                w2 = check_winner(board)
                if w2 != EMPTY:
                    st.session_state.winner = w2
                else:
                    if not is_draw(board):
                        st.session_state.turn = P1
            st.rerun()

# Render board
st.markdown('<div class="board-card">', unsafe_allow_html=True)
for r in range(ROWS):
    row_html = '<div class="row">'
    for c in range(COLS):
        row_html += f'<span class="cell">{emoji_cell(board[r][c])}</span>'
    row_html += "</div>"
    st.markdown(row_html, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.caption("Tip: In 'Vs Computer' mode, the CPU plays a simple win/block strategy and prefers the center.")
