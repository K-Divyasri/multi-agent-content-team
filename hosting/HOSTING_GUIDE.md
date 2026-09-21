# Publishing Multi-Agent Content Team

This project has two things worth showing the world, and hosting means both. First, a
**GitHub repo a recruiter can open and immediately get** — clean README, a little green
checkmark proving the tests pass on every push. Second — the fun part — an actual **live
app** anyone can open in a browser: type a topic, watch a Researcher, a Writer, and an
Editor collaborate, then approve or reject the post yourself. No install, no key, just a URL.

Here's the whole plan, so you know where this is going:

1. **A GitHub repo** — your code, online, public, with a README that lands the project fast.
2. **CI** — GitHub automatically runs your 18 tests on every push. Green check = it works.
3. **A live demo** — the Streamlit app, hosted free, with a public URL you can paste onto a
   CV. Because it defaults to the offline fake agents, the public demo costs nothing and
   needs no API key.

One thing about CI that's genuinely rare for an "AI project" and worth calling out up front:
**your whole test suite runs offline.** The team has deterministic fake agents built in, so
all 18 tests pass without ever calling a real LLM — including the full research → write →
edit → human-approval loop. That means CI needs **no API key and no secrets** — 18 tests go
green on a clean machine, free, every push. Most AI repos can't be tested in CI at all
because they need a paid key. Yours can, honestly, every time. Say so in your README; it's a
selling point.

The real code lives at the repo root: `content_team/`, `tests/`, `web_app.py`, and
`requirements.txt` sit directly next to this `hosting/` folder, so no path below needs a
subfolder prefix.

