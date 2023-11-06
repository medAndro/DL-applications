import copy
from collections import deque

# BFS 탐색, 블록과 보드로 막힌 공간 찾기
def bfs(board):
    dx = [-1, 1, 0, 0]
    dy = [0, 0, -1, 1]
    height, width = len(board), len(board[0])
    visited = [[False] * width for _ in range(height)]
    result = []

    for h in range(height):
        for w in range(width):
            if board[h][w] == 0 and not visited[h][w]:

                qu = deque()
                qu.append((h, w))

                visited[h][w] = True
                blocked_space = [(h, w)]

                while qu:
                    x, y = qu.popleft()
                    for i in range(4):
                        nx, ny = x + dx[i], y+dy[i]
                        if 0 <= nx < height and 0 <= ny < width and board[nx][ny] == 0 and not visited[nx][ny]:
                            visited[nx][ny] = True
                            blocked_space.append((nx, ny))
                            qu.append((nx, ny))
                result.append(blocked_space)
    return result


# 맨 앞을 포함한 곳 제외하고 실제로 막힌 공간 찾기
def get_blocked_space(result, height):
    check = set()
    for idx, space in enumerate(result):
        for x, y in space:
            if x == height-1:
                check.add(idx)
    for idx in sorted(list(check), reverse=True):
        del result[idx]
    return result

# 막힌 공간 -1로 채우기
def mark_blocked_space(board, result):
    for res in result:
        for x, y in res:
            board[x][y] = -1
    return board


class PentominoPiece:
    def __init__(self, shape):
        self.original_shape = shape
        self.current_shape = shape

    def rotate(self):
        self.current_shape = [(j, -i) for i, j in self.current_shape]

class Container:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0] * width for _ in range(height)]

    def can_place(self, piece, x, y):
        for i, j in piece.current_shape:
            if x + j >= self.width or y + i >= self.height or self.grid[y + i][x + j] != 0:
                return False
        return True

    def place_piece(self, piece, x, y, num):
        for i, j in piece.current_shape:
            self.grid[y + i][x + j] = num

    def remaining_space_after_placement(self, piece, x, y):
        remaining_space = 0
        for i, j in piece.current_shape:
            if self.grid[y + i][x + j] == 0:
                remaining_space += 1

        return remaining_space


def best_fit_algorithm(container, pieces, piece_num_list):
    global cnt_piece
    for piece, num in zip(pieces, pentomino_pieces_num_list):
        # 현재 보드판 복사
        prev_container_grid = copy.deepcopy(container.grid)
        for _ in range(4):
            best_fit_x, best_fit_y = None, None
            best_fit_remaining_space = float('inf')

            for y in range(container.height - max(i for i, _ in piece.current_shape) + 1):
                for x in range(container.width - max(j for _, j in piece.current_shape) + 1):
                    if container.can_place(piece, x, y):
                        remaining_space = container.remaining_space_after_placement(piece, x, y)

                        if remaining_space < best_fit_remaining_space:
                            best_fit_x, best_fit_y = x, y
                            best_fit_remaining_space = remaining_space

            if best_fit_x is not None and best_fit_y is not None:
                container.place_piece(piece, best_fit_x, best_fit_y, num)

                # 조각이 맨 아래 행에 닿으면 종료
                if best_fit_y + max(i for i, _ in piece.current_shape) == container.height - 1:
                    return container.grid

                break

            piece.rotate()

        # 조각을 못 놓았다면 게임 종료 (이전 보드판 = 현재 보드판)
        if prev_container_grid == container.grid:
            break

        ## 막힌 공간 마킹 ##
        blocked_space_list = bfs(container.grid)
        real_blocked_space = get_blocked_space(blocked_space_list, len(container.grid))
        container.grid = mark_blocked_space(container.grid, real_blocked_space)

        cnt_piece += 1


    return container.grid


shape_dict = {
    1: [(0, 0), (0, 1), (1, 0), (1, 1)], # 1: ㅁ 모양
    2: [(0, 0), (0, 1), (0, 2), (1, 1)], # 2: ㅜ 모양
    3: [(0, 0)], # 3: 1*1
    4: [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)], # 4: ㅁㅁ 모양
    5: [(0, 0), (0, 1), (0, 2), (0, 3)], # 5: --- 모양
    6: [(0, 3), (1, 0), (1, 1), (1, 2), (1, 3)], # 6: __| 모양
    7: [(0, 0), (1, 0), (1, 1), (1, 2)] # 7: ㄴ 모양
}



data_list = ['output_20231031191113.txt', 'output_20231031191136.txt', 'output_20231031191225.txt',
            'output_20231031191237.txt', 'output_20231031191249.txt', 'output_20231031191315.txt',
            'output_20231031191326.txt', 'output_20231031191336.txt', 'output_20231031191348.txt',
            'output_20231031191441.txt', 'output_20231031191453.txt']


result= []

for data_name in data_list:
    print(data_name)
    data = ''
    with open(f'Simulate_data\{data_name}') as f:
        for line in f:
            data += line
    data = data[data.find('Used')+13:-1] # Used piece만 추출
    data = eval(data) # 리스트 객체로

    data_piece_num = [] # 조각 번호로 기억하기

    for i in data:
        data_piece_num.append(max(i[0]))

    container = Container(width=15, height=20)
    pentomino_pieces = []
    pentomino_pieces_num_list = []
    cnt_piece = 0

    for i in range(len(data_piece_num)):
        pentomino_pieces.append(PentominoPiece(shape= shape_dict[data_piece_num[i]]))
        pentomino_pieces_num_list.append(data_piece_num[i])


    # Best Fit 알고리즘 실행
    result_grid = best_fit_algorithm(container, pentomino_pieces, pentomino_pieces_num_list)

    for  i in range(len(result_grid)):
        for j in range(len(result_grid[0])):
            if result_grid[i][j] == -1:
                result_grid[i][j] = 0 # 마킹한 곳 다시 0으로 
                
    result.append(result_grid)

    # 결과 출력
    for row in result_grid:
        print(*row)

    print('사용한 조각 :', cnt_piece)
    print()
