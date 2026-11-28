#!/usr/bin/env bash
set -euo pipefail
revision=8b7bca2810ca1fa6901c7120ac0cd4d41e91aaa0
repo="$(realpath "${1:?frozen checkout required}")"
out="$(realpath "${2:?existing empty evidence directory required}")"
test "$(git -C "$repo" rev-parse HEAD)" = "$revision"
test -z "$(git -C "$repo" status --porcelain --untracked-files=all)"
test "$(git -C "$repo" rev-parse HEAD:rust/quartz/Cargo.toml)" = 802fa18bcabab765432dcadd3d46d0be43a52590
test -z "$(ls -A "$out")"
printf '%s\n' "$revision" > "$out/source.txt"
cd "$repo/rust/quartz"
test ! -e Cargo.lock
rustc +1.85.1 -Vv > "$out/toolchain.txt"
cargo +1.85.1 -V >> "$out/toolchain.txt"
cargo +1.85.1 generate-lockfile > "$out/resolve.log" 2>&1
cp Cargo.toml Cargo.lock "$out/"
cargo +1.85.1 metadata --locked --format-version 1 > "$out/metadata.json"
cmp Cargo.lock "$out/Cargo.lock"
(cd "$out" && sha256sum source.txt toolchain.txt Cargo.toml Cargo.lock metadata.json resolve.log > SHA256SUMS)
echo 'Candidate lock captured; independent approval required.'
