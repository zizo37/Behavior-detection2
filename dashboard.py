import streamlit as st
import json
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import base64
import tempfile
from PIL import Image
import plotly.graph_objects as go
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Streamlit Config
st.set_page_config(
    page_title="Tableau de Bord des Commentaires",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main > div {
        padding: 2rem 1rem;
    }
    .stMetric {
        background-color: #0e1117;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        background-color: #0e1117;
        border-radius: 0.5rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .css-1d391kg {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ffffff;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Load JSON data
@st.cache_data
def load_data():
    try:
        with open('output7/analysis_report.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except UnicodeDecodeError as e:
        st.error(f"Erreur d'encodage : {e}")
        return {}

data = load_data()

# Screenshot function (unchanged)
def take_screenshot():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--force-device-scale-factor=1")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(st.query_params().get("url", [""])[0])
    time.sleep(2)
    screenshot = driver.get_screenshot_as_png()
    driver.quit()
    return Image.open(BytesIO(screenshot))

# PDF export function (unchanged)
def export_to_pdf(data, figures):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Rapport d'Analyse des Commentaires", ln=True, align='C')

    # Try screenshot
    try:
        screenshot = take_screenshot()
        screenshot_path = "dashboard_screenshot.png"
        screenshot.save(screenshot_path)
        pdf.image(screenshot_path, x=10, y=30, w=190)
    except Exception as e:
        print(f"Failed to take screenshot: {e}")

    # Rest of the PDF generation code (unchanged)
    # [Previous PDF generation code remains the same]

    buffer = BytesIO()
    pdf.output(buffer, 'F')
    buffer.seek(0)
    return buffer

# Main Dashboard Layout
def main():
    # Header Section with Overview
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("📊 Tableau de Bord des Commentaires")
        st.markdown("### Une analyse approfondie des interactions et sentiments")
    with col2:
        if st.button("Exporter en PDF", type="primary"):
            pdf_buffer = export_to_pdf(data, {"Analyse des Sentiments": create_sentiment_chart(), 
                                            "Distribution des Types": create_comment_types_chart(),
                                            "Longueurs des Commentaires": create_length_chart()})
            st.download_button(
                label="📥 Télécharger le Rapport PDF",
                data=pdf_buffer,
                file_name="rapport_commentaires.pdf",
                mime="application/pdf"
            )

    # Key Metrics Row
    st.markdown("### 📈 Métriques Clés")
    col1, col2, col3, col4 = st.columns(4)
    general_stats = data['general_statistics']
    with col1:
        st.metric("Commentaires Collectés", general_stats['total_comments_collected'])
    with col2:
        st.metric("Commentaires Analysés", general_stats['total_comments_analyzed'])
    with col3:
        st.metric("Doublons Supprimés", general_stats['duplicates_removed'])
    with col4:
        st.metric("Taux de Complétion", f"{general_stats['completion_rate']}%")

    # Main Analysis Section
    tab1, tab2, tab3 = st.tabs(["📊 Analyses Principales", "💬 Commentaires", "👥 Engagement Utilisateur"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎭 Analyse des Sentiments")
            sentiment_chart = create_sentiment_chart()
            st.plotly_chart(sentiment_chart, use_container_width=True)
        
        with col2:
            st.subheader("📝 Types de Commentaires")
            types_chart = create_comment_types_chart()
            st.plotly_chart(types_chart, use_container_width=True)

        st.subheader("⏰ Distribution Temporelle")
        temporal_chart = create_temporal_chart()
        st.plotly_chart(temporal_chart, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✨ Top Commentaires Positifs")
            for comment in data['comment_type_analysis']['comment_types']['positive_comments']['top_5']:
                with st.expander(f"Score: {comment['supportive_score']} - {comment['author']}"):
                    st.write(comment['text'])
        
        with col2:
            st.subheader("⚠️ Top Commentaires Critiques")
            for comment in data['comment_type_analysis']['comment_types']['aggressive_comments']['top_5']:
                with st.expander(f"Score: {comment['critical_score']} - {comment['author']}"):
                    st.write(comment['text'])

        st.subheader("🔍 Analyse des Mots-clés")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Mots-clés Positifs**")
            keywords_positive = pd.DataFrame(data['keyword_statistics']['most_common_positive'], 
                                          columns=["Keyword", "Count"])
            st.dataframe(keywords_positive, use_container_width=True)
        with col2:
            st.write("**Mots-clés Négatifs**")
            keywords_negative = pd.DataFrame(data['keyword_statistics']['most_common_negative'], 
                                          columns=["Keyword", "Count"])
            st.dataframe(keywords_negative, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👥 Auteurs les Plus Actifs")
            authors_df = pd.DataFrame(data['user_engagement']['most_active_authors'], 
                                    columns=["Author", "Comments"])
            st.dataframe(authors_df, use_container_width=True)
        
        with col2:
            st.subheader("📊 Intensité des Sentiments")
            intensity_data = data['sentiment_intensity']['sentiment_intensity']
            intensity_df = pd.DataFrame(list(intensity_data.items()), 
                                     columns=["Intensity", "Details"])
            intensity_expanded = pd.json_normalize(intensity_df["Details"])
            intensity_expanded["Intensity"] = intensity_df["Intensity"]
            st.dataframe(intensity_expanded, use_container_width=True)

# Chart creation functions
def create_sentiment_chart():
    sentiment_data = data['sentiment_analysis']
    sentiment_df = pd.DataFrame(list(sentiment_data.items()), columns=["Sentiment", "Pourcentage"])
    fig = px.pie(
        sentiment_df, 
        values="Pourcentage", 
        names="Sentiment",
        title="Distribution des Sentiments",
        color="Sentiment",
        color_discrete_map={"positive": "#28a745", "neutral": "#6c757d", "negative": "#dc3545"}
    )
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def create_comment_types_chart():
    comment_types_data = {
        "Types": ["Positifs", "Critiques", "Neutres", "Sarcastiques"],
        "Nombre": [
            data['comment_type_analysis']['comment_types']['positive_comments']['count'],
            data['comment_type_analysis']['comment_types']['aggressive_comments']['count'],
            data['comment_type_analysis']['comment_types']['pure_neutral_comments']['count'],
            data['comment_type_analysis']['comment_types']['sarcastic_comments']['count']
        ]
    }
    comment_types_df = pd.DataFrame(comment_types_data)
    fig = px.bar(
        comment_types_df,
        x="Types",
        y="Nombre",
        color="Types",
        title="Distribution des Types de Commentaires",
        text="Nombre",
        color_discrete_sequence=["#28a745", "#dc3545", "#6c757d", "#ffc107"]
    )
    fig.update_layout(
        xaxis_title="Type de Commentaire",
        yaxis_title="Nombre de Commentaires",
        showlegend=False
    )
    return fig

def create_temporal_chart():
    hourly_data = data['temporal_analysis']['hourly_distribution']
    hourly_df = pd.DataFrame(list(hourly_data.items()), columns=["Heure", "Nombre"])
    hourly_df["Heure"] = hourly_df["Heure"].astype(int)
    hourly_df = hourly_df.sort_values(by="Heure")
    
    fig = px.line(
        hourly_df,
        x="Heure",
        y="Nombre",
        title="Distribution Horaire des Commentaires",
        markers=True,
        color_discrete_sequence=["#0d6efd"]
    )
    fig.update_layout(
        xaxis_title="Heure",
        yaxis_title="Nombre de Commentaires",
        xaxis=dict(tickmode='linear', tick0=0, dtick=2)
    )
    return fig

def create_length_chart():
    length_data = data['comment_length_analysis']['distribution']
    length_df = pd.DataFrame(list(length_data.items()), 
                           columns=["Catégorie de Longueur", "Nombre"])
    fig = px.bar(
        length_df,
        x="Catégorie de Longueur",
        y="Nombre",
        color="Catégorie de Longueur",
        title="Distribution des Longueurs des Commentaires",
        text="Nombre",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(
        xaxis_title="Catégorie de Longueur",
        yaxis_title="Nombre",
        showlegend=False
    )
    return fig

if __name__ == "__main__":
    main()