# Penalty Shootout Game Rule

Let **N** denote the set of active players. During server turn *t* (t = 1, 2, …) every ordered pair (i, j) with i ≠ j plays exactly one penalty: player *i* shoots on *j*, and the symmetric event (j, i) is evaluated in the same turn.

## Action space

Each strategy submits a dictionary of the form

```
{
  "shoot": M_S,
  "keep":  M_K
}
```

For a given player *i*, both maps use opponent identifiers as keys and values in {0, 1, 2}, interpreted as left, centre, right. An optional `"*"` entry applies the same choice to every opponent not listed explicitly; the server resolves the broadcast before play.

## State carried forward

The server stores a list of round records. A typical entry looks like:

```json
{
  "_turnId": 4,
  "player-A": {
    "shoot":   { "player-B": "2" },
    "keep":    { "player-B": "0" },
    "outcome": { "player-B": { "goal": 1 } }
  },
  "player-B": {
    "shoot":   { "player-A": "1" },
    "keep":    { "player-A": "2" },
    "outcome": { "player-A": { "goal": 0 } }
  }
}
```

Directions are recorded as strings `"0"`, `"1"`, `"2"`. The `outcome` block appears only after the stochastic resolution described below.

## Match mechanics

Let **P** = (pₐᵦ) be the probability matrix defined in `penalty_shootout.py`. The default values are

| shooter\keeper | 0    | 1    | 2    |
|----------------|------|------|------|
| **0**          | 0.30 | 0.85 | 0.40 |
| **1**          | 0.60 | 0.25 | 0.50 |
| **2**          | 0.90 | 0.85 | 0.90 |

Deployments may override this matrix through environment variables.

For a penalty with shooter choice *a* = M_S(i→j) and keeper choice *b* = M_K(j→i), the server draws a Bernoulli trial with success probability pₐᵦ:

- success → the shot is a goal and the shooter receives R_goal;
- failure → the keeper records a save and receives R_save.

Payoffs are realised outcomes, not expectations. Defaults are R_goal = R_save = 1, configurable via `PENALTY_GOAL_REWARD` and `PENALTY_SAVE_REWARD`.

## Turn processing and submissions

At the close of turn *t* the server processes all actions submitted since turn *t − 1*. Late submissions roll into the next turn. Authentication depends on the GitHub token supplied in the `Authorization` header; the payload itself contains only the shoot/keep maps. The server enforces that `shoot` and `keep` reference the same opponent set and exclude the submitter’s own identifier. A strategy may resubmit during a turn, but the most recent valid action prior to processing is the one applied. Continuous play is achieved by allowing the scheduler to invoke the strategy on a fixed cadence.