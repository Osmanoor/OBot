# Deployment Plan: Containerizing with Docker

This document outlines the plan to create a portable, repeatable deployment process for the trading bot application using Docker.

## Phase 1: Create Docker Configuration

- [ ] **Create `.dockerignore` file:**
    - This file will prevent unnecessary files from being copied into the Docker image, keeping it lightweight and secure.
    - It will include entries like `.venv/`, `__pycache__/`, `.vscode/`, `trades.db`, and `.env`.

- [ ] **Create `Dockerfile`:**
    - This is the blueprint for building our application container. It will perform the following steps:
    1.  Start from an official Python base image matching your local version (`python:3.12-slim`).
    2.  Install necessary system dependencies for the headless browser (`pyppeteer`) on Debian/Linux.
    3.  Set up a non-root user for better security.
    4.  Set the working directory inside the container.
    5.  Copy and install all Python requirements from `requirements.txt`.
    6.  Run the `pyppeteer-install` command to download the Chromium browser *inside* the container image.
    7.  Copy the application source code (`app/` directory) into the container.
    8.  Define the command that will be executed when the container starts (i.e., `uvicorn app.main:app --host 0.0.0.0 --port 8000`).

## Phase 2: Document the Deployment Workflow

- [ ] **Create `DEPLOYMENT.md` file:**
    - This file will provide clear, step-by-step instructions for deploying and updating the application on any server with Docker installed.
    - **Initial Setup:**
        - How to install Docker on Windows and Linux.
        - How to prepare the server-specific `.env` file.
    - **Building the Image:**
        - The `docker build` command to create the application image from the `Dockerfile`.
    - **Running the Container:**
        - The `docker run` command, demonstrating how to:
            - Run the container in detached mode (`-d`).
            - Map the container's port 8000 to the host's port 8000 (`-p 8000:8000`).
            - Mount the server-specific `.env` file into the container (`--env-file`).
            - Persist the SQLite database by mounting a volume (`-v ./data:/app/data`), ensuring data is not lost when the container is updated.
    - **Updating the Application:**
        - A simple sequence of commands for pulling the latest code, rebuilding the image, and restarting the container with the new version.

This approach will provide you with a professional, robust, and easy-to-manage deployment workflow for both of your servers.