# Giải thích chi tiết `Minimax/minimax.py`

Tài liệu này mô tả từng hàm trong bộ giải Minimax cho trò chơi Connect 4. Ký hiệu bảng (`BoardState`) là ma trận 2D (hàng, cột) với giá trị: `0` ô trống, `1` và `2` là quân của hai người chơi.

Chú thích: `piece` là quân của người chơi hiện tại. (Player hoặc Agent)

## Các hàm tiện ích

- `_copy_board(state: Sequence[Sequence[int]]) -> List[List[int]]`  
  Sao chép bảng thành danh sách có thể chỉnh sửa, tránh làm biến đổi trạng thái gốc khi thử nước đi.

- `_opponent(piece: int) -> int`  
  Trả về mã quân đối thủ: nếu `piece == 2` thì trả `1`, ngược lại trả `2`.

- `_valid_actions(board: List[List[int]]) -> List[int]`  
  Liệt kê các cột chưa đầy (ô trên cùng bằng `0`). Duyệt tất cả cột, trả về danh sách chỉ số cột hợp lệ.

- `_drop_piece(board: List[List[int]], col: int, piece: int) -> bool`  
  Thả quân vào cột đã cho trên bản sao bảng (duyệt từ đáy lên). Ghi quân tại ô trống đầu tiên tìm được và trả `True`; nếu cột đầy, trả `False`.

## Kiểm tra thắng và đánh giá

- `_winning_move(board: List[List[int]], piece: int) -> bool`  
  Kiểm tra 4 điều kiện thắng cho `piece`: ngang, dọc, chéo `/`, chéo `\`. Với mỗi hướng, duyệt các cửa sổ 4 ô liên tiếp; trả `True` nếu tất cả đều là `piece`.

- `_evaluate_window(window: List[int], piece: int) -> int`  
  Tính điểm heuristics cho một cửa sổ 4 ô.  
  - Thưởng mạnh: 4 quân (+100000), 3 quân 1 trống (+100), 2 quân 2 trống (+10).  
  - Phạt đe dọa của đối thủ: 3 quân 1 trống (-80), 2 quân 2 trống (-5).  
  Dùng để đánh giá mức độ thuận lợi hay nguy hiểm của mỗi cửa sổ.

- `_score_position(board: List[List[int]], piece: int) -> int`  
  Tổng điểm heuristics của toàn bàn cho `piece`.  
  - Ưu tiên cột giữa: mỗi quân ở cột giữa cộng `6`. (Bởi vì cột giữa là vị trí quan trọng nhất) 
  - Cộng dồn điểm cho mọi cửa sổ 4 ô theo 4 hướng (ngang, dọc, chéo `/`, chéo `\`) bằng `_evaluate_window`.


## Thuật toán Minimax với cắt tỉa alpha-beta

- `_minimax(board, depth, alpha, beta, maximizing_player, piece) -> Tuple[Optional[int], float]`  
  Thực hiện tìm kiếm Minimax có cắt tỉa.  
  - Thứ tự duyệt nước đi ưu tiên gần cột giữa để cắt tỉa tốt hơn.  
  - Điều kiện dừng: `depth == 0` hoặc trạng thái kết thúc. Khi dừng, trả điểm thắng thua tuyệt đối (±1_000_000) nếu phát hiện thắng/thua, hoặc điểm heuristics bằng `_score_position`.  
  - Nhánh **maximizing** (đi của `piece`): thử thả quân, đệ quy giảm `depth`, cập nhật `alpha`, chọn giá trị lớn nhất.  
  - Nhánh **minimizing** (giả lập đối thủ): thả quân đối thủ, cập nhật `beta`, chọn giá trị nhỏ nhất.  
  - Dừng nhánh khi `alpha >= beta` (cắt tỉa). Trả về `(best_col, value)`, trong đó `best_col` có thể là một trong các nước đi hợp lệ; nếu không tìm được, có thể là `None`.

- `choose_best_action(state, piece, depth, allowed_actions) -> Optional[int]`  
  Điểm vào công khai dùng bởi `MinimaxPlayer`.  
  - Sao chép bảng, lọc nước đi theo `allowed_actions` và cột còn trống.  
  - Sắp xếp nước đi theo ưu tiên gần giữa rồi gọi `_minimax` (bắt đầu ở vai trò maximizing).  
  - Nếu cột do `_minimax` trả về không nằm trong `legal`, chọn phương án hợp lệ đầu tiên làm dự phòng. Trả `None` nếu không còn nước đi.

