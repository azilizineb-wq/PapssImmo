import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# ----------------------------
# CONFIGURATION DE LA PAGE
# ----------------------------
st.set_page_config(
    page_title="PapssImmo - Recommandateur de banlieues",
    page_icon="🏡",
    layout="wide"
)

st.title("🏡 PapssImmo – Trouvez votre ville idéale en Île-de-France")
st.markdown("Analysez et comparez les meilleures banlieues selon vos critères familiaux et personnels.")

# ----------------------------
# BASE DE DONNÉES SIMPLIFIÉE
# ----------------------------
data = [
    ["Asnières-sur-Seine", 6400, 9, 8, 7, 6, 8, 6, 20, 48.91, 2.28, "https://upload.wikimedia.org/wikipedia/commons/5/5b/Mairie_d%27Asni%C3%A8res-sur-Seine_02.jpg"],
    ["Boulogne-Billancourt", 8900, 10, 9, 8, 7, 9, 5, 15, 48.84, 2.24, "https://upload.wikimedia.org/wikipedia/commons/4/44/Boulogne-Billancourt_-_H%C3%B4tel_de_ville_1.jpg"],
    ["Nogent-sur-Marne", 5800, 8, 9, 8, 8, 7, 6, 30, 48.83, 2.47, "https://upload.wikimedia.org/wikipedia/commons/0/09/Mairie_de_Nogent-sur-Marne.jpg"],
    ["Noisy-le-Grand", 4000, 7, 7, 6, 7, 8, 7, 35, 48.84, 2.55, "https://upload.wikimedia.org/wikipedia/commons/7/70/Mairie_de_Noisy-le-Grand.jpg"],
    ["Clichy", 6800, 9, 7, 6, 5, 8, 5, 20, 48.90, 2.31, "https://upload.wikimedia.org/wikipedia/commons/e/e7/Mairie_de_Clichy_%28Hauts-de-Seine%29.jpg"],
    ["Saint-Germain-en-Laye", 7200, 8, 9, 9, 9, 8, 8, 40, 48.90, 2.09, "https://upload.wikimedia.org/wikipedia/commons/a/a8/Saint-Germain-en-Laye_mairie.jpg"],
    ["Levallois-Perret", 9600, 10, 9, 7, 8, 9, 5, 15, 48.90, 2.28, "https://upload.wikimedia.org/wikipedia/commons/0/00/H%C3%B4tel_de_ville_de_Levallois-Perret_03.jpg"],
    ["Suresnes", 7300, 9, 8, 8, 8, 8, 6, 25, 48.87, 2.22, "https://upload.wikimedia.org/wikipedia/commons/f/f8/Mairie_de_Suresnes_2.jpg"],
    ["Maisons-Alfort", 5600, 8, 8, 8, 8, 7, 6, 30, 48.80, 2.44, "https://upload.wikimedia.org/wikipedia/commons/f/f9/Mairie_de_Maisons-Alfort_2019.jpg"],
    ["Versailles", 8200, 7, 9, 10, 9, 7, 7, 45, 48.80, 2.13, "https://upload.wikimedia.org/wikipedia/commons/7/7e/H%C3%B4tel_de_Ville_de_Versailles.jpg"]
]

columns = [
    "Commune", "Prix_m2", "Transports", "Écoles", "Sécurité",
    "Nature", "Dynamisme", "Bruit", "Temps_Paris", "Latitude", "Longitude", "Photo_URL"
]

df = pd.DataFrame(data, columns=columns)

# ----------------------------
# ENTRÉE UTILISATEUR
# ----------------------------
col1, col2, col3 = st.columns(3)
budget = col1.number_input("💰 Budget total (€)", 200000, 1500000, 600000, step=50000)
surface = col2.number_input("📐 Surface (m²)", 40, 150, 80)
temps_max = col3.slider("⏱️ Temps max vers Paris (min)", 10, 90, 45)

age_couple = st.slider("👫 Âge moyen du couple", 25, 60, 32)
age_enfants = st.slider("👧👦 Âge moyen des enfants", 0, 18, 5)

