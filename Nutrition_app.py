import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title="Nutrition Paradox Dashboard")
st.title("🌍 Nutrition Paradox: Obesity vs Malnutrition")

# --- DATA LOAD ---
@st.cache_data
def load_data():
    df_obesity = pd.read_csv("cleaned_obesity.csv")
    df_malnutrition = pd.read_csv("cleaned_malnutrition.csv")
    return df_obesity, df_malnutrition

df_obesity, df_malnutrition = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.title("Filters")
region_options = sorted(df_obesity['Region'].dropna().unique())
year_min, year_max = int(df_obesity['Year'].min()), int(df_obesity['Year'].max())
selected_regions = st.sidebar.multiselect("Select Region(s):", region_options, default=region_options)
selected_years = st.sidebar.slider("Select Year Range:", year_min, year_max, (year_min, year_max))
search_country = st.sidebar.text_input("Search Country:")

def filter_data(df):
    df = df[df['Region'].isin(selected_regions)]
    df = df[df['Year'].between(*selected_years)]
    if search_country:
        df = df[df['Country'].str.contains(search_country, case=False)]
    return df

df_obesity = filter_data(df_obesity)
df_malnutrition = filter_data(df_malnutrition)

# --- MAIN TABS ---
main_tab1, main_tab2 = st.tabs(["🧮 Visual Exploration", "📊 Analytical Insights"])

# ==================== VISUAL EXPLORATION ====================
with main_tab1:
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "📊 Comparisons", "📦 Distributions", "⚖️ Nutrition Paradox"])


    with tab1:
        st.subheader("Obesity vs Malnutrition Over Time")
        obesity_trend = df_obesity.groupby('Year')['Mean_Estimate'].mean().reset_index()
        malnutrition_trend = df_malnutrition.groupby('Year')['Mean_Estimate'].mean().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=obesity_trend['Year'], y=obesity_trend['Mean_Estimate'],
                                 mode='lines+markers', name='Obesity', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=malnutrition_trend['Year'], y=malnutrition_trend['Mean_Estimate'],
                                 mode='lines+markers', name='Malnutrition', line=dict(color='blue')))
        fig.update_layout(template='plotly_white', xaxis_title='Year', yaxis_title='Mean Estimate (%)')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Top 10 Countries")
        latest_year = df_obesity['Year'].max()
        top_obesity = df_obesity[df_obesity['Year'] == latest_year].nlargest(10, 'Mean_Estimate')
        top_mal = df_malnutrition[df_malnutrition['Year'] == latest_year].nlargest(10, 'Mean_Estimate')
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(top_obesity, x='Mean_Estimate', y='Country', orientation='h',
                         color='Mean_Estimate', title='Top 10 Obesity Rates', color_continuous_scale='Reds')
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.bar(top_mal, x='Mean_Estimate', y='Country', orientation='h',
                         color='Mean_Estimate', title='Top 10 Malnutrition Rates', color_continuous_scale='Blues')
            st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.subheader("Distribution by Region")
        df_obesity['Type'] = 'Obesity'
        df_malnutrition['Type'] = 'Malnutrition'
        df_combined = pd.concat([df_obesity, df_malnutrition])
        fig3 = px.box(df_combined, x='Region', y='Mean_Estimate', color='Type', title='Distribution by Region')
        fig3.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig3, use_container_width=True)

    with tab4:
        st.subheader("Obesity vs Malnutrition Correlation")
        merged = pd.merge(
            df_obesity[['Country', 'Year', 'Mean_Estimate']],
            df_malnutrition[['Country', 'Year', 'Mean_Estimate']],
            on=['Country', 'Year'], suffixes=('_obesity', '_malnutrition')
        )
        fig4 = px.scatter(merged, x='Mean_Estimate_obesity', y='Mean_Estimate_malnutrition',
                          color='Year', hover_name='Country',
                          labels={
                              'Mean_Estimate_obesity': 'Obesity Rate (%)',
                              'Mean_Estimate_malnutrition': 'Malnutrition Rate (%)'
                          },
                          title='Obesity vs Malnutrition Scatter')
        st.plotly_chart(fig4, use_container_width=True)

