import cv2
import numpy as np
from ultralytics import YOLO
import math
from logging import getLogger

figures_detector = YOLO('./models/best3.pt')
board_detector = YOLO('./models/best_board.pt')
hand_detector = YOLO('yolov8x.pt')

CLASS_NAMES_DICT = {
    'black-bishop': 0,
    'black-king': 1,
    'black-knight': 2,
    'black-pawn': 3,
    'black-queen': 4,
    'black-rook': 5,
    'white-bishop': 6,
    'white-king': 7,
    'white-knight': 8,
    'white-pawn': 9,
    'white-queen': 10,
    'white-rook': 11,
}

logger = getLogger(__name__)


class ChessBoard:
    def __init__(self, x1: int, y1: int, x2: int, y2: int, phi: int):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.phi = phi

        self.top_left = (round(self.x1 + math.tan(self.phi) * (self.y2 - self.y1)), self.y1)
        self.bottom_left = (self.x1, self.y2)
        self.top_right = (self.x2, self.y2)
        self.bottom_right = (round(self.x2 - math.tan(self.phi) * (self.y2 - self.y1)), self.y1)

    def get_trapezoid(self) -> list:
        return [self.top_left, self.bottom_left, self.bottom_right, self.top_right]


class Figure:
    def __init__(self, x1: int, y1: int, x2: int, y2: int, name: str):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.name = name

        self.top_left = (self.x1, self.y1)
        self.bottom_left = (self.x1, self.y2)
        self.top_right = (self.x2, self.y1)
        self.bottom_right = (self.x2, self.y2)

    def get_fullrectangle(self):
        return [self.top_left, self.bottom_left, self.bottom_right, self.top_right]

    def get_part_rectangle(self, part_size: float):
        new_top_left = (self.x1, self.bottom_left[1] - (self.bottom_left[1] - self.top_left[1]) * part_size)
        new_top_right = (self.x2, self.bottom_right[1] - (self.bottom_right[1] - self.top_right[1]) * part_size)
        return [new_top_left, self.bottom_left, self.bottom_right, new_top_right]


class Trash(Figure):
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        super().__init__(x1, y1, x2, y2, '')


def detect_chessboard(img):
    logger.info(f'detecting chessboard in {detect_chessboard.__name__}')
    chess_board_predict = board_detector.predict(img)[0]
    logger.info(f'ready chessboard predict')
    chess_board_box = None
    for box in chess_board_predict.boxes.xyxy.cpu().numpy():
        chess_board_box = list(map(round, box))
    return chess_board_box


def calculate_perspective_transform(chess_board, img_shape):
    height, width = img_shape[:2]
    chess_board_vert = chess_board.get_trapezoid()
    orto_vert_img = np.float32([[0, 0], [0, height], [width, 0], [width, height]])
    perspective_matrix = cv2.getPerspectiveTransform(np.float32(chess_board_vert), orto_vert_img)
    inv_matrix = np.linalg.inv(perspective_matrix)
    return perspective_matrix, inv_matrix


def get_persective_dot(orto_dot_2d, perspective_inv_matrix):
    orto_dot_3d = orto_dot_2d + [1]
    perspective_dot_3d = np.dot(perspective_inv_matrix, orto_dot_3d)
    perspective_dot_3d /= perspective_dot_3d[2]
    return [int(perspective_dot_3d[0]), int(perspective_dot_3d[1])]


