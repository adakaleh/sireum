#!/usr/bin/env python3

import os
import math
from urllib.parse import parse_qs, urlencode

# CGI debugging
#import cgitb
#cgitb.enable()

EMPTY = 0
BLUE = 1
RED = 2
OM1 = 3 # push: blue vertical, red horizontal | flip: blue
OM2 = 4 # push: blue horizontal, red vertical | flip: red

response_start = """Content-Type: text/html
X-Robots-Tag: none
X-Accel-Buffering: no

<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="referrer" content="no-referrer">
  <link rel="icon" type="image/ico" href="favicon.ico">
  <title>Sireum</title>
  <style>
    table {
      width: 80vmin;
      max-height: 80vmin;
      max-width: 90%;
      border-collapse: collapse;
    }
    td {
      position: relative;
    }
    td:after {
      content: "";
      display: block;
      margin-top: 100%;
    }
    td span {
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
    }

    .allowed {
      background-color: #0f0;
    }
    .piece {
      color: transparent;
      border-radius: 50%;
    }
    .red {
      background-color: red;
    }
    .blue {
      background-color: blue;
    }
    .om {
      border-radius: 25%;
      border-style: solid;
    }
    .om1 {
      border-top-color: blue;
      border-bottom-color: blue;
      border-left-color: red;
      border-right-color: red;
    }
    .om2 {
      border-top-color: red;
      border-bottom-color: red;
      border-left-color: blue;
      border-right-color: blue;
    }
  </style>
</head>
<body>
"""

def respond(response):
    print(response_start)
    print(response)
    quit()

def redirect_to(url):
    print(f"""Status: 302
Location: {url}\n""")


def board_from_hex_string(hex_string):
    try:
        board_int = int(hex_string, 16)
    except ValueError:
        respond("board does not have a valid hexadecimal value")
    # get board size
    size = 0
    for i in range(5, 20, 2):
        if math.ceil(i ** 2 / 8) == len(hex_string) / 2:
            size = i
            break
    if not size:
        respond("board size out of bounds")
    # get board bits
    board_bits = format(board_int, "b").zfill(len(hex_string) * 4)
    # derive board matrix
    board = []
    for i in range(size):
        board.append([])
    for i in range(size ** 2):
        board[math.floor(i / size)].append(int(board_bits[i]) + 1)
    board[math.floor(size / 2)][math.floor(size / 2)] = OM1
    return board

def get_om_position(board):
    for i, row in enumerate(board):
        for j, item in enumerate(board[i]):
            if item == OM1 or item == OM2:
                return (i, j)

def piece_at(board, row, col):
    if -1 < row < len(board) and -1 < col < len(board[row]):
        return board[row][col]
    return EMPTY

def copy_board(board):
    new_board = []
    for row in board:
        new_board.append(row.copy())
    return new_board

def transform_board(board, moves):
    board = copy_board(board)
    om = get_om_position(board)
    for move in moves:
        # north
        if move == 8 and piece_at(board, om[0]-1, om[1]):
            board[om[0]-1][om[1]] = board[om[0]][om[1]]
            board[om[0]][om[1]] = EMPTY
            om = (om[0]-1, om[1])
        # south
        elif move == 2 and piece_at(board, om[0]+1, om[1]):
            board[om[0]+1][om[1]] = board[om[0]][om[1]]
            board[om[0]][om[1]] = EMPTY
            om = (om[0]+1, om[1])
        # east
        elif move == 4 and piece_at(board, om[0], om[1]-1):
            board[om[0]][om[1]-1] = board[om[0]][om[1]]
            board[om[0]][om[1]] = EMPTY
            om = (om[0], om[1]-1)
        # west
        elif move == 6 and piece_at(board, om[0], om[1]+1):
            board[om[0]][om[1]+1] = board[om[0]][om[1]]
            board[om[0]][om[1]] = EMPTY
            om = (om[0], om[1]+1)
        # rotate / flip
        elif move == 5:
            if board[om[0]][om[1]] == OM1:
                board[om[0]][om[1]] = OM2
            else:
                board[om[0]][om[1]] = OM1
    return board

def get_allowed_moves(board, style, previous_move=0, recurse=True):
    allowed_moves = {}
    om = get_om_position(board)
    if style == "push":
        if board[om[0]][om[1]] == OM1:
            om_vertical_color = BLUE
            om_horizontal_color = RED
        else:
            om_vertical_color = RED
            om_horizontal_color = BLUE
        # north
        if piece_at(board, om[0]-1, om[1]) == om_vertical_color:
            # check if this move allows for future moves
            if not recurse or get_allowed_moves(
                    board=transform_board(board, [8]),
                    style="push",
                    recurse=False):
                allowed_moves[8] = (om[0]-1, om[1])
        # south
        if piece_at(board, om[0]+1, om[1]) == om_vertical_color:
            # check if this move allows for future moves
            if not recurse or get_allowed_moves(
                    board=transform_board(board, [2]),
                    style="push",
                    recurse=False):
                allowed_moves[2] = (om[0]+1, om[1])
        # west
        if piece_at(board, om[0], om[1]-1) == om_horizontal_color:
            # check if this move allows for future moves
            if not recurse or get_allowed_moves(
                    board=transform_board(board, [4]),
                    style="push",
                    recurse=False):
                allowed_moves[4] = (om[0], om[1]-1)
        # east
        if piece_at(board, om[0], om[1]+1) == om_horizontal_color:
            # check if this move allows for future moves
            if not recurse or get_allowed_moves(
                    board=transform_board(board, [6]),
                    style="push",
                    recurse=False):
                allowed_moves[6] = (om[0], om[1]+1)
        # rotate
        # - Nu se poate executa rotirea piesei Om în două tururi consecutive.
        # - Nu se poate executa rotirea piesei Om dacă rotirea nu poate
        # fi urmată de o deplasare a piesei Om în tura următoare."
        if previous_move != 5:
            if get_allowed_moves(
                    board=transform_board(board, [5]),
                    style="push",
                    previous_move=5,
                    recurse=False):
                allowed_moves[5] = om
    else:
        raise Exception("Style not supported.")
    return allowed_moves


