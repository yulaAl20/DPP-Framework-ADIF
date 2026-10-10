# RECOVER.md — read this before running anything else
**Written:** 2026-10-08, from your PowerShell log.

Your log shows three separate things. One is a hazard on your machine, two are
defects in what I shipped. The defects are fixed in this zip. The hazard is not
something I can fix from here, and it is the first thing to deal with.

---

## 1. HAZARD — your home folder is a git repository

Your log contains this:

```
git rev-parse --show-toplevel
C:/Users/User
```

`C:\Users\User` — your entire Windows user profile — **is a git repository, with
a remote called `origin`.** It was not created by anything I gave you; it
already existed. That is why you saw hundreds of lines like:

```
warning: in the working copy of '.gradle/caches/transforms-4/.../values-ru.xml',
         LF will be replaced by CRLF
error: unable to index file '.gradle/caches/.../gradle-8.7/...'
fatal: adding files failed
```

Git was indexing an Android build cache, because from inside `adif\adif` every
`git add` was being applied to the repository rooted at your home folder.

**What it already did.** The 18 ADIF commits went into that repository, with
every path prefixed `Desktop/Degree/Research/research-product-software/adif/adif/`.
One commit also deleted three unrelated things from its index:

```
delete mode 160000 Desktop/Degree/Research/github docs/liviru
delete mode 160000 Desktop/Degree/Research/github docs/research-artefact-archive
delete mode 100644 Documents/DWM/cw/datamodler/.gitignore
```

**What you already did right.** `git reset --mixed origin/main` undid those 19
local commits and restored the index to match `origin/main`. And the log shows
`Your branch is ahead of 'origin/main' by 19 commits` with no `git push` — so
**nothing reached GitHub.** No cleanup is needed on the remote.

### Check it, then decide

Run these three in a **new** PowerShell window, from your home folder:

```powershell
cd $HOME
git log --oneline -5
git remote -v
git status --short | Select-Object -First 20
```

- **If `git log` shows real work and `git remote -v` shows a repository you
  recognise** — leave it alone. It is someone's real repo. Just make sure the
  research folder never gets committed into it: add
  `Desktop/Degree/Research/` to `C:\Users\User\.gitignore`.
- **If it looks like an accident** (one stray commit, no meaningful history, a
  remote you do not recognise) — you can remove it with
  `Remove-Item -Recurse -Force "$HOME\.git"`. **Only after reading the log.**
  Deleting a `.git` directory destroys every commit in it and there is no undo.

Either way, the guard in item 3 below now stops this recurring.

---

## 2. DEFECT (mine) — the semantic stage could not load the real model

```
TypeError: SentenceTransformer.__init__() got an unexpected keyword argument
'local_files_only'
  src/matching/stage3_semantic.py, line 86
```

This is why `python -m eval.grid_search --real-model` died after printing
`Searching 11x11 threshold pairs over 6 schema(s)...`. The search itself was
working — it got all the way to loading the model.

**My error, in two places.** `local_files_only` was added to
`SentenceTransformer.__init__` in version **3.x**. My
`requirements-optional.txt` allowed `>=2.7,<3`, so pip correctly installed a
2.x build, and my code then passed a keyword that version does not accept. I
shipped a version constraint incompatible with my own code.

**Fixed** by checking the installed signature at load time: the stronger
`local_files_only` assertion is used where it exists, and where it does not, the
`HF_HUB_OFFLINE` / `TRANSFORMERS_OFFLINE` environment variables already set two
lines above carry the offline guarantee. That is also what the NFR-1 acceptance
test actually verifies. The pin in `requirements-optional.txt` is widened to
`>=2.7,<6`, so **you do not need to reinstall anything.**

### A second defect found while fixing the first

`MiniLMEmbedder` accepted a `revision` argument, wrote it into `self.name` and
into every run record — and **never passed it to the loader.** The model
revision pin was decorative. Any revision sitting in your cache would have been
used while every run record claimed the pinned one. For a reproducibility claim
under NFR-5 that is worse than having no pin, because it reports a guarantee it
does not provide. The revision is now passed through, and
`tests/unit/test_matching.py` asserts both fixes against a fake with the 2.x
signature.

