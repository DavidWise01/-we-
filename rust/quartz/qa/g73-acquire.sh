#!/usr/bin/env bash
# Read-only GitHub API acquisition. Requires curl, jq, sha256sum and an authorized GH_TOKEN.
set -euo pipefail
: "${GH_TOKEN:?Set an authorized read-only GitHub token}"
out="${1:?Provide new output directory}"
mkdir "$out"
repo=DavidWise01/-we-
api="https://api.github.com/repos/$repo"
get(){ curl --fail --silent --show-error --location --header "Authorization: Bearer $GH_TOKEN" --header "Accept: application/vnd.github+json" "$1" -o "$2"; }
sha=09e5f802630e4be67d4c9d8db461a5d9f98d64b7
for event in push workflow_dispatch pull_request; do
 get "$api/actions/workflows/quartz-rust-g72.yml/runs?event=$event&head_sha=$sha&per_page=100" "$out/runs-$event.json"
 jq -e '.total_count <= 100' "$out/runs-$event.json" >/dev/null || { echo "Pagination required" >&2; exit 2; }
done
for run in $(jq -r '.workflow_runs[].id' "$out"/runs-*.json | sort -u); do
 get "$api/actions/runs/$run/jobs?per_page=100" "$out/jobs-$run.json"
 jq -e '.total_count <= 100' "$out/jobs-$run.json" >/dev/null
 for job in $(jq -r '.jobs[].id' "$out/jobs-$run.json"); do
  get "$api/actions/jobs/$job/logs" "$out/job-$job.log"
 done
 get "$api/actions/runs/$run/artifacts?per_page=100" "$out/artifacts-$run.json"
 jq -e '.total_count <= 100' "$out/artifacts-$run.json" >/dev/null
 for artifact in $(jq -r '.artifacts[] | select(.expired == false) | .id' "$out/artifacts-$run.json"); do
  get "$api/actions/artifacts/$artifact/zip" "$out/artifact-$artifact.zip"
 done
done
(cd "$out"; sha256sum -- * > SHA256SUMS)
echo "Acquisition only: no execution qualification granted."
