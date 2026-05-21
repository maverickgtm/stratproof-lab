# Stage 31 — Final Local Publishing Rehearsal

Stage 31 simulates the final local workflow before uploading StratProof Lab to GitHub.

It does **not** publish anything. It creates a clean temporary copy of the public package and runs:

1. Python compile check.
2. Public smoke test.
3. One-command public demo.
4. Release preflight.
5. Final GitHub preflight scanner.

The goal is to confirm that the community package behaves correctly when treated like a fresh clone.

## Command

```bash
python scripts/stage31_local_publishing_rehearsal.py
```

## Expected result

```text
STAGE31_REHEARSAL_STATUS=PASS
```

## What this stage proves

- The package can be copied cleanly.
- Python modules compile.
- Demo workflow runs.
- Release checks pass.
- Scanner checks pass.
- GitHub upload can now be done manually and intentionally.

## What this stage does not do

- It does not create a GitHub repo.
- It does not push code.
- It does not create a release.
- It does not connect payments.
- It does not enable Pro features.
