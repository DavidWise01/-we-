# WAG-162 — Localized causal independence

Local Python execution: 10 tests passed in 0.205 s. Each path binds all participating nodes' version, inventory and resource balance. Every committed relay increments versions along its path. Two disjoint funded paths [0,1,2] and [3,4,5] both commit in either order, reaching ten inventories of two, spending four credits and preserving 26 total including fixed center six. Two overlapping duplicate paths allow only one commitment. Withdrawal does not mutate inventory.

Limits: serialized SQLite writes, not distributed parallel execution. Conservative path-level conflict detection may reject compatible shared reads. Synthetic signing keys, unauthenticated admission, no independent witnesses or rollback anchor. Ordered journal by application convention. No physical field law; full address {{y:m:d:h:m:s:d:am:as:ad}} not implemented. Next: separate read/write footprints and witnessed causal joins.
.dlw
