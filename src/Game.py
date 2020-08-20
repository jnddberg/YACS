import copy
import enum


class ChessState(enum.Enum):
    inProgress = 1
    blackChecked = 2
    whiteChecked = 3
    blackCheckmated = 4
    whiteCheckmated = 5
    draw = 6


class PieceType(enum.Enum):
    empty = 0
    pawn = 1
    king = 2
    queen = 3
    rook = 4
    bishop = 5
    knight = 6


class Pos:
    colDict = {
        "A": 1,
        "B": 2,
        "C": 3,
        "D": 4,
        "E": 5,
        "F": 6,
        "G": 7,
        "H": 8,
    }

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def getPosAsPair(self):
        return self.colDict.get(self.col), self.row


class Color:
    # Black is false
    def __init__(self, color):
        self.color = color

    def setColor(self, color):
        self.color = color

    def getColor(self) -> bool:
        return self.color


class Piece:
    def __init__(self, row, column, active, pieceType, color):
        self.pos = Pos(row, column)
        self.active = active
        self.pieceType = pieceType
        self.color = Color(color)
        self.en_passant = False
        self.can_castle = True

    def setpos(self, pos):
        self.pos = pos

    def getpos(self) -> ():
        return self.pos

    def setActive(self, active):
        self.active = active

    def settype(self, piecetype):
        self.pieceType = piecetype

    def gettype(self):
        return self.pieceType

    def setColor(self, color):
        self.color.setColor(color)

    def getColor(self) -> Color:
        return self.color

    def getActive(self):
        return self.active

    def getEnPassant(self):
        return self.en_passant

    def setEnPassant(self, en_passant):
        self.en_passant = en_passant

    def getCanCastle(self):
        return self.can_castle

    def setCanCastle(self, can_castle):
        self.can_castle = can_castle


class ChessBoard:
    def __init__(self):
        self.tiles = []
        self.whitePieces = []
        self.blackPieces = []
        self.whitePieces.extend([Piece(1, "A", True, PieceType.rook, True),
                                 Piece(1, "B", True, PieceType.knight, True),
                                 Piece(1, "C", True, PieceType.bishop, True),
                                 Piece(1, "D", True, PieceType.queen, True),
                                 Piece(1, "E", True, PieceType.king, True),
                                 Piece(1, "F", True, PieceType.bishop, True),
                                 Piece(1, "G", True, PieceType.knight, True),
                                 Piece(1, "H", True, PieceType.rook, True)])
        self.blackPieces.extend([Piece(8, "A", True, PieceType.rook, False),
                                 Piece(8, "B", True, PieceType.knight, False),
                                 Piece(8, "C", True, PieceType.bishop, False),
                                 Piece(8, "D", True, PieceType.queen, False),
                                 Piece(8, "E", True, PieceType.king, False),
                                 Piece(8, "F", True, PieceType.bishop, False),
                                 Piece(8, "G", True, PieceType.knight, False),
                                 Piece(8, "H", True, PieceType.rook, False)])

        for letter in ["A", "B", "C", "D", "E", "F", "G", "H"]:
            self.blackPieces.append(Piece(7, letter, True, PieceType.pawn, False))
            self.whitePieces.append(Piece(2, letter, True, PieceType.pawn, True))

        self.tiles.append(self.whitePieces[0:8])
        self.tiles.append(self.whitePieces[8:16])

        for i in [3, 4, 5, 6]:
            emptyrow = []
            for letter in ["A", "B", "C", "D", "E", "F", "G", "H"]:
                emptyrow.append(Piece(i, letter, False, PieceType.empty, False))
            self.tiles.append(emptyrow)

        self.tiles.append(self.blackPieces[8:16])
        self.tiles.append(self.blackPieces[0:8])

    def getstate(self):
        logic = ChessLogic()
        return logic.checkState(self)

    def getWhitePieces(self):
        return self.whitePieces

    def getBlackPieces(self):
        return self.blackPieces

    def getpos(self, posx, posy):
        try:
            piece = self.tiles[posy - 1][posx - 1]
        except IndexError:
            return None
        return piece

    def setpos(self, posx, posy, piece: Piece):
        self.tiles[posy - 1][posx - 1] = piece

    def settiles(self, tiles):
        tiles = tiles

    def print(self, color=True):
        playerorder = self.tiles.copy()
        if color:
            playerorder.reverse()
        for row in playerorder:
            for item in row:
                if item is None:
                    print("none,", end="")
                else:
                    if item.getColor().getColor():
                        print("w", end="")
                    else:
                        print("b", end="")
                    print(item.gettype().name + ",", end="")
            print("")


