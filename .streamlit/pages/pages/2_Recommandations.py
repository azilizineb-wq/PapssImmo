import streamlit as st
import pandas as pd

st.title("🎯 Recommandations personnalisées")

# Exemple fictif
communes = [
    {"Commune": "Versailles", "Score": 92, "Prix moyen €/m²": 6800},
    {"Commune": "Saint-Germain-en-Laye", "Score": 88, "Prix moyen €/m²": 6400},
    {"Commune": "Rueil-Malmaison", "Score": 85, "Prix moyen €/m²": 6100},
]

df = pd.DataFrame(communes)
st.dataframe(df, use_container_width=True)
st.success("Voici les communes correspondant le mieux à vos critères !")
