# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 00:28:12 2024

@author: Administrator
"""

import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt

# Load data from JSON file
@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_json(file_path, encoding='utf-8')
        df = pd.DataFrame(data)
        return df
    except json.JSONDecodeError as e:
        st.error(f"Error loading JSON: {e}")
        return pd.DataFrame()  # return an empty DataFrame in case of error

# Streamlit app
def main():
    st.title("Team Data Filter")

    # Load data
    data_file = 'plantillas.json'  # Replace with your JSON file path
    signings = 'fichajes.json'
    departures = 'salidas.json'
    df = load_data(data_file)
    sig_df = load_data(signings)
    dep_df = load_data(departures)

    if not df.empty:
        # Selector for teams
        teams = df['equipo'].unique()
        selected_team = st.selectbox("Select a team:", teams)

        # Filter data by selected team
        filtered_data = df[df['equipo'] == selected_team]
        filtered_data['edad'] = filtered_data['edad'].apply(lambda x: x['age'] if isinstance(x, dict) and 'age' in x else None)

        # Display squad
        st.write("Plantilla:")
        df = filtered_data[filtered_data['termina'] == False]
        df = df[['nombre', 'edad', 'posicion', 'valor']]
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)

        # Display signings
        filtered_signings = sig_df[sig_df['equipo'] == selected_team]
        st.write("Fichajes:")
        filtered_signings = filtered_signings[['nombre', 'procedencia']]
        st.markdown(filtered_signings.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        
        # Display departures
        filtered_dep = dep_df[dep_df['equipo'] == selected_team]
        st.write("Bajas:")
        filtered_dep = filtered_dep[['nombre', 'destino']]
        st.markdown(filtered_dep.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        
        # Display expiring
        df = filtered_data[filtered_data['termina'] == True]
        df = df[['nombre', 'edad', 'posicion', 'valor']]
        if len(df) > 0:
            st.write("Terminan contrato:")
            st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
    else:
        st.write("No data to display.")

if __name__ == "__main__":
    main()

