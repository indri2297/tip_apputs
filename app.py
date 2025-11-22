from flask import Flask, render_template, request
from collections import deque
import heapq

app = Flask(__name__)

# =======================
# FUZZY MEMBERSHIP
# =======================

def triangular(x, a, b, c):
    if x <= a or x >= c:
        return 0
    elif a < x < b:
        return (x - a) / (b - a)
    elif b <= x < c:
        return (c - x) / (c - b)


def food_quality_fuzzy(x):
    return {
        "Bad": triangular(x, 0, 0, 5),
        "Good": triangular(x, 5, 10, 10)
    }

def service_quality_fuzzy(x):
    return {
        "Poor": triangular(x, 0, 0, 5),
        "Excellent": triangular(x, 5, 10, 10)
    }

def tip_fuzzy_low(x):
    return triangular(x, 0, 0, 10)

def tip_fuzzy_high(x):
    return triangular(x, 10, 20, 20)


# =======================
# FUZZY RULES
# =======================

def fuzzy_inference(food, service):
    f = food_quality_fuzzy(food)
    s = service_quality_fuzzy(service)

    rule_low = max(s["Poor"], f["Bad"])
    rule_high = min(s["Excellent"], f["Good"])

    return rule_low, rule_high


# =======================
# DEFUZZY
# =======================

def defuzzify(low_strength, high_strength):
    num, den = 0, 0
    for x in range(0, 21):
        mu_low = min(low_strength, tip_fuzzy_low(x))
        mu_high = min(high_strength, tip_fuzzy_high(x))
        mu = max(mu_low, mu_high)

        num += mu * x
        den += mu

    return num / den if den != 0 else 0


# =======================
# SEARCH AI ALGORITHMS
# =======================

def bfs(start, goal):
    queue = deque([start])
    visited = set()

    while queue:
        state = queue.popleft()
        if state in visited:
            continue
        visited.add(state)

        if state == goal:
            return state

        f, s = state
        neighbors = [
            (min(10, f+1), s),
            (max(0, f-1), s),
            (f, min(10, s+1)),
            (f, max(0, s-1))
        ]
        for n in neighbors:
            if n not in visited:
                queue.append(n)

    return None


def dfs(start, goal):
    stack = [start]
    visited = set()

    while stack:
        state = stack.pop()
        if state in visited:
            continue
        visited.add(state)

        if state == goal:
            return state

        f, s = state
        neighbors = [
            (min(10, f+1), s),
            (max(0, f-1), s),
            (f, min(10, s+1)),
            (f, max(0, s-1))
        ]
        for n in neighbors:
            if n not in visited:
                stack.append(n)

    return None


def heuristic(state, goal):
    return abs(state[0] - goal[0]) + abs(state[1] - goal[1])


def greedy_bfs(start, goal):
    pq = []
    heapq.heappush(pq, (0, start))
    visited = set()

    while pq:
        _, state = heapq.heappop(pq)

        if state in visited:
            continue
        visited.add(state)

        if state == goal:
            return state

        f, s = state
        neighbors = [
            (min(10, f+1), s),
            (max(0, f-1), s),
            (f, min(10, s+1)),
            (f, max(0, s-1))
        ]
        for n in neighbors:
            if n not in visited:
                h = heuristic(n, goal)
                heapq.heappush(pq, (h, n))

    return None


# =======================
# FLASK ROUTES
# =======================

@app.route("/", methods=["GET", "POST"])
def index():
    tip_result = None
    bfs_result = dfs_result = gbfs_result = None

    if request.method == "POST":
        food = float(request.form["food"])
        service = float(request.form["service"])

        start = (0, 0)
        goal = (int(food), int(service))

        bfs_result = bfs(start, goal)
        dfs_result = dfs(start, goal)
        gbfs_result = greedy_bfs(start, goal)

        low, high = fuzzy_inference(food, service)
        tip_result = defuzzify(low, high)

    return render_template(
        "index.html",
        tip=tip_result,
        bfs=bfs_result,
        dfs=dfs_result,
        gbfs=gbfs_result
    )


if __name__ == "__main__":
    app.run(debug=True)
