# Pushing to github.com/yulaAl20/DPP-Framework-ADIF

Run these from `...\research-product-software\adif\adif` — the folder where
`git rev-parse --show-toplevel` ends in `\adif\adif`. **Check that first**, for
the reason in RECOVER.md §1:

```powershell
git rev-parse --show-toplevel
```

If that does not print your project folder, stop and read RECOVER.md §1.

## If you have not initialised the repo yet

```powershell
python -m scripts.init_repo --name "yulaAl20" --email "yulani.alwis0@gmail.com"
```

Expect 18 commits and a clean tree.

## Push

```powershell
git remote add origin https://github.com/yulaAl20/DPP-Framework-ADIF.git
git branch -M main
git push -u origin main
```

If `git remote add` says the remote already exists:

```powershell
git remote set-url origin https://github.com/yulaAl20/DPP-Framework-ADIF.git
git push -u origin main
```

If the repo on GitHub already has commits in it (a README created at setup) and
the push is rejected, the cleanest fix is to take theirs out of the way rather
than force-push over your own history:

```powershell
git pull --rebase origin main
git push -u origin main
```

## After pushing, check these two things

```powershell
git log --oneline --stat | Select-Object -First 40
git show --stat HEAD
```

- No commit should contain `.venv/`, `.model_cache/`, `var/`, `__pycache__/` or
  anything under `data/heldout/`.
- The repository on GitHub should be **private** until you have submitted.
  `goldstandard/` contains your ground truth; a public repo makes the evaluation
  set public too.

## One thing to do on GitHub itself

Add `data/heldout/` to the repository description or README as sealed, and keep
it empty until after the freeze tag. If you push held-out schemas before the
freeze tag exists, the commit history stops supporting the ordering claim the
methodology makes — and the history is the only evidence of it.
