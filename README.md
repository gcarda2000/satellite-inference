# satellite-inference

This is a personal research project aimed at analyzing satellite imagery data from [Planet.com](https://www.planet.com/) to estimate changes in open-pit mines and other commodity extraction sites. By monitoring the daily or monthly changes in site activity, we aim to infer operational performance trends and potentially predict related stock price movements of the operating companies.

## Project Goals

- Process satellite data (daily or monthly) to detect physical changes in mines or commodity sites.
- Quantify changes (e.g., mine expansion, stockpile volumes, movement patterns).
- Correlate changes with financial data (e.g., stock prices, earnings reports).
- Explore predictive relationships between operational changes and stock performance.

## Key Components

- **Data Collection**: Fetch satellite imagery from Planet.com API.
- **Data Preprocessing**: Normalize and preprocess images for analysis.
- **Change Detection**: Use computer vision techniques (e.g., image differencing, segmentation) to detect physical changes.
- **Feature Extraction**: Quantify relevant features like area changes, activity levels, etc.
- **Inference & Modeling**: Link physical site changes to company stock price movements.
- **Visualization**: Generate visual reports and dashboards showing findings.

## File Structure

```plaintext
satellite-inference/
│
├── data/
│   ├── raw/                  # Raw satellite images (downloaded)
│   ├── processed/            # Preprocessed images ready for analysis
│   └── financial/            # Stock price and financial data
│
├── notebooks/
│   ├── 01_data_exploration.ipynb     # Initial EDA on satellite and financial data
│   ├── 02_change_detection.ipynb     # Detect and quantify changes
│   ├── 03_feature_engineering.ipynb  # Create features for modeling
│   ├── 04_modeling.ipynb             # Correlate features with stock data
│   └── 05_visualization.ipynb        # Generate plots and dashboards
│
├── src/
│   ├── data/
│   │   ├── fetch_planet_data.py     # Scripts to download data from Planet.com
│   │   └── preprocess_images.py     # Preprocessing functions
│   │
│   ├── analysis/
│   │   ├── change_detection.py      # Image comparison and change detection logic
│   │   └── feature_extraction.py    # Extract features from images
│   │
│   ├── models/
│   │   └── inference_model.py       # Scripts to build and train predictive models
│   │
│   └── visualization/
│       └── plot_results.py          # Plot and dashboard creation
│
├── outputs/
│   ├── figures/            # Saved plots and graphs
│   └── reports/            # PDF/HTML reports
│
├── config/
│   └── settings.yaml       # Configuration files for API keys, parameters
│
├── requirements.txt        # Python dependencies
├── README.md               # Project overview (this file)
└── .gitignore              # Ignore data and temporary files