# ==================== SQL ANALYSIS ====================
with main_tab2:
    tab1, tab2, tab3 = st.tabs(["Obesity", "Malnutrition", "Combined Insights"])

    def create_engine_connection():
        return create_engine("mysql+pymysql://root:ShaYug@localhost/nutrition_db")

    def run_query(query):
        try:
            engine = create_engine_connection()
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            st.error(f"Query failed: {e}")
            return pd.DataFrame()

    with tab1:
        st.header("Obesity Insights")
        obesity_queries = {
            "Top 5 regions with highest obesity in 2022": """
                SELECT Region, AVG(Mean_Estimate) AS Avg_Obesity
                FROM obesity
                WHERE Year = 2022
                GROUP BY Region
                ORDER BY Avg_Obesity DESC
                LIMIT 5;
            """,
            "Top 5 countries with highest obesity": """
                SELECT Country, MAX(Mean_Estimate) AS Max_Obesity
                FROM obesity
                GROUP BY Country
                ORDER BY Max_Obesity DESC
                LIMIT 5;
            """,
            "Obesity trend in India over the years": """
                SELECT Year, AVG(Mean_Estimate) AS Avg_Obesity
                FROM obesity
                WHERE Country = 'India'
                GROUP BY Year
                ORDER BY Year;
            """,
            "Average obesity by gender": """
                SELECT Gender, AVG(Mean_Estimate) AS Avg_Obesity
                FROM obesity
                GROUP BY Gender;
            """,
            "Country count by obesity level and age group": """
                SELECT Obesity_Level, Age_Group, COUNT(DISTINCT Country) AS Country_Count
                FROM obesity
                GROUP BY Obesity_Level, Age_Group;
            """,
            "Top 5 least and most reliable countries (CI_Width)": """
                SELECT Country, AVG(CI_Width) AS Avg_CI
                FROM obesity
                GROUP BY Country
                ORDER BY Avg_CI DESC
                LIMIT 5;
            """,
            "Average obesity by age group": """
                SELECT Age_Group, AVG(Mean_Estimate) AS Avg_Obesity
                FROM obesity
                GROUP BY Age_Group;
            """,
            "Top 10 consistent low obesity countries": """
                SELECT Country, AVG(Mean_Estimate) AS Avg_Obesity, AVG(CI_Width) AS Avg_CI
                FROM obesity
                GROUP BY Country
                HAVING Avg_Obesity < 25 AND Avg_CI < 3
                ORDER BY Avg_Obesity
                LIMIT 10;
            """,
            "Countries where female obesity exceeds male": """
                SELECT f.Country, f.Year, (f.Mean_Estimate - m.Mean_Estimate) AS Gender_Gap
                FROM obesity f
                JOIN obesity m ON f.Country = m.Country AND f.Year = m.Year
                WHERE f.Gender = 'Female' AND m.Gender = 'Male'
                HAVING Gender_Gap > 5
                ORDER BY Gender_Gap DESC;
            """,
            "Global average obesity percentage per year": """
                SELECT Year, AVG(Mean_Estimate) AS Global_Obesity
                FROM obesity
                GROUP BY Year
                ORDER BY Year;
            """
        }
        choice = st.selectbox("Select an obesity query", list(obesity_queries.keys()))
        df = run_query(obesity_queries[choice])
        st.dataframe(df)
        if not df.empty:
            st.plotly_chart(px.bar(df, x=df.columns[0], y=df.columns[1], title=choice), use_container_width=True)

    with tab2:
        st.header("Malnutrition Insights")
        malnutrition_queries = {
            "Avg. malnutrition by age group": """
                SELECT Age_Group, AVG(Mean_Estimate) AS Avg_Malnutrition
                FROM malnutrition
                GROUP BY Age_Group;
            """,
            "Top 5 countries with highest malnutrition": """
                SELECT Country, MAX(Mean_Estimate) AS Max_Malnutrition
                FROM malnutrition
                GROUP BY Country
                ORDER BY Max_Malnutrition DESC
                LIMIT 5;
            """,
            "Malnutrition trend in African region": """
                SELECT Year, AVG(Mean_Estimate) AS Avg_Malnutrition
                FROM malnutrition
                WHERE Region = 'Africa'
                GROUP BY Year
                ORDER BY Year;
            """,
            "Gender-based average malnutrition": """
                SELECT Gender, AVG(Mean_Estimate) AS Avg_Malnutrition
                FROM malnutrition
                GROUP BY Gender;
            """,
            "Malnutrition level-wise CI_Width by age group": """
                SELECT Malnutrition_Level, Age_Group, AVG(CI_Width) AS Avg_CI
                FROM malnutrition
                GROUP BY Malnutrition_Level, Age_Group;
            """,
            "Yearly malnutrition change (India, Nigeria, Brazil)": """
                SELECT Country, Year, AVG(Mean_Estimate) AS Avg_Malnutrition
                FROM malnutrition
                WHERE Country IN ('India', 'Nigeria', 'Brazil')
                GROUP BY Country, Year
                ORDER BY Country, Year;
            """,
            "Regions with lowest malnutrition averages": """
                SELECT Region, AVG(Mean_Estimate) AS Avg_Malnutrition
                FROM malnutrition
                GROUP BY Region
                ORDER BY Avg_Malnutrition ASC
                LIMIT 5;
            """,
            "Countries with increasing malnutrition": """
                SELECT Country, MAX(Mean_Estimate) - MIN(Mean_Estimate) AS Increase
                FROM malnutrition
                GROUP BY Country
                HAVING Increase > 0
                ORDER BY Increase DESC;
            """,
            "Min/Max malnutrition levels year-wise": """
                SELECT Year, MIN(Mean_Estimate) AS Min_Level, MAX(Mean_Estimate) AS Max_Level
                FROM malnutrition
                GROUP BY Year
                ORDER BY Year;
            """,
            "High CI_Width flags (CI_Width > 5)": """
                SELECT *
                FROM malnutrition
                WHERE CI_Width > 5
                ORDER BY CI_Width DESC;
            """
        }
        choice = st.selectbox("Select a malnutrition query", list(malnutrition_queries.keys()))
        df = run_query(malnutrition_queries[choice])
        st.dataframe(df)
        if not df.empty:
            st.plotly_chart(px.bar(df, x=df.columns[0], y=df.columns[1], title=choice), use_container_width=True)

    with tab3:
        st.header("Combined Insights")
        combined_queries = {
            "Obesity vs malnutrition (5 countries)": """
                SELECT o.Country, o.Year, o.Mean_Estimate AS Obesity, m.Mean_Estimate AS Malnutrition
                FROM obesity o
                JOIN malnutrition m ON o.Country = m.Country AND o.Year = m.Year
                WHERE o.Country IN ('India', 'Nigeria', 'Brazil', 'USA', 'China');
            """,
            "Gender-based disparity in both": """
                SELECT o.Gender, AVG(o.Mean_Estimate) AS Avg_Obesity, AVG(m.Mean_Estimate) AS Avg_Malnutrition
                FROM obesity o
                JOIN malnutrition m ON o.Gender = m.Gender AND o.Country = m.Country AND o.Year = m.Year
                GROUP BY o.Gender;
            """,
            "Region-wise avg estimates (Africa vs America)": """
                SELECT o.Region, AVG(o.Mean_Estimate) AS Obesity, AVG(m.Mean_Estimate) AS Malnutrition
                FROM obesity o
                JOIN malnutrition m ON o.Region = m.Region AND o.Country = m.Country AND o.Year = m.Year
                WHERE o.Region IN ('Africa', 'Americas')
                GROUP BY o.Region;
            """,
            "Countries with obesity up & malnutrition down": """
                SELECT o.Country
                FROM (
                    SELECT Country, MAX(Mean_Estimate) - MIN(Mean_Estimate) AS Obesity_Change
                    FROM obesity
                    GROUP BY Country
                ) o
                JOIN (
                    SELECT Country, MIN(Mean_Estimate) - MAX(Mean_Estimate) AS Malnutrition_Change
                    FROM malnutrition
                    GROUP BY Country
                ) m ON o.Country = m.Country
                WHERE o.Obesity_Change > 0 AND m.Malnutrition_Change > 0;
            """,
            "Age-wise trend analysis": """
                SELECT o.Year, o.Age_Group, AVG(o.Mean_Estimate) AS Avg_Obesity, AVG(m.Mean_Estimate) AS Avg_Malnutrition
                FROM obesity o
                JOIN malnutrition m ON o.Year = m.Year AND o.Age_Group = m.Age_Group AND o.Country = m.Country
                GROUP BY o.Year, o.Age_Group;
            """
        }
        choice = st.selectbox("Select a combined query", list(combined_queries.keys()))
        df = run_query(combined_queries[choice])
        st.dataframe(df)
        if not df.empty:
            st.plotly_chart(px.line(df, x=df.columns[0], y=df.columns[1:], title=choice), use_container_width=True)
