# Git workflow

The grading needs **every member's work to be traceable to commits from their own GitHub account**.
These rules make that automatic.

## One-time setup (each member, on their own laptop)
```bash
git config --global user.name  "Your Full Name"
git config --global user.email "the-email-of-your-github-account@example.com"   # must match GitHub
git clone https://github.com/<group-repository>.git
cd <repo> && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python -m pytest            # must pass before you start
```
A commit counts on your GitHub profile only if its e-mail matches one of your GitHub e-mails
(*GitHub → Settings → Emails*).

## Akshat (repository owner) once
1. Create the repository on GitHub (private or public as the faculty prefers) and push the project.
2. *Settings → Collaborators*: add the four others with **Write** access.
3. *Settings → Branches → Add rule* for `main`: **Require a pull request before merging**, with
   **1 approval**.

## Every change
```bash
git switch main && git pull                      # start from the latest main
git switch -c feat/harsh-tab-completion          # branch: <type>/<name>-<topic>
# ... edit, then run the tests ...
python -m pytest
git add teleop/cli.py tests/test_cli.py
git commit -m "feat(cli): tab-completion for command names"
git push -u origin feat/harsh-tab-completion
```
Then open a **pull request** on GitHub. Ask the reviewer named in your commit plan to review it, then
merge it with **"Squash and merge" OFF** (use "Create a merge commit" or "Rebase and merge"), so your
individual commits keep your name.

## Commit message format (Conventional Commits)
```
<type>(<scope>): <what changed, imperative, <= 72 chars>

optional body: why, and what was tested
```
Types: `feat` new feature · `fix` bug fix · `test` tests only · `docs` documentation · `perf` speed ·
`refactor` restructure without behaviour change · `chore` tooling · `exp` experiment data/results.
Scopes: `cli protocol tcp mqtt server backend coppelia control safety netem exp report docs`.

## Review rule
Each pull request is reviewed by a **different** member. The default reviewer pairs are:

| Author | Reviewer |
|---|---|
| Akshat | Priyam |
| Harsh | Aniket |
| Aniket | Harsh |
| Priyam | Yeshang |
| Yeshang | Akshat |

The reviewer runs `python -m pytest` on the branch and leaves at least one specific comment.

## Do not
* commit for someone else, or with someone else's name or e-mail;
* rewrite shared history (`git push --force` to `main`);
* commit `.venv/`, large binaries, or personal logs (`.gitignore` covers them).

## Contribution evidence for report Section 10
```bash
python scripts/git_author_stats.py --files
```
prints commits, files and lines per author. Paste the table into Section 10 and the Appendix.
