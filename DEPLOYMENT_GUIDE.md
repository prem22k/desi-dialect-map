# Deployment Guide

This guide explains how to deploy the **Desi Dialect Map** application. The application is built with Streamlit and connects to the **Indic Corpus Collections API** for backend services.

## 📋 Prerequisites

- **Python 3.8+** installed
- **Git** installed
- An account on **Streamlit Cloud** (for cloud deployment)
- Access to the **Indic Corpus Collections API** (handled via user login in the app)

## 🛠️ Local Deployment

To run the application locally for development or testing:

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd soai2025-ahjin-guild-dialect-map
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

5.  **Access the app:**
    Open your browser and navigate to `http://localhost:8501`.

## ☁️ Streamlit Cloud Deployment

The easiest way to deploy this application publicly is using Streamlit Cloud.

1.  **Push your code to GitHub.**
2.  **Log in to [Streamlit Cloud](https://streamlit.io/cloud).**
3.  **Click "New app".**
4.  **Select your repository, branch (main), and main file path (`app.py`).**
5.  **Click "Deploy!".**

Streamlit Cloud will automatically install the dependencies from `requirements.txt` and start the application.

## 🔧 Configuration

The application uses the following configuration files:
- `config/settings.py`: Contains application settings like supported image formats and file size limits.
- `api_*.py`: Handles API communication. The base URL is set to `https://api.corpus.swecha.org`.

No environment variables are strictly required for the basic app to run, as it relies on user authentication against the public API.

## 🔄 CI/CD

The project is set up with a basic CI/CD pipeline (if applicable, check `.gitlab-ci.yml` or `.github/workflows`) to ensure code quality.

## 🔍 Troubleshooting

-   **ModuleNotFoundError:** Ensure all dependencies in `requirements.txt` are installed.
-   **API Connection Issues:** Check your internet connection and verify that `https://api.corpus.swecha.org` is accessible.
