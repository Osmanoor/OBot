# TODO List: Web UI Enhancements

This document outlines the tasks to add authentication and a live-updating trade dashboard to the application.

## Phase 1: Implement Authentication

- [ ] **Update Configuration:**
    - Add `ADMIN_USERNAME` and `ADMIN_PASSWORD` to the `.env` file.
    - Update `app/config.py` to load these new variables.
- [ ] **Create Authentication Service:**
    - Create a new file `app/auth.py`.
    - Implement a simple dependency function using FastAPI's `HTTPBasicCredentials` that checks the provided username and password against the values in the config.
- [ ] **Secure Endpoints:**
    - In `app/main.py`, add the new authentication dependency to the main page (`/`) endpoint and the trade submission (`/trade`) endpoint.

## Phase 2: Enhance Backend for Real-time Updates

- [ ] **Create WebSocket Manager:**
    - In `app/main.py` (or a new `websocket.py` module), create a `ConnectionManager` class to handle active WebSocket connections (connect, disconnect, broadcast).
- [ ] **Create WebSocket Endpoint:**
    - Add a `/ws` WebSocket endpoint to `app/main.py`. This will handle new client connections.
- [ ] **Integrate Broadcasting with Price Updater:**
    - Modify `app/workflows/price_updater.py`.
    - When a trade's `current_price` is updated, call the `ConnectionManager`'s broadcast method to send the new price data (e.g., `{'trade_id': 123, 'new_price': 4.55}`) to all connected clients.
- [ ] **Create Manual Close Endpoint:**
    - In `app/main.py`, create a new authenticated endpoint, `POST /trade/{trade_id}/close`.
    - This endpoint will find the specified trade in the database, update its status to `CLOSED`, set the `exit_price` to the `current_price`, and record the `closed_at` timestamp.
    - It should also broadcast a "trade_closed" message via the WebSocket so the UI can remove it from the table.

## Phase 3: Overhaul Frontend for Live Dashboard

- [ ] **Update `index.html`:**
    - Restructure the page to include two main sections: the trade initiation form and a new table for displaying active trades.
    - The table should have columns like `Symbol`, `Type`, `Entry Price`, `Current Price`, `Peak Price`, and an `Actions` column.
    - Each row in the table should have a unique ID based on the trade's ID (e.g., `<tr id="trade-123">`).
- [ ] **Add WebSocket JavaScript:**
    - Add a `<script>` block to `index.html`.
    - This script will establish a connection to the `/ws` endpoint on page load.
    - It will have an `onmessage` handler to process incoming data from the server.
- [ ] **Implement Live Updates in JavaScript:**
    - When a `price_update` message is received, the JavaScript will find the correct table row by its ID and update the `Current Price` and `Peak Price` cells.
    - When a `trade_closed` message is received, the JavaScript will remove the corresponding row from the table.
    - When a `new_trade` message is received (an enhancement), the JavaScript will dynamically add a new row to the table.
- [ ] **Implement "Close Trade" Button Logic:**
    - The "Close" button in each row will trigger a JavaScript function.
    - This function will make an authenticated `fetch` request to the `POST /trade/{trade_id}/close` endpoint.