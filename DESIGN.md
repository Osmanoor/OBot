# System Design: Python Stock Option Trading Bot

This document outlines the requirements and proposed architecture for reimplementing the n8n-based trading alert system in Python, incorporating user feedback for local image generation and a web-based command interface.

## 1. System Requirements

### Functional Requirements:
- **Trade Initiation via Web UI:** The system must provide a simple web page with a form for users to input trade parameters (Symbol, Type, Strike, etc.). Submitting this form will initiate a new trade.
- **Visual Alerting (Local):** Upon initiating a trade or reaching a new price peak, the system must generate a custom PNG image *locally* without relying on external APIs.
- **Price Tracking:** The system must continuously monitor the price of all 'Active' trades.
- **Peak Price Detection:** It must identify when a trade's price reaches a new high for the day.
- **Goal Management:** The system must track a trade's progress against 5 predefined profit goals.
- **Automated Closing:** Trades must be automatically marked as 'Closed' if they expire or hit a stop-loss threshold.
- **Daily & Weekly Reporting:** The system must automatically generate and send daily and weekly summary images to a Telegram chat.

### Non-Functional Requirements:
- **High-Frequency Polling:** The price checking mechanism must run approximately every second.
- **Decoupled Tasks:** Price checking must be separate from image generation and alerting.
- **Concurrency Safety:** The design must prevent race conditions.
- **Externalized Configuration:** All secrets and parameters must be stored in a `.env` file.
- **Local Persistence:** The system must use a local SQLite database.
- **Self-Contained:** The system should have minimal external dependencies, preferring local solutions for core tasks like image generation.

## 2. Proposed Architecture & Design

### System Diagram

```mermaid
graph TD
    subgraph User Interaction
        A[User] -- Opens Web Browser --> B[Web UI];
        B -- Submits Form --> C{Web Server (Flask/FastAPI)};
    end

    subgraph Core Logic
        C -- New Trade Request --> D[Workflow: Trade Initiator];
        D -- Fetches Option Data --> E[API: Marketdata.app];
        D -- Generates Image --> F[Service: Local Image Generator];
        F -- Renders PNG via --> G[Local Headless Browser];
        D -- Stores Trade --> H[DB: SQLite];
        D -- Sends Alert --> I[Service: Telegram Alerter];
        I -- Sends Message --> J[Telegram Chat];
    end

    subgraph High-Frequency Price Tracking
        K[Task: Price Updater (Producer)] -- Every second --> E;
        K -- Fetches Active Trades --> H;
        K -- Price Update --> H;
        K -- If New Peak --> L{Message Queue};
    end

    subgraph Peak Alerting
        M[Task: Peak Alerter (Consumer)] -- Listens for New Peaks --> L;
        M -- Fetches Trade Data --> H;
        M -- Generates Image --> F;
        M -- Stores Peak Image --> H;
        M -- Sends Peak Alert --> I;
    end

    subgraph Reporting
        N[Scheduler: Daily] --> O[Workflow: Daily Reporter];
        O -- Fetches Closed Trades --> H;
        O -- Generates Report Image --> F;
        O -- Sends Report --> I;

        P[Scheduler: Weekly] --> Q[Workflow: Weekly Reporter];
        Q -- Fetches Weekly Trades --> H;
        Q -- Generates Report Image --> F;
        Q -- Sends Report --> I;
    end
```

### Design Rationale:

1.  **Web UI for Input:**
    *   A lightweight web server using **Flask** or **FastAPI** will serve a simple HTML form.
    *   This replaces the need for parsing complex text commands from Telegram, making the input process more structured and less error-prone.
    *   The web server will have an endpoint (e.g., `/trade`) that accepts POST requests from the form and triggers the `Trade Initiator` workflow.

2.  **Local SVG-to-PNG Conversion:**
    *   The external `Browserless.io` service will be replaced by a local headless browser instance controlled by Python.
    *   We will use a library like **`pyppeteer`** (a Python port of Puppeteer) to programmatically open a page, set the HTML content (with the SVG), and take a screenshot, saving it as a PNG.
    *   This approach eliminates external API costs and dependencies while maintaining high-fidelity image rendering that can handle complex CSS and SVG structures.

3.  **Decoupled Price Tracking (Producer/Consumer Pattern):**
    *   This core design remains unchanged.
    *   **The `Price Updater` (Producer):** A fast, lightweight task that runs every second to fetch prices, update the DB, and place peak notifications in a **Message Queue**.
    *   **The `Peak Alerter` (Consumer):** A separate task that processes notifications from the queue, handling the slower image generation and Telegram alerting. This ensures the price checker is never blocked.

4.  **Modular Services:** The application will be broken into distinct Python modules for each core responsibility (database, external services, image generation, workflows) to ensure the code is clean and maintainable.

This updated design is more robust, self-contained, and user-friendly. Does this revised plan align with your vision?