def generate_chess_cells(inv_matrix, img_shape):
    height, width = img_shape[:2]
    chess_cell_vert = []
    for row in range(9):
        for col in range(9):
            orto_dot = [width // 8 * col, height // 8 * row]
            perspective_dot = get_persective_dot(orto_dot, inv_matrix)
            chess_cell_vert.append(perspective_dot)
    board_cells = []
    for i in range(len(chess_cell_vert) - 9):
        if i % 9 != 8:
            board_cell = [chess_cell_vert[i], chess_cell_vert[i + 9], chess_cell_vert[i + 10], chess_cell_vert[i + 1]]
            board_cells.append(board_cell)
    return board_cells, chess_cell_vert


def detect_figures(img):
    return figures_detector.predict(img, conf=0.5)[0]


def anylize_hand(chess_board, img):
    height, width = img.shape[:2]
    trapezoid = chess_board.get_trapezoid()

    predict = hand_detector.predict(img, save=True)[0]

    obj = []
    for box in predict.boxes.xyxy.cpu().numpy():
        obj.append(list(map(int, box)))

    obj_box = []
    for object in obj:
        box = Trash(object[0], object[1], object[2], object[3]).get_fullrectangle()
        obj_box.append(box)

    for obj in obj_box:
        figure_mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(figure_mask, np.array([trapezoid], dtype=np.int32), 255)
        cell_mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(cell_mask, np.array([obj], dtype=np.int32), 255)
        intersection = cv2.bitwise_and(cell_mask, figure_mask)
        contours, _ = cv2.findContours(intersection, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            return True


def assign_figures_to_cells(figures, board_cells, img_shape):
    height, width = img_shape[:2]
    figures_board = [[20 for _ in range(8)] for _ in range(8)]
    for figure in figures:
        figure_mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(figure_mask, np.array([figure.get_part_rectangle(0.2)], dtype=np.int32), 255)
        max_interseption = 0
        cell_idx = -1
        for idx, cell in enumerate(board_cells):
            cell_mask = np.zeros((height, width), dtype=np.uint8)
            cv2.fillPoly(cell_mask, np.array([cell], dtype=np.int32), 255)
            intersection = cv2.bitwise_and(cell_mask, figure_mask)
            contours, _ = cv2.findContours(intersection, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                intersection_area = cv2.contourArea(contours[0])
                if intersection_area > max_interseption:
                    max_interseption = intersection_area
                    cell_idx = idx
        figures_board[cell_idx // 8][cell_idx % 8] = CLASS_NAMES_DICT[figure.name]
    return figures_board


def visualize_cells(img, chess_cell_vert):
    for vert in chess_cell_vert:
        cv2.circle(img, vert, 5, (0, 0, 255), -1)


def visualize_figures(img, figures):
    for figure in figures:
        for vert in figure.get_part_rectangle(0.3):
            cv2.circle(img, list(map(int, vert)), 5, (0, 255, 0), -1)


def digitalization(img):
    logger.info('get new image')

    # cv2.imshow('frame', img)
    # cv2.waitKey(1)
    logger.info('detecting chessboard')
    chess_board_box = detect_chessboard(img)
    if chess_board_box is None:
        return None
    angle = np.radians(9)
    chess_board = ChessBoard(*chess_board_box, angle)

    # has_hand = anylize_hand(chess_board, img)
    # if has_hand:
    #     return None
    logger.info('generating perspective matrix')
    perspective_matrix, inv_matrix = calculate_perspective_transform(chess_board, img.shape)
    board_cells, chess_cell_vert = generate_chess_cells(inv_matrix, img.shape)

    logger.info('detecting figures')
    fiqures_predict = detect_figures(img)
    class_names = fiqures_predict.names

    figures = [Figure(*box, class_names[class_idx]) for class_idx, box in
               zip(fiqures_predict.boxes.cls.cpu().numpy().astype(int), fiqures_predict.boxes.xyxy.cpu().numpy())]

    logger.info('assigning figures to cells')
    figures_board = assign_figures_to_cells(figures, board_cells, img.shape)

    figures_board = np.rot90(np.array(figures_board, dtype=np.int32), k=-1)
    logger.info('sending figures')

    visualize_cells(img, chess_cell_vert)
    visualize_figures(img, figures)

    img = cv2.resize(img, (0, 0), fx=1, fy=1)
    cv2.imshow('test2', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return figures_board

    return figures_board