###############################################


# get parameters from query string
query = parse_qs(os.environ["QUERY_STRING"])

if "style" in query and "size" in query:
    # redirect to ?board=<random>, where
    # <random> = size * size random bits, hex-encoded
    try:
        size = int(query["size"][0])
    except ValueError:
        respond("size must be an integer")
    if size < 5:
        respond("size must be at least 5")
    if size > 19:
        respond("size must be no more than 19")
    if size % 2 == 0:
        respond("size must be an odd number")
    nbits = size ** 2
    nbytes = math.ceil(nbits / 8) # the last few bits will be ignored
    board_bytes = os.urandom(nbytes)
    redirect_to("?board=" + board_bytes.hex())

elif "board" in query:
    initial_board_state = board_from_hex_string(query["board"][0])
    board = copy_board(initial_board_state)
    # we now have the board's initial state;
    # replay previous moves, if any
    previous_moves = []
    if "moves" in query:
        if not query["moves"][0].isdigit():
            respond("moves must be integers")
        previous_moves = list(map(int, query["moves"][0]))
        board = transform_board(board, previous_moves)
    # get allowed moves
    allowed_moves = get_allowed_moves(
            board = board,
            style = "push",
            previous_move = previous_moves[-1] if previous_moves else 0
        )
    # display board
    board_html = "<center>"
    # - heading
    if allowed_moves:
        player = int(len(previous_moves) % 2) + 1
        board_html += f"""<h2>Player: {player} \
| Turn: {len(previous_moves) + 1} \
| <a href="{os.environ["SCRIPT_NAME"]}">Home</a></h2>"""
    else:
        winner = int(not len(previous_moves) % 2) + 1
        board_html += f"""<h2>Player {winner} wins!
| <a href="{os.environ["SCRIPT_NAME"]}">New game</a></h2>"""
    # - get widths for CSS
    piece_width = 100 / len(board) # percent
    om_border_width = 40 / len(board) # board width = 80 vmin
    board_html += f"""
    <style>
      td {{
        width: {piece_width}%;
      }}
      .om {{
        border-width: {om_border_width}vmin;
      }}
    </style>"""
    # - start table
    board_html += "<table>"
    for i in range(len(board)):
        board_html += "<tr>"
        for j in range(len(board[i])):
            # - make links for allowed moves ("?query_string")
            query_string = ""
            for allowed_move, allowed_position in allowed_moves.items():
                if (i, j) == allowed_position:
                    moves = str(allowed_move)
                    if "moves" in query:
                        moves = query["moves"][0] + moves
                    query_string = urlencode({
                        "board": query["board"][0],
                        "moves": moves,
                    })
                    break
            # - draw pieces
            piece = " "
            if board[i][j] == RED:
                piece = '<span class="piece red">🔴</span>'
            elif board[i][j] == BLUE:
                piece = '<span class="piece blue">🔵</span>'
            elif board[i][j] == OM1:
                piece = '<span class="piece om om1">🔃</span>'
            elif board[i][j] == OM2:
                piece = '<span class="piece om om2">🔁</span>'
            if query_string:
                board_html += f'<td class="allowed"><a href="?{query_string}">{piece}</a></td>'
            else:
                board_html += f"<td>{piece}</td>"
        board_html += "</tr>"
    board_html += "</table>"
    board_html += "</center>"
    respond(board_html)

else:
    # home page
    respond("""
<h1>Sireum</h1>
<p><a href="https://leftclickghinea.ro/sireum-prezentare/">About</a>
    | <a href="https://github.com/adakaleh/sireum">Code</a></p>
<form>
  <fieldset>
    <legend>Game Style</legend>
    <label>
      <input type="radio" name="style" value="push" required checked >
      Push
    </label>
    <label>
      <input type="radio" name="style" value="flip" required disabled >
      Flip
    </label>
  </fieldset>

  <fieldset>
    <legend>Board Size</legend>
    <label>
      <input type="radio" name="size" value="5" required checked >
      5x5
    </label>
    <label>
      <input type="radio" name="size" value="7" required >
      7x7
    </label>
    <label>
      <input type="radio" name="size" value="9" required >
      9x9
    </label>
    <label>
      <input type="radio" name="size" value="11" required >
      11x11
    </label>
  </fieldset>

  <button type="submit">Start</button>
</form>
</body>
</html>""")
