# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 00:28:12 2024

@author: Administrator
"""

import streamlit as st
import pandas as pd
import json
import re

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

# Streamlit app
def main():
    st.markdown("<h1 style='text-align: center; color: white; font-size: 2.5em;'>Plantillas 2ª RFEF. Grupo 1.</h1>", unsafe_allow_html=True)

    # Load data
    data_file = 'plantillas.json'  # Replace with your JSON file path
    signings = 'fichajes.json'
    departures = 'salidas.json'
    df = load_data(data_file)
    sig_df = load_data(signings)
    dep_df = load_data(departures)

    if not df.empty:   
        # Create columns for centering
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Selector for teams
            teams = sorted(df['equipo'].unique())
       
            # Streamlit selectbox
            # Load the custom CSS
            with open("style.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            
            # Create a selectbox
            selected_team = st.selectbox(
                'Choose an option:',
                teams
            )
            
            st.write('You selected:', selected_team)        

            # Filter data by selected team
            filtered_data = df[df['equipo'] == selected_team]
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
        
    else:
        st.write("No data to display.")

if __name__ == "__main__":
    main()

