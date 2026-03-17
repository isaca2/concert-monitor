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

## Auto-Deployment (Web Dashboard)

To make your web dashboard accessible online and auto-update whenever a new concert is found:

1.  **Create a [Render](https://render.com) Account.**
2.  **Click "New" > "Blueprint".**
3.  **Connect your GitHub Repository.**
4.  Render will automatically find the `render.yaml` file and set up your web service.
5.  **Set Environment Variables:**
    In the Render dashboard for your service, go to **Environment** and add:
    - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `RECIPIENT_EMAIL` (Same as GitHub Secrets).

### How the "Poor Man's Sync" Works:
1.  **GitHub Action** runs the scraper -> Updates `instance/concerts.db` -> **Pushes** back to GitHub.
2.  **Render** sees the new push -> **Auto-deploys** your web app.
3.  The new web app now has the updated database with the latest concerts!

*Note: Since the database is stored in the Git repo, if you add an artist on the **deployed website**, it will work temporarily but will be **overwritten** the next time the scraper runs and pushes. For permanent artist changes, add them in your **local** app and push.*
