import cv2
import torch
import random
import numpy as np
from PIL import Image
from matplotlib import style
from src.Visualization import Visualization

class Pentomino:
    pieces = [
        [[1, 1], [1, 1]],
        [[0, 2, 0], [2, 2, 2]],
        [[3]],
        [[4, 4, 4], [4, 4, 4]],
        [[5, 5, 5, 5]],
        [[0, 0, 0, 6], [6, 6, 6, 6]],
        [[7, 0, 0], [7, 7, 7]]
    ]

    piece_colors = [
        (0, 0, 0),
        (255, 255, 0),
        (147, 88, 254),
        (54, 175, 144),
        (255, 0, 0),
        (102, 217, 238),
        (254, 151, 32),
        (0, 0, 255)
    ]

    def __init__(self, height=20, width=15, block_size=20):
        self.height = height
        self.width = width
        self.block_size = block_size
        self.extra_board = np.ones((self.height * self.block_size, self.width * int(self.block_size / 2), 3), dtype=np.uint8) * np.array([255, 255, 255], dtype=np.uint8)
        self.text_color = (0, 0, 0)

        self.reset()

    def reset(self):
        self.score = 0
        self.pentominoes = 0
        self.cleared = 0
        self.board = [[0] * self.width for _ in range(self.height)]
        self.b = list(range(len(self.pieces)))
        random.shuffle(self.b)
        self.ind = self.b.pop()
        self.current_pos = {"x": self.width // 2 - len(self.piece[0]) // 2, "y": 0}
        self.piece = [row[:] for row in self.pieces[self.ind]]
        self.gameover = False    
        self.filled = 0
        self.blank_count = 0
        self.used = []

        return self.getStateProp(self.board)

    def rotate(self, piece):
        num_rows_orig = num_cols_new = len(piece)
        num_rows_new = len(piece[0])
        rotated_array = []

        for i in range(num_rows_new):
            new_row = [0] * num_cols_new
            for j in range(num_cols_new):
                new_row[j] = piece[(num_rows_orig - 1) - j][i]
            rotated_array.append(new_row)
        return rotated_array

    def getStateProp(self, board):
        lines_cleared, board = self.checkRows(board)
        holes = self.getBlankHole(board)
        bumpiness, height = self.getBumpnHeight(board)

        return torch.FloatTensor([lines_cleared, holes, bumpiness, height])

    def getBlankHole(self, board):
        num_holes = 0
        for col in zip(*board):
            row = 0
            while row < self.height and col[row] == 0:
                row += 1
            num_holes += len([x for x in col[row + 1:] if x == 0])
        return num_holes

    def getBumpnHeight(self, board):
        board = np.array(board)
        mask = board != 0
        invert_heights = np.where(mask.any(axis=0), np.argmax(mask, axis=0), self.height)
        heights = self.height - invert_heights
        total_height = np.sum(heights)
        currs = heights[:-1]
        nexts = heights[1:]
        diffs = np.abs(currs - nexts)
        total_bumpiness = np.sum(diffs)
        return total_bumpiness, total_height

    def getNextState(self):
        states = {}
        piece_id = self.ind
        curr_piece = [row[:] for row in self.piece]
        if piece_id == 0:
            num_rotations = 1
        elif piece_id == 2 or piece_id == 3 or piece_id == 4:
            num_rotations = 2
        else:
            num_rotations = 4

        for i in range(num_rotations):
            valid_xs = self.width - len(curr_piece[0])
            for x in range(valid_xs + 1):
                piece = [row[:] for row in curr_piece]
                pos = {"x": x, "y": 0}
                while not self.checkCol(piece, pos):
                    pos["y"] += 1
                self.trunc(piece, pos)
                board = self.store(piece, pos)
                states[(x, i)] = self.getStateProp(board)
            curr_piece = self.rotate(curr_piece)
        return states

    def getBoardsCurrent(self):
        board = [x[:] for x in self.board]
        for y in range(len(self.piece)):
            for x in range(len(self.piece[y])):
                board[y + self.current_pos["y"]][x + self.current_pos["x"]] = self.piece[y][x]
        return board

    def setNewPiece(self):
        if not len(self.b):
            self.b = list(range(len(self.pieces)))
            random.shuffle(self.b)
        self.ind = self.b.pop()
        self.piece = [row[:] for row in self.pieces[self.ind]]
        self.current_pos = {"x": self.width // 2 - len(self.piece[0]) // 2,
                            "y": 0
                            }
        if self.checkCol(self.piece, self.current_pos):
            self.gameover = True

    def checkCol(self, piece, pos):
        future_y = pos["y"] + 1
        for y in range(len(piece)):
            for x in range(len(piece[y])):
                if future_y + y > self.height - 1 or self.board[future_y + y][pos["x"] + x] and piece[y][x]:
                    return True
        return False

    def trunc(self, piece, pos):
        gameover = False
        last_collision_row = -1
        for y in range(len(piece)):
            for x in range(len(piece[y])):
                if self.board[pos["y"] + y][pos["x"] + x] and piece[y][x]:
                    if y > last_collision_row:
                        last_collision_row = y

        if pos["y"] - (len(piece) - last_collision_row) < 0 and last_collision_row > -1:
            while last_collision_row >= 0 and len(piece) > 1:
                gameover = True
                last_collision_row = -1
                del piece[0]
                for y in range(len(piece)):
                    for x in range(len(piece[y])):
                        if self.board[pos["y"] + y][pos["x"] + x] and piece[y][x] and y > last_collision_row:
                            last_collision_row = y
        return gameover

    def store(self, piece, pos):
        board = [x[:] for x in self.board]
        for y in range(len(piece)):
            for x in range(len(piece[y])):
                if piece[y][x] and not board[y + pos["y"]][x + pos["x"]]:
                    board[y + pos["y"]][x + pos["x"]] = piece[y][x]
        return board

    def checkRows(self, board):
        to_delete = []

        for i, row in enumerate(board[::-1]):
            if 0 not in row:
                to_delete.append(len(board) - 1 - i)
            
        return len(to_delete), board

    def step(self, action, render=True, video=None):
        x, num_rotations = action

        self.current_pos = {"x": x, "y": 0}

        for _ in range(num_rotations):
            self.piece = self.rotate(self.piece)

        while not self.checkCol(self.piece, self.current_pos):
            self.current_pos["y"] = self.current_pos["y"] + 1
            if render:
                visualization.render(video)

        overflow = self.trunc(self.piece, self.current_pos)
        if overflow:
            self.gameover = True

        self.board = self.store(self.piece, self.current_pos)
        self.used.append(self.piece)

        count = 0
        c = 0
        cc = 0
        for i in self.board:
            if 0 not in i:
                count = count + 1
            else:
                cc += i.count(0)

        if count > self.filled:
            c = count - self.filled
            self.filled = count

        score = 10 + c * self.width

        self.score += score
        self.pentominoes += 1
        self.cleared += c

        if not self.gameover:
            self.setNewPiece()

        if self.gameover:
            self.score += self.filled * 10

            if self.filled >= 10:
                ss = (self.filled / 10 - 1) * 10
                self.score += ss * 5
                
            self.score -= 2
            self.score -= cc * 10

        return score, self.gameover, cc
