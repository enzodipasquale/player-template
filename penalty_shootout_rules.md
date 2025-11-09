# Penalty Shootout Game Rule

Let \(N\) denote the set of active players. During each server turn \(t = 1,2,\ldots\), every ordered pair \((i,j)\) with \(i \neq j\) participates in exactly one penalty event with roles \(i\) shooting and \(j\) keeping; the symmetric event \((j,i)\) occurs in the same turn.

## Action space

Each strategy submits a dictionary
\[
  \bigl\{ \texttt{"shoot"}: M^{\mathrm{S}}_i,\ \texttt{"keep"}: M^{\mathrm{K}}_i \bigr\},
\]
where \(M^{\mathrm{S}}_i(j), M^{\mathrm{K}}_i(j) \in \{0,1,2\}\) for all \(j \neq i\). Values correspond to left, centre, right. A wildcard entry `"*"` applies the same choice to every opponent yet to be specified; the server resolves it before play.

## State carried forward

The server stores a list of round records. Entry \(r\) has the form
```json
{
  "_turnId": r,
  "i": { "shoot": { "j": "a" }, "keep": { "j": "b" }, "outcome": { "j": { "goal": 1 } } },
  "j": { "shoot": { "i": "c" }, "keep": { "i": "d" }, "outcome": { "i": { "goal": 0 } } }
}
```
with one block per player. Directions are stored as strings `"0"`, `"1"`, `"2"`. The `outcome` map appears only after the stochastic resolution described below.

## Match mechanics

Let \(P = (p_{ab})_{a,b \in \{0,1,2\}}\) be the probability matrix defined in `penalty_shootout.py`. By default
\[
P =
\begin{pmatrix}
0.30 & 0.85 & 0.40 \\
0.60 & 0.25 & 0.50 \\
0.90 & 0.85 & 0.90
\end{pmatrix},
\]
but deployments may override it through environment variables.

For a penalty with shooter choice \(a = M^{\mathrm{S}}_i(j)\) and keeper choice \(b = M^{\mathrm{K}}_j(i)\), a Bernoulli draw with success probability \(p_{ab}\) determines the outcome:

- If the draw succeeds, the shot is a goal and shooter \(i\) receives \(R_{\mathrm{goal}}\).
- Otherwise the keeper \(j\) is credited with a save and receives \(R_{\mathrm{save}}\).

Payoffs are therefore realised, not expected values. The default parameters are \(R_{\mathrm{goal}} = R_{\mathrm{save}} = 1\), configurable via `PENALTY_GOAL_REWARD` and `PENALTY_SAVE_REWARD`.

## Turn processing and submissions

At the close of turn \(t\) the server processes all actions submitted since turn \(t-1\). Late submissions roll into the next turn. Authentication relies on the GitHub token in the HTTP `Authorization` header; the payload itself contains only the direction maps above. The server enforces that `shoot` and `keep` reference the same opponent set and exclude the player’s own ID. A strategy may resubmit within a turn, but the most recent valid action before the processing deadline is the one applied. Continuous play is achieved by letting the scheduler call the strategy periodically. 