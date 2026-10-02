# 3.2 LLM fundamentals

**One-liner:** An LLM predicts a score (logit) for every possible next token;
softmax turns scores into probabilities, and a decoding rule picks one.
Temperature and top-k change the pick, not the model.

## The idea

- **Tokens.** The model reads and writes tokens (word pieces), not words. Cost
  and context limits are counted in tokens.
- **Logits → probabilities.** For each step the model outputs one logit per
  token in its vocabulary. `softmax` turns them into probabilities that sum to
  1.
- **Temperature** divides the logits before softmax. Below 1 the distribution
  gets sharper (more predictable); above 1 it flattens (more varied).
- **Decoding.** Greedy always takes the most likely token. Sampling draws from
  the distribution. Top-k first throws away everything except the `k` most
  likely tokens.
- **Hallucination.** The model only picks likely-sounding tokens; nothing in
  this loop checks facts. Grounding (3.1) and evals are how you catch it.

## Why it matters

"Set temperature to 0 for extraction, higher for brainstorming" and "why did
the same prompt give a different answer?" both come straight from this loop.

## Spec

Standard library only. Implement in `s03_ai_agents/c02_llm_fundamentals/example.py`,
re-export the four functions from `__init__.py`, add `__main__.py`, and write
`tests/s03_ai_agents/test_c02_llm_fundamentals.py`.

```python
def softmax(logits: list[float], temperature: float = 1.0) -> list[float]: ...

def greedy(logits: list[float]) -> int: ...

def top_k_filter(logits: list[float], k: int) -> list[float]: ...

def sample(logits: list[float], temperature: float, rng: random.Random) -> int: ...
```

### `softmax`

- Divide each logit by `temperature`, subtract the largest scaled logit, then
  exponentiate and normalize. Subtracting the max keeps `math.exp` from
  overflowing on large logits.
- Result has the same length as `logits` and sums to `1.0` (use
  `pytest.approx`).
- `float("-inf")` logits get probability `0.0`.
- Empty `logits` or `temperature <= 0` raises `ValueError`.

### `greedy`

- Return the index of the largest logit. On a tie, the lowest index wins.
- Empty `logits` raises `ValueError`.

### `top_k_filter`

- Return a new list: the `k` largest logits keep their value, every other
  position becomes `float("-inf")`. Ties at the cut-off keep the lower index.
- `k >= len(logits)` returns an unchanged copy. `k < 1` raises `ValueError`.
- Never mutate the input.

### `sample`

- `probs = softmax(logits, temperature)`, then `r = rng.random()`.
- Walk the cumulative sum and return the first index where `r < cumulative`.
  If rounding leaves `r` past the end, return the last index with a non-zero
  probability.
- The `rng` argument makes it deterministic in tests: pass
  `random.Random(seed)`, never use the global `random` module.

### `main()`

Print `softmax` of one logit list at temperatures `0.5`, `1.0` and `2.0`, then
the greedy pick and five seeded samples.

### Tests you should write

| Test | Assert |
|---|---|
| softmax sums to 1 | `sum(softmax([1, 2, 3])) == pytest.approx(1.0)` |
| softmax order | larger logit → larger probability |
| temperature sharpens | `softmax([1, 2], 0.5)[1] > softmax([1, 2], 1.0)[1]` |
| temperature flattens | `softmax([1, 2], 5.0)[1] < softmax([1, 2], 1.0)[1]` |
| no overflow | `softmax([1000, 1001])` returns finite numbers summing to 1 |
| -inf → 0 | `softmax([0, float("-inf")])[1] == 0.0` |
| softmax bad args | `[]` and `temperature=0` raise `ValueError` |
| greedy | picks the max; tie returns the lower index |
| top-k keeps k | `top_k_filter([1, 5, 3, 4], 2)` → `[-inf, 5, -inf, 4]` |
| top-k no mutation | input list unchanged afterward |
| top-k bad k | `k=0` raises `ValueError` |
| sample deterministic | same seed → same sequence of picks |
| sample top-1 equals greedy | `sample(top_k_filter(x, 1), 1.0, rng) == greedy(x)` for any seed |
| sample distribution | with logits `[0, 0]` and 1000 seeded draws, each index appears 400–600 times |

## Interview trap

> Q: Temperature 0 — is the output fully deterministic?
> A: In principle it is greedy decoding, so yes. In practice hosted APIs can
> still vary slightly (batching, floating-point order), so don't rely on exact
> string matches in tests — that's what evals are for.

> Q: Why do LLMs hallucinate?
> A: They generate likely text, not checked facts. Ground them with retrieved
> context and measure with evals.
