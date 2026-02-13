import random as rand
import os
import json
import sys
import time
import datetime
import colorama
import hashlib

from colorama import Fore, Style, init

init(autoreset=True)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def resize_terminal(cols, rows):
    sys.stdout.write(f"\x1b[8;{rows};{cols}t")
    sys.stdout.flush()

def resize_window(board_size):
    cols = max(50, (board_size * 2) + 5)
    lines = max(10, board_size + 20)
    resize_terminal(cols, lines)

def board_size():
    while True:
        try:
            size = int(input("Enter board size (5-20): "))
            if 5 <= size <= 20:
                return size
            else:
                print(Fore.RED + "Size must be between 5 and 20.")
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number.")

def board_difficulty():
    while True:
        difficulty = input("Select difficulty - Easy (E), Medium (M), Hard (H): ").upper()
        if difficulty in ['E', 'M', 'H']:
            return difficulty
        else:
            print(Fore.RED + "Invalid choice. Please select E, M, or H.")

def board_seed():
    seed_input = input("Enter a Seed (Leave blank for random): ").strip()

    if seed_input == "":
        current_seed = str(int(time.time()))
    else:
        current_seed = seed_input

    hashed_seed = hashlib.sha256(current_seed.encode()).hexdigest()[:8]
    rand.seed(hashed_seed)
    return hashed_seed, seed_input if seed_input != "" else current_seed

def color_cell(cell):
    colors = {
        "[X]": Fore.LIGHTBLACK_EX, "[F]": Fore.LIGHTRED_EX, "[M]": Fore.RED,
        "[0]": Fore.WHITE, "[1]": Fore.BLUE, "[2]": Fore.GREEN,
        "[3]": Fore.YELLOW, "[4]": Fore.MAGENTA, "[5]": Fore.CYAN,
        "[6]": Fore.LIGHTRED_EX, "[7]": Fore.LIGHTBLUE_EX, "[8]": Fore.LIGHTGREEN_EX
    }
    return colors.get(cell, "") + cell + Style.RESET_ALL

def create_board(size):
    return [[0 for _ in range(size)] for _ in range(size)]

def place_mines(board, num_mines, size, safe_row, safe_col):
    mines = 0
    while mines < num_mines:
        row = rand.randint(0, size - 1)
        col = rand.randint(0, size - 1)
        if board[row][col] != "[M]" and not (row == safe_row and col == safe_col):
            board[row][col] = "[M]"
            mines += 1
    return board

def update_numbers(board, size):
    for row in range(size):
        for col in range(size):
            if board[row][col] == "[M]":
                continue
            count = 0
            for i in range(max(0, row - 1), min(size, row + 2)):
                for j in range(max(0, col - 1), min(size, col + 2)):
                    if board[i][j] == "[M]":
                        count += 1
            board[row][col] = f"[{count}]"
    return board

def display_board(player_board, size):
    # Print column headers
    header = "   " + "".join([f"{i:2} " for i in range(size)])
    print(Fore.YELLOW + header)
    
    for r in range(size):
        # Print row header
        row_str = Fore.YELLOW + f"{r:2} " + Style.RESET_ALL
        for c in range(size):
            row_str += color_cell(player_board[r][c])
        print(row_str)

def flood_reveal(board, revealed, row, col, size):
    if not (0 <= row < size and 0 <= col < size) or revealed[row][col]:
        return
    
    revealed[row][col] = True
    
    if board[row][col] == "[0]":
        for i in range(max(0, row - 1), min(size, row + 2)):
            for j in range(max(0, col - 1), min(size, col + 2)):
                flood_reveal(board, revealed, i, j, size)

def main_menu():
    while True:
        clear_console()
        print(Fore.CYAN + "=== CLI MINESWEEPER ===")
        print("1. Start New Game")
        print("2. Exit")
        choice = input("Select an option: ")
        if choice == '1':
            return
        elif choice == '2':
            sys.exit()

