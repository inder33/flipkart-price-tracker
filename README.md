# Flipkart Price Tracker

An async Python scraper that tracks product prices on Flipkart for any iPhone series search query. It scrapes all paginated search results, extracts structured product data, detects price changes on re-runs, and emails a summary report with the updated tracking sheet attached.

## Features

- **Dynamic search** — enter any product query (e.g. `17 pro max`) and the scraper builds the search URL automatically , caution : putting " iphone " in starting can cause double naming so please only enter the model number ex: 17,16 etc ..
- **Full pagination** — dynamically detects total page count and scrapes every page, no hardcoded limits
- **Async multi-tab scraping** — runs 5 browser tabs in parallel using `asyncio.gather()` for faster throughput
- **Structured data extraction** — pulls SKU, name, color, rating, price, currency, and availability directly from each product page's JSON-LD (`application/ld+json`) data
- **Duplicate & price-change detection** — checks scraped SKUs against existing CSV records; skips unchanged products, updates changed prices
- **Price history logging** — every detected price change is logged separately with old price vs. new price and a timestamped filename
- **Email reporting** — automatically sends a summary email with the price-change CSV attached and a total count of modified products
- **Anti-bot evasion** — uses SeleniumBase's undetected Chrome (CDP) mode connected to Playwright for more reliable scraping

## Tech Stack

- Python 3.12
- Playwright (async API)
- SeleniumBase (CDP / undetected-chrome mode)
- `csv` for data storage
- `smtplib` + `email.mime` for reporting
- `python-dotenv` for credential management

## How It Works

1. Launches an undetected Chrome browser via SeleniumBase CDP, connected to Playwright
2. Takes a product query as input and navigates to Flipkart's search results
3. Detects total page count from the pagination UI and loops through every page
4. Extracts product links from each results page
5. Visits each product page (5 at a time, in parallel) and pulls structured data from the embedded JSON-LD script tag
6. Cross-checks each SKU against the existing CSV:
   - New SKU → saved to `data.csv`
   - Existing SKU, same price → skipped
   - Existing SKU, price changed → updates `data.csv` and logs the change to a separate price-history CSV
7. Sends an email at the end of the run with the price-change CSV attached and a total change count

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file inside `src/` with your email credentials:

```
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

Run the scraper:

```bash
python src/main.py
```

You'll be prompted to enter a product query (e.g. `17 pro max`), and the scraper will handle the rest.

## Notes

- Email sending uses Gmail's SMTP with an [App Password](https://support.google.com/accounts/answer/185833) — not your main account password.
- This project is under active development. Planned additions include Google Sheets sync, proxy rotation, scheduled runs, and Docker support.

## Disclaimer

This project is for educational purposes. Scraping any website should comply with that site's terms of service.
