# VIP-Data-Scripts

Python scrapers for pulling real estate and property data from multiple US states (Florida, Kansas, Maine, Minnesota, Vermont). Each state has its own scraper tuned to the source site's structure. Data is written to CSV and can be pushed to Google Sheets via the Sheets API with pandas for transformation.

```bash
pip install pandas gspread oauth2client requests beautifulsoup4
python Florida/Sarasotascraper.py
```
