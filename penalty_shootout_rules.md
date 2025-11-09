# Penalty Shootout Notes

Each turn every ordered pair of players plays twice: once where player \(i\) shoots on \(j\), then the roles flip. A direction \(d \in \{0,1,2\}\) is interpreted as left, centre, or right. You can set a direction for each opponent or broadcast a default with `"*"`.

## State

- The server keeps a round-by-round history.
- In round \(t\), shooter \(i\) records a mapping from opponent \(j\) to direction \(d_{i \to j, t}\).
- A strategy submits:
  \[
  \{\texttt{"shoot"}: M_{\text{shoot}},\ \texttt{"keep"}: M_{\text{keep}}\}
  \]
  where both maps use opponent IDs as keys and \(\{0,1,2\}\) for values.

## Scoring

- Probabilities \(p^{S}_{d_i, d_j}\) (shooter success) and \(p^{K}_{d_j, d_i}\) (keeper success when roles flip) come from `penalty_shootout.py`.
- With `randomize_outcomes = False` (the default), rewards are expectations:
  - Shooter \(i\): \(p^{S}_{d_i, d_j} \cdot \text{goal\_reward} + (1 - p^{K}_{d_j, d_i}) \cdot \text{save\_reward}\)
  - Keeper \(j\): \((1 - p^{S}_{d_i, d_j}) \cdot \text{save\_reward} + p^{K}_{d_j, d_i} \cdot \text{goal\_reward}\)
- When `randomize_outcomes` is `True`, the same probabilities drive Bernoulli draws and rewards are tallied from those results.

## Timing

- Turns are processed every \(\Delta\) minutes (server config). All actions received since the last tick are included.
- Submissions that arrive after processing are counted for the next turn.
- Authentication relies on the GitHub token; the payload does not need an explicit player ID.