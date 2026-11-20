# WAG-210 — Adversarial frequency qualification
.dlw

Executed 7 disturbance patterns × 4 qualification policies × 4 underlying period choices × 32 seeds, 384 observed slots per fixture. 1376256 polarity-mirrored slot checks. Modes are baseline WAG-209 cross, half-window agreement, thirds agreement, and the new cadence guard: WAG-209 candidate AND early/late agreement AND no more than floor(1/8 of complete intervals) beyond ±2 of proposed period. This is a designed condition, not an independently validated threshold.

periodic, baseline: correct=128, wrong=0, unknown=0
periodic, half: correct=128, wrong=0, unknown=0
periodic, thirds: correct=96, wrong=0, unknown=32
periodic, guard: correct=128, wrong=0, unknown=0
jittered, baseline: correct=120, wrong=1, unknown=7
jittered, half: correct=116, wrong=1, unknown=11
jittered, thirds: correct=80, wrong=0, unknown=48
jittered, guard: correct=116, wrong=1, unknown=11
skipped, baseline: correct=32, wrong=0, unknown=96
skipped, half: correct=32, wrong=0, unknown=96
skipped, thirds: correct=0, wrong=0, unknown=128
skipped, guard: correct=32, wrong=0, unknown=96
drift, baseline: correct=0, wrong=0, unknown=128
drift, half: correct=0, wrong=0, unknown=128
drift, thirds: correct=0, wrong=0, unknown=128
drift, guard: correct=0, wrong=0, unknown=128
mixed, baseline: correct=0, wrong=32, unknown=96
mixed, half: correct=0, wrong=32, unknown=96
mixed, thirds: correct=0, wrong=32, unknown=96
mixed, guard: correct=0, wrong=0, unknown=128
shuffled, baseline: correct=0, wrong=0, unknown=128
shuffled, half: correct=0, wrong=0, unknown=128
shuffled, thirds: correct=0, wrong=0, unknown=128
shuffled, guard: correct=0, wrong=0, unknown=128
alternating, baseline: correct=0, wrong=0, unknown=128
alternating, half: correct=0, wrong=0, unknown=128
alternating, thirds: correct=0, wrong=0, unknown=128
alternating, guard: correct=0, wrong=0, unknown=128

The planted fixed period is ground truth for periodic, ±1 jittered, and skipped-beat patterns. Drift, mixed, alternating and shuffled have no designated single stationary period. A committed single period on these fixtures is scored false even when it describes a component of a mixture.

Important caveats: 32 baseline false locks for mixed rhythms occur in the period-9 category with identical deterministic sequences across seeds, so not 32 independent error mechanisms. Skipped beats yield only 32/128 recognized underlying periods for guard and baseline: substantial abstention. One jittered seed still gives a wrong period under guard. Seed choices and thresholds are exploratory, not held-out validation.

Failures are preserved in counterexamples.json including exact binary sequences. Next WAG-211: source/ancestry-aware spectral decomposition to describe mixtures rather than simply withhold them.