# Pondérations
st.subheader("⚖️ Vos priorités")
poids_transports = st.slider("🚇 Transports", 0.0, 1.0, 0.25)
poids_ecoles = st.slider("🏫 Écoles", 0.0, 1.0, 0.20)
poids_securite = st.slider("🛡️ Sécurité", 0.0, 1.0, 0.15)
poids_nature = st.slider("🌳 Nature / calme", 0.0, 1.0, 0.10)
poids_prix = st.slider("💶 Prix abordable", 0.0, 1.0, 0.15)
poids_dynamisme = st.slider("🔥 Dynamisme", 0.0, 1.0, 0.10)
poids_bruit = st.slider("🔇 Sensibilité au bruit (moins = mieux)", 0.0, 1.0, 0.05)

# Ajustements selon âge
if age_enfants < 10:
    poids_ecoles += 0.10
    poids_securite += 0.05
elif 10 <= age_enfants < 16:
    poids_transports += 0.10
    poids_dynamisme += 0.05

if age_couple < 35:
    poids_dynamisme += 0.10
elif age_couple > 45:
    poids_nature += 0.10
    poids_bruit += 0.05

# Normalisation
df["Prix_norm"] = (df["Prix_m2"].max() - df["Prix_m2"]) / (df["Prix_m2"].max() - df["Prix_m2"].min()) * 10
df["Bruit_norm"] = 10 - df["Bruit"]

# Scoring
def calcul_score(row):
    score = (
        row["Transports"] * poids_transports +
        row["Écoles"] * poids_ecoles +
        row["Sécurité"] * poids_securite +
        row["Nature"] * poids_nature +
        row["Prix_norm"] * poids_prix +
        row["Dynamisme"] * poids_dynamisme +
        row["Bruit_norm"] * poids_bruit
    )
    return round(score / (poids_transports + poids_ecoles + poids_securite + poids_nature +
                          poids_prix + poids_dynamisme + poids_bruit), 2)

df["Score"] = df.apply(calcul_score, axis=1)
df["Prix_total"] = df["Prix_m2"] * surface
df_filtré = df[(df["Prix_total"] <= budget) & (df["Temps_Paris"] <= temps_max)]

# ----------------------------
# AFFICHAGE DES RÉSULTATS
# ----------------------------
st.markdown("## 🏆 Résultats : Vos meilleures options")
if len(df_filtré) == 0:
    st.warning("Aucune commune ne correspond à votre budget et critères.")
else:
    top = df_filtré.sort_values("Score", ascending=False).head(5)

    # Carte interactive
    m = folium.Map(location=[48.86, 2.35], zoom_start=10)
    for _, row in top.iterrows():
        folium.Marker(
            [row["Latitude"], row["Longitude"]],
            popup=f"{row['Commune']}<br>Score: {row['Score']}/10<br>Prix: {row['Prix_m2']} €/m²"
        ).add_to(m)
    st_folium(m, width=700, height=400)

    # Résultats détaillés
    for _, row in top.iterrows():
        st.markdown(f"### 🏙️ {row['Commune']} — {row['Score']}/10")
        st.image(row["Photo_URL"], width=500)
        st.write(f"💶 **Prix moyen** : {row['Prix_m2']} €/m²  |  🚇 **Temps vers Paris** : {row['Temps_Paris']} min")
        st.write(f"🏫 Écoles : {row['Écoles']}/10  |  🛡️ Sécurité : {row['Sécurité']}/10  |  🌳 Nature : {row['Nature']}/10")
        radar_df = pd.DataFrame({
            "Critère": ["Transports", "Écoles", "Sécurité", "Nature", "Dynamisme", "Prix_norm", "Bruit_norm"],
            "Score": [row["Transports"], row["Écoles"], row["Sécurité"], row["Nature"], row["Dynamisme"], row["Prix_norm"], row["Bruit_norm"]]
        })
        fig = px.line_polar(radar_df, r='Score', theta='Critère', line_close=True, range_r=[0,10])
        fig.update_traces(fill='toself', line_color="#FF6600")
        st.plotly_chart(fig, use_container_width=True)
        st.divider()
