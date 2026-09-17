"""Public reference algorithms for tests and explicit experiments; never imported by admission.

The existence of these algorithms is why PoA is NOT an identity discriminator.
"""
from agent_preprints.poa import pgcd, pmod


def quotient(a, b):
    result = 0
    while a and a.bit_length() >= b.bit_length():
        shift = a.bit_length() - b.bit_length()
        result ^= 1 << shift
        a ^= b << shift
    assert a == 0
    return result


def factor(f):
    n = f.bit_length() - 1
    if n <= 1:
        return [f]
    derivative = sum(((f >> i) & 1) << (i - 1) for i in range(1, n + 1, 2))
    if derivative == 0:
        root = sum(((f >> (2 * i)) & 1) << i for i in range(n // 2 + 1))
        return sorted(factor(root) * 2)
    g = pgcd(f, derivative)
    if g != 1:
        return sorted(factor(g) + factor(quotient(f, g)))
    # Berlekamp kernel of Q-I, computed from the polynomial, never from a secret seed.
    columns = [pmod(1 << (2 * j), f) ^ (1 << j) for j in range(n)]
    rows = [sum(((columns[j] >> i) & 1) << j for j in range(n)) for i in range(n)]
    pivot_columns, rank = [], 0
    for j in range(n):
        pivot = next((i for i in range(rank, n) if (rows[i] >> j) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(n):
            if i != rank and (rows[i] >> j) & 1:
                rows[i] ^= rows[rank]
        pivot_columns.append(j)
        rank += 1
    for free in set(range(n)) - set(pivot_columns):
        vector = 1 << free
        for row, pivot in zip(rows, pivot_columns):
            if (row >> free) & 1:
                vector |= 1 << pivot
        g = pgcd(f, vector)
        if g not in (1, f):
            return sorted(factor(g) + factor(quotient(f, g)))
    return [f]


def assignment(costs):
    # Integer Hungarian primal-dual algorithm, 1-indexed working arrays.
    n = len(costs)
    u, v, p, way = [0] * (n + 1), [0] * (n + 1), [0] * (n + 1), [0] * (n + 1)
    for i in range(1, n + 1):
        p[0], j0 = i, 0
        best, used = [10**30] * (n + 1), [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], 10**30, 0
            for j in range(1, n + 1):
                if not used[j]:
                    reduced = costs[i0 - 1][j - 1] - u[i0] - v[j]
                    if reduced < best[j]:
                        best[j], way[j] = reduced, j0
                    if best[j] < delta:
                        delta, j1 = best[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    best[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
    permutation = [0] * n
    for j in range(1, n + 1):
        permutation[p[j] - 1] = j - 1
    return {"permutation": list(map(str, permutation)), "u": list(map(str, u[1:])), "v": list(map(str, v[1:]))}


def solve(problems):
    answers = []
    for problem in problems:
        if problem["family"] == "gf2-factor-v1":
            answers.append({"factors": list(map(str, factor(int(problem["polynomial"]))))})
        else:
            answers.append(assignment([[int(c) for c in row] for row in problem["costs"]]))
    return answers
