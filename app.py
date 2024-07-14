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
from src.visualization import create_uf_plot, formatar_scr_para_plot, adaptar_tupla_porte_scr

DATADIR = CWDDIR / 'Bases_de_Dados'
SCR_INADIMPLENCIA_DIR = DATADIR / 'SCR_inadimplencia'
# SCR_INADIMPLENCIA_MODALIDADE_DIR = SCR_INADIMPLENCIA_DIR / 'modalidade'
# SCR_INADIMPLENCIA_OCUPACAO_DIR = SCR_INADIMPLENCIA_DIR / 'ocupacao'
# SCR_INADIMPLENCIA_PORTE_SCR_DIR = SCR_INADIMPLENCIA_DIR / 'porte_SCR'
RECORTE_DICT = dict()
RECORTE_DICT['modalidade'] = SCR_INADIMPLENCIA_DIR / 'modalidade'
RECORTE_DICT['ocupacao']   = SCR_INADIMPLENCIA_DIR / 'ocupacao'
RECORTE_DICT['porte_scr']  = SCR_INADIMPLENCIA_DIR / 'porte_scr'

@st.cache_data
def load_scr_data():
    """Load SCR data"""
    scr_inadimplencia = dict()
    for recorte, diretorio in RECORTE_DICT.items():
        pkl_fp = max(diretorio.glob('*'), key=os.path.getmtime)
        scr_inadimplencia[recorte] = pd.read_pickle(pkl_fp)
    return scr_inadimplencia


scr_inadimplencia = load_scr_data()
# se recorte for porte_scr, adaptar tupla para str, e depois para o texto original do SCR
recorte = 'porte_scr'
if recorte=='porte_scr':
    adaptar_tupla_porte_scr(scr_inadimplencia[recorte])

# Streamlit App
st.title("Evolução do Saldo de Carteira e Ativos Problemáticos")

# Sidebar for user inputs
st.sidebar.header("Menu de Seleções")
aggregation = st.sidebar.selectbox("Selecionar Agregação", ['trimestre', 'ano_mes'])

recorte_options = {
    'modalidade': 'modalidade',
    'ocupação': 'ocupacao',
    'porte': 'porte_scr'
}
opcao_selecionada = st.sidebar.selectbox("Selecionar Recorte"  , list(recorte_options.keys()))
recorte = recorte_options[opcao_selecionada]

# Format data based on user selection
scr_plot = formatar_scr_para_plot(df=scr_inadimplencia, 
                                  recorte=recorte, 
                                  value_cols=['carteira_ativa', 'carteira_inadimplida_arrastada'],
                                  n_top_UFs=None,
                                  periodicidade=aggregation, 
                                  trimestre_incompleto_drop=True)
uf = st.sidebar.selectbox("Selecionar UF", scr_plot['uf'].unique())


# Create Plotly figure
col_map = {
    'date': aggregation,
    'uf': 'uf',
    'recorte': recorte,
    'value': ['carteira_ativa', 'carteira_inadimplida_arrastada']
}
title = "UF Plot"  # Define your title
fig = create_uf_plot(scr_plot, uf, col_map, title, division='bilhão')

# Display Plotly figure in the main window
st.plotly_chart(fig)
