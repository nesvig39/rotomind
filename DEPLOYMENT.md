# Deployment Instructions

Follow these steps to deploy the Fantasy NBA Assistant code to your GitHub repository.

## Prerequisites

1.  **GitHub Account**: Ensure you have an active account on [GitHub](https://github.com).
2.  **Git Installed**: Ensure `git` is installed on your local machine (`git --version`).
3.  **Local Project**: You should be in the root directory of this project (`fantasy_nba/`).

## Step 1: Create a Repository on GitHub

1.  Log in to GitHub.
2.  Click the **+** icon in the top-right corner and select **New repository**.
3.  **Name**: Enter a name (e.g., `fantasy-nba-assistant`).
4.  **Visibility**: Choose Public or Private.
5.  **Initialize**: Do **NOT** check "Add a README", ".gitignore", or "License" (we already have these locally).
6.  Click **Create repository**.
7.  Copy the URL provided (e.g., `https://github.com/your-username/fantasy-nba-assistant.git`).

## Step 2: Prepare Local Environment

Open your terminal and navigate to the project root.

1.  **Initialize Git** (if not already done):
    ```bash
    git init
    ```

2.  **Verify `.gitignore`**:
    Ensure you have a `.gitignore` file to exclude sensitive or unnecessary files. It should contain at least:
    ```text
    __pycache__/
    *.pyc
    *.db
    .pytest_cache/
    venv/
    .env
    ```

3.  **Add Files**:
    Stage all your files for the commit.
    ```bash
    git add .
    ```

4.  **Commit**:
    Create your first commit.
    ```bash
    git commit -m "Initial commit: Fantasy NBA Assistant MVP"
    ```

## Step 3: Link and Push to GitHub

1.  **Add Remote**:
    Link your local folder to the GitHub repo you created in Step 1. Replace the URL with your actual repo URL.
    ```bash
    git remote add origin https://github.com/your-username/fantasy-nba-assistant.git
    ```

2.  **Rename Branch** (Optional but recommended):
    Ensure your main branch is named `main`.
    ```bash
    git branch -M main
    ```

3.  **Push Code**:
    Upload your code to GitHub.
    ```bash
    git push -u origin main
    ```

## Step 4: Environment Variables (Security Warning)

This project uses environment variables (e.g., `DATABASE_URL` for PostgreSQL).

*   **DO NOT** commit a `.env` file containing real passwords or API keys to GitHub.
*   If you deploy this application (e.g., to Heroku, Vercel, Railway), set these variables in the hosting provider's dashboard.

## Verification

Visit your GitHub repository URL in the browser. You should see all your source code (`src/`, `tests/`, `requirements.txt`, etc.) listed there.