def play_game():
    main_menu()
    size = board_size()
    difficulty = board_difficulty()
    num_mines = int((size ** 2) // {'E': 8, 'M': 6.5, 'H': 5}[difficulty])

    hashed_seed, input_seed = board_seed()
    
    board = create_board(size)
    revealed = [[False for _ in range(size)] for _ in range(size)]
    flags = [[False for _ in range(size)] for _ in range(size)]
    
    resize_window(size)
    
    game_over = False
    first_move = True

    start_time = None
    elapsed_time = 0

    third_recent_move = None
    second_recent_move = None
    first_recent_move = None

    max_flags = num_mines
    num_placed_flags = 0

    while not game_over:
        clear_console()

        if start_time is not None:
            elapsed_time = time.time() - start_time
        formatted_time = str(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
        
        display_matrix = []
        cells_revealed = 0
        for r in range(size):
            row_display = []
            for c in range(size):
                if revealed[r][c]:
                    row_display.append(board[r][c])
                    cells_revealed += 1
                elif flags[r][c]:
                    row_display.append("[F]")
                else:
                    row_display.append("[X]")
            display_matrix.append(row_display)

        if (size * size) - cells_revealed == num_mines:
            clear_console()
            print(Fore.GREEN + "=======================================")
            print(Fore.GREEN + f"        VICTORY! FIELD CLEARED")
            print(Fore.GREEN + "=======================================")
            print(Fore.WHITE + f"  Time: {formatted_time}")
            print(Fore.WHITE + f"  Size: {size}x{size}")
            print(Fore.WHITE + f"  Seed: {input_seed}")
            print(Fore.GREEN + "=======================================\n")
            display_board(board, size)
            break

        print(Fore.CYAN + f"Mines: {num_mines} | Safe cells revealed: {cells_revealed}/{(size*size - num_mines)}")
        print(Fore.CYAN + f"Flags: {num_placed_flags}/{max_flags}")
        print(Fore.CYAN + f"Time Elapsed: {formatted_time}\n")
        print(Fore.CYAN + f"Seed: {input_seed} (Hash: {hashed_seed})\n")
        display_board(display_matrix, size)
        print(Fore.YELLOW + "\nRecent Moves:")
        if first_recent_move: 
            print(Fore.WHITE + f"1. {first_recent_move}")
            if second_recent_move: 
                print(Fore.WHITE + f"2. {second_recent_move}")
                if third_recent_move: 
                    print(Fore.WHITE + f"3. {third_recent_move}")
                else: print(Fore.WHITE + "No earlier moves.")
            else: print(Fore.WHITE + "No earlier moves.")
        else: print(Fore.WHITE + "No moves yet.")
        
        try:
            move = input("\nEnter (r c) or (f r c): ").lower().strip().split()
            if not move: continue
            
            if move[0] == 'f':
                r, c = int(move[1]), int(move[2])
                if not revealed[r][c]: # Can't flag revealed cells
                    if not flags[r][c] and num_placed_flags >= max_flags:
                        print(Fore.RED + "Flag limit reached! Unflag another cell first.")
                        time.sleep(1.5)
                        continue
                    flags[r][c] = not flags[r][c] # Toggle flag
                    # Update flag count
                    if flags[r][c]:
                        num_placed_flags += 1
                        # Update recent moves tracking
                        third_recent_move = second_recent_move
                        second_recent_move = first_recent_move
                        first_recent_move = f"Flagged:   ({Fore.YELLOW + str(r) + Fore.WHITE}, {Fore.YELLOW + str(c) + Fore.WHITE})"
                    else:
                        num_placed_flags -= 1
                        # Update recent moves tracking
                        third_recent_move = second_recent_move
                        second_recent_move = first_recent_move
                        first_recent_move = f"Unflagged: ({Fore.YELLOW + str(r) + Fore.WHITE}, {Fore.YELLOW + str(c) + Fore.WHITE})"
                else:
                    print(Fore.RED + f"Cell ({Fore.WHITE + str(r) + Fore.RED}, {Fore.WHITE + str(c) + Fore.RED}) is already revealed! Can't flag.")
                    time.sleep(1.5)
                continue
            
            r, c = int(move[0]), int(move[1])

            if first_move:
                board = place_mines(board, num_mines, size, r, c)
                board = update_numbers(board, size)
                start_time = time.time()
                first_move = False
            if flags[r][c]:
                print(Fore.RED + f"Cell ({Fore.WHITE + str(r) + Fore.RED}, {Fore.WHITE + str(c) + Fore.RED}) is flagged! Unflag it first.")
                time.sleep(1.5)
                continue
            third_recent_move = second_recent_move
            second_recent_move = first_recent_move
            first_recent_move = f"Revealed:  ({Fore.YELLOW + str(r) + Fore.WHITE}, {Fore.YELLOW + str(c) + Fore.WHITE})"
            if board[r][c] == "[M]":
                if start_time:
                    elapsed_time = time.time() - start_time
                formatted_time = str(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
                
                clear_console()

                correct_flags = 0
                for row_idx in range(size):
                    for col_idx in range(size):
                        if flags[row_idx][col_idx] and board[row_idx][col_idx] == "[M]":
                            correct_flags += 1
                
                print(Fore.RED + "=======================================")
                print(Fore.RED + "        GAME OVER - BOOM!")
                print(Fore.RED + "=======================================")
                print(Fore.WHITE + f"  Time Survived:      {formatted_time}")
                print(Fore.WHITE + f"  Mines Identified:   {correct_flags}/{num_mines}")
                print(Fore.WHITE + f"  Size:               {size}x{size}")
                print(Fore.WHITE + f"  Seed:               {input_seed}")
                print(Fore.RED + "=======================================\n")
                display_board(board, size)
                game_over = True
            else:
                flood_reveal(board, revealed, r, c, size)

        except (ValueError, IndexError):
            print(Fore.RED + "Invalid input.")
            time.sleep(1.5)

    input("\nPress Enter...")
    return play_game()

if __name__ == "__main__":
    play_game()