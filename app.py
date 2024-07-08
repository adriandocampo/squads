# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 00:28:12 2024

@author: Administrator
"""

import streamlit as st
import pandas as pd
import json
import re
import requests
from bs4 import BeautifulSoup
import time

# Load data from JSON file
@st.cache_data(ttl=3600)
def load_data(file_path):
    try:
        data = pd.read_json(file_path, encoding='utf-8')
        df = pd.DataFrame(data)
        return df
    except json.JSONDecodeError as e:
        st.error(f"Error loading JSON: {e}")
        return pd.DataFrame()  # return an empty DataFrame in case of error

def wide_space_default():
    st.set_page_config(layout="wide")

wide_space_default()

def get_data(url, selected_team):
    altas = url.split('startseite')
    altas = f'{altas[0]}transferrekorde{altas[1]}/saison_id/2024'
    bajas = url.split('startseite')
    bajas = f'{bajas[0]}rekordabgaenge{bajas[1]}/saison_id/2024'
    
    # Send a GET request to the URL
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    header = soup.find('header', class_='data-header')
    team = header.find('h1')
    target_team = team.get_text(strip=True)
    # Find the table with the class "items"
    table = soup.find('table', class_='items')
    
    # Find all tr elements with the class "odd"
    rows = table.find_all('tr', class_='odd')
    
    # Initialize lists to store the results
    url = []
    name = []
    raw_date = []
    date = []
    value = []
    
    # Loop through each row and extract the desired data
    for row in rows:
        # Find the first td element with the class "hauptlink"
        hauptlink_td = row.find('td', class_='hauptlink')
        if hauptlink_td and hauptlink_td.find('a'):
            name.append(hauptlink_td.get_text(strip=True))
            url.append(hauptlink_td.find('a')['href'])
        
        # Find the first td element with the class "zentriert"
        zentriert_td = row.find_all('td', class_='zentriert')
        if zentriert_td:
            raw_date.append(zentriert_td[1].get_text(strip=True))
        value_td = row.find('td', class_='rechts')
        value.append(value_td.text)   
            
    rows = table.find_all('tr', class_='even')
    
    # Loop through each row and extract the desired data
    for row in rows:
        # Find the first td element with the class "hauptlink"
        hauptlink_td = row.find('td', class_='hauptlink')
        if hauptlink_td and hauptlink_td.find('a'):
            name.append(hauptlink_td.get_text(strip=True))
            url.append(hauptlink_td.find('a')['href'])
        
        # Find the first td element with the class "zentriert"
        zentriert_td = row.find_all('td', class_='zentriert')
        if zentriert_td:
            raw_date.append(zentriert_td[1].get_text(strip=True))
        value_td = row.find('td', class_='rechts')
        value.append(value_td.text)
    
    for player in raw_date:
        match = re.search(r'(\d{4}) \((\d+)\)', player)
        if match:
            year = match.group(1)
            age = match.group(2)
            date.append({'year': int(year), 'age': int(age)})
            
    since = []
    expire = []
    position = []
    
    # Iterate through each link and get the desired span element
    for href in url:
        player_url = f"https://www.transfermarkt.es{href}"
        player_response = requests.get(player_url, headers=headers)
        player_soup = BeautifulSoup(player_response.content, 'html.parser')
        div_row = player_soup.find('div', class_='row')
    
        # Busca la coincidencia usando re.search
        expire_date = re.search("Contrato hasta:\n(.*)", div_row.text).group(1)
        expire.append(expire_date)
        since_date = re.search("Fichado:</span>\n<span class=\"info-table__content info-table__content--bold\">\n(.*)</span>", str(div_row)).group(1)
        since_date = since_date.strip()
        since.append(since_date)
        
        div_row = player_soup.find('div', class_="detail-position")
        if div_row:
            player_position = div_row.find('dd').text
        else:
            player_position = '-'
        position.append(player_position)
    
    data = {
        'nombre': name,
        'edad': date,
        'equipo' : target_team,
        'since': since,
        'contract' : expire,
        'posicion' : position,
        'valor' : value
    }
    
    df = pd.DataFrame(data)
    df['since'] = pd.to_datetime(df['since'], format='%d/%m/%Y')
    df['fichaje'] = (df['since'].dt.month > 5) & (df['since'].dt.year == 2024)
    df['fichado'] = df['since'].apply(lambda x: {'month': x.month, 'year': x.year})
    df['contract'] = pd.to_datetime(df['contract'], format='%d/%m/%Y', errors='coerce')
    df['contrato'] = df['contract'].apply(lambda x: {'month': x.month, 'year': x.year})
    df = df.drop(columns=['contract'])
    df['termina'] = df['contrato'].apply(lambda x: x['year'] == 2024)
    df['sub23'] = df['edad'].apply(lambda x: x['year'] > 2001)
    
    #### BAJAS
    response = requests.get(bajas, headers=headers)
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table with the class "items"
    table = soup.find('table', class_='items')
    
    # Initialize lists for names and teams
    names = []
    teams = []
    
    # Check if the table exists
    if table:
        # Find all td elements with the class "hauptlink"
        links_tds = table.find_all('td', class_='links')
        
        for td in links_tds:
            hauptlinks_tds = td.find_all('td', class_='hauptlink')
        
            # Iterate over each td element with the class "hauptlink"
            for td in hauptlinks_tds:
                # Find the <a> tag within the td element
                a_tag = td.find('a')
                if a_tag:
                    href = a_tag.get('href', '')
                    title = a_tag.get_text(strip=True)
                    
                    # Check if "spieler" is in the href
                    if 'spieler' in href:
                        names.append(title)
                    else:
                        teams.append(title)
                else:
                    title = 'Retirado'
                    teams.append(title)
        
    else:
        print("No table found with class 'responsive-table'.")    
    
    bajas = {'nombre' : names,
             'equipo' : target_team,
             'destino' : teams}
    
    bajas = pd.DataFrame(bajas)
    
    #### ALTAS
    response = requests.get(altas, headers=headers)
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table with the class "items"
    table = soup.find('table', class_='items')
    
    # Initialize lists for names and teams
    names = []
    teams = []
    
    # Check if the table exists
    if table:
        # Find all td elements with the class "hauptlink"
        links_tds = table.find_all('td', class_='links')
        
        for td in links_tds:
            hauptlinks_tds = td.find_all('td', class_='hauptlink')
        
            # Iterate over each td element with the class "hauptlink"
            for td in hauptlinks_tds:
                # Find the <a> tag within the td element
                a_tag = td.find('a')
                if a_tag:
                    href = a_tag.get('href', '')
                    title = a_tag.get_text(strip=True)
                    
                    # Check if "spieler" is in the href
                    if 'spieler' in href:
                        names.append(title)
                    else:
                        teams.append(title)
        
    else:
        print("No table found with class 'responsive-table'.")    
    
    altas = {'nombre' : names,
             'equipo' : target_team,
             'procedencia' : teams}
    
    altas = pd.DataFrame(altas)
    return df, altas, bajas

# Streamlit app
def main():
    with st.sidebar:
        st.page_link('app.py', label='Plantillas', icon='📌')
        st.page_link('pages/fichajes.py', label='Últimos movimientos', icon='✒️')
    
    st.markdown("<h1 style='text-align: center; color: white; font-size: 2.5em;'>Plantillas 2ª RFEF. Grupo 1.</h1>", unsafe_allow_html=True)
  
        # Create columns for centering
    col1, col2, col3 = st.columns([1, 2, 1])
    
    squad_url = ['https://www.transfermarkt.es/pontevedra-cf/startseite/verein/5650',
              'https://www.transfermarkt.es/fc-coruxo/startseite/verein/13227',
              'https://www.transfermarkt.es/deportivo-de-la-coruna-b/startseite/verein/11603',
              'https://www.transfermarkt.es/sd-compostela/startseite/verein/2855',
              'https://www.transfermarkt.es/bergantinos-fc/startseite/verein/16055',
              'https://www.transfermarkt.es/real-aviles-cf/startseite/verein/20844',
              'https://www.transfermarkt.es/up-langreo/startseite/verein/16646',
              'https://www.transfermarkt.es/ud-llanera/startseite/verein/55881',
              'https://www.transfermarkt.es/marino-luanco/startseite/verein/11601',
              'https://www.transfermarkt.es/real-avila-cf/startseite/verein/6212',
              'https://www.transfermarkt.es/salamanca-cf-uds/startseite/verein/42039',
              'https://www.transfermarkt.es/cd-guijuelo/startseite/verein/11615',
              'https://www.transfermarkt.es/real-valladolid-b/startseite/verein/7078',
              'https://www.transfermarkt.es/cd-numancia/startseite/verein/2296',
              'https://www.transfermarkt.es/um-escobedo/startseite/verein/41444',
              'https://www.transfermarkt.es/cd-laredo/startseite/verein/36285',
              'https://www.transfermarkt.es/gimnastica-torrelavega/startseite/verein/12588',
              'https://www.transfermarkt.es/racing-santander-b/startseite/verein/10980'
         ]
    equipo = ['Pontevedra CF', 'Coruxo FC', 'RC Deportivo Fabril', 'SD Compostela', 'Bergantiños FC',
              'Real Avilés Industrial', 'UP Langreo', 'UD Llanera', 'Marino de Luanco', 'Real Ávila CF',
              'Salamanca CF UDS', 'CD Guijuelo', 'Real Valladolid Promesas', 'CD Numancia', 'UM Ecobedo',
              'CD Laredo', 'Gimnástica de Torrelavega', 'Rayo Cantabria']
    squads = {'equipo' : equipo,
              'url' : squad_url}
    squads = pd.DataFrame(squads)
    
    with col2:
        # Selector for teams
        teams = sorted(squads['equipo'].unique())
   
        # Streamlit selectbox
        # Load the custom CSS
        st.markdown("""
            <style>
            div[data-baseweb="select"] > div {
                background-color: #421617;
            }
        
            li[role="option"] {
                background-color: #232a39;
            }
            </style>
            """, unsafe_allow_html=True)
        
        # Streamlit selectbox
        selected_team = st.selectbox("Selecciona un equipo:", teams, index=7)     
        
        url = squads['url'][squads['equipo'] == selected_team]
        url.reset_index(drop=True, inplace=True)
        with st.spinner(f'Cargando plantilla del {selected_team}'):
            df, sig_df, dep_df = get_data(url[0], selected_team)

        #########
        # Filter data by selected team
        filtered_data = df.copy()
        filtered_data['edad'] = filtered_data['edad'].apply(lambda x: x['age'] if isinstance(x, dict) and 'age' in x else None)
        def convert_to_numeric(value):
            # Regular expression to find numeric and text parts
            match = re.match(r"(\d+(\.\d+)?)(\s*(mil|bil|tril)?\s*€)", value, re.IGNORECASE)
            
            if match:
                num = float(match.group(1))
                unit = match.group(4)
                
                # Convert based on unit
                if unit:
                    if unit.lower() == 'mil':
                        num *= 1000
                    elif unit.lower() == 'bil':
                        num *= 1000000000
                    elif unit.lower() == 'tril':
                        num *= 1000000000000
                
                # Format number with dot as thousand separator
                formatted_num = f"{int(num):,}".replace(",", ".")
                
                # Recombine the numeric value with the currency symbol
                return formatted_num
            
            return value  # Return the original value if no match       
        # Apply the function to the DataFrame
        filtered_data['valor'] = filtered_data['valor'].apply(convert_to_numeric)
        filtered_data['Value'] = filtered_data['valor'].apply(lambda x: f'{x} €')
        filtered_data['valor'] = [int(value.replace('.', '').replace('-', '0')) for value in filtered_data['valor']]
        filtered_data['ficha'] = 'P'
        # Update 'ficha' based on 'sub23' condition
        for index, row in filtered_data.iterrows():
            if row['sub23']:
                filtered_data.at[index, 'ficha'] = 'Sub23'
        # Display squad
        df = filtered_data[filtered_data['termina'] == False]
        total_value = df['valor'].sum()
        fichas_p = (df['ficha'] == 'P').sum()
        fichas_sub23 = (df['ficha'] == 'Sub23').sum()
        formatted_total_value = '{:,.0f}'.format(total_value).replace(',', '.')
        df = df[['ficha', 'nombre', 'edad', 'posicion', 'Value']]
        custom_order = ['Portero', 'Defensa central', 'Lateral derecho', 'Lateral izquierdo', 'Pivote', 
                        'Mediocentro', 'Mediocentro ofensivo', 'Mediapunta', 'Extremo derecho', 
                        'Extremo izquierdo', 'Delantero centro', '-']
        df['posicion'] = pd.Categorical(df['posicion'], categories=custom_order, ordered=True)
        df = df.sort_values('posicion')
        df.columns = ['Ficha', 'Nombre', 'Edad', 'Posición', 'Valor']
        # Display the dataframe 
        st.header("Plantilla:")
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.write(f"Valor total de la plantilla: {formatted_total_value} €")
        st.write(f"Fichas P: {fichas_p}")
        st.write(f"Fichas sub23: {fichas_sub23}")

        # Display signings
        filtered_signings = sig_df[sig_df['equipo'] == selected_team]
        st.header("Fichajes:")
        if len(filtered_signings) > 0: 
            filtered_signings = filtered_signings[['nombre', 'procedencia']]
            filtered_signings.columns = ['Nombre', 'Procedencia']
            st.markdown(filtered_signings.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        else:
            st.write("_Sin fichajes oficiales_")
            
        # Display departures
        filtered_dep = dep_df[dep_df['equipo'] == selected_team]
        st.header("Bajas:")
        if len(filtered_dep) > 0:
            filtered_dep = filtered_dep[['nombre', 'destino']]
            filtered_dep.columns = ['Nombre', 'Destino']
            st.markdown(filtered_dep.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        else:
            st.write("_Sin bajas oficiales_")
        # Display expiring
        df = filtered_data[filtered_data['termina'] == True]
        df = df[['nombre', 'edad', 'posicion', 'Value']]
        df.columns = ['Nombre', 'Edad', 'Posición', 'Valor']
        if len(df) > 0:
            st.header("Terminan contrato:")
            st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        

if __name__ == "__main__":
    main()

