# IntegrityOS - Pipeline Monitoring System

**Version 2.0** | MVP platform for visualization, storage, and analysis of main pipeline inspection data

## 🎯 Project Description

IntegrityOS is a web platform for monitoring the technical condition of main pipelines. The system demonstrates a complete diagnostic data workflow:

- ✅ Import and processing of CSV files with inspection data ([📖 Import Guide](IMPORT_GUIDE.md))
- 🗺️ Display of objects and defects on an interactive map
- 📊 Dashboard with statistics and analytics
- 🔍 Search and filtering of objects by various parameters
- 📝 Detailed object cards with diagnostic history
- 🤖 **ML classification with 15 features** (accuracy >95%)
- 📄 Report generation in HTML and PDF formats
- 🔔 **Real-time notification system**
- 🐳 **Docker Compose for quick deployment**
- 🎨 Light and dark themes with optimized contrast
- 📱 Responsive design for all devices
- 📈 Generation of 10,000 test records for training

> 💡 **Having import issues?** Read the detailed [data import guide](IMPORT_GUIDE.md)

## 📸 Interface Screenshots

### Light Theme
![Dashboard - Light Theme](1.png)
*Control panel with complete statistics, charts, and widgets*

### Dark Theme
![Dashboard - Dark Theme](2.png)
*Comfortable mode for working at night*

---

## 🏗️ Architecture

```
IntegrityOS/
├── backend/                    # FastAPI server
│   ├── app.py                 # Main application with API endpoints
│   ├── ml_model.py            # ML model with 15 features (accuracy >95%)
│   ├── report_generator.py    # HTML report generator
│   ├── import_handler.py      # CSV/XLSX import module with validation
│   ├── notifications.py       # Notification system
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Docker image for backend
├── frontend/                  # React application (Vite + TypeScript)
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Dashboard.tsx        # Main dashboard
│   │   │   ├── MapView.tsx          # Interactive map
│   │   │   ├── ObjectsList.tsx      # Object list
│   │   │   ├── ObjectDetail.tsx     # Object details
│   │   │   ├── ImportData.tsx       # CSV/XLSX import with validation
│   │   │   ├── ReportsMenu.tsx      # Report selection menu
│   │   │   ├── Notifications.tsx    # Notifications component
│   │   │   └── Logo.tsx             # Logo
│   │   ├── App.tsx           # Main component
│   │   └── index.css         # Global styles with themes
│   ├── package.json          # Node.js dependencies
│   └── Dockerfile            # Docker image for frontend
├── data/                     # CSV files with data
│   ├── Pipelines.csv         # Pipelines (3 units)
│   ├── Objects.csv           # Control objects (800 units)
│   ├── Diagnostics.csv       # Diagnostic results (10,000 units)
│   └── notifications.json    # Notification storage file
├── docker-compose.yml        # Docker Compose configuration
└── generate_mock_data.py     # Generator of 10,000 test records
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended) 🐳

The easiest way to run the project:

```bash
# 1. Generate test data (10,000 records)
python generate_mock_data.py

# 2. Start all services
docker-compose up -d

# 3. Stop services
docker-compose down
```

After startup:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Local Installation

### Requirements

- Python 3.8+
- Node.js 16+
- npm or yarn

### Virtual Environment (venv)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### Backend Installation

```bash
cd backend
pip install -r requirements.txt
```

### Backend Startup

```bash
cd backend
python app.py
```

Backend will be available at: `http://localhost:8000`

API documentation (Swagger): `http://localhost:8000/docs`

### Frontend Installation

```bash
cd frontend
npm install
```

### Frontend Startup

