# Stage 29 — GitHub Commands for Mac

> Replace `YOUR_GITHUB_USERNAME` with the real GitHub username or organization.

## 1. Unzip package

```bash
cd ~/Downloads
unzip stratproof-lab-community-stage29.zip -d stratproof-lab-release
cd stratproof-lab-release/stratproof-lab-community-stage29
```

## 2. Final local test

```bash
python3 scripts/run_public_demo.py
python3 scripts/stage28_release_preflight.py
```

Expected result:

```text
PASS
```

## 3. Initialize git

```bash
git init
git branch -M main
git status
```

## 4. First commit

```bash
git add .
git commit -m "Initial StratProof Lab community preview"
```

## 5. Create empty GitHub repo

Create a new GitHub repository:

```text
Repository name: stratproof-lab
Description: Evidence engine for trading strategies
Visibility: Public
Initialize with README: No
License: No, already included
.gitignore: No, already included
```

## 6. Connect remote and push

```bash
git remote add origin git@github.com:YOUR_GITHUB_USERNAME/stratproof-lab.git
git push -u origin main
```

HTTPS alternative:

```bash
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/stratproof-lab.git
git push -u origin main
```

## 7. Tag release

```bash
git tag -a v0.1.0-community-preview -m "StratProof Lab v0.1.0 Community Preview"
git push origin v0.1.0-community-preview
```

## 8. Create GitHub Release

Use:

```text
Tag: v0.1.0-community-preview
Title: StratProof Lab v0.1.0 Community Preview
Body: paste RELEASE_NOTES_v0.1.0.md
```
