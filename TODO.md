# Implementation TODO List

This document breaks down the development of the Python Stock Option Trading Bot into actionable tasks based on the approved design.

## Phase 1: Project Setup & Configuration
- [ ] Create the project directory structure (`/app`, `/app/services`, `/app/workflows`, `/app/static`, `/app/templates`).
- [ ] Create `requirements.txt` with initial dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `python-dotenv`, `requests`, `pyppeteer`, `apscheduler`.
- [ ] Create `.env.example` file with placeholders for all required configuration variables.
- [ ] Create `app/config.py` to load and manage environment variables.

## Phase 2: Database & Core Services
- [ ] Create `app/database.py`:
    - Set up SQLAlchemy engine and session management for SQLite.
    - Define the `Trade` model using SQLAlchemy ORM, matching the required schema.
    - Include a function to initialize the database.
- [ ] Create `app/services/marketdata_service.py` to handle all API calls to Marketdata.app.
- [ ] Create `app/services/telegram_service.py` for sending messages and photos to the Telegram channel.
- [ ] Create `app/services/local_image_generator.py`:
    - Implement a function that accepts trade data.
    - It will populate the SVG/HTML template with this data.
    - It will use `pyppeteer` to launch a headless browser, load the HTML, and take a screenshot, returning the PNG image data.

## Phase 3: Web Interface & Trade Initiation
- [ ] Create `app/templates/index.html`: A simple HTML page with a form for submitting new trades.
- [ ] Create `app/main.py` (initial version):
    - Set up a FastAPI application.
    - Create a `/` endpoint to serve the `index.html` form.
- [ ] Create `app/workflows/trade_initiator.py`:
    - Define a function `initiate_trade(trade_data)`.
    - This function will contain the logic to:
        1. Call `marketdata_service` to find the option.
        2. Calculate profit goals.
        3. Call `local_image_generator` to create the entry image.
        4. Save the new trade to the database.
        5. Call `telegram_service` to send the initial alert.
- [ ] Add a `/trade` endpoint to `app/main.py` that receives the form data and calls `initiate_trade`.

## Phase 4: Price Tracking & Peak Alerting
- [ ] Create `app/workflows/price_updater.py`:
    - This will be the "Producer" task.
    - Implement a function that runs in a continuous loop.
    - Inside the loop, it will:
        1. Fetch all 'Active' trades from the database.
        2. Query `marketdata_service` for the latest price of each.
        3. Update `current_price` in the database.
        4. If a new peak is found, update `peak_price_today` and put the trade's ID into a shared queue.
- [ ] Create `app/workflows/peak_alerter.py`:
    - This will be the "Consumer" task.
    - Implement a function that listens to the shared queue.
    - When a trade ID is received, it will:
        1. Fetch the trade's full details from the database.
        2. Check if a new profit goal was met.
        3. Call `local_image_generator` for the peak image.
        4. Save the peak image to the database.
        5. Send the peak alert via `telegram_service`.

## Phase 5: Reporting Workflows
- [ ] Create `app/workflows/daily_reporter.py`:
    - Implement a function `run_daily_report()`.
    - This function will fetch trades closed today, generate the composite images, and send them.
- [ ] Create `app/workflows/weekly_reporter.py`:
    - Implement a function `run_weekly_report()`.
    - This function will fetch trades from the last 7 days, generate the summary image, and send it.

## Phase 6: System Orchestration & Finalization
- [ ] Create `app/scheduler.py`:
    - Configure `apscheduler` to run `run_daily_report` and `run_weekly_report` at the correct times.
- [ ] Update `app/main.py`:
    - Integrate and start the `price_updater` and `peak_alerter` tasks (e.g., using `asyncio` or `threading`).
    - Start the scheduler.
    - Start the FastAPI web server.
- [ ] Write a comprehensive `README.md` with setup and usage instructions.