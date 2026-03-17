# GitHub Pages Auto-Deployment (FREE)

Since your repository is now **Public**, you can host your concert dashboard for **FREE** forever using GitHub Pages.

## How it works:
1.  **Manage Artists Locally:** Run `python app.py` on your Mac to add/remove artists. When done, `git add`, `commit`, and `push` your changes.
2.  **GitHub Action:** 
    - Runs the scraper twice a day.
    - Updates `instance/concerts.db`.
    - Generates a static dashboard (`index.html`).
    - **Deploys automatically to GitHub Pages.**
3.  **View Results Anywhere:** Access your dashboard at `https://isaca2.github.io/concert-monitor/`.

## Setup Steps:

1.  **Enable GitHub Pages:**
    - Go to your GitHub Repo **Settings > Pages**.
    - Under **Build and deployment > Source**, select **"Deploy from a branch"**.
    - Select branch: **`gh-pages`** and folder: **`/(root)`**.
    - Click **Save**.

2.  **Add Repository Secrets (CRITICAL for Privacy):**
    Even though the repo is public, your email credentials stay private! Go to **Settings > Secrets and variables > Actions** and add:
    - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `RECIPIENT_EMAIL`.

3.  **Workflow Permissions:**
    - Go to **Settings > Actions > General**.
    - Under **Workflow permissions**, select **"Read and write permissions"**.
    - Click **Save**.

## Manual Trigger:
You can manually update the website by going to the **Actions** tab on GitHub, selecting "Concert Monitor Scrape & Deploy", and clicking **"Run workflow"**.