**Suite is now 119 tests.**

---

## 3. DEFECT (mine) — `scripts/init_repo.py` did not notice it was in the wrong repo

The script checked `git rev-parse --git-dir`, which **succeeds from inside any
ancestor repository.** With your home folder under version control, that check
passed, no `git init` happened, and every commit landed in the wrong place. The
final catch-all `git add -A` then tried to sweep your whole profile.

**Fixed.** The script now compares `git rev-parse --show-toplevel` against the
current directory and **refuses to run** if they differ, printing which repo it
found and the three ways out. The catch-all is also scoped to `-- .` so it can
never reach above the project directory even if the guard is bypassed.

Verified: in a nested repo it refuses; at the correct root it produces 18
commits and a clean tree.

### Also fixed: the 19th commit

Your run produced **19** commits, the last named "Add remaining project files".
That was `QUICKSTART.md`, which I wrote after building the increment list, so it
fell into the catch-all. It is now part of the documentation increment. A clean
run gives **18** commits and nothing in a catch-all — which matters, because the
increment commits are the evidence that the rulebook preceded the ground truth.

---

## 4. Your folder layout is nested, and that is fine

```
research-product-software\
  adif\
    .venv\          <- the virtual environment
    adif\           <- the project, and the git repository root
```

The venv being one level above the project is harmless — it is activated by
path, not by position. Do not try to tidy this now. The only thing that matters
is that **`git init` and every `git` command run from the inner `adif\adif`**,
which is where your log shows them running.

---

## 5. What to do, in order

Everything below runs from `...\research-product-software\adif\adif` with the
venv active.

### Step 0 — deal with the home-folder repo (item 1 above). Do this first.

### Step 1 — replace the code with this zip

Unzip over the top. **Keep your own `config/default.yaml`** if it already has
`model_revision` filled in — the copy in this zip has it as `null`, and
overwriting yours loses the hash. If you have already committed, check with
`git status` afterwards; you should see changes to `src/matching/stage3_semantic.py`,
`scripts/init_repo.py`, `requirements-optional.txt`, `requirements.txt`,
`tests/unit/test_matching.py`, plus this file.

### Step 2 — record the model revision

Your fetch succeeded and resolved:

```
1110a243fdf4706b3f48f1d95db1a4f5529b4d41
```

Open `config/default.yaml` and set it under the semantic stage:

```yaml
    semantic:
      model_revision: "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
```

This now actually constrains what gets loaded, which it did not before.

### Step 3 — confirm the fix

```powershell
python -m pytest -q                    # expect 119 passed
python -m scripts.demo --real-model    # loads the real model offline
```

If the demo runs, the `TypeError` is gone and the grid search will get further
than it did.

### Step 4 — derive the thresholds

```powershell
python -m eval.grid_search --real-model
```

This is the blocker everything else is waiting on. It searches on the six
development schemas and refuses to touch `data/heldout`. It prints the selected
thresholds; **copy them into `config/default.yaml` by hand** and log them in
methodology.md §5 with the date and the search range. They are development-set
results and must be labelled as such.

### Step 5 — fit the calibrator

```powershell
python -m eval.fit_calibration --real-model
```

### Step 6 — commit, then check the freeze gate

```powershell
git add -A -- .
git commit -m "Pin model revision and record grid-searched thresholds"
python -m scripts.freeze --check
```

`freeze --check` previously reported three blockers — no thresholds, no
calibrator, dirty tree. Steps 4, 5 and 6 clear all three.

### Step 7 — only then: tag the freeze, and build the held-out schemas

In that order, never the reverse. The tag's position in the history is the
entire anti-circularity argument.

---

## 6. Still yours, not mine

Three decisions block the freeze, and none is a coding task: **D20** (how many
ablation conditions), **D21** (how a demoted conflict loser is scored), **D22**
(whether batch is ADID identity or CDM data). They are written up in
`decisions.md`, with a recommendation on each. D21 in particular has to be
settled before the first scored run, because deciding it afterwards looks like
choosing a definition once you have seen the numbers.
