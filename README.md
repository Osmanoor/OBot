# Python Stock Option Trading Bot

This project is a self-hosted, automated system for tracking and reporting on stock option trades. It provides a web interface to initiate trades, which are then monitored for price changes, goal achievements, and expiration. The system sends real-time visual alerts and generates daily/weekly reports to a Telegram channel.

This is a Python reimplementation of an original system built on the n8n automation platform.

## Features

- **Web-based Trade Initiation:** A simple web form to enter and start new option trades.
- **Local Image Generation:** Creates custom, professional-looking alert images locally using a headless browser, with no external API dependencies.
- **High-Frequency Price Tracking:** A dedicated service checks for price updates every second.
- **Peak Price & Goal Alerts:** Automatically detects new peak prices and sends Telegram alerts when predefined profit goals are met.
- **Automated Reporting:** Generates and sends daily "before and after" reports and comprehensive weekly summary reports.
- **Local Database:** Uses SQLite for all data persistence.

## Project Structure

```
/
├── app/
│   ├── services/         # Clients for external APIs and local services
│   ├── templates/        # HTML templates for the web UI
│   ├── workflows/        # Core business logic for different tasks
│   ├── config.py         # Configuration loader
│   ├── database.py       # SQLAlchemy models and DB setup
│   ├── main.py           # FastAPI application entrypoint
│   └── scheduler.py      # APScheduler job definitions
├── .env.example          # Example environment file
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

## Setup and Installation

### 1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment.
```bash
python -m venv .venv
```
Activate the environment:
- **Windows:** `.venv\Scripts\activate`
- **macOS/Linux:** `source .venv/bin/activate`

### 3. Install Dependencies
Install all the required Python packages.
```bash
pip install -r requirements.txt
```
**Note:** The first time you run the application, `pyppeteer` will download a compatible version of the Chromium browser. This is a one-time download of a few hundred megabytes.

### 4. Configure Environment Variables
Create a `.env` file by copying the example file:
```bash
# On Windows
copy .env.example .env
# On macOS/Linux
cp .env.example .env
```
Now, open the `.env` file and fill in your actual credentials:
- `MARKETDATA_API_TOKEN`: Your API token from Marketdata.app.
- `TELEGRAM_BOT_TOKEN`: The token for your Telegram bot.
- `TELEGRAM_CHAT_ID`: The ID of the channel or chat where alerts will be sent.
- `BACKGROUND_IMAGE_B64`: (Optional) A Base64-encoded string for the background image used in reports.

## How to Run

Once the setup is complete, you can run the application using `uvicorn`.

```bash
uvicorn app.main:app --reload
```

This will start the web server. You can now access the trade initiation form by navigating to `http://127.0.0.1:8000` in your web browser.

The application will also start the background tasks for price tracking, peak alerting, and the scheduled reports.