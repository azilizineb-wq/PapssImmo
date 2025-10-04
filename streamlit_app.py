import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from io import StringIO

# ====== CONFIG GLOBALE ======
st.set_page_config(page_title="PapssImmo", page_icon="🏡", layout="wide")

# (facultatif) cacher le menu/habillage streamlit pour faire plus "app"
HIDE_STREAMLIT_STYLE = """
    <style>
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      .block-container{padding-top:1.5rem; padding-bottom:2rem; max-width:1200px;}
      .metric {border-radius:16px; padding:14px 16px; border:1px solid #eee; background:#fff;}
      .card {border-radius:18px; padding:16px; border:1px solid #eee; background:#fff;}
      .subtle {color:#6b7280}
    </style>
"""
st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)

# ====== DONNÉES (démo) ======
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
BASE = pd.DataFrame(data, columns=cols)

# ====== FONCTIONS ======
def compute_scores(df, surface, budget, tmax, w):
    tmp = df.copy()
    tmp["Prix_total"] = tmp["Prix_m2"] * surface
    tmp = tmp[(tmp["Prix_total"] <= budget) & (tmp["Temps_Paris"] <= tmax)]
    if tmp.empty:
        return tmp

    tmp["Prix_norm"]  = (tmp["Prix_m2"].max() - tmp["Prix_m2"]) / (tmp["Prix_m2"].max() - tmp["Prix_m2"].min()) * 10
    tmp["Bruit_norm"] = 10 - tmp["Bruit"]
    denom = sum(w.values())
    def s(r):
        sc = (r["Transports"]*w["trans"] + r["Écoles"]*w["ecole"] + r["Sécurité"]*w["sec"] +
              r["Nature"]*w["nat"] + r["Dynamisme"]*w["dyn"] + r["Prix_norm"]*w["prix"] +
              r["Bruit_norm"]*w["bruit"])
        return round(sc/denom, 2)
    tmp["Score"] = tmp.apply(s, axis=1)
    return tmp.sort_values("Score", ascending=False)

def radar_fig(row: pd.Series):
    df = pd.DataFrame({
        "Critère":["Transports","Écoles","Sécurité","Nature","Dynamisme","Prix_norm","Bruit_norm"],
        "Score":[row["Transports"],row["Écoles"],row["Sécurité"],row["Nature"],row["Dynamisme"],row["Prix_norm"],row["Bruit_norm"]],
    })
    fig = px.line_polar(df, r="Score", theta="Critère", line_close=True, range_r=[0,10])
    fig.update_traces(fill="toself")
    return fig

# ====== SIDEBAR / NAV ======
with st.sidebar:
    st.image("https://em-content.zobj.net/thumbs/160/apple/354/house-with-garden_1f3e1.png", width=64)
    st.markdown("### **PapssImmo**")
    page = st.radio("Navigation", ["Accueil", "Recommandations", "Carte", "À propos"], label_visibility="collapsed")

    st.markdown("---")
    st.caption("Profil & critères")

    budget   = st.number_input("💰 Budget (€)", 200000, 1500000, 600000, step=50000)
    surface  = st.number_input("📐 Surface (m²)", 40, 150, 80)
    tmax     = st.slider("⏱️ Temps max vers Paris (min)", 10, 90, 45)
    age_cpl  = st.slider("👫 Âge du couple", 25, 60, 32)
    age_enf  = st.slider("👧👦 Âge des enfants", 0, 18, 5)

    st.markdown("##### Pondérations")
    w = {
        "trans": st.slider("🚇 Transports", 0.0, 1.0, 0.25),
        "ecole": st.slider("🏫 Écoles", 0.0, 1.0, 0.20),
        "sec":   st.slider("🛡️ Sécurité", 0.0, 1.0, 0.15),
        "nat":   st.slider("🌳 Nature", 0.0, 1.0, 0.10),
        "prix":  st.slider("💶 Prix abordable", 0.0, 1.0, 0.15),
        "dyn":   st.slider("🔥 Dynamisme", 0.0, 1.0, 0.10),
        "bruit": st.slider("🔇 Sensibilité bruit", 0.0, 1.0, 0.05),
    }
    # Ajustements selon âges
    if age_enf < 10:
        w["ecole"] += 0.10; w["sec"] += 0.05
    elif 10 <= age_enf < 16:
        w["trans"] += 0.10; w["dyn"] += 0.05
    if age_cpl < 35:
        w["dyn"] += 0.10
    elif age_cpl > 45:
        w["nat"] += 0.10; w["bruit"] += 0.05

