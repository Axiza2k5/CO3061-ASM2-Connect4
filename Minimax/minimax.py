import math
import random
from typing import List, Optional, Sequence, Tuple

BoardState = Sequence[Sequence[int]]


def _copy_board(state: BoardState) -> List[List[int]]:
    """Trả về bản sao của bảng"""
    return [list(row) for row in state]


def _opponent(piece: int) -> int:
    """Trả về quân đối thủ"""
    return 1 if piece == 2 else 2


def _valid_actions(board: List[List[int]]) -> List[int]:
    """Cột không đầy. Cột đầy khi ô trên cùng không phải là 0."""
    cols = len(board[0])
    return [c for c in range(cols) if board[0][c] == 0]


def _drop_piece(board: List[List[int]], col: int, piece: int) -> bool:
    """Thả quân vào cột đã cho trên bản sao bảng (duyệt từ đáy lên). 
    Ghi quân tại ô trống đầu tiên tìm được và trả True; nếu cột đầy, trả False."""
    for r in range(len(board) - 1, -1, -1):
        if board[r][col] == 0:
            board[r][col] = piece
            return True
    return False


def _winning_move(board: List[List[int]], piece: int) -> bool:
    """Kiểm tra 4 điều kiện thắng cho piece: ngang, dọc, chéo /, chéo \."""
    rows = len(board)
    cols = len(board[0])
    # Kiểm tra ngang
    for r in range(rows):
        for c in range(cols - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
    # Kiểm tra dọc
    for c in range(cols):
        for r in range(rows - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
    # Kiểm tra chéo /
    for r in range(3, rows):
        for c in range(cols - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
    # Kiểm tra chéo \
    for r in range(rows - 3):
        for c in range(cols - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
    return False


def _evaluate_window(window: List[int], piece: int) -> int:
    """
    Đánh giá heuristic của một cửa sổ 4 ô.
    Điểm dương ưu tiên 'piece'; điểm âm phạt đe dọa từ đối thủ.
    """
    score = 0
    opp = _opponent(piece)

    piece_count = window.count(piece)
    empty_count = window.count(0)
    opp_count = window.count(opp)

    if piece_count == 4:
        score += 100000
    elif piece_count == 3 and empty_count == 1:
        score += 100
    elif piece_count == 2 and empty_count == 2:
        score += 10

    if opp_count == 3 and empty_count == 1:
        score -= 80
    elif opp_count == 2 and empty_count == 2:
        score -= 5

    return score


def _score_position(board: List[List[int]], piece: int) -> int:
    """Duyệt tất cả các cửa sổ 4 ô và tính điểm heuristic."""
    score = 0
    rows = len(board)
    cols = len(board[0])
    center_col = cols // 2

    center_column_values = [board[r][center_col] for r in range(rows)]
    center_count = center_column_values.count(piece)
    score += center_count * 6
    
    for r in range(rows):
        for c in range(cols - 3):
            window = board[r][c : c + 4]
            score += _evaluate_window(window, piece)
            
    for c in range(cols):
        for r in range(rows - 3):
            window = [board[r + i][c] for i in range(4)]
            score += _evaluate_window(window, piece)
            
    for r in range(3, rows):
        for c in range(cols - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += _evaluate_window(window, piece)
            
    for r in range(rows - 3):
        for c in range(cols - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += _evaluate_window(window, piece)
            
    return score

def _is_terminal_node(board: List[List[int]], piece: int) -> bool:
    """Kiểm tra xem node hiện tại có phải là node kết thúc hay không."""
    opp = _opponent(piece)
    return (
        _winning_move(board, piece)
        or _winning_move(board, opp)
        or len(_valid_actions(board)) == 0
    )


def _minimax(
    board: List[List[int]],
    depth: int,
    alpha: float,
    beta: float,
    maximizing_player: bool,
    piece: int,
) -> Tuple[Optional[int], float]:
    """Tìm kiếm Minimax có cắt tỉa alpha-beta."""
    valid_cols = _valid_actions(board)
    center = len(board[0]) // 2
    valid_cols.sort(key=lambda c: abs(center - c))
    opp = _opponent(piece)

    if depth == 0 or _is_terminal_node(board, piece):
        if _winning_move(board, piece):
            return None, 1_000_000
        elif _winning_move(board, opp):
            return None, -1_000_000
        else:
            return None, _score_position(board, piece)
    
    for col in valid_cols:
        from copy import deepcopy
from math import inf
from typing import List, Tuple, Optional

def _minimax(
    board: List[List[int]],
    depth: int,
    alpha: float,
    beta: float,
    maximizing_player: bool,  # thực ra không cần dùng trong negamax, nhưng giữ cho tương thích
    piece: int,
) -> Tuple[Optional[int], float]:
    """Tìm kiếm Minimax có cắt tỉa alpha-beta (dạng negamax)."""

    valid_cols = _valid_actions(board)
    center = len(board[0]) // 2
    valid_cols.sort(key=lambda c: abs(center - c))  # ưu tiên cột gần giữa hơn

    opp = _opponent(piece)

    # 1. DEEP-ENOUGH / Nút lá
    if depth == 0 or _is_terminal_node(board, piece):
        if _winning_move(board, piece):
            return None, 1_000_000
        elif _winning_move(board, opp):
            return None, -1_000_000
        else:
            return None, _score_position(board, piece)

    # 3. Nếu không còn nước đi: đánh giá static như nút lá
    if not valid_cols:
        return None, _score_position(board, piece)

    # 4. Có successor: duyệt các nước đi, áp dụng mã giả MINIMAX-A-B
    best_col: Optional[int] = None
    value = -inf           # PassTd trong mã giả

    for col in valid_cols:
        # SUCCESSOR = MOVE-GEN(Position, Player)
        # -> tạo board mới sau khi đánh vào cột col
        temp_board = _copy_board(board)
        _drop_piece(temp_board, col, piece)  # hoặc hàm bạn đang dùng để đặt quân

        # RESULT-SUCC = MINIMAX-A-B(SUCC, Depth + 1, Opp(Player), -PassTd, -UseTd)
        _, child_val = _minimax(
            temp_board,
            depth - 1,          # dùng depth còn lại nên trừ 1
            -beta,              # -UseTd
            -alpha,             # -PassTd
            not maximizing_player,
            opp,                # Opp(Player)
        )

        # NEW-VALUE = - VALUE(RESULT-SUCC)
        new_value = -child_val

        # if NEW-VALUE > PassTd then cập nhật
        if new_value > value:
            value = new_value
            best_col = col

        # cập nhật alpha (PassTd)
        if value > alpha:
            alpha = value

        # if PassTd ≥ UseTd thì cắt tỉa
        if alpha >= beta:
            break

    # 5. Trả về VALUE = PassTd, PATH = BEST-PATH (ở đây PATH chỉ là cột tốt nhất)
    return best_col, value


    


def choose_best_action(
    state: BoardState, piece: int, depth: int, allowed_actions: Sequence[int]
) -> Optional[int]:
    """
    Chọn cột tốt nhất dùng bởi Player.
    Trả về cột tốt nhất để đi, hoặc None nếu không còn nước đi hợp lệ.
    """
    board = _copy_board(state)

    if not allowed_actions:
        return None
        
    best_col, _ = _minimax(board, depth, -math.inf, math.inf, True, piece)
    
    return best_col

