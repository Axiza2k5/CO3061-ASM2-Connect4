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

    return (
        any(
            # ngang
            all(board[r][c + i] == piece for i in range(4))  
            for r in range(rows)
            for c in range(cols - 3)    # ô đầu tiên phải thuộc cột [0,2] để có thể tạo thành cửa sổ 4 ô liên tiếp
        )
        or any(
            # dọc
            all(board[r + i][c] == piece for i in range(4))
            for c in range(cols)
            for r in range(rows - 3)    # ô đầu tiên phải thuộc hàng [0,2] để có thể tạo thành cửa sổ 4 ô liên tiếp
        )
        or any(
            # chéo /
            all(board[r - i][c + i] == piece for i in range(4))
            for r in range(3, rows)
            for c in range(cols - 3)
        )
        or any(
            # chéo \
            all(board[r + i][c + i] == piece for i in range(4))
            for r in range(rows - 3)
            for c in range(cols - 3)
        )
    )


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
    rows = len(board)
    cols = len(board[0])
    center_col = cols // 2

    center_bonus = sum(board[r][center_col] == piece for r in range(rows)) * 6

    horizontal = sum(
        _evaluate_window(board[r][c : c + 4], piece)
        for r in range(rows)
        for c in range(cols - 3)
    )

    vertical = sum(
        _evaluate_window([board[r + i][c] for i in range(4)], piece)
        for c in range(cols)
        for r in range(rows - 3)
    )

    diag_pos = sum(
        _evaluate_window([board[r - i][c + i] for i in range(4)], piece)
        for r in range(3, rows)
        for c in range(cols - 3)
    )

    diag_neg = sum(
        _evaluate_window([board[r + i][c + i] for i in range(4)], piece)
        for r in range(rows - 3)
        for c in range(cols - 3)
    )

    return center_bonus + horizontal + vertical + diag_pos + diag_neg


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

    self_win = _winning_move(board, piece)
    opp_win = _winning_move(board, opp)
    if self_win:
        return None, 1_000_000
    if opp_win:
        return None, -1_000_000
    if depth == 0 or not valid_cols:
        return None, _score_position(board, piece)

    if maximizing_player:
        """Nhánh maximizing"""
        value = -math.inf
        best_col = random.choice(valid_cols) if valid_cols else None
        for col in valid_cols:
            temp_board = _copy_board(board)
            _drop_piece(temp_board, col, piece)
            _, new_score = _minimax(temp_board, depth - 1, alpha, beta, False, piece)
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value

    """Nhánh minimizing (giả lập đối thủ)"""
    value = math.inf
    best_col = random.choice(valid_cols) if valid_cols else None
    for col in valid_cols:
        temp_board = _copy_board(board)
        _drop_piece(temp_board, col, opp)
        _, new_score = _minimax(temp_board, depth - 1, alpha, beta, True, piece)
        if new_score < value:
            value = new_score
            best_col = col
        beta = min(beta, value)
        if alpha >= beta:
            break
    return best_col, value


def choose_best_action(
    state: BoardState, piece: int, depth: int, allowed_actions: Sequence[int]
) -> Optional[int]:
    """
    Chọn cột tốt nhất dùng bởi Player.
    Trả về cột tốt nhất để đi, hoặc None nếu không còn nước đi hợp lệ.
    """
    board = _copy_board(state)
    allowed = set(allowed_actions)
    legal = [c for c in _valid_actions(board) if c in allowed]
    if not legal:
        return None

    # Sắp xếp nước đi để cắt tỉa tốt hơn (ưu tiên cột giữa)
    legal.sort(key=lambda c: abs((len(board[0]) // 2) - c))
    best_col, _ = _minimax(board, depth, -math.inf, math.inf, True, piece)
    if best_col not in legal:
        # Trở về nước đi hợp lệ tốt nhất nếu cắt tỉa chọn một nước đi không hợp lệ
        best_col = legal[0]
    return best_col

