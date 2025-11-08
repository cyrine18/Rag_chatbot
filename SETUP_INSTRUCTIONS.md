# Setup Instructions

## Prerequisites

1. Python 3.8 or higher
2. Google Drive API credentials (for technician agent)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Google Drive API (for Technician Agent)

The technician agent requires Google Drive API access to read technician data, planning, and daily reports.

#### Steps:

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google Drive API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the credentials file

4. **Save Credentials**:
   - Rename the downloaded file to `client_secrets.json`
   - Place it in the project root directory
   - On first run, the application will create `credentials.json` automatically

5. **First Run Authentication**:
   - When you first run the application, it will open a browser window
   - Sign in with your Google account
   - Grant permissions to access Google Drive
   - The `credentials.json` file will be created automatically



### 3. Configuration

Edit `config/settings.py` if needed:
- Update API keys (currently using Groq API)
- Adjust model parameters
- Modify data paths if necessary

### 4.Run the Application

```bash
streamlit run app.py
```






