#!/usr/bin/env bash
set -euo pipefail
revision=8b7bca2810ca1fa6901c7120ac0cd4d41e91aaa0
base="$(pwd)"
out="$(mktemp -d "$base/quartz-g90.XXXXXXXX")"
printf '%s\n' "$out"
git clone --no-checkout https://github.com/DavidWise01/-we-.git "$out/source"
git -C "$out/source" checkout --detach "$revision"
test "$(git -C "$out/source" rev-parse HEAD)" = "$revision"
mkdir "$out/evidence"
e="$out/evidence"
printf '%s\n' "$revision" > "$e/source.txt"
git -C "$out/source" ls-tree -r HEAD rust/quartz > "$e/source-tree.txt"
uname -a > "$e/platform.txt"
trap '(cd "$e" && find . -maxdepth 1 -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 -r sha256sum > SHA256SUMS)' EXIT
capture(){ local name="$1"; shift; local rc=0; "$@" > "$e/$name.log" 2>&1 || rc=$?; printf '%s\n' "$rc" > "$e/$name.exit"; return "$rc"; }
capture install rustup toolchain install 1.85.1 --profile minimal
capture rustc rustc +1.85.1 -Vv
capture cargo cargo +1.85.1 -V
cd "$out/source/rust/quartz"
capture resolve cargo +1.85.1 generate-lockfile
cp Cargo.lock "$e/Cargo.lock"
capture metadata cargo +1.85.1 metadata --locked --format-version 1
capture check cargo +1.85.1 check --locked --all-targets --message-format=json
failed=0
for suite in lib g64_integrated g77_reference g82_reconciled; do
 if [ "$suite" = lib ]; then capture "$suite" cargo +1.85.1 test --release --locked --lib || failed=1
 else capture "$suite" cargo +1.85.1 test --release --locked --test "$suite" || failed=1; fi
done
printf '%s\n' "$failed" > "$e/current-suite-exit.txt"
exit "$failed"
