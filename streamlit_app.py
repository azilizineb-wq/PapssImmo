import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# ---------- CONFIG ----------
st.set_page_config(page_title="PapssImmo - Recommandateur de banlieues", page_icon="🏡", layout="wide")
st.title("🏡 PapssImmo – Trouvez votre ville idéale en Île-de-France")
st.markdown("Analysez et comparez les meilleures banlieues selon vos critères familiaux et personnels.")

# ---------- DONNÉES (démo) ----------
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
    ["Versailles", 8200, 7, 9, 10, 9, 7, 7, 45, 48.80, 2.13, "https://upload.wikimedia.org/wikipedia/commons/7/7e/H%C3%B4tel_de_Ville_de_Versailles.jpg"],
]
cols = ["Commune","Prix_m2","Transports","Écoles","Sécurité","Nature","Dynamisme","Bruit","Temps_Paris","Lat","Lon","Photo"]
df = pd.DataFrame(data, columns=cols)

# ---------- PROFIL & POIDS ----------
c1,c2,c3 = st.columns(3)
budget   = c1.number_input("💰 Budget total (€)", 200000, 1500000, 600000, step=50000)
surface  = c2.number_input("📐 Surface (m²)", 40, 150, 80)
tempsmax = c3.slider("⏱️ Temps max vers Paris (min)", 10, 90, 45)

age_couple  = st.slider("👫 Âge moyen du couple", 25, 60, 32)
age_enfants = st.slider("👧👦 Âge moyen des enfants", 0, 18, 5)

st.subheader("⚖️ Vos priorités")
w_trans = st.slider("🚇 Transports", 0.0, 1.0, 0.25)
w_ecole = st.slider("🏫 Écoles", 0.0, 1.0, 0.20)
w_sec   = st.slider("🛡️ Sécurité", 0.0, 1.0, 0.15)
w_nat   = st.slider("🌳 Nature / calme", 0.0, 1.0, 0.10)
w_prix  = st.slider("💶 Prix abordable", 0.0, 1.0, 0.15)
w_dyn   = st.slider("🔥 Dynamisme", 0.0, 1.0, 0.10)
w_bruit = st.slider("🔇 Sensibilité au bruit (moins = mieux)", 0.0, 1.0, 0.05)

# Ajustements selon âges
if age_enfants < 10:
    w_ecole += 0.10; w_sec += 0.05
elif 10 <= age_enfants < 16:
    w_trans += 0.10; w_dyn += 0.05
if age_couple < 35:
    w_dyn += 0.10
elif age_couple > 45:
    w_nat += 0.10; w_bruit += 0.05

# ---------- SCORING ----------
df["Prix_total"] = df["Prix_m2"] * surface
df = df[(df["Prix_total"] <= budget) & (df["Temps_Paris"] <= tempsmax)]

if df.empty:
    st.warning("Aucune commune ne correspond à vos critères.")
    st.stop()

# normalisations
df["Prix_norm"]  = (df["Prix_m2"].max() - df["Prix_m2"]) / (df["Prix_m2"].max() - df["Prix_m2"].min()) * 10
df["Bruit_norm"] = 10 - df["Bruit"]

def score_row(r):
    s = (r["Transports"]*w_trans + r["Écoles"]*w_ecole + r["Sécurité"]*w_sec +
         r["Nature"]*w_nat + r["Dynamisme"]*w_dyn + r["Prix_norm"]*w_prix +
         r["Bruit_norm"]*w_bruit)
    denom = (w_trans+w_ecole+w_sec+w_nat+w_dyn+w_prix+w_bruit)
    return round(s/denom, 2)

df["Score"] = df.apply(score_row, axis=1)
top = df.sort_values("Score", ascending=False).head(5)

# ---------- CARTE ----------
m = folium.Map(location=[48.86, 2.35], zoom_start=10)
for _, r in top.iterrows():
    folium.Marker([r["Lat"], r["Lon"]],
                  popup=f"{r['Commune']}<br>Score: {r['Score']}/10<br>Prix: {r['Prix_m2']} €/m²").add_to(m)
st_folium(m, width=720, height=420)

# ---------- FICHES ----------
for _, r in top.iterrows():
    st.markdown(f"### 🏙️ {r['Commune']} — **{r['Score']} / 10**")
    st.image(r["Photo"], width=520)
    st.write(f"💶 **Prix** : {r['Prix_m2']} €/m²  |  ⏱️ **Paris** : {r['Temps_Paris']} min")
    st.write(f"🏫 Écoles : {r['Écoles']}/10  |  🛡️ Sécurité : {r['Sécurité']}/10  |  🌳 Nature : {r['Nature']}/10  |  🔇 Bruit : {r['Bruit']}/10")
    radar = pd.DataFrame({
        "Critère":["Transports","Écoles","Sécurité","Nature","Dynamisme","Prix_norm","Bruit_norm"],
        "Score":[r["Transports"],r["Écoles"],r["Sécurité"],r["Nature"],r["Dynamisme"],r["Prix_norm"],r["Bruit_norm"]]
    })
    fig = px.line_polar(radar, r="Score", theta="Critère", line_close=True, range_r=[0,10])
    fig.update_traces(fill="toself")
    st.plotly_chart(fig, use_container_width=True)
    st.divider()
