# Penalty Shootout Game Rule

Let $N$ be the finite set of active players. Server time is indexed by discrete turns $t = 1,2,\dots$. During each turn all ordered pairs $(i,j)$ with $i \neq j$ are evaluated. The ordered pair $(i,j)$ represents a penalty in which player $i$ shoots on player $j$; the symmetric pair $(j,i)$ is resolved independently in the same turn.

## Action space

At the start of turn $t$, every $i \in N$ submits
$$
a_i(t) = \bigl\{\texttt{shoot} : M^{\mathrm{S}}_i(t),\ \texttt{keep} : M^{\mathrm{K}}_i(t)\bigr\},
$$
where the maps $M^{\mathrm{S}}_i(t), M^{\mathrm{K}}_i(t) : N \setminus \{i\} \rightarrow \{0,1,2\}$ prescribe shooting and keeping directions against each opponent. Labels $0,1,2$ correspond to left, centre, right. A broadcast entry `"*"` is interpreted as a fallback value:
$$
M^{\mathrm{S}}_i(t,j) =
\begin{cases}
\text{specified value}, & \text{if } j \text{ is listed explicitly},\\
M^{\mathrm{S}}_i(t,"*"), & \text{otherwise},
\end{cases}
$$
and analogously for $M^{\mathrm{K}}_i(t)$.

## Public state

The state observed by all players is the history $H(t) = \{h_1,\dots,h_t\}$. For each round $r$, the record
$$
h_r = \bigl\{\, (k,\, \Theta_k(r)) : k \in N \,\bigr\} \cup \{(\_turnId, r)\}
$$
contains, for every player $k$, the tuple
$$
\Theta_k(r) = \bigl(\text{shoot}_k(r),\ \text{keep}_k(r),\ \text{outcome}_k(r)\bigr),
$$
where $\text{shoot}_k(r)$ and $\text{keep}_k(r)$ reproduce the canonical direction maps (stored as strings `"0"`, `"1"`, `"2"`). Once the stochastic resolution is complete, $\text{outcome}_k(r)$ records realised indicators $\{\text{opponent} \mapsto \text{goal}\in\{0,1\}\}$; otherwise the field is absent.

## Match mechanics

Let $P = (p_{ab})_{a,b \in \{0,1,2\}}$ denote the success-probability matrix specified in `penalty_shootout.py`. The default parameterisation is
$$
P = \begin{pmatrix}
0.30 & 0.85 & 0.40\\
0.60 & 0.25 & 0.50\\
0.90 & 0.85 & 0.90
\end{pmatrix},
$$
and may be overridden through the environment variables `PENALTY_MATRIX` or `PENALTY_SHOOTER_MATRIX`.

Fix a duel $(i,j)$ in round $t$. Let
$$
a = M^{\mathrm{S}}_i(t,j), \qquad b = M^{\mathrm{K}}_j(t,i).
$$
Conditional on $(a,b)$ the platform draws
$$
Y_{ij}(t) \sim \mathrm{Bernoulli}(p_{ab}).
$$
If $Y_{ij}(t)=1$, the shot is converted and shooter $i$ receives $R_{\mathrm{goal}}$; if $Y_{ij}(t)=0$, the keeper $j$ records a save and receives $R_{\mathrm{save}}$. By default $R_{\mathrm{goal}} = R_{\mathrm{save}} = 1$, configurable via `PENALTY_GOAL_REWARD` and `PENALTY_SAVE_REWARD`.

## Turn processing

Let $\tau_t$ be the server timestamp at which turn $t$ is processed. All actions submitted in the half-open interval $[\tau_{t-1}, \tau_t)$ are canonicalised and evaluated during turn $t$, while messages arriving after $\tau_t$ are queued for turn $t+1$. Authentication relies solely on the GitHub token transmitted in the HTTP `Authorization` header; the payload contains only the maps $M^{\mathrm{S}}_i(t)$ and $M^{\mathrm{K}}_i(t)$. The server enforces that these maps share an identical domain and exclude player $i$. A participant may submit multiple actions within the interval; the final valid action received before $\tau_t$ is the one implemented. Continuous play is obtained by running automated submissions at the cadence chosen by the organiser.