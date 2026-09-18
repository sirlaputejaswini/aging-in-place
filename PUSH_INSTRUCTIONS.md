# Pushing this repo to GitHub

This repo was built locally and has **not** been published. To put it on GitHub:

1. Create a new **public** repository on github.com named `aging-in-place`
   (do not initialize it with a README, license, or .gitignore — this repo
   already has them).
2. From this directory, run:

```bash
git remote add origin git@github.com:<your-username>/aging-in-place.git
git branch -M main
git push -u origin main
```

3. Double-check before pushing:
   - `git status` shows no files under `data/` (gitignored).
   - No API keys or credentials anywhere: `git grep -i "api_key\|apikey\|secret\|token" -- .`
