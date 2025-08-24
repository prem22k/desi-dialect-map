# Desi Dialect Map 🗺️📍

Welcome to the repository for the **Desi Dialect Map**! This is a collaborative project by the **ahjin Guild** team from Sreenidhi Institute of Science and Technology, designed to be a high-performance, interactive platform for documenting and celebrating the rich linguistic diversity of India.

### [➡️ View the Live Demo](https://desi-dialect-map.streamlit.app/) `(Link to be updated after deployment)`

---

## ✨ About the Project

The Desi Dialect Map is a full-stack Streamlit application that functions as a powerful "Corpus Collection Engine." It allows users to upload images of objects, scenes, or cultural items and tag them with the words used in their local dialects. This crowdsourced data is then visualized on an interactive map of India, creating a living, breathing atlas of our country's vernacular languages.

The mission is to ethically gather a rich, geotagged dataset of text and images to power the next generation of inclusive AI.

## 🚀 Key Features

- **Interactive Folium Map:** A high-performance map with custom emoji markers, interactive popups (displaying images and dialect words), and a heatmap layer to visualize submission density.
- **User-Generated Content:** A robust file uploader allows users to contribute their own images, which are stored locally and metadata in SQLite.
- **Advanced Data Exploration:** The platform features a powerful search bar and a state-based dropdown to filter submissions on both the map and the gallery.
- **Performance-Optimized:** The application is built for speed, with smart caching for all database queries and geocoding lookups to ensure a snappy user experience.
- **Dynamic UI:** The app features a "Submission of the Day" section to keep the content fresh and engaging, along with a dashboard of project statistics.
- **Data Export:** All collected data can be easily exported to a CSV file for further analysis.

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

This project was built with a modern, performance-oriented stack:

- **Frontend:** Streamlit
- **Backend:** Python, SQLite + Local File Storage
- **Mapping:** Folium, Geopy
- **Data Handling:** Pandas
- **Deployment:** Streamlit Community Cloud
- **Development:** VSCode with team-standardized configuration
- **Version Control:** GitLab with comprehensive CI/CD

## 🗂️ Local Storage Setup

This project uses **100% local storage** - no cloud services needed!

### Prerequisites

- Python 3.7+ with write permissions
- No external accounts or API keys required

### Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Test local storage: `python test_local_storage.py`
3. Run the app: `streamlit run app.py`

### Deployment

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

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
