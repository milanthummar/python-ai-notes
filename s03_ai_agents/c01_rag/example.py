import re
from collections import Counter


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Invalid chunk size or overlap")

    words = text.split()
    chunks = []
    step = size - overlap

    for i in range(0, len(words), step):
        chunks.append(" ".join(words[i:i + size]))
        if i + size >= len(words):
            break
    return chunks

def tokenize(text: str) -> list[str]:
    return re.findall(r'[a-z0-9]+', text.lower())

def embed(text: str) -> Counter[str]:
    return Counter(tokenize(text))

def cosine(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0

    dot_product = sum(a[key] * b[key] for key in a if key in b)
    magnitude_a = sum(a[key] ** 2 for key in a) ** 0.5
    magnitude_b = sum(b[key] ** 2 for key in b) ** 0.5
    return dot_product / (magnitude_a * magnitude_b)

def retrieve(query: str, chunks: list[str], k: int) -> list[tuple[str, float]]:
    if k <= 0:
        raise ValueError("k must be positive")

    pair_of_scores: list[tuple[str, float]] = []
    for chunk in chunks:
        score = cosine(embed(query), embed(chunk))
        if score == 0.0:
            continue
        pair_of_scores.append((chunk, score))

    pair_of_scores.sort(key = lambda pair: pair[1], reverse=True)
    return pair_of_scores[:k]

def build_prompt(question: str, contexts: list[str]) -> str:
    lines = [
        'Answer using only the context below. If the answer is not in the context, say "I don\'t know".',
        "",
        "Context:",
    ]
    if not contexts:
        lines.append("(none)")
    else:
        for number, chunk in enumerate(contexts, start=1):
            lines.append(f"[{number}] {chunk}")

    lines.append("")
    lines.append(f"Question: {question}")
    return "\n".join(lines)

def main() -> None:
    paragraph = (
        "The capital of France is Paris. Paris is known for the Eiffel Tower and the Seine. "
        "France is a country in western Europe. Lyon and Marseille are other major cities."
    )
    question = "What is the capital of France?"
    chunks = chunk_text(paragraph, size=8, overlap=2)
    retrieved = retrieve(question, chunks, 2)

    for chunk, score in retrieved:
        print(f"{score:.3f}  {chunk}")
    print()
    print(build_prompt(question, [chunk for chunk, _ in retrieved]))

if __name__ == "__main__":
    main()