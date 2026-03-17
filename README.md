# Concert Monitor

A personal concert monitoring system to track announcements for your favorite artists across Australia, China, Hong Kong, and SEA.

## Features
-   **Artist Management:** Add artists with multiple keywords (English/Chinese).
-   **Multi-Source Monitoring:** Designed to support multiple ticketing sites (Ticketmaster, Damai, etc.).
-   **Email Notifications:** Get alerted when new concerts are found.
-   **Dashboard:** Simple web interface to view upcoming concerts and logs.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install  # Required if using real scrapers
    ```

2.  **Configuration:**
    Create a `.env` file (optional, for email):
    ```ini
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USER=your-email@gmail.com
    SMTP_PASS=your-app-password
    RECIPIENT_EMAIL=your-email@gmail.com
    ```

3.  **Run the App:**
    ```bash
    python app.py
    ```
    Open http://127.0.0.1:5001 in your browser.

## Usage
1.  Go to the **Artists** tab.
2.  Add an artist (e.g., Name: "Eason Chan", Keywords: "Eason Chan,陈奕迅").
3.  Go to the **Dashboard** and click "Check for Updates Now".
4.  If the Mock Scraper is active, you might see a fake concert appear (30% chance).

## Extending
To add real scrapers, edit `app.scrapers.ticketmaster_au.py` or create new scrapers inheriting from `BaseScraper`. Register them in `app.py`.
