import streamlit as st
import pandas as pd
import os
from pathlib import Path
import sys

# streamlit wide by default
st.set_page_config(layout="wide")

CWDDIR = Path.cwd()
# PARDIR = CWDDIR.parent

# torna subdiretorio scr disponivel para imports
# sys.path.append(str(PARDIR))
from src.visualization import create_uf_plot, formatar_scr_para_plot#, create_uf_modalidade_plot

DATADIR = CWDDIR / 'Bases_de_Dados'
SCR_INADIMPLENCIA_DIR = DATADIR / 'SCR_inadimplencia'
SCR_INADIMPLENCIA_MODALIDADE_DIR = SCR_INADIMPLENCIA_DIR / 'modalidade'

@st.cache_data
def load_scr_data():
    """Load SCR data"""
    pkl_fp = SCR_INADIMPLENCIA_MODALIDADE_DIR / 'scr_inadimplencia_2012_2024.pkl'
    scr_inadimplencia = pd.read_pickle(pkl_fp)
    return scr_inadimplencia

# Load SCR data
# pkl_fp = SCR_INADIMPLENCIA_MODALIDADE_DIR / 'scr_inadimplencia_2012_2024.pkl'
# scr_inadimplencia = pd.read_pickle(pkl_fp)

scr_inadimplencia = load_scr_data()



# Streamlit App
st.title("Evolução do Saldo de Carteira e Ativos Problemáticos")

# Sidebar for user inputs
st.sidebar.header("Menu de Seleções")
aggregation = st.sidebar.selectbox("Selecionar Agregação", ['trimestre', 'ano_mes'])


# Format data based on user selection
scr_plot = formatar_scr_para_plot(df=scr_inadimplencia, n_top_UFs=None, 
                                  value_cols=['carteira_ativa', 'carteira_inadimplida_arrastada'],
                                  periodicidade=aggregation, trimestre_incompleto_drop=True)
uf = st.sidebar.selectbox("Selecionar UF", scr_plot['uf'].unique())


# Create Plotly figure
col_map = {
    'date': aggregation,
    'uf': 'uf',
    'modalidade': 'modalidade',
    'value': ['carteira_ativa', 'carteira_inadimplida_arrastada']
}
title = "UF Plot"  # Define your title
fig = create_uf_plot(scr_plot, uf, col_map, title, division='bilhão')

# Display Plotly figure in the main window
st.plotly_chart(fig)