class SpecialMove(enum.Enum):
    king_castle = 0
    queen_castle = 1
    en_passant_trigger = 2
    en_passant = 3


class ChessLogic:

    def __init__(self):
        self.moveHistory = []

    def validateMove(self, startPos, endPos, board: ChessBoard, check_for_check=True):
        # if move is not on board.
        if startPos[0] > 8 or startPos[1] > 8 or endPos[0] > 8 or endPos[1] > 8:
            return False

        piece = board.getpos(startPos[0], startPos[1])

        if piece is None:
            return False

        color = piece.getColor().getColor()
        piece_type = piece.gettype()

        if piece_type == PieceType.empty:
            return False

        if board.getpos(endPos[0], endPos[1]) is None:
            return False

        # if piece at end is same color
        if board.getpos(endPos[0], endPos[1]).gettype() != PieceType.empty \
                and board.getpos(endPos[0], endPos[1]).getColor().getColor() == piece.getColor().getColor():
            return False

        method_dict = {1: self.getValidPawnMoves,
                       2: self.getValidKingMoves,
                       3: self.getValidQueenMoves,
                       4: self.getValidRookMoves,
                       5: self.getValidBishopMoves,
                       6: self.getValidKnightMoves}

        if (startPos, endPos) in method_dict[piece_type.value](startPos, board):
            simboard = self.sim_move(startPos, endPos, board)
            if not check_for_check or not self.inCheck(color, simboard):
                self.moveHistory.append((startPos, endPos, board))
                return simboard
        return False

    def inCheck(self, color, board: ChessBoard):
        king_pos = self.findking(color, board)
        for i in range(len(board.tiles)):
            row = board.tiles[i]
            for j in range(len(row)):
                item = row[j]
                if item.gettype() != PieceType.empty and item.gettype() != PieceType.king:
                    if item.getColor().getColor != color:
                        logic = ChessLogic()
                        if logic.validateMove((j + 1, i + 1), king_pos, board, False):
                            return True

    def sim_move(self, startpos, endpos, board):
        newboard = copy.deepcopy(board)
        piece = newboard.getpos(startpos[0], startpos[1])

        if piece.gettype() == PieceType.king or piece.gettype() == PieceType.rook:
            piece.setCanCastle(False)

        taken_piece = newboard.getpos(endpos[0], endpos[1])
        pivot_pos = taken_piece.getpos()
        taken_piece.setpos(piece.getpos())
        taken_piece.settype(PieceType.empty)
        taken_piece.setActive(False)
        piece.setpos(pivot_pos)
        newboard.setpos(endpos[0], endpos[1], piece)
        newboard.setpos(startpos[0], startpos[1], taken_piece)
        return newboard

    def untriggerEnPassant(self, board, color):
        if color:
            pieces = board.getWhitePieces()
        else:
            pieces = board.getBlackPieces()
        for piece in pieces:
            if piece.gettype() == PieceType.pawn:
                piece.setEnPassant(False)

    def findking(self, color, board):
        for i in range(len(board.tiles)):
            row = board.tiles[i]
            for j in range(len(row)):
                item = row[j]
                if item.gettype() == PieceType.king:
                    if item.getColor().getColor() == color:
                        return j + 1, i + 1

    def getValidPawnMoves(self, startpos, board):
        color = board.getpos(startpos[0], startpos[1]).getColor().getColor()
        if color:
            direction = 1
        else:
            direction = -1
        moves = []
        if board.getpos(startpos[0], startpos[1] + 1 * direction) is not None \
                and board.getpos(startpos[0], startpos[1] + 1 * direction).gettype() == PieceType.empty:
            moves.append((startpos, (startpos[0], startpos[1] + 1 * direction)))

        if ((color and startpos[0] == 2) or (not color and startpos == 7)) \
                and board.getpos(startpos[0], startpos[1] + 2 * direction) is not None \
                and board.getpos(startpos[0], startpos[1] + 1 * direction).gettype() == PieceType.empty \
                and board.getpos(startpos[0], startpos[1] + 2 * direction).gettype() == PieceType.empty:

            en_passant_king_side = board.getpos(startpos[0] + 1, startpos[1] + 2 * direction)
            en_passant_queen_side = board.getpos(startpos[0] - 1, startpos[1] + 2 * direction)

            if self.canEnPassantTrigger(en_passant_king_side, color) \
                    or self.canEnPassantTrigger(en_passant_queen_side, color):
                moves.append((startpos, (startpos[0], startpos[1] + 2 * direction, SpecialMove.en_passant_trigger)))
            else:
                moves.append((startpos, (startpos[0], startpos[1] + 2 * direction)))

        if board.getpos(startpos[0] + 1, startpos[1] + 1 * direction) is not None \
                and board.getpos(startpos[0] + 1, startpos[1] + 1 * direction).gettype() != PieceType.empty \
                and board.getpos(startpos[0] + 1, startpos[1] + 1 * direction).getColor().getColor() != color:
            moves.append((startpos, (startpos[0] + 1, startpos[1] + 1 * direction)))

        if board.getpos(startpos[0] - 1, startpos[1] + 1 * direction) is not None \
                and board.getpos(startpos[0] - 1, startpos[1] + 1 * direction).gettype() != PieceType.empty \
                and board.getpos(startpos[0] - 1, startpos[1] + 1 * direction).getColor().getColor() != color:
            moves.append((startpos, (startpos[0] - 1, startpos[1] + 1 * direction)))

        moves.extend(self.getEnPassant(startpos, color, direction, board))

        return moves

    def canEnPassantTrigger(self, piece, color):
        return piece is not None and piece.gettype() == PieceType.pawn and piece.getColor().getColor() != color

    def getEnPassant(self, startpos, color, direction, board):
        moves = []

        if board.getpos(startpos[0] - 1, startpos[1] + 1 * direction) is not None \
                and board.getpos(startpos[0] - 1, startpos[1] + 1 * direction).gettype() == PieceType.empty \
                and board.getpos(startpos[0] - 1, startpos[1]).getColor().getColor() != color \
                and board.getpos(startpos[0] - 1, startpos[1]).getEnPassant():
            moves.append((startpos, (startpos[0] - 1, startpos[1] + 1 * direction, SpecialMove.en_passant)))

        if board.getpos(startpos[0] + 1, startpos[1] + 1 * direction) is not None \
                and board.getpos(startpos[0] + 1, startpos[1] + 1 * direction).gettype() == PieceType.empty \
                and board.getpos(startpos[0] + 1, startpos[1]).getColor().getColor() != color \
                and board.getpos(startpos[0] + 1, startpos[1]).getEnPassant():
            moves.append((startpos, (startpos[0] + 1, startpos[1] + 1 * direction, SpecialMove.en_passant)))

        return moves

    def getValidKingMoves(self, startpos, board):
        moves = []
        l = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]
        color = board.getpos(startpos[0], startpos[1]).getColor().getColor()
        for pair in l:
            if self.isEnemyOrEmpty(color, (startpos[0] + pair[0], startpos[1] + pair[1]), board):
                moves.append((startpos, (startpos[0] + pair[0], startpos[1] + pair[1])))
        if self.canCastleKingSide(startpos, color, board):
            moves.append((startpos, (startpos[0] + 2, startpos[1], SpecialMove.king_castle)))

        if self.canCastleQueenSide(startpos, color, board):
            moves.append((startpos, (startpos[0] - 2, startpos[1], SpecialMove.queen_castle)))
        return moves

    def canCastleKingSide(self, startpos, color, board):
        if self.inCheck(color, board):
            return False
        rook = board.getpos(8, startpos[1])
        king = board.getpos(startpos[0], startpos[1])
        if rook is None or king is None:
            return False
        if not rook.getCanCastle() or not king.getCanCastle():
            return False
        if not board.getpos(7, startpos[1]).gettype() == PieceType.empty \
                and board.getpos(6, startpos[1]) == PieceType.empty:
            return False
        simboard = self.sim_move(startpos, (6, startpos[1]), board)
        if self.inCheck(color, simboard):
            return False
        return True

    def canCastleQueenSide(self, startpos, color, board):
        if self.inCheck(color, board):
            return False
        rook = board.getpos(1, startpos[1])
        king = board.getpos(startpos[0], startpos[1])
        if rook is None or king is None:
            return False
        if not rook.getCanCastle() or not king.getCanCastle():
            return False
        if not board.getpos(4, startpos[1]).gettype() == PieceType.empty \
                and board.getpos(3, startpos[1]) == PieceType.empty:
            return False
        simboard = self.sim_move(startpos, (4, startpos[1]), board)
        if self.inCheck(color, simboard):
            return False
        return True

    def getValidKnightMoves(self, startpos, board):
        moves = []
        l = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        color = board.getpos(startpos[0], startpos[1]).getColor().getColor()
        for pair in l:
            if self.isEnemyOrEmpty(color, (startpos[0] + pair[0], startpos[1] + pair[1]), board):
                moves.append((startpos, (startpos[0] + pair[0], startpos[1] + pair[1])))
        return moves

    def isEnemyOrEmpty(self, color, endpos, board):
        if board.getpos(endpos[0], endpos[1]) is None:
            return False
        if board.getpos(endpos[0], endpos[1]).gettype() == PieceType.empty:
            return True
        if board.getpos(endpos[0], endpos[1]).getColor().getColor() != color:
            return True
        return False

    def getValidRookMoves(self, startpos, board):
        color = board.getpos(startpos[0], startpos[1]).getColor().getColor()
        moves = []
        moves.extend(self.iterateMoves(board, color, startpos, 1, 0))
        moves.extend(self.iterateMoves(board, color, startpos, -1, 0))
        moves.extend(self.iterateMoves(board, color, startpos, 0, 1))
        moves.extend(self.iterateMoves(board, color, startpos, 1, -1))
        return moves

    def getValidBishopMoves(self, startpos, board):
        color = board.getpos(startpos[0], startpos[1]).getColor().getColor()
        moves = []
        moves.extend(self.iterateMoves(board, color, startpos, 1, 1))
        moves.extend(self.iterateMoves(board, color, startpos, -1, 1))
        moves.extend(self.iterateMoves(board, color, startpos, 1, -1))
        moves.extend(self.iterateMoves(board, color, startpos, -1, -1))
        return moves

    def getValidQueenMoves(self, startpos, board):
        moves = []
        moves.extend(self.getValidBishopMoves(startpos, board))
        moves.extend(self.getValidRookMoves(startpos, board))
        return moves

    def iterateMoves(self, board, color, startpos, horistep, vertstep):
        moves = []

        i, j = startpos[0] + horistep, startpos[1] + vertstep

        while board.getpos(i, j) is not None:
            piece = board.getpos(i, j)
            if piece.gettype() != PieceType.empty:
                if piece.getColor().getColor() != color:
                    moves.append((startpos, (i, j)))
                break
            moves.append((startpos, (i, j)))
            i += horistep
            j += vertstep
        return moves

    def getAnyMoves(self, color, board: ChessBoard):
        if color:
            pieces = board.getWhitePieces()
        else:
            pieces = board.getBlackPieces()

        method_dict = {1: self.getValidPawnMoves,
                       2: self.getValidKingMoves,
                       3: self.getValidQueenMoves,
                       4: self.getValidRookMoves,
                       5: self.getValidBishopMoves,
                       6: self.getValidKnightMoves}

        for piece in pieces:
            if not piece.getActive():
                continue
            startpos = piece.getpos().getPosAsPair()
            piecetype = piece.gettype()
            for move in method_dict[piecetype.value](startpos, board):
                simboard = self.sim_move(move[0], move[1], board)
                if not self.inCheck(color, simboard):
                    return True
        return False

    def checkState(self, board):
        white_has_moves = self.getAnyMoves(True, board)
        black_has_moves = self.getAnyMoves(False, board)
        if self.inCheck(True, board):
            if white_has_moves:
                return ChessState.whiteChecked
            else:
                return ChessState.whiteCheckmated
        if self.inCheck(False, board):
            if black_has_moves:
                return ChessState.blackChecked
            else:
                return ChessState.blackCheckmated
        if not white_has_moves and not black_has_moves:
            return ChessState.draw
        return ChessState.inProgress


class Game:
    board = ChessBoard()
    logic = ChessLogic()
    color = True

    def make_move(self, startpos, endpos):
        piece = self.board.getpos(startpos[0], startpos[1])
        if piece is None:
            return False
        if piece.gettype() == PieceType.empty or self.color != piece.getColor().getColor():
            return False
        move_result = self.logic.validateMove(startpos, endpos, self.board)
        if move_result:
            self.board = move_result
            self.color = not self.color
            return True
        return False

    def print(self):
        self.board.print()


game = Game()

while True:
    if game.color:
        print("White")

    else:
        print("Black")

    print(game.board.getstate().name)

    game.print()
    print()

    start = input()
    start_point = (int(start.split(",")[0]), int(start.split(",")[1]))

    end = input()
    end_point = (int(end.split(",")[0]), int(end.split(",")[1]))

    print("move from " + start + " to " + end)
    print(game.make_move(start_point, end_point))
