# Deployment Guide

This guide provides instructions for deploying and managing the trading bot application using Docker. This method is recommended for both Windows and Linux servers.

## 1. Initial Server Setup

### 1.1. Install Docker
You must install Docker on your server. Follow the official instructions for your operating system:
- **For Linux (Ubuntu/Debian):** [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- **For Windows:** [Install Docker Desktop on Windows](https://docs.docker.com/desktop/install/windows-install/)

### 1.2. Get the Application Code
Clone your repository onto the server:
```bash
git clone <your_repository_url>
cd <your_project_directory>
```

### 1.3. Prepare Configuration and Data Directory
**a. Create the `.env` file:**
Create a file named `.env` in the root of the project directory. This file will contain all your secrets and server-specific settings. Fill it with the required values.

**Crucially, for a Docker deployment, you must add the following line to this `.env` file:**
```
DATABASE_URL=sqlite:///data/trades.db
```
This tells the application inside the container to save the database to the persistent `data` volume.

**b. Create a data directory:**
The SQLite database (`trades.db`) will be stored outside the container to ensure data persists across updates. Create a directory for it.
```bash
mkdir data
```
The `Dockerfile` is configured to look for the database at `/home/appuser/trades.db`. We will mount our `data` directory to this location.

## 2. Building and Running the Application

### 2.1. Build the Docker Image
From the root of your project directory, run the following command to build the application image. This may take several minutes the first time as it downloads the base image and Chromium.
```bash
docker build -t trading-bot .
```

### 2.2. Run the Container
Run the application using the following command. This command starts the container in detached mode, maps the port, provides the environment file, and mounts the data directory.

**For Linux:**
```bash
docker run -d \
  --name trading-bot-app \
  -p 8000:8000 \
  --env-file ./.env \
  -v $(pwd)/data:/home/appuser/data \
  trading-bot:latest
```

**For Windows (using PowerShell):**
```powershell
docker run -d `
  --name trading-bot-app `
  -p 8000:8000 `
  --env-file ./.env `
  -v ${PWD}/data:/home/appuser/data `
  trading-bot:latest
```
**Note:** In `app/config.py`, I will update the `DATABASE_URL` to point to `/home/appuser/data/trades.db` to use this mounted volume.

Your application should now be running. You can view logs with `docker logs trading-bot-app`.

## 3. Updating the Application

When you have new code changes, the update process is simple and repeatable:

**Step 1: Pull the latest code**
```bash
git pull
```

**Step 2: Rebuild the Docker image**
```bash
docker build -t trading-bot .
```

**Step 3: Stop and remove the old container**
```bash
docker stop trading-bot-app
docker rm trading-bot-app
```

**Step 4: Run the new container**
Use the same `docker run` command from step 2.2 to start the updated application. Your data in the `data` directory will be preserved and used by the new container.