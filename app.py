import streamlit as st
from typing import List, Optional
import random

ROWS = 6
COLS = 7
EMPTY = 0
P1 = 1
P2 = 2

CELL = 56          # cell size in px
GAP = 10           # gap between cells in px
BOARD_BG = "rgba(255,255,255,.05)"

st.set_page_config(page_title="Connect Four", page_icon="🟡", layout="centered")

# ---------- CSS: aligned layout (fixed board width + CSS grid) ----------
BOARD_WIDTH = COLS * CELL + (COLS - 1) * GAP

st.markdown(
    f"""
<style>
.block-container {{
  padding-top: 3.8rem !important;
  padding-bottom: 2.6rem !important;
  max-width: {BOARD_WIDTH + 120}px; /* keep app snug around board */
}}

header[data-testid="stHeader"] {{
  background: rgba(0,0,0,.35) !important;
  backdrop-filter: blur(8px);
}}

.title {{
  font-size: 2.1rem;
  font-weight: 900;
  margin: 0.2rem 0 0.1rem 0;
}}
.subtle {{
  color: rgba(255,255,255,.72);
  margin-bottom: 1rem;
}}

/* Game container centered */
.game-wrap {{
  width: {BOARD_WIDTH}px;
  margin: 0 auto;
}}

/* Controls row doesn't break alignment */
.controls {{
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  width: {BOARD_WIDTH}px;
  margin: 0 auto 10px auto;
}}

/* Column drop buttons aligned to board width */
.drop-row {{
  width: {BOARD_WIDTH}px;
  margin: 0 auto 12px auto;
  display: grid;
  grid-template-columns: repeat({COLS}, 1fr);
  gap: {GAP}px;
}}

.drop-row button {{
  width: 100% !important;
}}

/* Board */
.board {{
  width: {BOARD_WIDTH}px;
  margin: 0 auto;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,.12);
  background: {BOARD_BG};
  box-shadow: 0 16px 50px rgba(0,0,0,.45);
}}

.grid {{
  display: grid;
  grid-template-columns: repeat({COLS}, {CELL}px);
  grid-template-rows: repeat({ROWS}, {CELL}px);
  gap: {GAP}px;
  justify-content: center;
}}

.cell {{
  width: {CELL}px;
  height: {CELL}px;
  border-radius: 999px;
  border: 2px solid rgba(255,255,255,.10);
  background: rgba(0,0,0,.18);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  line-height: 1;
}}

/* Small legend */
.legend {{
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  color: rgba(255,255,255,.75);
  font-size: .95rem;
}}
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
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            board[r][col] = player
            return r
    return None

def check_winner(board: List[List[int]]) -> int:
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            p = board[r][c]
            if p != EMPTY and all(board[r][c+i] == p for i in range(4)):
                return p
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
    if val == P1:
        return "🟡"
    if val == P2:
        return "🔴"
    return "⚫"

def simulate_move_and_check(board: List[List[int]], col: int, player: int) -> bool:
    b = [row[:] for row in board]
    if drop_piece(b, col, player) is None:
        return False
    return check_winner(b) == player

def cpu_pick_move(board: List[List[int]]) -> int:
    moves = valid_moves(board)
    if not moves:
        return 0

    # win now
    for c in moves:
        if simulate_move_and_check(board, c, P2):
            return c
    # block
    for c in moves:
        if simulate_move_and_check(board, c, P1):
            return c
    # center-ish
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
    st.session_state.mode = "2 Players"

def reset_game():
    st.session_state.board = new_board()
    st.session_state.turn = P1
    st.session_state.winner = EMPTY

# ---------- UI ----------
st.markdown('<div class="title">Connect Four</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">Drop discs, connect four in a row — horizontal, vertical, or diagonal.</div>', unsafe_allow_html=True)

board = st.session_state.board
moves_locked = st.session_state.winner != EMPTY or is_draw(board)

# Controls (kept tight and aligned)
st.markdown('<div class="controls">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([0.52, 0.30, 0.18])
with c1:
    st.session_state.mode = st.selectbox(
        "Mode",
        ["2 Players", "Vs Computer"],
        index=0 if st.session_state.mode == "2 Players" else 1,
    )
with c2:
    st.button("🔄 Reset", use_container_width=True, on_click=reset_game)
with c3:
    st.markdown('<div class="legend">P1 🟡 <span style="opacity:.6;">|</span> P2 🔴</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Status
if st.session_state.winner != EMPTY:
    st.success("🟡 Player 1 wins!" if st.session_state.winner == P1 else "🔴 Player 2 wins!")
elif is_draw(board):
    st.info("It's a draw 🤝")
else:
    who = "🟡 Player 1" if st.session_state.turn == P1 else "🔴 Player 2"
    if st.session_state.mode == "Vs Computer" and st.session_state.turn == P2:
        who = "🔴 Computer"
    st.write(f"**Turn:** {who}")

# Drop buttons row (true grid aligned with board)
st.markdown('<div class="drop-row">', unsafe_allow_html=True)
btn_cols = st.columns(COLS, gap="small")
for c in range(COLS):
    with btn_cols[c]:
        can_play = (not moves_locked) and (board[0][c] == EMPTY)
        if st.button(f"⬇️ {c+1}", key=f"drop_{c}", use_container_width=True, disabled=not can_play):
            drop_piece(board, c, st.session_state.turn)
            w = check_winner(board)
            if w != EMPTY:
                st.session_state.winner = w
            else:
                if not is_draw(board):
                    st.session_state.turn = P2 if st.session_state.turn == P1 else P1

            # CPU response
            if (
                st.session_state.mode == "Vs Computer"
                and st.session_state.winner == EMPTY
                and not is_draw(board)
                and st.session_state.turn == P2
            ):
                cpu_col = cpu_pick_move(board)
                drop_piece(board, cpu_col, P2)
                w2 = check_winner(board)
                if w2 != EMPTY:
                    st.session_state.winner = w2
                else:
                    if not is_draw(board):
                        st.session_state.turn = P1

            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# Board render (CSS grid)
st.markdown('<div class="board"><div class="grid">', unsafe_allow_html=True)
for r in range(ROWS):
    for c in range(COLS):
        st.markdown(f'<div class="cell">{emoji_cell(board[r][c])}</div>', unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)

st.caption("In 'Vs Computer' mode, the CPU plays a simple win/block strategy and prefers the center.")

