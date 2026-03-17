# GitHub Actions Setup

Your Concert Monitor is now configured to run automatically on GitHub Actions!

## How it works:
1.  **Schedule:** The monitor runs **twice per day** (10:00 AM and 10:00 PM UTC).
2.  **Notification:** It uses GitHub Secrets for your email credentials.
3.  **Persistence:** It commits the updated `concerts.db` back to your repository so it remembers what it has already found.

## Deployment Steps:

1.  **Push to GitHub:**
    ```bash
    git add .
    git commit -m "Add GitHub Actions workflow"
    git push origin main
    ```

2.  **Add Repository Secrets:**
    In your GitHub Repo, go to **Settings > Secrets and variables > Actions** and add the following:
    - `SMTP_SERVER`: (e.g., `smtp.gmail.com`)
    - `SMTP_PORT`: (e.g., `587`)
    - `SMTP_USER`: (Your email)
    - `SMTP_PASS`: (Your app-specific password)
    - `RECIPIENT_EMAIL`: (Where you want the alerts)

3.  **Grant Workflow Permissions:**
    Go to **Settings > Actions > General**. Under "Workflow permissions", select **"Read and write permissions"** and click **Save**. This allows the action to commit the database changes.

## Manual Run:
You can trigger a check anytime by going to the **Actions** tab on GitHub, selecting "Concert Monitor Scrape", and clicking **"Run workflow"**.