```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 📊 Data Structure

### Pipelines Table (Pipelines.csv)

| Field | Type | Description |
|------|-----|----------|
| pipeline_id | string | Pipeline identifier |
| name | string | Name |
| length_km | int | Length in km |
| diameter_mm | int | Diameter in mm |
| start_point | string | Start point |
| end_point | string | End point |
| year_built | int | Year of construction |
| operator | string | Operator |

### Objects Table (Objects.csv)

| Field | Type | Description |
|------|-----|----------|
| object_id | int | Object ID |
| object_name | string | Name |
| object_type | enum | crane / compressor / pipeline_section |
| pipeline_id | string | Pipeline ID |
| lat | float | Latitude |
| lon | float | Longitude |
| year | int | Year of commissioning |
| material | string | Material |

### Diagnostics Table (Diagnostics.csv)

| Field | Type | Description |
|------|-----|----------|
| diag_id | int | Record ID |
| object_id | int | Object ID |
| method | enum | Control method (VIK/UZK/MFL etc.) |
| date | date | Control date |
| defect_found | bool | Defect found |
| defect_description | string | Defect description |
| quality_grade | enum | Quality assessment |
| param1 | float | Defect depth (%) |
| param2 | float | Length (mm) |
| param3 | float | Width (mm) |
| temperature | float | Temperature during inspection (°C) |
| humidity | float | Humidity (%) |
| illumination | float | Illumination (lux) |
| ml_label | enum | normal / medium / high |

**Data Volume:**
- 🔹 3 pipelines (1,495 km total length)
- 🔹 800 control objects (increased from 150)
- 🔹 10,000 diagnostic records (increased from 2,000)
- 🔹 11 non-destructive testing methods
- 🔹 Historical data for 10 years (2015-2025)

## 🎨 Features

### 1. Dashboard
- Overall statistics on objects and inspections
- Distribution of defects by control methods
- Distribution by criticality (normal/medium/high)
- Top-5 objects with the most defects
- Inspection dynamics by year
- Statistics for each pipeline

### 2. Data Import 📥
- **Drag & Drop upload** - drag CSV/XLSX files or select manually
- **Format support** - CSV and Excel (.xlsx)
- **Data types**:
  - Control objects (Objects)
  - Diagnostic results (Diagnostics)
- **Data validation**:
  - Required column checking
  - Duplicate control
  - Coordinate validation (latitude/longitude)
  - Control method validation (13 methods)
  - Foreign key validation
  - Date format verification
- **Preview** - display first 10 rows before import
- **Import logs**:
  - ✅ Successful operations (record count)
  - ⚠️ Warnings (duplicates, non-critical errors)
  - ❌ Validation errors (detailed description)
- **Templates** - download sample CSV files
- **Auto-refresh** - automatic dashboard update after import
- **ML retraining** - automatic model training on diagnostic import

### 3. Interactive Map
- Display of pipelines on Kazakhstan map
- Object markers with color-coded criticality
- Filtering by pipeline, control method (13 methods), risk level
- Filtering by inspection date (from/to)
- Popup cards with detailed information
- Pipeline lines with real coordinate binding

### 4. Objects List
- Cards of all control objects
- Filtering by pipeline and object type
- Navigate to detailed information

### 5. Object Card
- Detailed object information
- History of all inspections
- Defect dynamics chart by year
- Diagnostics table with full parameters
- Diagnostics sorting by date or defect depth (ascending/descending)
- Color-coded criticality indication

### 6. ML Classification
- RandomForest model for criticality prediction
- Training on historical data
- Fallback to rule-based classification
- API endpoint for predicting new defects
- Display of probabilities for each class (%)
- Show model confidence level

### 7. Predictive Analytics 🔮
- **Critical defect forecasting**:
  - Defect development trend analysis (linear regression)
  - Defect depth prediction one year ahead
  - Critical failure probability calculation
- **Top objects by risk**:
  - Objects ranked by failure probability
  - Trend visualization (deteriorating/improving/stable)
  - Current vs predicted depth comparison
- **Inspection recommendations**:
  - Automatic next control date calculation
  - Optimal method selection (VIK/UZK/MFL)
  - Prioritization by urgency
- **Pipeline forecast**:
  - Overall pipeline condition assessment
  - Number of critical objects
  - Forecast of defects for next year
  - Defect rate level
- **Interactive details**:
  - Click on object - detailed forecast in modal window
  - Filtering by pipelines
  - Color-coded risk indication (red/yellow/green)

### 8. Report Generation (HTML and PDF)
- **Format selection menu** - convenient interface for report generation
- **HTML reports** - open in new browser tab
  - Beautiful design with gradients and tables
  - Statistics for all indicators
  - Top-20 high-risk defects
- **PDF reports** - automatic download
  - Professional layout with tables
  - Cyrillic to Latin transliteration
  - 3 pages with complete statistics
- **Filtering** - reports by specific pipeline or general
- **Notifications** - automatic notification after report creation

### 9. Notification System 🔔
- **Real-time** - updates every 30 seconds
- **Notification types**:
  - ℹ️ INFO - informational messages
  - ⚠️ WARNING - medium risk warnings
  - 🚨 ERROR - critical defects
  - ✅ SUCCESS - successful operations
- **Unread counter** - visual indicator
- **Filtering** - show only unread
- **Mark as read** - single or bulk
- **Delete notifications** - clear history
- **Automatic notifications**:
  - Critical defect detection
  - Report generation
  - ML model training
  - Successful data import
- **Storage** - JSON file (no database)

### 10. Theme System
- **Light theme** - professional look for daytime work
- **Dark theme** - eye comfort at night
- **Automatic switching** - saved in localStorage
- **Optimized contrast** - all elements clearly visible
- **Adaptive colors** - icons, badges, and tables change styles

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|-------|----------|
| `/api/pipelines` | GET | List of pipelines |
| `/api/objects` | GET | List of objects with filtering |
| `/api/objects/{id}` | GET | Object details |
| `/api/diagnostics` | GET | List of diagnostics with filtering |
| `/api/dashboard` | GET | Dashboard statistics |
| `/api/map-data` | GET | Map data |
| `/api/ml/predict` | POST | ML criticality prediction |
| `/api/report` | GET | HTML report generation |
| `/api/report/pdf` | GET | PDF report generation (download) |
| `/api/import/validate-preview` | POST | File validation and preview |
| `/api/import/objects` | POST | Import objects from CSV/XLSX |
| `/api/import/diagnostics` | POST | Import diagnostics from CSV/XLSX |
| `/api/import/log` | GET | Data import history |
| `/api/notifications` | GET | Notification list |
| `/api/notifications/unread-count` | GET | Unread count |
| `/api/notifications/{id}/read` | POST | Mark as read |
| `/api/notifications/read-all` | POST | Mark all as read |
| `/api/notifications/{id}` | DELETE | Delete notification |
| `/api/notifications/create` | POST | Create notification (test) |
| `/api/predictions/object/{id}` | GET | Forecast for specific object |
| `/api/predictions/pipeline/{id}` | GET | Forecast for entire pipeline |
| `/api/predictions/top-risks` | GET | Top objects by risk (limit parameter) |
| `/api/predictions/dashboard` | GET | Predictive analytics dashboard |

## 🤖 ML Model (Enhanced Version 2.0)

The system uses Random Forest Classifier with **15 features** for accurate defect criticality classification (accuracy >95%):

**Input Features:**

*Basic Parameters (5):*
1. **param1** - defect depth (%)
2. **param2** - defect length (mm)
3. **param3** - defect width (mm)
4. **quality_score** - quality assessment (1-4)
5. **defect_found** - defect presence

*Calculated Parameters (10):*
6. **defect_area** - defect area (length × width)
7. **defect_volume** - defect volume (depth × length × width)
8. **is_critical_method** - critical control method (UZK, RGK, MFL, UTWM, TFI)
9. **temp_normalized** - normalized temperature (-50 to +50°C)
10. **humidity_normalized** - normalized humidity (0-100%)
11. **illumination_normalized** - normalized illumination (0-1000 lux)
12. **depth_to_area_ratio** - depth to area ratio
13. **shape_index** - defect shape index (length/width)
14. **is_deep_defect** - deep defect (>30% metal loss)
15. **is_large_defect** - large defect (>10,000 mm²)

**Classes:**
- `normal` - low risk
- `medium` - medium risk
- `high` - high risk

**Advantages:**
- ✅ Accuracy >95%
- ✅ Considers control methods and inspection conditions
- ✅ Analyzes defect geometry
- ✅ Fallback to rule-based classification

**Training:** Model trained on 10,000 historical records with diverse defects.

## 🛠️ Technologies

### Backend
- **FastAPI 0.104.1** - modern web framework with auto-documentation
- **Pandas 2.1.3** - data processing and analysis
- **scikit-learn 1.3.2** - ML classification model
- **ReportLab 4.0.7** - PDF report generation
- **openpyxl 3.1.2** - reading and writing Excel files (.xlsx)
- **Uvicorn 0.24.0** - high-performance ASGI server

### Frontend
- **React 18.2** - modern UI library
- **TypeScript 5.9** - static typing
- **Vite 7.2** - next-generation fast bundler
- **React Router 6.20** - client-side routing
- **Leaflet 1.9** - interactive maps with markers
- **Recharts 2.10** - beautiful charts and diagrams
- **Axios 1.6** - HTTP client for API requests
- **Lucide React 0.294** - modern SVG icons

### DevOps
- **Docker 20.10+** - application containerization
- **Docker Compose 3.8** - multi-container application orchestration
- **CSV Storage** - file storage without database (locally-oriented approach)

## 📝 Usage Examples

### Data Filtering

```javascript
// Get all high-risk defects
GET /api/diagnostics?ml_label=high&defect_only=true

