# CALIBER Submission Artifact Report

Generated: 2026-06-28T07:38:44Z

This report summarizes repository artifacts used by the CALIBER paper. It is an evidence index, not a new theorem or a production-deployment claim.

## Attack Timeline Replay

| scheme | miner_lb_sat | bob_ub_sat | width_sat | selected_br_sat | profitable | outcome |
|---|---|---|---|---|---|---|
| Naive CRAB+He | 3000000 | 5500000 | 2500000 | 4250000 | true | profitable CLBA interval exists; stale-state and HTLC-side gains fund the bribe |
| CALIBER | 3000000 | 3000000 | 0 | 0 | false | no jointly profitable BR exists; dep-B reveals pre_b and triggers fixed linked burn/fee spend |

## Parallel Independent Swaps

Invariant: `c*_n = v + n*v_dep` for independent standalone HTLC instances; this is not a routed-Lightning multi-hop claim.

| n | c_n_star_sat | overhead_sat |
|---|---|---|
| 1 | 3000000 | 1000000 |
| 3 | 5000000 | 3000000 |
| 5 | 7000000 | 5000000 |
| 7 | 9000000 | 7000000 |

## Linked ACS Evidence

| network | fundTxid | spendTxid | fundSat | burnSat | feeSat | createdAtUtc |
|---|---|---|---|---|---|---|
| regtest | missing | missing | - | - | - | - |
| signet | missing | missing | - | - | - | - |

## Fee-Profile Campaign

| network | runs | successful |
|---|---|---|
| regtest | missing | missing |
| signet | missing | missing |

## Non-Claims

- No production miner bribery marketplace.
- No modified Bitcoin miner client performing real censorship.
- No confirmed CLBA mainnet incident.
- No full routed-Lightning HTLC model.
- No theorem-level multi-miner coalition game.
