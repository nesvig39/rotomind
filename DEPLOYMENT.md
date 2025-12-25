# Deployment Instructions

Follow these steps to deploy the Fantasy NBA Assistant code to your GitHub repository.

## Prerequisites

1.  **GitHub Account**: Ensure you have an active account on [GitHub](https://github.com).
2.  **Local Project**: You should be in the root directory of this project (`fantasy_nba/`).

---

## Option 1: Using Git Command Line (Recommended)

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

5.  **Link and Push to GitHub**:
    Replace the URL below with your actual repository URL.
    ```bash
    git remote add origin https://github.com/nesvig39/rotomind.git
    git branch -M main
    git push -u origin main
    ```

---

## Option 2: Manual Upload via Web Interface

If you are uncomfortable with the command line, you can upload files directly through the browser.

1.  **Prepare Your Files**:
    - Ensure your code is organized in a folder on your computer.
    - Delete any `__pycache__` folders or `.db` files if they exist locally to avoid uploading clutter.

2.  **Go to GitHub**:
    - Navigate to your repository: [https://github.com/nesvig39/rotomind](https://github.com/nesvig39/rotomind)

3.  **Upload**:
    - Click on the **Add file** button (usually near the top right of the file list).
    - Select **Upload files**.
    - Drag and drop your project folders (`src`, `tests`, etc.) and files (`requirements.txt`, `README.md`, etc.) into the drop zone.
    - **Note**: GitHub Web Upload has a limit of 100 files per upload. If you have many files, you may need to upload them in batches or use Option 1.

4.  **Commit**:
    - In the "Commit changes" box at the bottom, type a description (e.g., "Initial code upload").
    - Click **Commit changes**.

---

## Step 4: Environment Variables (Security Warning)

This project uses environment variables (e.g., `DATABASE_URL` for PostgreSQL).

*   **DO NOT** upload a `.env` file containing real passwords or API keys to GitHub.
*   If you deploy this application (e.g., to Heroku, Vercel, Railway), set these variables in the hosting provider's dashboard.
