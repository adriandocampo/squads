# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 14:57:34 2024

@author: Administrator
"""

import streamlit as st
import pandas as pd
import json

with st.sidebar:
    st.page_link('app.py', label='Plantillas', icon='📌')
    st.page_link('pages/fichajes.py', label='Últimos movimientos', icon='✒️')

def load_data(file_path):
    try:
        data = pd.read_json(file_path, encoding='utf-8')
        df = pd.DataFrame(data)
        return df
    except json.JSONDecodeError as e:
        st.error(f"Error loading JSON: {e}")
        return pd.DataFrame()  # return an empty DataFrame in case of error
    
data_file = 'plantillas.json'
df = load_data(data_file)
signings = 'fichajes.json'
sig_df = load_data(signings)

if not df.empty:
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: white; font-size: 2.5em;'>Últimos fichajes</h1>", unsafe_allow_html=True)
        df['ficha'] = 'P'
        # Update 'ficha' based on 'sub23' condition
        for index, row in df.iterrows():
            if row['sub23']:
                df.at[index, 'ficha'] = 'Sub23'
        df['edad'] = df['edad'].apply(lambda x: x['age'] if isinstance(x, dict) and 'age' in x else None)
        df['since'] = pd.to_datetime(df['since']).dt.date
        df.sort_values('since', ascending=False, inplace=True)
        df['since'] = df['since'].apply(lambda x: x.strftime("%d-%m-%Y"))
        df = df[['nombre', 'edad', 'posicion', 'since', 'ficha']]

        data = pd.merge(df, sig_df, on='nombre', how='inner')
        data = data[['since', 'nombre', 'edad', 'ficha', 'posicion', 'equipo', 'procedencia']]
        data.columns = ['Fecha', 'Nombre', 'Edad', 'Ficha', 'Posición', 'Equipo', 'Procedencia']
        data = data.head(10)
        st.markdown(data.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        