A note on the commands: the terminal runner is `python -m content_team "your topic"`, because
that's how the package runs. After a `pip install -e .` you can also type `content-team
"your topic"` directly. Both do the same thing. Use whichever you actually installed.

---

## Step 0 — Install Git and make a GitHub account

Git is the program that tracks versions of your files. GitHub is the website that stores a
copy online so other people (and recruiters) can see it. You need both. They're different
things — Git runs on your laptop, GitHub lives on the internet. Git is the filing system;
GitHub is the shelf you put the folder on so others can reach it.

### Install Git

1. Go to https://git-scm.com/download/win. The download starts on its own.
2. Run the installer. Click Next through every screen — the defaults are fine. You do not
   need to understand any of the options.
3. When it finishes, open a **new** PowerShell window (it has to be new so it picks up the
   install) and check it worked:

```powershell
git --version
```

If you see something like `git version 2.45.0`, you're done. If PowerShell says it doesn't
recognize `git`, close every terminal, open a fresh one, and try again.

### Make a GitHub account

1. Go to https://github.com and sign up. Use your real email (`mathuransada@gmail.com` is the
   one on file). Verify it.
2. Pick a username you'd be happy putting on a CV — recruiters see it. `divya-dev` beats
   `xX_coder_Xx_2009`.
3. That's all for now. You'll make the actual repo in Step 3.

### Tell Git who you are

Do this once per machine. Git stamps your name and email onto every commit (a commit is a
saved snapshot of your code). Use the same email as your GitHub account.

```powershell
git config --global user.name "Your Name"
git config --global user.email "mathuransada@gmail.com"
```

---

## Step 1 — Know what goes in the repo and what must NOT

This is the part that bites people, so read it before you touch any Git command.

Some files belong on GitHub. Some must never leave your laptop. The line between them is a
file called `.gitignore` — a plain-text list of things Git pretends don't exist. This project
ships one, at the repo root (`.gitignore`). It covers everything that matters. Open it
and confirm it includes at least these lines.

Repo-root `.gitignore`, the essentials:

```
.env
__pycache__/
*.pyc
.venv/
venv/
*.egg-info/
.pytest_cache/
.ipynb_checkpoints/
data/*.json
data/*.md
data/*.txt
```

Project-specific lines, also in the same `.gitignore`:

```
.env
*.post.md
post.md
run_transcript.json
__pycache__/
*.pyc
.venv/
venv/
*.egg-info/
.pytest_cache/
```

Here's what these keep out and why it matters:

- **`.env`** — this is the important one. If you turn on the "use a real model" toggle (or run
  the CLI with `--real`), your `.env` holds an API key — your free Gemini key, or a Groq /
  Anthropic one. **A key is a password.** If you commit it, it's on the public internet
  **forever** — deleting it in a later commit doesn't help, because Git keeps the whole
  history, and bots scrape GitHub for leaked keys within minutes of a push. Someone else then
  runs up a bill on your account. So: **`.env` never gets committed, ever.** The repo ships a
  `.env.example` instead, which lists the variable names with blank values so other people
  know what to fill in. That one is safe and is *meant* to be committed. This is the golden
  rule of this whole guide — everything else is mechanics.
- **`data/*.json`, `data/*.md`, `data/*.txt`** — the sample data is *generated* by
  `generate_data.py`, not hand-written source. Anyone who clones the repo just runs that
  script to recreate it, so there's no need to store it in Git. Good news specific to this
  project: **the web app doesn't need any data file to run.** It builds a fresh `TeamState` in
  memory and runs the team from scratch every time. So unlike some projects, there is nothing
  in `data/` you must commit for the demo to work. Leaving `data/*` ignored is exactly right.
- **`*.post.md`, `post.md`, `run_transcript.json`** — posts and run logs you generate while
  driving the team (for example with the CLI's `--out post.md`). They're your own output, not
  source; keep them off GitHub.
- **`__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`** — junk Python and pytest create
  as they run. Nobody needs to see it; it just clutters the repo.
- **`.venv/`, `venv/`** — your virtual environment. It's hundreds of megabytes of installed
  packages specific to your machine. Other people rebuild it from `requirements.txt`; they
  never want yours.

The `.env.example` pattern, spelled out, because it's the safe habit to internalize:

```
# .env.example  -- committed. Names only, no values. Safe.
GEMINI_API_KEY=
CONTENT_TEAM_MODEL=gemini/gemini-1.5-flash
```

```
# .env  -- NEVER committed. Real secret. Git-ignored.
GEMINI_API_KEY=AIzaSyD-your-actual-secret-key-here
CONTENT_TEAM_MODEL=gemini/gemini-1.5-flash
```

Same file, one word of difference in the name, and `.gitignore` makes all the difference
between them. Anyone who clones your repo copies `.env.example` to `.env` and pastes in their
own key.

The rule of thumb: **source code, config, docs, and the tests go in. Secrets, generated data,
saved posts, and machine-specific junk stay out.**

---

## Step 2 — Make the local repo and commit

The repo root is the **project folder** — the one that
contains `content_team/`, `tests/`, and this `hosting/` folder. Open PowerShell
*there*.

```powershell
git init
```
Creates an empty Git repo here — a hidden `.git` folder that will track your files.

```powershell
git add .
```
Stages every file in the folder *except* the ones `.gitignore` excludes. "Staging" means
marking them to go into the next snapshot. This project has a `.gitignore` at the repo root
that protects `.env`. That's exactly what you want.

```powershell
git commit -m "Initial commit: Multi-Agent Content Team -- Researcher/Writer/Editor + human gate"
```
Saves a snapshot of everything staged, with a short message describing it.

Now the single most important check in this whole guide:

```powershell
git status
```

Read the output. You want to see `nothing to commit, working tree clean`. Then run one more,
which lists every file Git is actually tracking:

```powershell
git ls-files
```

Scan that list. You must **not** see `.env` anywhere (`.env.example` is fine and expected). If
`.env` shows up, you committed your secret — go to the troubleshooting section at the bottom
(`Committed .env by accident`) and fix it before you push anything to the internet.

---

## Step 3 — Make the empty repo on GitHub and push

### 3a. Create the empty repo

A "remote" is just a copy of your repo that lives somewhere else — in this case, on GitHub's
servers. You're about to create that remote copy and then connect your local repo to it.

In the browser:

1. Go to github.com, signed in.
2. Top-right, click the **+** then **New repository**.
3. Name it `multi-agent-content-team` (lowercase, hyphens, no spaces).
4. Add a one-line description: *"A Researcher/Writer/Editor agent team that collaborates to
   write a blog post through a hand-rolled orchestrator, with a human-in-the-loop approval
   gate."*
5. Leave it **Public** — you want recruiters to see it.
6. Do **not** tick "Add a README", "Add .gitignore", or "Add a license". You need the repo
   completely empty, or your first push will collide with the files GitHub adds. Leave every
   box off.
7. Click **Create repository**.

GitHub shows you a setup page with a bunch of commands. Ignore most of it; use what's below.

### 3b. Connect your local repo to GitHub and push

Copy the repo URL from that page — the
`https://github.com/YOURNAME/multi-agent-content-team.git` one. Then, back in PowerShell at
the project root:

```powershell
git branch -M main
```
Renames your current branch to `main`. A "branch" is a line of development; `main` is GitHub's
default name for the primary one. You'll only ever have the one branch for a project like this.

```powershell
git remote add origin https://github.com/YOURNAME/multi-agent-content-team.git
```
Tells your local repo where the GitHub copy lives. `origin` is just the conventional nickname
for that URL, so you don't have to type the whole thing every time.

```powershell
git push -u origin main
```
Uploads ("pushes") your commits to GitHub. The `-u` links your local `main` to the remote one,
so next time you can just type `git push` with nothing after it.

The first push pops up a browser window or a login prompt to authenticate with GitHub. Do it.
If it asks for a *password* typed into the terminal, that won't work — GitHub turned off
password auth years ago. Use the browser sign-in it offers (easiest), or a Personal Access
Token as the password (covered in troubleshooting).

Refresh your GitHub repo page. Your files are there. The code is published.

---

## Step 4 — Write a README a recruiter will actually read

A recruiter spends maybe twenty seconds on your repo before deciding whether to keep reading.
The README is the first thing they see (GitHub renders it right under the file list), so it
has to land the project fast.

You already have a strong README at the repo root (`README.md`) — it's the model to
follow for voice and length, and it already covers the problem, the skills, how to run it, and
what you learned. GitHub shows the **root** `README.md` first, so make sure its top sells the
project and the full detail sits further down.

Keep it skimmable. Five things, in this order:

1. **The problem, in one or two sentences.** Asking one model to "research, write, and edit a
   great post" in a single shot makes it hold three mindsets at once, and nothing checks its
   work. Split the job across role-specialised agents — a Researcher, a Writer, an Editor —
   and they hand drafts back and forth, catch each other's gaps, and produce something better,
   the way a real content team does. The hard part isn't the agents; it's the **orchestrator**
   that routes work between them.
2. **What it does.** A short bullet list: three role agents that collaborate on a blog post;
   an explicit **state machine** that routes handoffs (Researcher → Writer → Editor) with a
   **revision loop** and a stop condition (`max_revisions`) so the Editor can't bounce a draft
   forever; a **human-in-the-loop** approval gate (approve / revise / reject); runs **offline
   by default** with deterministic fake agents so no API key is needed, and flips to a real
   LLM through LiteLLM when you provide a key.
3. **The live demo link.** Put the `*.streamlit.app` URL right near the top once Step 6 is
   done — a clickable app where you watch three agents collaborate is the strongest thing on
   the page. (See Step 6e.)
4. **How to run it.** The exact commands, copy-pasteable:

   ```powershell
   python -m venv .venv ; .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python -m content_team "how sleep affects learning"        # offline run in the terminal
   python -m content_team "remote work" --interactive         # you are the approval gate
   streamlit run web_app.py                                    # the web UI in a browser
   ```

   Mention that the optional real-model path (`--real`, or the web app's sidebar toggle) needs
   a free Gemini key in `.env` (point at `.env.example`), and that everything else — including
   the whole test suite — works with no key at all.
5. **What you learned.** Two or three honest lines: that a multi-agent "system" is really a
   **state machine** over role-specialised agents — the agents are the easy part, the routing
   is the design; that handoffs need one shared **state object**, not a game of telephone; that
   any agent loop (the Editor bouncing a draft back to the Writer) needs a **stop condition**
   or it runs forever; and that **human-in-the-loop** is just a gate function, so swapping
   auto-approve for a real person is a one-line change — which is exactly what makes this
   shippable rather than a toy. This is the section that separates "I followed a tutorial" from
   "I understand what I built."

Don't pad it. A tight README beats a long one.

### 4b. Add a screenshot or GIF — this is high value

For this app a picture does a lot of work: it proves it's a real running thing, and the
**collaboration story is the memorable visual**. Start the app locally (`streamlit run
web_app.py` from the repo root), enter a topic, run the team, and capture it.

- **Screenshot:** press **Win + Shift + S**, drag a box around the browser window showing the
  **"How the team collaborated (handoffs)"** panel expanded plus the final post, paste into
  Paint, save as `docs/team.png`. Embed with `![Three agents collaborating on a post,
  with the handoff log](docs/team.png)`.
- **GIF (even better):** use the built-in Xbox Game Bar (**Win + G**) or a tool like
  ScreenToGif to record a full run — you type a topic, the status panel shows the Researcher,
  then the Writer, then the Editor asking for a revision, then the human Approve/Reject
  buttons. Watching the handoffs tick past and then clicking **Approve and ship** is genuinely
  compelling — it *shows* the whole idea in ten seconds. Save it under `docs/` and embed the
  same way.

Either way, the payoff is that someone judges the project in five seconds without cloning
anything.

---

## Step 5 — Add CI so the tests run on every push

Right now your tests pass *on your laptop*. CI proves they pass on a clean machine too, every
time you push. "Continuous Integration" is just that idea: every change is automatically built
and tested the moment it lands, so a broken change gets caught in minutes instead of sitting
there until someone trips over it. GitHub shows a green checkmark next to your commits when the
tests pass — recruiters notice it, and it catches the classic "works on my machine" bug where
you forgot to list a dependency.

Here's the part that's a genuine selling point for *this* project, and it's worth repeating:
**the tests run offline, so CI needs no API key.** The team has deterministic fake agents
standing in for a real LLM, so all 18 tests pass — including the full research → write → edit →
human loop — without ever calling a model. That means there are no secrets to configure in
GitHub, nothing to leak, and the CI run is fast and free. A lot of "AI projects" can't be
tested in CI at all because they need a paid key — yours can, honestly, every push. Put that
line in your README.

In this hosting folder there's a ready-to-use workflow at `github_actions/ci.yml`. A workflow
only runs if it lives at `.github/workflows/` **inside the repo**. So copy it there. From the
project root:

```powershell
mkdir .github\workflows
copy hosting\github_actions\ci.yml .github\workflows\ci.yml
```

Open `.github\workflows\ci.yml` and read the comments — it's annotated line by line. The one
thing worth understanding: because the code sits at the repo root, the workflow installs
from `requirements.txt` and runs pytest straight from the repo root, with no
`working-directory`. Then commit and push:

```powershell
git add .github\workflows\ci.yml
git commit -m "Add GitHub Actions CI to run tests offline on every push"
git push
```

Go to your repo's **Actions** tab. You'll see the workflow running. Click into it to watch the
steps expand live — checkout, install Python, install dependencies, run pytest. Green check
means all 18 tests passed on GitHub's machine, with no key configured. If it goes red, click
the failed step and read the log bottom-up; the real error is usually in the last few lines (a
missing dependency in `requirements.txt` is the most common cause).

Once it's green, add the status badge to the top of your README so the checkmark is visible
without clicking. On the workflow's Actions page there's a `...` menu with **Create status
badge** — it gives you a line of markdown to paste at the very top of `README.md`.

---

## Step 6 — Deploy the live demo

This is the payoff. Your app is already a Streamlit app (`web_app.py`), and
Streamlit apps host free in a couple of places. You don't rewrite anything — the app *imports*
your `content_team` package and drives the same `research` → `write` → `edit` stages the CLI
uses, then draws a page with a status panel, the handoff log, and Approve/Reject buttons
instead of printing to a terminal.

The default is the **offline fake agents**, so the deployed demo costs nothing and needs no
secret. Someone can open the URL, type a topic, and watch the team work immediately. If you
later want a real model behind it, there's a sidebar toggle and you add a key as a host
Secret — covered in 6c.

**Try it locally first.** If it runs on your laptop, it'll run hosted:

```powershell
pip install -r requirements.txt
streamlit run web_app.py
```

It opens a browser tab at `http://localhost:8501` with the topic box in the sidebar, a live
status panel, and the human review buttons. Run a topic through to confirm.

### 6a. Streamlit Community Cloud (easiest, since your code is already on GitHub)

1. Go to https://share.streamlit.io and **sign in with GitHub**.
2. Click **New app**, then **Deploy a public app from GitHub**.
3. Pick your `multi-agent-content-team` repo and the `main` branch.
4. Set **Main file path** to `web_app.py`. The app lives at the repo root.
5. Click **Deploy**. Streamlit reads `requirements.txt` automatically,
   installs `streamlit` and the rest, builds, and gives you a public `*.streamlit.app` URL.

That URL is your live demo. It runs the offline agents, so it just works for anyone, no key.

**The one gotcha worth understanding — imports.** The app does
`from content_team.agents import edit, research, write`, so Python has to be able to find the
`content_team` package. On Streamlit Cloud the process starts at the repo root, but Streamlit
automatically adds the **main file's own folder** to the import path — and since you pointed it
at `web_app.py`, that puts the repo root on the path, right where
`content_team/` sits next to `web_app.py`. So the import resolves with no extra work. If for
some reason you ever see a `ModuleNotFoundError: content_team`, the belt-and-braces fix is
three lines at the very top of `web_app.py`, before the `from content_team...` imports:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
```

That explicitly adds the app's folder to the path. You almost certainly won't need it, but now
you know the fix if you do.

### 6b. Or — Hugging Face Spaces

Hugging Face **Spaces** also hosts Streamlit apps free.

1. Make a free account at https://huggingface.co.
2. Click **New Space**. Name it `multi-agent-content-team`, pick **Streamlit** as the SDK,
   leave it public.
3. A Space *is* a Git repo. Push your project to it (it gives you the URL), or use the web UI
   to upload your files. A Space expects the app at a top-level `app.py` and reads a top-level
   `requirements.txt`. The simplest way to fit that shape: at the Space's root add a tiny
   `app.py` that hands off to your real app, and a `requirements.txt` listing at least
   `streamlit`. The one-line `app.py`:

   ```python
   # app.py -- entry point for Hugging Face Spaces; runs the real app.
   import runpy, sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent))
   runpy.run_path("web_app.py", run_name="__main__")
   ```

4. The Space builds and gives you a public URL like
   `https://huggingface.co/spaces/YOURNAME/multi-agent-content-team`. That's your live demo.

Streamlit Cloud (6a) is less fiddly because it points straight at
`web_app.py` and needs no wrapper. Use it unless you specifically want a
Space.

### 6c. If you want the demo to use a REAL model

The offline demo is the safe default and needs no secret. If you want a "run the team on a real
model" option, the app already has it: the sidebar's **"Use a real model"** toggle. When it's
on, the app looks for an API key — first in the host's Secrets, then in the environment — and
routes each agent's call through LiteLLM. (If no key is found, it prints a note and quietly
falls back to the offline agents, so the demo never breaks.)

Here's the rule that never changes: **the key goes in the hosting service's Secrets manager,
never in your code or your repo.**

- **Streamlit Cloud:** open the app's **Settings → Secrets** and add your key, for example:

  ```toml
  GEMINI_API_KEY = "AIzaSyD-your-actual-secret-key-here"
  ```

- **Hugging Face:** the Space's **Settings → Secrets and variables**, add `GEMINI_API_KEY`.

The service injects it at runtime, so your public `web_app.py` never contains the key. Same
golden rule as `.env`, just in the cloud. Get a free Gemini key in about 30 seconds at
https://aistudio.google.com/apikey.

**A word on cost before you reach for a paid model.** Gemini's free tier is plenty for a demo,
so start there — it costs nothing. If you later want to pay for a higher-quality model, Claude
is the usual choice; current model IDs are `claude-opus-4-8`, `claude-sonnet-5`, and
`claude-haiku-4-5`, with `claude-haiku-4-5` being the cheap, fast one. You'd set
`ANTHROPIC_API_KEY` as the Secret and type the model string into the sidebar's model box. But
for a public portfolio demo, leaving it on the free offline agents — or free Gemini — is the
sensible default. A stranger clicking your link should never cost you money.

### 6d. Keep the demo cheap and safe

Because the default is offline, a public link can't run up a bill on its own. If you *do* wire
up a real key, remember that anyone with the URL can now spend your quota — and this team makes
several model calls per run (Researcher, Writer, and Editor, once per revision), so prefer the
free Gemini tier, and know you can pull the key out of Secrets any time to instantly fall the
demo back to offline.

### 6e. Link the demo from your README

Once it's live, put the URL near the top of your README so nobody misses it:

```markdown
**Live demo:** https://YOURNAME-multi-agent-content-team.streamlit.app
```

A clickable app where three agents collaborate and you approve the result, a green CI badge,
and a short GIF of the handoffs is a genuinely strong portfolio page.

---

## Step 7 — Pin the repo on your profile

By default your GitHub profile shows repos in whatever order. Pinning puts the good ones up top
so a recruiter sees them first.

1. Go to your profile page (`github.com/YOURNAME`).
2. Find the **Customize your pins** link (or **Pin** on a repo card).
3. Tick `multi-agent-content-team`. You can pin up to six.
4. Save.

Now it's one of the first things on your profile. Done.

---

## Optional — publishing it for others to install

You don't need this for a portfolio, but it's worth knowing the next step exists.

Because the repo root has a `pyproject.toml` with a `content-team` console script, it's
already shaped like a real installable package. Later, you could publish it to **PyPI** (the
Python Package Index) so anyone can `pip install` it, or let people run it in an isolated
environment with **pipx**. That involves making a PyPI account, building the package, and
uploading with a tool called `twine`. It's a good exercise once the repo is polished — but
don't let it block you now. A clean GitHub repo with green CI and a live demo is what gets you
the interview.

---

## Common Git mistakes (troubleshooting)

**You committed `.env` by accident.** First, stop and treat the key as compromised — go to the
provider (Google AI Studio, Groq, Anthropic) and **revoke/rotate it**, because if you already
pushed, it's already public. Then remove the file from Git while keeping it on disk:

```powershell
git rm --cached .env
git commit -m "Remove committed .env"
git push
```

Confirm `.env` is in `.gitignore` so it doesn't come back. Note that `git rm --cached` only
removes it going forward — the key still sits in your Git *history*, which is exactly why you
rotate the key rather than relying on deletion. (Fully scrubbing history is possible with tools
like `git filter-repo`, but rotating the key is the real fix.)

**`error: failed to push` / push rejected.** The remote has commits your local repo doesn't —
almost always because you let GitHub add a README or license when creating the repo. Pull and
replay your work on top, then push:

```powershell
git pull origin main --rebase
git push
```

Next time, create the repo completely empty.

**Authentication fails on push.** GitHub no longer accepts your account password in the
terminal. Two clean ways to fix it:

- **GitHub CLI (easiest):** install it from https://cli.github.com, then run `gh auth login`
  and follow the browser prompts. It handles auth for all future Git commands.
- **Personal Access Token:** on github.com go to **Settings → Developer settings → Personal
  access tokens → Tokens (classic) → Generate new token**, give it the `repo` scope, copy the
  token, and paste it as the *password* when Git prompts you. Treat the token like a password —
  don't commit it anywhere.

**`git: command not found` after installing.** You're in a terminal that opened before the
install. Close every PowerShell window and open a fresh one.

**A huge file won't push (over ~100 MB).** GitHub rejects files above 100 MB. You probably
staged something that should've been ignored — a `.venv`, a cached model. Remove it from
staging, add it to `.gitignore`, and commit again:

```powershell
git rm --cached path\to\the\big\file
```

**CI is red but the tests pass on my laptop.** Read the Actions log bottom-up. The usual cause
is a dependency you have installed locally but forgot to list in
`requirements.txt` — CI starts from nothing, so it only has what's listed.
Add the missing package, commit, push, and it re-runs automatically. (It won't be a missing API
key — the tests are offline by design, which is the whole point.)

**The deployed app shows `ModuleNotFoundError: content_team`.** Streamlit couldn't find the
package. Make sure the **Main file path** is `web_app.py` (at the repo root), so
the app's own folder — where `content_team/` lives — lands on the import
path. If it still happens, add the three `sys.path` lines from Step 6a to the top of
`web_app.py`.
