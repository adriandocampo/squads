# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 14:57:34 2024

@author: Administrator
"""

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

with st.sidebar:
    st.page_link('app.py', label='Plantillas', icon='📌')
    st.page_link('pages/fichajes.py', label='Últimos movimientos', icon='✒️')

url = 'https://www.transfermarkt.es/segunda-federacion-grupo-i/letztetransfers/wettbewerb/E4G1'
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}
response = requests.get(url, headers=headers)
data = pd.read_html(response.content)
data = data[0]
data = data[['Edad']]

chunk_size = 5

# List to hold the smaller DataFrames
df_list = [data.iloc[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
list_of_lists = [df_chunk.values.tolist() for df_chunk in df_list]
columns = ['Edad', 'Nombre', 'Posición', 'Desde:', 'A:']

# Create the DataFrame
df = pd.DataFrame(list_of_lists, columns=columns)
def list_to_str(lst):
    return str(lst[0])

# Apply the conversion function to each column in the DataFrame
df = df.applymap(list_to_str)
df = df['Nombre', 'Edad', 'Posición', 'Desde:', 'A:']

if not df.empty:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: white; font-size: 2.5em;'>Últimos movimientos</h1>", unsafe_allow_html=True)
        data = df.head(15)
        st.markdown(data.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        
