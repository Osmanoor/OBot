# Git Guide: Creating and Pushing to a Private Repository

This guide provides the command-line steps to turn your project into a Git repository and push it to a new private repository on a service like GitHub, GitLab, or Bitbucket.

### Step 1: Create a New Private Repository on Your Git Provider

1.  Go to your preferred Git hosting service (e.g., [GitHub](https://github.com/new)).
2.  Create a **new repository**.
3.  Give it a name (e.g., `trading-bot`).
4.  Select **"Private"**.
5.  **Do not** initialize it with a README, .gitignore, or license. We will be pushing our existing files.
6.  After creating the repository, you will be on the repository's main page. Look for the repository URL. It will be something like `https://github.com/your-username/trading-bot.git`. Copy this URL.

### Step 2: Initialize Git in Your Local Project

Open a terminal in the root directory of your project (`d:\Projects\Workflows\Option\OBot`) and run the following commands one by one.

**1. Initialize the local repository:**
This command turns your current directory into a Git repository.
```bash
git init
```

**2. Add all your files to be tracked:**
This stages all files (except those in `.gitignore`) for the first commit.
```bash
git add .
```

**3. Create the first commit:**
This saves the staged files to your local repository's history.
```bash
git commit -m "Initial commit of the trading bot application"
```

**4. (Recommended) Rename the default branch to `main`:**
The default branch name is often `master`, but `main` is the new standard.
```bash
git branch -M main
```

### Step 3: Connect and Push to the Remote Repository

**1. Add the remote repository URL:**
This command tells your local repository where the remote repository is located. **Replace the URL** with the one you copied in Step 1.
```bash
git remote add origin https://github.com/your-username/trading-bot.git
```

**2. Push your code to the remote repository:**
This command uploads your commit from your local `main` branch to the `origin` (your remote repository). The `-u` flag sets it as the default upstream branch for future pushes.
```bash
git push -u origin main
```

After this, your code will be safely stored in your private remote repository. For future updates, you will just need to use `git add`, `git commit`, and `git push`.