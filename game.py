import sys
import time
import tkinter as tk
from random import choice, randint, shuffle
from tkinter import messagebox


class ChessChallenge:
    RULES = {
        "FULL_DIAGONAL" : lambda qr, qc, r, c: abs(qr - r) == abs(qc - c),
        "ADJACENT_DIAGONAL" : lambda qr, qc, r, c: qr - 1 <= r <= qr + 1 and qc - 1 <= c <= qc + 1
    }

    def __init__(self, root, size):
        self.size = size  # Tamanho do tabuleiro
        self.root = root
        self.root.title(ChessChallenge.title())
        #FIXME put the window on center of screen
        # screen_width = self.root.winfo_screenwidth()
        # screen_height = self.root.winfo_screenheight()
        window_width = 50 * size
        window_height = 50 * size
        # pos_x = (screen_width // 2 - window_width) // 2
        # pos_y = (screen_height - window_height) // 3
        # self.root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
        self.root.protocol("WM_DELETE_WINDOW", self.close_check_data)
        self.canvas = tk.Canvas(root, width=window_width, height=window_height)
        self.canvas.pack()
        response = messagebox.askyesno("Regras!", "Usar a regra de diagonal adjacente?")
        if response:
            self.diagonal_rule = self.RULES.get("ADJACENT_DIAGONAL")
        else:
            self.diagonal_rule = self.RULES.get("FULL_DIAGONAL")
        self.solution = self.colors = self.queens = []
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.start_time = None

        self.init_board()
        self.update_timer()

    def close_check_data(self):
        answer = messagebox.askyesno("Confirmação", "Você realmente deseja sair do jogo?")
        if answer:
            self.root.destroy()
            sys.exit()

    def init_board(self):
        self.queens.clear()
        self.solution = choice(self.solve_n_queens())
        self.board, self.colors = self.generate_color_regions()
        self.canvas.config(width=50 * self.size, height=50 * self.size)
        self.canvas.delete("all")
        self.display_board()
        self.start_time = time.time()

    def update_timer(self):
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        title = ChessChallenge.title(minutes, seconds)
        self.root.title(title)
        self.root.after(1000, self.update_timer)  # Atualiza a cada 1 segundo

    def solve_n_queens(self):
        """Encontra todas as soluções para o problema das N-rainhas."""

        def is_safe(board, row, col):
            for i in range(row):
                if board[i] == col or abs(board[i] - col) == abs(i - row):
                    return False
            return True

        def backtrack(row, board):
            if row == self.size:
                solutions.append(board[:])
                return
            for col in range(self.size):
                if is_safe(board, row, col):
                    board[row] = col
                    backtrack(row + 1, board)
                    board[row] = -1

        solutions = []
        backtrack(0, [-1] * self.size)
        return solutions

    def generate_distinct_medium_pastel_colors(self):
        """Gera n cores distintas em tons pastéis médios."""
        colors = []
        for _ in range(self.size):
            # Componentes de cor em tons pastéis médios (valores mais equilibrados)
            r = randint(150, 210)
            g = randint(150, 210)
            b = randint(150, 210)

            # Garantir que as cores sejam distintas (diferentes uma das outras)
            while any(
                    abs(r - int(c[1:3], 16)) < 20 and abs(g - int(c[3:5], 16)) < 20 and abs(b - int(c[5:], 16)) < 20 for
                    c in colors):
                r = randint(150, 210)
                g = randint(150, 210)
                b = randint(150, 210)

            colors.append(f"#{r:02x}{g:02x}{b:02x}")
        return colors

    def generate_color_regions(self):
        """Gera as regiões adjacentes de cores no tabuleiro."""
        board = [[-1 for _ in range(self.size)] for _ in range(self.size)]
        colors = self.generate_distinct_medium_pastel_colors()
        for i, col in enumerate(self.solution):
            board[i][col] = i  # Marca as casas das rainhas com seus índices
        adjacents_to_fill = [(row, col) for row in range(self.size) for col in range(self.size) if
                             board[row][col] == -1]

        shuffle(adjacents_to_fill)  # Embaralha a ordem de preenchimento
        while adjacents_to_fill:
            row, col = adjacents_to_fill.pop()
            neighbors = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                r, c = row + dr, col + dc
                if 0 <= r < self.size and 0 <= c < self.size and board[r][c] != -1:
                    neighbors.append(board[r][c])
            if neighbors:
                board[row][col] = choice(neighbors)
            else:
                adjacents_to_fill = [(row, col)] + adjacents_to_fill
        return board, colors

    def display_board(self):
        """Exibe o tabuleiro com cores na interface gráfica."""
        for row in range(self.size):
            for col in range(self.size):
                color = self.colors[self.board[row][col]]
                x1, y1 = col * 50, row * 50
                x2, y2 = x1 + 50, y1 + 50
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
        self.canvas.bind("<Button-1>", self.place_queen)

    def place_queen(self, event):
        col, row = event.x // 50, event.y // 50
        color = self.board[row][col]
        if (row, col, color) in self.queens:
            self.remove_queen(row, col, color)
        elif self.is_safe(row, col, color):
            self.add_queen(row, col, color)
        if len(self.queens) == self.size:
            self.win_message()

    def add_queen(self, row, col, color):
        x1, y1 = col * 50, row * 50
        self.queens.append((row, col, color))
        self.canvas.create_text(x1 + 25, y1 + 25, text="♛", fill="black", font=("Arial", 24), tags=f"queen-{row}-{col}")

    def remove_queen(self, row, col, color):
        self.queens.remove((row, col, color))
        self.canvas.delete(f"queen-{row}-{col}")

    def is_safe(self, row, col, color):
        for q_row, q_col, q_color in self.queens:
            if q_row == row or q_col == col or self.diagonal_rule(q_row, q_col, row, col) or color == q_color:
                return False
        return True

    def win_message(self):
        self.canvas.unbind("<Button-1>")
        response = messagebox.askyesno("Parabéns!", "Você venceu! Deseja jogar novamente com um tabuleiro maior?")
        if response:
            self.next_challenge()
        else:
            self.root.destroy()

    def next_challenge(self):
        self.size += 1
        self.queens.clear()
        self.init_board()

    @staticmethod
    def title(minutes=0, seconds=0):
        return f"Queens - {minutes:02}:{seconds:02}"


def main():
    n = 6  # Tamanho inicial do tabuleiro
    root = tk.Tk()
    _ = ChessChallenge(root, n)
    root.mainloop()


if __name__ == "__main__":
    main()