# ====== PAGES ======
if page == "Accueil":
    st.markdown("## Bienvenue 👋")
    st.write("Réglez vos critères dans la barre de gauche puis allez dans **Recommandations** ou **Carte**.")
    c1, c2, c3 = st.columns(3)
    for col, title, txt in [
        (c1, "🎯 Reco personnalisées", "Classement des meilleures communes selon VOS priorités."),
        (c2, "🗺️ Carte interactive", "Visualisez les résultats sur la carte d’Île-de-France."),
        (c3, "📤 Export", "Téléchargez vos résultats pour les partager."),
    ]:
        with col:
            st.markdown(f'<div class="metric"><b>{title}</b><div class="subtle">{txt}</div></div>', unsafe_allow_html=True)

elif page == "Recommandations":
    res = compute_scores(BASE, surface=surface, budget=budget, tmax=tmax, w=w)
    st.markdown("## 🏆 Vos meilleures options")
    if res.empty:
        st.warning("Aucune commune ne correspond à vos critères.")
    else:
        top = res.head(5).reset_index(drop=True)

        # cartes de métriques (Top 3)
        c1, c2, c3 = st.columns(3)
        for col, row in zip([c1,c2,c3], [top.loc[0], top.loc[1] if len(top)>1 else None, top.loc[2] if len(top)>2 else None]):
            if row is not None:
                with col:
                    st.markdown(f'<div class="metric"><b>{row.Commune}</b><br/>Score <b>{row.Score}</b>/10<br/><span class="subtle">{row.Prix_m2} €/m² • {row.Temps_Paris} min</span></div>', unsafe_allow_html=True)

        st.markdown("### Détails")
        for _, r in top.iterrows():
            with st.container(border=True):
                cA, cB = st.columns([1,1])
                with cA:
                    st.image(r.Photo, use_column_width=True)
                with cB:
                    st.subheader(f"{r.Commune} — {r.Score}/10")
                    st.write(f"💶 **Prix** : {r.Prix_m2} €/m²")
                    st.write(f"⏱️ **Paris** : {r.Temps_Paris} min")
                    st.write(f"🏫 {r['Écoles']}/10 | 🛡️ {r['Sécurité']}/10 | 🌳 {r['Nature']}/10 | 🔥 {r['Dynamisme']}/10 | 🔇 {r['Bruit']}/10")

                    # radar
                    fig = radar_fig(r)
                    st.plotly_chart(fig, use_container_width=True)
        # export
        csv = top.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Télécharger le Top 5 (CSV)", data=csv, file_name="papssimmo_top5.csv", mime="text/csv")

elif page == "Carte":
    res = compute_scores(BASE, surface=surface, budget=budget, tmax=tmax, w=w)
    st.markdown("## 🗺️ Carte des recommandations")
    if res.empty:
        st.warning("Aucune commune ne correspond à vos critères.")
    else:
        m = folium.Map(location=[48.86, 2.35], zoom_start=10)
        for _, r in res.head(20).iterrows():
            folium.Marker([r.Lat, r.Lon],
                          popup=f"{r.Commune}<br>Score {r.Score}/10<br>{r.Prix_m2} €/m²").add_to(m)
        st_folium(m, width=900, height=500)

elif page == "À propos":
    st.markdown("## À propos")
    st.write("PapssImmo — prototype d’aide à la décision immobilière pour l’Île-de-France.")
    st.write("Made with ❤️ by Zineb. Données démo ; connectable à des APIs (prix, transports, écoles).")
