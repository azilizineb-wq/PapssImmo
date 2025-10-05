import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("🗺️ Carte interactive")

# Exemple : carte centrée sur l'Île-de-France
m = folium.Map(location=[48.8566, 2.3522], zoom_start=9)
folium.Marker([48.8, 2.35], tooltip="Paris 🏙").add_to(m)
folium.Marker([48.81, 2.13], tooltip="Versailles 🌳").add_to(m)

st_folium(m, width=700, height=500)
