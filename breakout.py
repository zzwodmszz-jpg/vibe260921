import tkinter as tk

WIDTH, HEIGHT = 600, 500
PADDLE_W, PADDLE_H = 90, 12
BALL_R = 8
ROWS, COLS = 5, 10
BRICK_W, BRICK_H = 54, 20
BRICK_GAP = 4
COLORS = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db"]


class Breakout:
    def __init__(self, root):
        self.root = root
        root.title("블럭깨기")
        root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack()
        self.left = self.right = False
        root.bind("<KeyPress-Left>", lambda e: self.set_dir(True, None))
        root.bind("<KeyRelease-Left>", lambda e: self.set_dir(False, None))
        root.bind("<KeyPress-Right>", lambda e: self.set_dir(None, True))
        root.bind("<KeyRelease-Right>", lambda e: self.set_dir(None, False))
        root.bind("<space>", self.on_space)
        self.canvas.bind("<Motion>", self.on_mouse)
        self.new_game()
        self.loop()

    def set_dir(self, left, right):
        if left is not None:
            self.left = left
        if right is not None:
            self.right = right

    def new_game(self):
        self.canvas.delete("all")
        self.score = 0
        self.lives = 3
        self.running = False
        self.over = False
        self.bricks = {}
        offset_x = (WIDTH - (COLS * (BRICK_W + BRICK_GAP) - BRICK_GAP)) / 2
        for r in range(ROWS):
            for c in range(COLS):
                x = offset_x + c * (BRICK_W + BRICK_GAP)
                y = 50 + r * (BRICK_H + BRICK_GAP)
                item = self.canvas.create_rectangle(x, y, x + BRICK_W, y + BRICK_H,
                                                    fill=COLORS[r], outline="")
                self.bricks[item] = (x, y, x + BRICK_W, y + BRICK_H)
        px = (WIDTH - PADDLE_W) / 2
        self.paddle = self.canvas.create_rectangle(px, HEIGHT - 40, px + PADDLE_W, HEIGHT - 40 + PADDLE_H,
                                                   fill="white", outline="")
        self.ball = self.canvas.create_oval(0, 0, BALL_R * 2, BALL_R * 2, fill="white", outline="")
        self.hud = self.canvas.create_text(10, 10, anchor="nw", fill="white",
                                           font=("Arial", 14), text="")
        self.msg = self.canvas.create_text(WIDTH / 2, HEIGHT / 2 + 40, fill="white",
                                           font=("Arial", 16), text="스페이스바로 시작 (← → 또는 마우스로 이동)")
        self.reset_ball()
        self.update_hud()

    def reset_ball(self):
        p = self.canvas.coords(self.paddle)
        cx = (p[0] + p[2]) / 2
        self.canvas.coords(self.ball, cx - BALL_R, p[1] - BALL_R * 2, cx + BALL_R, p[1])
        self.vx, self.vy = 4, -5
        self.running = False

    def update_hud(self):
        self.canvas.itemconfig(self.hud, text=f"점수: {self.score}   목숨: {self.lives}")

    def on_space(self, _):
        if self.over:
            self.new_game()
        elif not self.running:
            self.running = True
            self.canvas.itemconfig(self.msg, text="")

    def on_mouse(self, e):
        self.move_paddle_to(e.x - PADDLE_W / 2)

    def move_paddle_to(self, x):
        x = max(0, min(WIDTH - PADDLE_W, x))
        y = self.canvas.coords(self.paddle)[1]
        self.canvas.coords(self.paddle, x, y, x + PADDLE_W, y + PADDLE_H)

    def end(self, text):
        self.over = True
        self.running = False
        self.canvas.itemconfig(self.msg, text=text + "\n스페이스바로 다시 시작")

    def loop(self):
        if self.left:
            self.move_paddle_to(self.canvas.coords(self.paddle)[0] - 8)
        if self.right:
            self.move_paddle_to(self.canvas.coords(self.paddle)[0] + 8)

        if self.running:
            self.step()
        elif not self.over:
            self.reset_ball_follow()
        self.root.after(16, self.loop)

    def reset_ball_follow(self):
        p = self.canvas.coords(self.paddle)
        cx = (p[0] + p[2]) / 2
        self.canvas.coords(self.ball, cx - BALL_R, p[1] - BALL_R * 2, cx + BALL_R, p[1])

    def step(self):
        self.canvas.move(self.ball, self.vx, self.vy)
        x1, y1, x2, y2 = self.canvas.coords(self.ball)

        if x1 <= 0:
            self.vx = abs(self.vx)
        elif x2 >= WIDTH:
            self.vx = -abs(self.vx)
        if y1 <= 0:
            self.vy = abs(self.vy)

        # 패들 충돌
        px1, py1, px2, py2 = self.canvas.coords(self.paddle)
        if self.vy > 0 and y2 >= py1 and y1 <= py2 and x2 >= px1 and x1 <= px2:
            hit = ((x1 + x2) / 2 - (px1 + px2) / 2) / (PADDLE_W / 2)
            speed = (self.vx ** 2 + self.vy ** 2) ** 0.5
            self.vx = hit * 6
            self.vy = -max(3, (speed ** 2 - self.vx ** 2) ** 0.5) if speed ** 2 > self.vx ** 2 else -3
            self.canvas.move(self.ball, 0, py1 - y2)

        # 블럭 충돌
        for item, (bx1, by1, bx2, by2) in list(self.bricks.items()):
            if x2 >= bx1 and x1 <= bx2 and y2 >= by1 and y1 <= by2:
                overlap_x = min(x2 - bx1, bx2 - x1)
                overlap_y = min(y2 - by1, by2 - y1)
                if overlap_x < overlap_y:
                    self.vx = -self.vx
                else:
                    self.vy = -self.vy
                self.canvas.delete(item)
                del self.bricks[item]
                self.score += 10
                self.update_hud()
                break

        if not self.bricks:
            self.end("클리어! 🎉")
            return

        # 바닥
        if y1 >= HEIGHT:
            self.lives -= 1
            self.update_hud()
            if self.lives <= 0:
                self.end("게임 오버")
            else:
                self.reset_ball()
                self.canvas.itemconfig(self.msg, text="스페이스바로 계속")


if __name__ == "__main__":
    root = tk.Tk()
    Breakout(root)
    root.mainloop()
