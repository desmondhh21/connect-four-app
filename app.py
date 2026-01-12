import streamlit as st
from typing import List, Optional
import random

ROWS = 6
COLS = 7
EMPTY = 0
P1 = 1
P2 = 2

st.set_page_config(page_title="Connect Four", page_icon="🟡", layout="centered")

# ---------- CSS (responsive + aligned) ----------
st.markdown(
    """
<style>
/* Keep everything in a centered, consistent width so buttons + board align */
.block-container{
  padding-top: 3.6rem !important;
  padding-bottom: 2.6rem !important;
  max-width: 860px !important;
}
header[data-testid="stHeader"]{
  background: rgba(0,0,0,.35) !important;
  backdrop-filter: blur(8px);
}

.title{
  font-size: 2.2rem;
  font-weight: 900;
  margin: .2rem 0 .1rem 0;
}
.subtle{
  color: rgba(255,255,255,.72);
  margin-bottom: 1rem;
}

/* Board card */
.board-card{
  width: 100%;
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.05);
  border-radius: 18px;
  padding: 14px;
  box-shadow: 0 16px 50px rgba(0,0,0,.45);
}

/* Actual grid: 7 equal columns, responsive */
.c4-grid{
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
}

/* Cells: perfectly square */
.c4-cell{
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 999px;
  border: 2px solid rgba(255,255,255,.10);
  background: rgba(0,0,0,.18);
  display:flex;
  align-items:center;
  justify-content:center;
  position: relative;
  overflow: hidden;
}

/* Disc layer */
.c4-disc{
  width: 78%;
  height: 78%;
  border-radius: 999px;
  box-shadow:
    inset 0 10px 18px rgba(255,255,255,.08),
    inset 0 -14px 22px rgba(0,0,0,.35),
    0 10px 22px rgba(0,0,0,.35);
}

/* Colors */
.disc-empty{
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.10), rgba(0,0,0,.35));
  opacity: .35;
}
.disc-p1{
  background: radial-gradient(circle at 30% 30%, #fff3a6, #eab308 58%, #8a6a00);
}
.disc-p2{
  background: radial-gradient(circle at 30% 30%, #ffb4b4, #ef4444 58%, #7f1d1d);
}

/* Make Streamlit buttons a bit tighter and consistent */
.stButton>button{
  border-radius: 14px !important;
  padding: .65rem .85rem !important;
}

/* Small legend */
.legend{
  color: rgba(255,255,255,.75);
  font-size: .95rem;
  text-align: right;
  padding-top: 1.75rem;
}
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

def simulate_move_and_check(board: List[List[int]], col: int, player: int) -> bool:
    b = [row[:] for row in board]
    if drop_piece(b, col, player) is None:
        return False
    return check_winner(b) == player

def cpu_pick_move(board: List[List[int]]) -> int:
    moves = valid_moves(board)
    if not moves:
        return 0
    # Win now
    for c in moves:
        if simulate_move_and_check(board, c, P2):
            return c
    # Block
    for c in moves:
        if simulate_move_and_check(board, c, P1):
            return c
    # Prefer center
    center_order = sorted(moves, key=lambda x: abs(x - (COLS // 2)))
    return random.choice(center_order[:3] if len(center_order) >= 3 else center_order)

def disc_class(v: int) -> str:
    if v == P1:
        return "disc-p1"
    if v == P2:
        return "disc-p2"
    return "disc-empty"

def render_board_html(board: List[List[int]]) -> str:
    # Render entire board in ONE HTML block so the CSS grid stays intact.
    cells = []
    for r in range(ROWS):
        for c in range(COLS):
            cls = disc_class(board[r][c])
            cells.append(
                f'<div class="c4-cell"><div class="c4-disc {cls}"></div></div>'
            )
    return f"""
    <div class="board-card">
      <div class="c4-grid">
        {''.join(cells)}
      </div>
    </div>
    """

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

top1, top2, top3 = st.columns([0.52, 0.28, 0.20])
with top1:
    st.session_state.mode = st.selectbox(
        "Mode", ["2 Players", "Vs Computer"],
        index=0 if st.session_state.mode == "2 Players" else 1
    )
with top2:
    st.button("🔄 Reset", use_container_width=True, on_click=reset_game)
with top3:
    st.markdown('<div class="legend">P1 🟡 &nbsp; | &nbsp; P2 🔴</div>', unsafe_allow_html=True)

board = st.session_state.board
locked = st.session_state.winner != EMPTY or is_draw(board)

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

# Column buttons (these will align because board is width:100% and columns are equal fractions)
btn_cols = st.columns(COLS, gap="small")
for c in range(COLS):
    with btn_cols[c]:
        can_play = (not locked) and (board[0][c] == EMPTY)
        if st.button(f"⬇️ {c+1}", key=f"drop_{c}", use_container_width=True, disabled=not can_play):
            # Human move
            drop_piece(board, c, st.session_state.turn)
            w = check_winner(board)
            if w != EMPTY:
                st.session_state.winner = w
            else:
                if not is_draw(board):
                    st.session_state.turn = P2 if st.session_state.turn == P1 else P1

            # CPU move if enabled
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

# Render board (single HTML call = no layout break)
st.markdown(render_board_html(board), unsafe_allow_html=True)

st.caption("Tip: In 'Vs Computer' mode, the CPU tries to win, block, and prefers center columns.")
