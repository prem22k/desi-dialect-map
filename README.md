# Desi Dialect Map
A crowdsourcing platform for collecting and visualizing geotagged Indian dialect data to support inclusive AI development.

## Problem Statement
India's linguistic landscape is incredibly diverse, with dialects often changing every few kilometers. However, most existing digital datasets and AI models focus primarily on standardized versions of major languages. This exclusion of vernacular variations results in technology that fails to serve a significant portion of the population. There is a critical need for a structured, geotagged corpus of dialect data to train more inclusive language models.

## Key Features
- **Crowdsourced Data Collection:** Interface for users to upload images and tag them with specific dialect words, language, and location.
- **Interactive Mapping:** Visualizes submissions on a map of India using Folium, featuring marker clustering and density heatmaps.
- **Automated Geocoding:** Integrates with Geopy (Nominatim) to convert user-provided location names into precise geographic coordinates.
- **User Authentication:** Secure login and signup system integrated directly with the Indic Corpus Collections API.
- **Contribution Dashboard:** Allows users to view their submission history, track verification status, and browse a gallery of their uploaded content.
- **API Integration:** Fully decoupled frontend that communicates with the Indic Corpus Collections API for all data storage and retrieval operations.

## Tech Stack
- **Frontend Framework:** Streamlit (Python)
- **Mapping Library:** Folium, Streamlit-Folium
- **Geocoding:** Geopy
- **Image Processing:** Pillow (PIL)
- **Backend Service:** Indic Corpus Collections API (RESTful)
- **Data Handling:** Pandas

## Architecture
The application operates as a stateless frontend client interacting with external services:
1.  **User Interface:** The Streamlit app captures user inputs (images, text, metadata).
2.  **Geocoding Layer:** Location strings are resolved to latitude/longitude coordinates via the Nominatim service.
3.  **API Layer:** Authenticated requests (using Bearer tokens) are sent to the Indic Corpus Collections API to store records.
4.  **Visualization:** Data is fetched from the API and rendered on the client side using Folium maps and image galleries.

## Local Development

### Prerequisites
- Python 3.8 or higher
- Git

### Installation
1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd soai2025-ahjin-guild-dialect-map
    ```

2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Run the application:
    ```bash
    streamlit run app.py
    ```

The application will be accessible at `http://localhost:8501`.

## Deployment
The application is optimized for deployment on Streamlit Cloud. Since it relies on an external API for data persistence, no persistent storage configuration is required on the hosting server.

## Limitations
-   **API Dependency:** The application is strictly dependent on the availability of the Indic Corpus Collections API. It does not currently support offline caching or local storage fallback.
-   **Geocoding Rate Limits:** The use of the free Nominatim service may result in rate limiting during high-traffic periods.
-   **Category Filtering:** Advanced filtering by category is currently limited by the API response structure.

## Contributors
-   **Prem Sai K** - Tech Lead & Full-Stack Developer
-   **Lakshya Chitkul** - Full-Stack Developer & AI/ML Lead
-   **Eesha Gone** - Data Scientist & Product Lead
-   **Architha Reddy** - Growth & Marketing Lead
-   **Bommu Bhavani** - Core Developer
