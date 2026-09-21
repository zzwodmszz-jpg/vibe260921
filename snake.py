import random
import tkinter as tk
from collections import deque

CELL = 20
COLS = 30
ROWS = 20
DELAY = 110  # ms

DIRS = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0),
}
OPPOSITE = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}


def in_bounds(p):
    return 0 <= p[0] < COLS and 0 <= p[1] < ROWS


def add(p, d):
    return (p[0] + DIRS[d][0], p[1] + DIRS[d][1])


class Snake:
    def __init__(self, body, direction, head_color, body_color):
        self.body = body
        self.direction = direction
        self.next_direction = direction
        self.score = 0
        self.alive = True
        self.head_color = head_color
        self.body_color = body_color


class SnakeGame:
    def __init__(self, root):
        self.root = root
        root.title("뱀 게임 - 사람 vs AI")
        root.resizable(False, False)

        self.score_var = tk.StringVar()
        tk.Label(root, textvariable=self.score_var, font=("Arial", 14)).pack()

        self.canvas = tk.Canvas(root, width=COLS * CELL, height=ROWS * CELL, bg="black")
        self.canvas.pack()

        root.bind("<Key>", self.on_key)
        self.reset()

    def reset(self):
        cy = ROWS // 2
        self.human = Snake([(5, cy - 3), (4, cy - 3), (3, cy - 3)], "Right", "lime", "green")
        self.ai = Snake([(COLS - 6, cy + 3), (COLS - 5, cy + 3), (COLS - 4, cy + 3)],
                        "Left", "cyan", "dodgerblue")
        self.game_over = False
        self.paused = False
        self.result = ""
        self.place_food()
        self.update_score()
        self.draw()
        self.root.after(DELAY, self.tick)

    def update_score(self):
        self.score_var.set(
            f"나(초록): {self.human.score}   vs   AI(파랑): {self.ai.score}"
            "   (P: 일시정지, R: 재시작)"
        )

    def place_food(self):
        taken = set(self.human.body) | set(self.ai.body)
        free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in taken]
        self.food = random.choice(free) if free else None

    def on_key(self, event):
        key = event.keysym
        if key in DIRS:
            if key != OPPOSITE[self.human.direction]:
                self.human.next_direction = key
        elif key in ("p", "P"):
            self.paused = not self.paused
        elif key in ("r", "R") and self.game_over:
            self.reset()

    # ---------------- AI ----------------
    def bfs(self, start, goal, blocked):
        """start에서 goal까지의 최단 거리 (도달 불가면 None)."""
        queue = deque([(start, 0)])
        seen = {start}
        while queue:
            pos, dist = queue.popleft()
            if pos == goal:
                return dist
            for d in DIRS:
                nxt = add(pos, d)
                if in_bounds(nxt) and nxt not in blocked and nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, dist + 1))
        return None

    def flood(self, start, blocked):
        """start에서 도달 가능한 칸 수."""
        stack = [start]
        seen = {start}
        while stack:
            pos = stack.pop()
            for d in DIRS:
                nxt = add(pos, d)
                if in_bounds(nxt) and nxt not in blocked and nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return len(seen)

    def ai_choose(self):
        ai, human = self.ai, self.human
        # 꼬리는 다음 턴에 비므로 막힌 칸에서 제외
        blocked = set(ai.body[:-1]) | set(human.body[:-1])
        # 사람 머리가 다음에 갈 수 있는 칸은 정면충돌 위험이 있어 피한다
        danger = {add(human.body[0], d) for d in DIRS if d != OPPOSITE[human.direction]}

        best, best_key = ai.direction, None
        for d in DIRS:
            if d == OPPOSITE[ai.direction]:
                continue
            nxt = add(ai.body[0], d)
            if not in_bounds(nxt) or nxt in blocked:
                continue
            space = self.flood(nxt, blocked)
            safe_space = space >= len(ai.body)
            dist = self.bfs(nxt, self.food, blocked) if self.food else None
            key = (
                nxt not in danger,                       # 충돌 위험 없는 칸 우선
                safe_space,                              # 갇히지 않을 공간 확보
                -(dist if dist is not None else 10**6),  # 사과와 가까울수록 좋음
                space,                                   # 마지막으로 넓은 공간
            )
            if best_key is None or key > best_key:
                best_key, best = key, d
        return best

    # ---------------- 게임 진행 ----------------
    def tick(self):
        if self.game_over:
            return
        if not self.paused:
            self.step()
        self.draw()
        if not self.game_over:
            self.root.after(DELAY, self.tick)

    def step(self):
        h, a = self.human, self.ai
        h.direction = h.next_direction
        a.direction = self.ai_choose()

        heads = {
            h: add(h.body[0], h.direction),
            a: add(a.body[0], a.direction),
        }
        eating = {s: heads[s] == self.food for s in (h, a)}
        # 먹지 않는 뱀은 꼬리가 빠지므로 그 칸은 충돌 대상이 아님
        solid = set()
        for s in (h, a):
            solid |= set(s.body if eating[s] else s.body[:-1])

        for s in (h, a):
            if not in_bounds(heads[s]) or heads[s] in solid:
                s.alive = False
        if heads[h] == heads[a]:
            h.alive = a.alive = False

        for s in (h, a):
            if s.alive:
                s.body.insert(0, heads[s])
                if eating[s]:
                    s.score += 10
                else:
                    s.body.pop()

        if not (h.alive and a.alive):
            self.finish()
            return
        if eating[h] or eating[a]:
            self.place_food()
            self.update_score()

    def finish(self):
        self.game_over = True
        h, a = self.human, self.ai
        self.update_score()
        if h.alive and not a.alive:
            self.result = "승리! AI가 충돌했습니다"
        elif a.alive and not h.alive:
            self.result = "패배... AI 승리"
        elif h.score != a.score:
            self.result = "무승부 충돌 - 점수: " + ("내 승리" if h.score > a.score else "AI 승리")
        else:
            self.result = "무승부"

    # ---------------- 그리기 ----------------
    def draw_cell(self, pos, color):
        x, y = pos
        self.canvas.create_rectangle(
            x * CELL + 1, y * CELL + 1, (x + 1) * CELL - 1, (y + 1) * CELL - 1,
            fill=color, outline="",
        )

    def draw(self):
        self.canvas.delete("all")
        if self.food:
            self.draw_cell(self.food, "red")
        for s in (self.human, self.ai):
            for i, seg in enumerate(s.body):
                self.draw_cell(seg, s.head_color if i == 0 else s.body_color)
        if self.game_over:
            self.canvas.create_text(
                COLS * CELL // 2, ROWS * CELL // 2,
                text=f"게임 오버!\n{self.result}\nR 키로 재시작",
                fill="white", font=("Arial", 22, "bold"), justify="center",
            )


if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()
