# Penalty Shootout Game Rule

Let N denote the finite set of active players. Server time evolves in discrete turns (t = 1, 2, …). During each turn the platform inspects every unordered pair {i, j} with i ≠ j. For the ordered realisation (i, j) we read the event as “player i shoots on player j”; the reverse ordering (j, i) is evaluated in the same turn.

## Action space

At the start of turn t each player i submits an action consisting of two maps:

- shoot map: opponents → {0, 1, 2}
- keep map: opponents → {0, 1, 2}

The labels 0, 1, 2 correspond respectively to left, centre, and right. Players may provide an explicit direction for every opponent or rely on a broadcast entry "*" to supply a fallback value for any opponent not listed. The server resolves the broadcast before play and applies the same convention to both shoot and keep maps.

## State tracked by the server

The server maintains a turn-by-turn log `H(t) = {h₁, …, h_t}`. Each entry `h_r` is a dictionary with:

- `_turnId`: the round counter `r`
- one entry per player identifier, storing that player’s record for round `r`

A player record contains three fields:

- `shoot`: a map from opponent identifiers to the shooter’s chosen direction (`"0"`, `"1"`, or `"2"`)
- `keep`: a map from opponent identifiers to the keeper’s chosen direction
- `outcome`: (optional) once the duel has been resolved, a map from opponent identifiers to the realised result (`goal = 1` or `goal = 0`)

If the outcome is not yet known, the `outcome` field is omitted for that round.

## Payoff mechanism

Let P be the 3 × 3 success-probability matrix whose rows index shooting directions and columns index keeping directions. The matrix satisfies the dominance property `P[d, d] < P[u, v]` for every direction d and any ordered pair (u, v) with u ≠ v. Intuitively, a shot aimed away from the keeper’s chosen direction strictly improves the conversion probability relative to a shot that matches it.

During round t a duel between shooter i and keeper j is determined by their chosen directions. Let `a` be the shooter’s direction against j and `b` the keeper’s defence against i. The shot succeeds with probability `P[a, b]`; success yields a goal for i, otherwise i is denied and j records a save. The reverse duel (j, i) is evaluated symmetrically within the same turn.