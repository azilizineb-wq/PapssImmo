import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(
    page_title="PapssImmo - Recommandateur de banlieues",
    page_icon="🏡",
    layout="wide"
)

st.title("🏡 PapssImmo – Trouvez votre ville idéale en Île-de-France")
st.markdown("Analysez et comparez les meilleures banlieues selon vos critères familiaux et personnels.")

# ----------------------------
# Données de base
# ----------------------------
data = [
    ["Asnières-sur-Seine", 6400, 9, 8, 7, 6, 8, 6, 20, 48.91, 2.28],
    ["Boulogne-Billancourt", 8900, 10, 9, 8, 7, 9, 5, 15, 48.84, 2.24],
    ["Nogent-sur-Marne", 5800, 8, 9, 8, 8, 7, 6, 30, 48.83, 2.47],
    ["Noisy-le-Grand", 4000, 7, 7, 6, 7, 8, 7, 35, 48.84, 2.55],
    ["Clichy", 6800, 9, 7, 6, 5, 8, 5, 20, 48.90, 2.31],
    ["Saint-Germain-en-Laye", 7200, 8, 9, 9, 9, 8, 8, 40, 48.90, 2.09],
    ["Levallois-Perret", 9600, 10, 9, 7, 8, 9, 5, 15, 48.90, 2.28],
    ["Suresnes", 7300, 9, 8, 8, 8, 8, 6, 25, 48.87, 2.22],
    ["Maisons-Alfort", 5600, 8, 8, 8, 8, 7, 6, 30, 48.80, 2.44],
    ["Versailles", 8200, 7, 9, 10, 9, 7, 7, 45, 48.80, 2.13]
]

columns = ["Commune", "Prix_m2", "Transports", "Écoles", "Sécurité", "Nature", "Dynamisme", "Bruit", "Temps_Paris", "Lat", "Lon"]
df = pd.DataFrame(data, columns=columns)

# ----------------------------
# Filtres utilisateur
# ----------------------------
col1, col2, col3 = st.columns(3)
budget = col1.number_input("💰 Budget total (€)", 200000, 1500000, 600000, step=50000)
surface = col2.number_input("📐 Surface (m²)", 40, 150, 80)
temps_max = col3.slider("⏱️ Temps max vers Paris (min)", 10, 90, 45)

# Calcul des critères
df["Prix_total"] = df["Prix_m2"] * surface
df["Score"] = (
    df["Transports"] * 0.2 +
    df["Écoles"] * 0.2 +
    df["Sécurité"] * 0.15 +
    df["Nature"] * 0.15 +
    df["Dynamisme"] * 0.1 +
    (10 - df["Bruit"]) * 0.1 +
    ((df["Prix_m2"].max() - df["Prix_m2"]) / (df["Prix_m2"].max() - df["Prix_m2"].min()) * 10) * 0.1
)

# Filtrage
df = df[(df["Prix_total"] <= budget) & (df["Temps_Paris"] <= temps_max)]
df = df.sort_values("Score", ascending=False)

# ----------------------------
# Affichage
# ----------------------------
if df.empty:
    st.warning("Aucune commune ne correspond à vos critères.")
else:
    st.success(f"{len(df)} communes correspondent à vos critères.")
    m = folium.Map(location=[48.86, 2.35], zoom_start=10)
    for _, row in df.head(5).iterrows():
        folium.Marker([row["Lat"], row["Lon"]], popup=f"{row['Commune']} — {row['Score']:.1f}/10").add_to(m)
    st_folium(m, width=700, height=400)
