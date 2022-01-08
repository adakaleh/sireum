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

def transform_board(board, om, moves):
    board = copy_board(board)
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
                    board=transform_board(board, om, [8]),
                    style="push",
                    recurse=False):
                allowed_moves[8] = (om[0]-1, om[1])
        # south
        if piece_at(board, om[0]+1, om[1]) == om_vertical_color:
            # check if this move allows for future moves
            if not recurse or get_allowed_moves(
                    board=transform_board(board, om, [2]),
                    style="push",
                    recurse=False):
                allowed_moves[2] = (om[0]+1, om[1])
        # west
        if piece_at(board, om[0], om[1]-1) == om_horizontal_color:
            # check if this move allows for future moves
            if not recurse or get_allowed_moves(
                    board=transform_board(board, om, [4]),
                    style="push",
                    recurse=False):
                allowed_moves[4] = (om[0], om[1]-1)
        # east
        if piece_at(board, om[0], om[1]+1) == om_horizontal_color:
            # check if this move allows for future moves
            if not recurse or get_allowed_moves(
                    board=transform_board(board, om, [6]),
                    style="push",
                    recurse=False):
                allowed_moves[6] = (om[0], om[1]+1)
        # rotate
        # - Nu se poate executa rotirea piesei Om în două tururi consecutive.
        # - Nu se poate executa rotirea piesei Om dacă rotirea nu poate
        # fi urmată de o deplasare a piesei Om în tura următoare."
        if previous_move != 5:
            if get_allowed_moves(
                    board=transform_board(board, om, [5]),
                    style="push",
                    previous_move=5,
                    recurse=False):
                allowed_moves[5] = om
    else:
        raise Exception("Style not supported.")
    return allowed_moves

def ai(board, style, previous_move=0, ai_player = True, depth = 10):

    # Returns weighted moves:
    #   0 - certain win
    #   0.0001...1 - higher number -> higher chance of losing

    # TODO: replace depth with recursion_budget (to be split among
    # branches and redistributed when appropriate)

    if depth == 0:
        # reached maximum depth, can't explore further;
        # assume this is a losing branch with weight = 5
        return {-1: 0.5}
    om = get_om_position(board)
    # get allowed moves
    allowed_moves = get_allowed_moves(board, style, previous_move)
    if not allowed_moves:
        # if it's the AI's turn, it loses - and viceversa
        return {-1: int(ai_player)}
    weighted_moves = {}
    for move in allowed_moves:
        # get future weighted moves
        future_wm = ai(transform_board(board, om, [move]), style, move, not ai_player, depth - 1)
        if ai_player: # human makes next move
            if all(m == 0 for m in future_wm.values()):
                # all moves are losing moves for the human;
                # this is a wining branch for the AI
                weighted_moves[move] = 0
                return weighted_moves # AI will choose this path, no need to continue
            else:
                # calculate move weight based on the proportion of losing moves
                winning_move_count = list(future_wm.values()).count(0)
                weighted_moves[move] = 1 - winning_move_count / len(future_wm)
        else: # AI makes next move
            if 0 in future_wm.values():
                # AI has a winning move;
                # this is a wining branch for the AI
                weighted_moves[move] = 0
            else:
                # calculate move weight based on the proportion of losing moves
                winning_move_count = list(future_wm.values()).count(0)
                weighted_moves[move] = 1 - winning_move_count / len(future_wm)
    return weighted_moves

###############################################


# get parameters from query string
query = parse_qs(os.environ["QUERY_STRING"])

if "opponent" in query and "style" in query and "size" in query:
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
    query_string = urlencode({
        "opponent": query["opponent"][0],
        "style": query["style"][0],
        "board": board_bytes.hex()
    })
    redirect_to("?" + query_string)


elif "opponent" in query and "style" in query and "board" in query:
    opponent = query["opponent"][0]
    style = query["style"][0]
    if opponent not in ("human", "computer"):
        respond("opponent can only be human or computer")
    if style != "push":
        respond("only push style is currently supported")
    initial_board_state = board_from_hex_string(query["board"][0])
    board = copy_board(initial_board_state)
    om = get_om_position(board)
    # we now have the board's initial state;
    # replay previous moves, if any
    previous_moves = []
    if "moves" in query:
        if not query["moves"][0].isdigit():
            respond("moves must be integers")
        previous_moves = list(map(int, query["moves"][0]))
        board = transform_board(board, om, previous_moves)
    previous_move = previous_moves[-1] if previous_moves else 0

    # get allowed moves
    allowed_moves = get_allowed_moves(board, style, previous_move)

    if allowed_moves and query["opponent"][0] == "computer":
        if len(previous_moves) % 2: # AI - odd moves, human - even moves
            if len(board) == 5:
                # table is small, AI can afford to predict the entire game
                ai_moves = ai(board, style, previous_move, depth=100)
            else:
                # table is large, limit the AI to a reasonable depth
                ai_moves = ai(board, style, previous_move, depth=10)
            # choose move with smallest weight
            move = min(list(ai_moves), key=ai_moves.get)
            new_query = {
                "opponent": opponent,
                "style": style,
                "board": query["board"][0],
                "moves": query["moves"][0] + str(move),
            }
            if ai_moves[move] == 0:
                new_query["ai_win"] = 1
            redirect_to("?" + urlencode(new_query))

    # display board
    board_html = "<center>"
    # - heading
    if allowed_moves:
        player = int(len(previous_moves) % 2) + 1
        ai_win_indicator = ""
        if "ai_win" in query and query["ai_win"][0] == "1":
            ai_win_indicator = "<h4>The AI will win.</h4>"
        board_html += f"""<h2>Player: {player} \
| Turn: {len(previous_moves) + 1} \
| <a href="{os.environ["SCRIPT_NAME"]}">Home</a></h2>{ai_win_indicator}"""
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
                        "opponent": query["opponent"][0],
                        "style": query["style"][0],
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
    <legend>Opponent</legend>
    <label>
      <input type="radio" name="opponent" value="human" required checked >
      Human
    </label>
    <label>
      <input type="radio" name="opponent" value="computer" required >
      Computer
    </label>
  </fieldset>

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
