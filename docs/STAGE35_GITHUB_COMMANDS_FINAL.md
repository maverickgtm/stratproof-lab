# Stage 35 — Final GitHub Commands

Run these commands from your Mac after extracting the final package.

## 1. Enter folder

```bash
cd ~/Downloads/stratproof-lab-community-stage35-github-final-pack
```

## 2. Final local validation

```bash
python3 -m compileall .
python3 tests/smoke_test_public_package.py
python3 scripts/run_public_demo.py
python3 scripts/stage28_release_preflight.py
python3 scripts/stage22_final_github_preflight.py
```

## 3. Clean generated Python cache before git

```bash
bash scripts/stage35_clean_before_git_upload.sh
```

## 4. Initialize git

```bash
git init
git branch -M main
git add .
git status
git commit -m "Initial community preview release"
```

## 5. Create GitHub repo manually

Create a new GitHub repo named:

```text
stratproof-lab
```

Use:

```text
Public
No template
Do not add README
Do not add license
Do not add .gitignore
```

The package already includes these files.

## 6. Push to GitHub

Replace `<YOUR_GITHUB_USERNAME>` with your GitHub username or organization.

```bash
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/stratproof-lab.git
git push -u origin main
```

## 7. Create release tag

```bash
git tag -a v0.1.0-community-preview -m "StratProof Lab v0.1.0 Community Preview"
git push origin v0.1.0-community-preview
```

## 8. GitHub release title

```text
StratProof Lab v0.1.0 Community Preview
```

## 9. GitHub release body

Use `RELEASE_NOTES_v0.1.0.md` or `docs/STAGE30_RELEASE_NOTES_FINAL.md`.

