# Deploy checklist — Multi-Agent Content Team

This is the project's "definition of done." Walk it top to bottom. Don't tick a box you
haven't actually verified by running the command — "should work" isn't the same as "works."

## Runs locally

- [ ] Fresh virtual environment, dependencies installed cleanly (from `build_from_scratch/`):
      `python -m venv .venv ; .\.venv\Scripts\Activate.ps1` then `pip install -r requirements.txt`
- [ ] The terminal runner works offline, no API key:
      `python -m content_team "how sleep affects learning"` prints the handoff log and the
      final post.
- [ ] The interactive human gate works:
      `python -m content_team "remote work" --interactive` lets you approve / revise / reject.
- [ ] The web app runs offline in a browser:
      `streamlit run web_app.py` opens the page at `http://localhost:8501`, you enter a topic,
      click **Run the team**, and watch the Researcher → Writer → Editor status panel.
- [ ] The handoff panel ("How the team collaborated") shows the agent handoffs, and the
      **Approve and ship** / **Reject** buttons produce the final post.
- [ ] (Optional) The "use a real model" toggle works with a key in `.env`, OR is left alone —
      offline is the default and needs nothing.

## Tests pass

- [ ] `pytest` run from `build_from_scratch/` is all green (18 tests, all offline, no key).
- [ ] You ran it in the fresh venv, not just your everyday one, so you know the deps are complete.

## README is recruiter-ready

- [ ] A root `README.md` exists and covers: the problem, what the team does, how to run it, and
      what you learned. (Point deeper detail at `build_from_scratch/README.md`.)
- [ ] A **screenshot or GIF** of the team collaborating — the handoff log plus the final post —
      is embedded (`docs/team.png` or a short GIF). The collaboration story is the memorable
      visual; show it.
- [ ] The live demo URL is near the top (add it after Step 6).
- [ ] The CI status badge is at the top.

## Secrets are clean

- [ ] The root `.gitignore` contains `.env` and `build_from_scratch/.env`; the
      `build_from_scratch/.gitignore` contains `.env` (plus `*.post.md`, `post.md`,
      `run_transcript.json`, `.venv/`, `__pycache__/`). The root also ignores `data/*`.
- [ ] `git status` shows `.env` is NOT tracked.
- [ ] `git ls-files` output contains NO `.env` (only `.env.example`). If `.env` is there,
      remove it and rotate the key — see the hosting guide's troubleshooting section.
- [ ] No API key is hardcoded anywhere in the source.

## Pushed to GitHub

- [ ] Repo created empty on github.com (no auto README/license), named
      `multi-agent-content-team`, public.
- [ ] `git init` → `git add .` → `git commit` → `git branch -M main` →
      `git remote add origin ...` → `git push -u origin main` all done (from the project root).
- [ ] Files visible on the GitHub repo page after a refresh.

## CI is green

- [ ] `.github/workflows/ci.yml` is committed and pushed.
- [ ] The Actions tab shows a completed run with a green checkmark.
- [ ] The run used NO secrets (the tests are offline) — confirm it passed without any API key
      configured. That's a selling point; mention it in the README.
- [ ] If it was red, you read the log and fixed the cause (usually a missing dep in
      `build_from_scratch/requirements.txt`), then re-ran to green.

## Live demo

- [ ] Deployed free to Streamlit Community Cloud (main file path
      `build_from_scratch/web_app.py`) or Hugging Face Spaces.
- [ ] Opening the public URL loads the page and you can run a topic through the team — it uses
      the **offline agents**, so it works for anyone with no key.
- [ ] (Only if you enabled a real model) the API key is set as a host **Secret**
      (`GEMINI_API_KEY`) — never in code — and the sidebar toggle uses it. You chose the free
      Gemini tier, or accepted the cost of a paid model knowingly.
- [ ] The live demo URL is added to the top of the README.

## Repo pinned

- [ ] `multi-agent-content-team` is pinned on your GitHub profile so it shows up first.

When every box is ticked, the project is done and presentable. Send the repo link with
confidence.
