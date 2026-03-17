# GitHub Pages Auto-Deployment

Your Concert Monitor is now configured for a simple, completely free **"Local Management + Online Dashboard"** workflow using GitHub Pages.

## How it works:
1.  **Manage Artists Locally:** Use the `python app.py` interface on your computer to add/remove artists. When done, `git add`, `commit`, and `push` your database.
2.  **GitHub Action:** 
    - Runs the scraper twice a day.
    - Updates your `concerts.db` in the repo.
    - Generates a static version of your dashboard (`index.html`).
    - **Deploys that dashboard to GitHub Pages.**
3.  **View Results Anywhere:** Access your dashboard online (e.g., `https://isaca2.github.io/concert-monitor/`).

## Setup Steps:

1.  **Push the new configuration:**
    ```bash
    git add .
    git commit -m "Switch to GitHub Pages static deployment"
    git push origin main
    ```

2.  **Add Repository Secrets (for Email):**
    On GitHub, go to **Settings > Secrets and variables > Actions** and add:
    - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `RECIPIENT_EMAIL`.

3.  **Enable GitHub Pages:**
    - Go to **Settings > Pages**.
    - Under **Build and deployment > Source**, select **"Deploy from a branch"**.
    - Select branch: **`gh-pages`** and folder: **`/(root)`**.
    - Click **Save**.

4.  **Workflow Permissions:**
    - Go to **Settings > Actions > General**.
    - Under **Workflow permissions**, select **"Read and write permissions"**.
    - Click **Save**.

## Manual Trigger:
You can manually run a check and update the website by going to the **Actions** tab on GitHub, selecting "Concert Monitor Scrape & Deploy", and clicking **"Run workflow"**.
