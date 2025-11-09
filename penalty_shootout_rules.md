# Penalty Shootout Game Rule

Let \(N\) denote the finite set of active players. Server time is indexed by discrete turns \(t = 1,2,\dots\). During each turn the platform evaluates every ordered pair \((i,j) \in N \times N\) with \(i \neq j\); the event \((i,j)\) is interpreted as player \(i\) attempting a penalty on keeper \(j\). The symmetric event \((j,i)\) is treated independently within the same turn.

## Action space

At the beginning of turn \(t\) each player \(i \in N\) submits an action
\[
  a_i(t) = \bigl\{\texttt{"shoot"} : M^{\mathrm{S}}_i(t),\ \texttt{"keep"} : M^{\mathrm{K}}_i(t)\bigr\},
\]
where the maps \(M^{\mathrm{S}}_i(t), M^{\mathrm{K}}_i(t) : N \setminus \{i\} \rightarrow \{0,1,2\}\) prescribe shooting and keeping directions against every opponent. The labels \(0,1,2\) correspond to left, centre, right. A broadcast entry `"*"` is interpreted as a fallback direction and is resolved by the server as
\[
  M^{\mathrm{S}}_i(t,j) =
  \begin{cases}
    \text{specified value}, & \text{if } j \text{ is explicitly listed},\\[4pt]
    M^{\mathrm{S}}_i(t, "*"), & \text{otherwise},
  \end{cases}
\]
with the same convention for \(M^{\mathrm{K}}_i(t)\).

## State carried forward

The public state is a history \(H(t) = \{h_1,\dots,h_t\}\). For each round \(r\) the record
\[
  h_r = \bigl\{\, (k,\, \Theta_k(r)) : k \in N \,\bigr\} \cup \{(\_turnId, r)\}
\]
contains, for every player \(k\), the tuple
\[
  \Theta_k(r) = \bigl(\, \text{shoot}_k(r),\ \text{keep}_k(r),\ \text{outcome}_k(r) \,\bigr),
\]
where \(\text{shoot}_k(r)\) and \(\text{keep}_k(r)\) reproduce the canonical maps \(\{0,1,2\}\) stored as strings, and \(\text{outcome}_k(r)\) is populated ex post with realised goal indicators. Absent information, \(\text{outcome}_k(r)\) is omitted.

## Stochastic match mechanics

Let \(P = (p_{ab})_{a,b \in \{0,1,2\}}\) denote the success-probability matrix hard-coded in `penalty_shootout.py`. The default specification is
\[
P =
\begin{pmatrix}
0.30 & 0.85 & 0.40\\
0.60 & 0.25 & 0.50\\
0.90 & 0.85 & 0.90
\end{pmatrix},
\]
though any deployment may replace \(P\) via environment variables `PENALTY_MATRIX` or `PENALTY_SHOOTER_MATRIX`.

Consider a single duel in round \(t\) with shooter \(i\) and keeper \(j\). Write
\[
a = M^{\mathrm{S}}_i(t,j), \qquad b = M^{\mathrm{K}}_j(t,i).
\]
Conditional on \((a,b)\), the platform draws
\[
Y_{ij}(t) \sim \mathrm{Bernoulli}\bigl(p_{ab}\bigr).
\]
If \(Y_{ij}(t) = 1\), the shot is converted and shooter \(i\) receives the monetary payoff \(R_{\mathrm{goal}}\); if \(Y_{ij}(t) = 0\), keeper \(j\) is credited with a save and obtains \(R_{\mathrm{save}}\). The default rewards satisfy \(R_{\mathrm{goal}} = R_{\mathrm{save}} = 1\) and may be reparametrised via `PENALTY_GOAL_REWARD` and `PENALTY_SAVE_REWARD`.

## Turn processing

Let \(\tau_t\) denote the server timestamp at which turn \(t\) is processed. All actions submitted in the half-open interval \([\tau_{t-1}, \tau_t)\) are canonicalised and evaluated during turn \(t\). Messages arriving after \(\tau_t\) are queued for turn \(t+1\). Authentication rests solely on the GitHub token conveyed in the HTTP `Authorization` header; the payload transmitted by the client consists of the maps \(M^{\mathrm{S}}_i(t)\) and \(M^{\mathrm{K}}_i(t)\). The server enforces the constraints \(M^{\mathrm{S}}_i(t)\) and \(M^{\mathrm{K}}_i(t)\) share identical domains and exclude the submitter’s own identifier. A player may send multiple actions within the same interval; the last valid submission prior to \(\tau_t\) is the one implemented. Continuous contestation is achieved by scheduling automated submissions at the cadence determined by the experimenter.