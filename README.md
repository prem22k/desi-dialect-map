# Desi Dialect Map 🗺️📍

Welcome to the repository for the **Desi Dialect Map**! This is a collaborative project by the **ahjin Guild** team from Sreenidhi Institute of Science and Technology, designed to be a high-performance, interactive platform for documenting and celebrating the rich linguistic diversity of India.

### [➡️ View the Live Demo](https://desi-dialect-map.streamlit.app/)

---

## ✨ About the Project

The Desi Dialect Map is a full-stack Streamlit application that functions as a powerful "Corpus Collection Engine." It allows users to upload images of objects, scenes, or cultural items and tag them with the words used in their local dialects. This crowdsourced data is then visualized on an interactive map of India, creating a living, breathing atlas of our country's vernacular languages.

The mission is to ethically gather a rich, geotagged dataset of text and images to power the next generation of inclusive AI through integration with the Indic Corpus Collections API.

## 🚀 Key Features

- **Interactive Folium Map:** A high-performance map with custom emoji markers, interactive popups (displaying images and dialect words), and a heatmap layer to visualize submission density.
- **API-First Architecture:** Full integration with the Indic Corpus Collections API for centralized data storage and collaboration.
- **Advanced Data Exploration:** The platform features a powerful search bar and state-based dropdown to filter submissions on both the map and the gallery.
- **Performance-Optimized:** The application is built for speed, with smart caching for all API queries and geocoding lookups to ensure a snappy user experience.
- **Dynamic UI:** The app features a "Submission of the Day" section to keep the content fresh and engaging, along with a dashboard of project statistics.
- **Data Export:** All collected data can be easily exported to a CSV file for further analysis.
- **Category Management:** Support for predefined categories to organize submissions effectively.

## 👥 Team ahjin Guild

Our team brings together diverse expertise to create this innovative platform:

| Role                                  | Team Member     | Key Contributions                                              |
| ------------------------------------- | --------------- | -------------------------------------------------------------- |
| **Tech Lead & Full-Stack Developer**  | Prem Sai K      | Core application development, deployment, project architecture |
| **Full-Stack Developer & AI/ML Lead** | Lakshya Chitkul | Database design, data pipeline architecture, AI integration    |
| **Data Scientist & Product Lead**     | Eesha Gone      | Data analysis, UI/UX guidance, product strategy                |
| **Growth & Marketing Lead**           | Architha Reddy  | User acquisition, community building, marketing strategy       |
| **Core Developer & Problem Solver**   | Bommu Bhavani   | Database operations, testing, quality assurance                |

## 💻 Tech Stack

This project was built with a modern, API-first stack:

- **Frontend:** Streamlit
- **Backend:** Python, Indic Corpus Collections API
- **Mapping:** Folium, Geopy
- **Data Handling:** Pandas
- **Deployment:** Streamlit Community Cloud
- **Development:** VSCode with team-standardized configuration
- **Version Control:** GitLab with comprehensive CI/CD

## 🗂️ API Integration Setup

This project uses **100% API-based storage** - no local database required!

### Prerequisites

- Python 3.7+ with internet connectivity
- Access to Indic Corpus Collections API

### Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `streamlit run app.py`
3. Login with your API credentials to start contributing

### API Authentication

The application integrates with the Indic Corpus Collections API for:
- User authentication via OTP
- Record submission and retrieval
- Category management
- Data synchronization across users

## 🤝 Contributing

This is a collaborative project by the ahjin Guild team. We welcome feedback and contributions from the community. If you have an idea for a new feature or find a bug, please feel free to open an issue using our templates.

### **Development Workflow**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a merge request using our template
5. Wait for team review and approval

### **Code Standards**

- Follow our VSCode configuration for consistent formatting
- Use the provided GitLab templates for issues and merge requests
- Ensure all tests pass before submitting changes

---

Thank you for checking out our project!

**- Team ahjin Guild**  
_Sreenidhi Institute of Science and Technology_
