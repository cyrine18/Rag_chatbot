# GitHub Setup Guide

## Step 1: Configure Git (Required First Time)

Before committing, you need to set your Git identity:

```bash
git config --global user.name "cyrine ben younes"
git config --global user.email "your-email@example.com"
```

Replace `your-email@example.com` with your actual email address (the one associated with your GitHub account).

## Step 2: Create Repository on GitHub

1. Go to https://github.com/cyrine18
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Repository name: `Rag_chatbot` (or any name you prefer)
5. Description: "RAG Chatbot for Hikvision and Satel Products with Technician Agent"
6. Choose **Public** or **Private**
7. **DO NOT** initialize with README, .gitignore, or license (we already have these)
8. Click **"Create repository"**

## Step 3: Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote repository
git remote add origin https://github.com/cyrine18/Rag_chatbot.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Alternative: Using SSH (if you have SSH keys set up)

If you prefer SSH:
```bash
git remote add origin git@github.com:cyrine18/Rag_chatbot.git
git branch -M main
git push -u origin main
```

## Verification

After pushing, visit:
https://github.com/cyrine18/Rag_chatbot

You should see all your files there!

## Important Notes

✅ **Credentials are protected**: `credentials.json` and `client_secrets.json` are in `.gitignore` and will NOT be uploaded

✅ **Data files**: Your CSV files in `data/` are included. If they're large, you can add `data/*.csv` to `.gitignore` later.

✅ **All code is organized**: The project is ready for GitHub with proper structure!

