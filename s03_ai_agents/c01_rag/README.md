# 3.1 RAG

**One-liner:** Retrieval-augmented generation finds the few passages that match
the question and puts only those in the prompt, so the model answers from your
data instead of from memory.

## The idea

Four steps, every time:

1. **Chunk.** Split documents into small overlapping windows. Too big and one
   chunk mixes topics; too small and it loses context. Overlap keeps a
   sentence that straddles a boundary in at least one chunk.
2. **Embed.** Turn text into a vector. Real systems use an embedding model;
   here a bag-of-words count stands in for it, so everything runs offline.
3. **Retrieve.** Score every chunk against the question (cosine similarity)
   and keep the top `k`.
4. **Augment.** Put the retrieved chunks into the prompt, numbered, with an
   instruction to answer only from them and to say "I don't know" otherwise.

## Why it matters

The prompt stays small, which keeps cost and latency down, and answers can
cite the chunk they came from. Most "the agent made it up" bugs are retrieval
bugs: the right chunk never reached the prompt.

## Spec

Standard library only. Implement in `s03_ai_agents/c01_rag/example.py`, re-export
the six functions from `__init__.py`, add `__main__.py`, and write
`tests/s03_ai_agents/test_c01_rag.py`.

```python
def chunk_text(text: str, size: int, overlap: int) -> list[str]: ...

def tokenize(text: str) -> list[str]: ...

def embed(text: str) -> Counter[str]: ...

def cosine(a: Counter[str], b: Counter[str]) -> float: ...

def retrieve(query: str, chunks: list[str], k: int) -> list[tuple[str, float]]: ...

def build_prompt(question: str, contexts: list[str]) -> str: ...
```

### `chunk_text`

- Split `text` on whitespace into words. Each chunk is up to `size` words
  joined by single spaces.
- The next chunk starts `size - overlap` words after the previous one.
- Stop after the first chunk that reaches the last word. Never emit a chunk
  that is fully contained in the previous one.
- Empty or whitespace-only `text` returns `[]`.
- `size <= 0`, `overlap < 0`, or `overlap >= size` raises `ValueError`.

Example with words `w1 … w10`, `size=4`, `overlap=1`:
`["w1 w2 w3 w4", "w4 w5 w6 w7", "w7 w8 w9 w10"]`.

### `tokenize` and `embed`

- `tokenize` lowercases and returns `re.findall(r"[a-z0-9]+", text.lower())`.
- `embed` returns `Counter(tokenize(text))`.

### `cosine`

- Dot product of the two counters divided by the product of their lengths
  (square root of the sum of squared counts).
- Returns `0.0` if either counter is empty. Never divides by zero.
- Identical non-empty inputs return `1.0` (compare with `pytest.approx`).

### `retrieve`

- Score every chunk with `cosine(embed(query), embed(chunk))`.
- Drop chunks that score `0.0`.
- Return at most `k` `(chunk, score)` pairs, highest score first. Equal scores
  keep their original order (`sorted` is stable).
- `k <= 0` raises `ValueError`.

### `build_prompt`

Return exactly this shape (contexts numbered from 1, one per line):

```text
Answer using only the context below. If the answer is not in the context, say "I don't know".

Context:
[1] first chunk
[2] second chunk

Question: <question>
```

With no contexts, the `Context:` section contains the single line `(none)`.

### `main()`

Chunk a short paragraph of your own, retrieve the top 2 chunks for one
question, and print the prompt.

### Tests you should write

| Test | Assert |
|---|---|
| chunk windows | the `w1 … w10`, `size=4`, `overlap=1` example above |
| chunk short text | fewer words than `size` → one chunk |
| chunk empty | `""` and `"   "` → `[]` |
| chunk bad args | `size=0`, `overlap=-1`, `overlap=size` each raise `ValueError` |
| tokenize | `"Reset, PASSWORD!"` → `["reset", "password"]` |
| cosine identical | same text → `pytest.approx(1.0)` |
| cosine disjoint / empty | no shared words → `0.0`; empty counter → `0.0` |
| retrieve ranking | the chunk sharing the most query words comes first |
| retrieve drops zeros | unrelated chunks are not returned |
| retrieve k | never more than `k` results; `k=0` raises `ValueError` |
| prompt numbering | contexts appear as `[1] …`, `[2] …`, question on the last line |
| prompt no context | contains `(none)` |

## Interview trap

> Q: The answer is wrong. Is it the model or retrieval?
> A: Check retrieval first: log the retrieved chunks for that request. If the
> right chunk isn't there, no prompt change will fix it.

> Q: Why overlap chunks?
> A: So a fact that spans a chunk boundary still appears whole in one chunk.
