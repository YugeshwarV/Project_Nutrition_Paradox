# Project_Nutrition_Paradox
# Nutrition Paradox: A Global View on Obesity and Malnutrition

## 📌 Project Overview
This project investigates the *Nutrition Paradox* — the simultaneous rise of obesity and persistence of malnutrition across different parts of the world. It leverages WHO datasets to explore temporal, regional, and demographic patterns using data analysis and visualization.

## 📁 Project Structure
```
📦 Nutrition Paradox
├── cleaned_obesity.csv
├── cleaned_malnutrition.csv
├── Nutrition_app.py
├── Nutrition Paradox NB.ipynb
├── Nutrition Paradox SQL.ipynb
├── Nutrition_Paradox_Summary.pdf
├── Nutrition_Paradox_Summary.pptx
└── README.md
```

## 🧩 Components

### Data Sources
- **WHO Obesity Dataset**
- **WHO Malnutrition Dataset**

### Preprocessing
- Cleaned, standardized, and merged into two main tables:
  - `obesity`: Includes Mean_Estimate, CI_Width, Gender, Age_Group, Obesity_Level
  - `malnutrition`: Includes similar fields with Malnutrition_Level

### Database
- Data stored in **MySQL** under `nutrition_db`
- Accessed using SQLAlchemy and `pymysql`

## 📊 Exploratory Data Analysis
Performed via Streamlit dashboard and Jupyter notebooks:
- Trends of obesity & malnutrition over time
- Country-wise comparisons
- Regional distributions
- Obesity vs Malnutrition correlation

## 🧮 SQL-Based Analytical Insights

### Obesity Queries
- Top countries and regions by obesity
- Trends by age, gender, and CI reliability
- Gender gaps and consistent low obesity performers

### Malnutrition Queries
- Trends by region, gender, and age group
- CI width reliability
- Countries with rising malnutrition

### Combined Insights
- Side-by-side comparison
- Age and gender-wise disparities
- Regional contrasts and reversal trends

## 🌐 Streamlit Dashboard

### Filters
- Region
- Year Range
- Country Search

### Features
- Visualizations: Line, Bar, Box, Scatter (via Plotly)
- SQL query explorer with dynamic result charts
- MySQL backend integration

### Run Locally
```bash
pip install streamlit pandas plotly sqlalchemy pymysql
streamlit run Nutrition_app.py
```

## 💡 Insights
- Obesity rising globally, including in some developing nations
- Malnutrition persists in vulnerable regions
- Both conditions coexist due to inequality, poor diets, and transitions
- CI width used to assess data reliability

---

**Author**: *Yugeshwar V*  
**Tools Used**: Streamlit, MySQL, SQLAlchemy, Plotly, Pandas, Python  