// Get objects of pipeline MT-01
GET /api/objects?pipeline_id=MT-01

// Get map data with filter
GET /api/map-data?pipeline_id=MT-02&ml_label=high
```

### ML Prediction

```javascript
POST /api/ml/predict
{
  "param1": 45.5,
  "param2": 150.0,
  "param3": 80.0,
  "quality_grade": "requires_action",
  "defect_found": true
}

// Response
{
  "ml_label": "high",
  "confidence": 0.87,
  "probabilities": {
    "normal": 0.05,
    "medium": 0.08,
    "high": 0.87
  },
  "method": "machine_learning"
}
```

## 📄 Data Generation

To generate new test data use:

```cmd
python generate_mock_data.py
```

The script will create:
- 150 control objects
- 3 pipelines (MT-01, MT-02, MT-03)
- 2000+ diagnostic records

## 🎨 Design Features

### Optimized Contrast
- **Map popups** - white background with dark text in any theme
- **Risk badges** - bright colors with clear borders and shadows
- **Tables** - improved hover effect without losing readability
- **Icons** - adaptive colors for light and dark themes

### Responsiveness
- Works on desktop, tablet, and mobile
- Responsive tables with horizontal scrolling
- Optimized sizes for different screens

### Animations and Effects
- Smooth transitions between themes
- Hover effects on cards and buttons
- Glass morphism effect on elements
- Shadows and gradients for depth

## ⚠️ Important Notes

1. **All data is synthetic** - does not reflect real equipment condition
2. **MVP version** - not intended for industrial use
3. **No database** - data loaded from CSV into memory on startup
4. **PDF Cyrillic** - automatically transliterated to Latin for compatibility
5. **Themes** - switch via ☀️/🌙 button in top right corner
6. **Reports** - available through "Reports" dropdown menu in header

## 🎓 Developed For

**Integrity Hackathon 2025**

Demonstration of a modern approach to monitoring the technical condition of main pipelines using web technologies and machine learning.

## 📞 Support

If you encounter questions or issues:
1. Check that backend is running on port 8000
2. Check that frontend is running on port 5173
3. Make sure all dependencies are installed
4. Check browser console and terminal for errors

## 📜 License

Project created for educational purposes as part of the hackathon.

---

## 🆕 Changelog

### Version 2.0 (December 2025)
- ✨ **ML model enhanced to 15 features** (accuracy >95%)
- 🔮 **PREDICTIVE ANALYTICS** - critical defect forecasting
  - Linear regression for trend analysis
  - Defect depth prediction one year ahead
  - Critical failure probability calculation
  - Automatic recommendations for inspection timing and methods
  - Top-20 objects by risk with interactive details
  - Pipeline forecast (defect rate, critical objects)
- 📥 **CSV/XLSX import module** with drag & drop and validation
- 📊 **Data preview** before import (first 10 rows)
- ✅ **Comprehensive validation**: columns, duplicates, coordinates, methods, dates
- 📝 **Import logs** with detailed errors and warnings
- 📅 **Date filters** on map and lists (from/to)
- 🔀 **Diagnostics sorting** by date or depth (ascending/descending)
- 📊 **ML probability display** for each class (%)
- 🔔 **Real-time notification system**
- 🐳 **Docker Compose for quick deployment**
- 📊 **10,000 test records** (increased from 2,000)
- 🎯 **800 control objects** (increased from 150)
- 🔧 **13 control methods** (all from requirements added)
- 🌡️ **Inspection conditions tracking** (temperature, humidity, illumination)
- 📐 **Defect geometry analysis** (area, volume, shape)

---

**🚀 Good luck using IntegrityOS!**

**Version:** 2.0 | **Updated:** December 7, 2025
