from typing import Callable


def by_score(pair: tuple[str, float]) -> float:
    return pair[1]

def sort_by_score(pairs: list[tuple[str, float]]) -> list[tuple[str, float]]:
    return sorted(pairs, key=lambda pair: pair[1], reverse=True)

def sort_by_name(pairs: list[tuple[str, float]]) -> list[tuple[str, float]]:
    return sorted(pairs, key = lambda pair: pair[0])

def top_k(pairs: list[tuple[str, float]], k: int) -> list[tuple[str, float]]:
    if k <= 0:
        raise ValueError("k must be positive")
    return sort_by_score(pairs)[:k]

def apply_all(fns: list[Callable[[int], int]], x: int) -> list[int]:
    return [fn(x) for fn in fns]


def main() -> None:
    pairs = [("b", 0.2), ("c", 0.9), ("a", 0.5)]

    print("sort by score", sort_by_score(pairs))
    print("sort by name", sort_by_name(pairs))
    print("top 1", top_k(pairs, 1))
    print("apply all", apply_all([lambda n: n + 1, lambda n: n * 2], 10))

if __name__ == "__main__":
    main()



