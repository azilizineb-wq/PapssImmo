# =========================
#  PapssImmo – version propre (multi-pages)
# =========================
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px

# ---------- CONFIG ----------
st.set_page_config(page_title="PapssImmo", page_icon="🏡", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
  #MainMenu, footer {visibility:hidden;}
  .block-container {max-width: 1180px; padding-top: 1.2rem; padding-bottom: 1.2rem;}
  .hero {
    background: linear-gradient(90deg, rgba(14,165,233,.15), rgba(16,185,129,.10));
    border: 1px solid #e5e7eb; border-radius: 18px; padding: 18px 20px; margin-bottom: 14px;
  }
  .metric {border-radius:16px; padding:14px 16px; border:1px solid #eee; background:var(--secondaryBg,#fff);}
  .subtle {color:#6b7280}
</style>
""", unsafe_allow_html=True)

# ---------- EN-TÊTE ----------
st.markdown(
  "<div class='hero'><h2 style='margin:0'>🏡 PapssImmo</h2>"
  "<div>Trouvez votre ville idéale en Île-de-France selon vos priorités.</div></div>",
  unsafe_allow_html=True
)

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
    ["Versailles", 8200, 7, 9,10, 9, 7, 7, 45, 48.80, 2.13, "https://upload.wikimedia.org/wikipedia/commons/7/7e/H%C3%B4tel_de_Ville_de_Versailles.jpg"],
]
cols = ["Commune","Prix_m2","Transports","Écoles","Sécurité","Nature","Dynamisme","Bruit","Temps_Paris","Lat","Lon","Photo"]
BASE = pd.DataFrame(data, columns=cols)

# ---------- OUTILS ----------
def _scale01(s: pd.Series) -> pd.Series:
    if s.max() == s.min():
        return pd.Series(0.5, index=s.index)
    return (s - s.min()) / (s.max() - s.min())

def compute_scores(df: pd.DataFrame, surface: int, budget: int, tmax: int, w: dict) -> pd.DataFrame:
    X = df.copy()
    X["Prix_total"] = X["Prix_m2"] * surface
    X = X[(X["Prix_total"] <= budget) & (X["Temps_Paris"] <= tmax)]
    if X.empty:
        return X
    X["Prix_norm"]  = (1 - _scale01(X["Prix_m2"])) * 10
    X["Bruit_norm"] = (10 - X["Bruit"]).clip(0, 10)
    denom = sum(w.values()) or 1.0
    X["Score"] = (
        X["Transports"]*w["trans"] + X["Écoles"]*w["ecole"] + X["Sécurité"]*w["sec"] +
        X["Nature"]*w["nat"] + X["Dynamisme"]*w["dyn"] + X["Prix_norm"]*w["prix"] +
        X["Bruit_norm"]*w["bruit"]
    ) / denom
    X["Score"] = X["Score"].round(2).clip(0, 10)
    return X.sort_values("Score", ascending=False)

def radar_fig(row: pd.Series):
    df = pd.DataFrame({
        "Critère":["Transports","Écoles","Sécurité","Nature","Dynamisme","Prix_norm","Bruit_norm"],
        "Score":[row["Transports"],row["Écoles"],row["Sécurité"],row["Nature"],row["Dynamisme"],row["Prix_norm"],row["Bruit_norm"]],
    })
    fig = px.line_polar(df, r="Score", theta="Critère", line_close=True, range_r=[0,10])
    fig.update_traces(fill="toself")
    return fig

# ---------- PAGE D’ACCUEIL ----
