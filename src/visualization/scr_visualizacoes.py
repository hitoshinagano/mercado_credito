import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st

# documentação API plotly
# https://plotly.com/python-api-reference/

def create_uf_modalidade_plot(df, col_map, title, division=None, plot_total=False):
    
    df_copy = df.copy()
    
    # se plot_total=True, adiciona um ultimo plot
    if plot_total:
        add_one = 1
    else:
        add_one = 0
        
    # Map the columns
    date_col = col_map['date']
    uf_col = col_map['uf']
    modalidade_col = col_map['modalidade']
    value_col = col_map['value']

    if division == None:
        divisor = 1
    elif division == 'milhão':
        divisor = 1e6
    elif division == 'bilhão':
        divisor = 1e9
    elif division == 'trilhão':
        divisor = 1e12
    else:
        print('Divisor não reconhecido. Utilizando 1')
        divisor = 1
    df_copy[value_col] = df_copy[value_col] / divisor
    
    # Get unique modalidades
    unique_modalidades = df_copy[modalidade_col].unique()
    # Define a list of colors
    color_list = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#FF97FF', '#FECB52']
    # Build the colors dictionary
    colors = {modalidade: color_list[i % len(color_list)] for i, modalidade in enumerate(unique_modalidades)}
    
    # Create a list of unique 'uf's
    # unique_ufs = df_copy[uf_col].unique()
    uf_order = df_copy.groupby(uf_col)[value_col].sum().sort_values(ascending=False).index
    uf_order = [uf for uf in uf_order if uf!='demais UFs']
    uf_order.append('demais UFs')

    # Create a subplot with a row for each 'uf'
    fig = make_subplots(rows=len(uf_order) + add_one, 
                        cols=1, 
                        shared_xaxes=True, 
                        subplot_titles=list(uf_order),
                        vertical_spacing=0.01)

    # Add traces for each 'uf'
    for i, uf in enumerate(uf_order):
        df_uf = df_copy[df_copy[uf_col] == uf]
        for modalidade in unique_modalidades:
            df_modalidade = df_uf[df_uf[modalidade_col] == modalidade]
            fig.add_trace(
                go.Bar(
                    x=df_modalidade[date_col],
                    y=df_modalidade[value_col],
                    name=modalidade,
                    marker_color=colors[modalidade],
                    showlegend=(i == 0),  # Show legend only once
                    legendgroup=modalidade,  # Group by modalidade
                    # offsetgroup=modalidade
                ),
                row=i + 1, col=1
            )
    
    if plot_total:
        # Add aggregated data for top UFs and other states
        agg_df = df_copy.groupby([date_col, uf_col]).sum().reset_index()
        for uf in uf_order:
            df_uf = agg_df[agg_df[uf_col] == uf]
            fig.add_trace(
                go.Bar(
                    x=df_uf[date_col],
                    y=df_uf[value_col],
                    name=uf,
                    # marker_color=colors[modalidade],
                    showlegend=True,  
                    legendgroup='grupo UF',  
                    # offsetgroup='grupo UF'
                ),
                row=len(uf_order) + 1, col=1
            )

    # Rotate x labels and tighten layout
    for i in range(len(uf_order) + add_one):
        fig['layout'][f'xaxis{i + 1}']['tickangle'] = -45
    
    # fig.update_annotations(x=0.02, selector={'text': 'SP'})
    for i in range(len(uf_order) + add_one):
        fig.add_hline(y=0, line=dict(width=0.5), row=i + 1, col=1)
        
    for a in fig.layout.annotations:
        a['y'] = a['y'] - 0.04
        a['x'] = 0.05
        a['font'] = {'size': 24}
        a['xanchor'] = 'left'
        
    fig.update_layout(plot_bgcolor = "white")

    # Update layout to have a single legend
    fig.update_layout(
        height=800 + 150 * (len(uf_order) + add_one),  # Adjust height based on number of subplots
        # title_text='Carteira Ativa por UF e Modalidade',
        barmode='stack',
        margin=dict(l=80, r=20, t=150, b=20),
        showlegend=True,
        legend=dict(
            title='Modalidade',
            x=1.05,
            y=1,
            traceorder='normal',
        ),
        legend_tracegroupgap = 180,
    )
    fig.update_layout(
        # title_text="Carteira Ativa por Modalidade",
        title=dict(text=title, 
                   font=dict(size=36), 
                   yref='paper',
                   pad = dict(t = -200), 
                   xanchor='center', 
                   yanchor='top'),
        title_x=0.5,  # Center the title text
        title_y=0.975,  # Add space to the first subplot
    )
    fig.update_layout(margin=dict(t=200))

    # Set the x-axis title only at the bottom
    # fig.update_xaxes(title_text='Date', row=len(uf_order) + 1, col=1)

    return fig

def insert_newline(modalidade):
    words = modalidade.split()
    if len(words) > 3:
        # print(' '.join(words[:3]) + '\n' + ' '.join(words[3:]))
        return ' '.join(words[:3]) + '\n' + ' '.join(words[3:])
    else:
        return modalidade

def create_uf_plot(df, uf, col_map, title, division=None):
    
    df_copy = df.copy()
        
    # Map the columns
    date_col = col_map['date']
    uf_col = col_map['uf']
    modalidade_col = col_map['modalidade']
    value_cols = col_map['value']

    if division == None:
        divisor = 1
    elif division == 'milhão':
        divisor = 1e6
    elif division == 'bilhão':
        divisor = 1e9
    elif division == 'trilhão':
        divisor = 1e12
    else:
        print('Divisor não reconhecido. Utilizando 1')
        divisor = 1
    for value_col in value_cols:
        df_copy[value_col] = df_copy[value_col] / divisor
        
    # Update the modalidade labels
    df_copy[modalidade_col] = df_copy[modalidade_col].apply(insert_newline)
    
    # Get unique modalidades
    unique_modalidades = df_copy[modalidade_col].unique()
    # Define a list of colors
    color_list = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#FF97FF', '#FECB52']
    # Build the colors dictionary
    colors = {modalidade: color_list[i % len(color_list)] for i, modalidade in enumerate(unique_modalidades)}

    # Create a subplot with a row for each 'uf'
    fig = make_subplots(rows=3, 
                        cols=1, 
                        shared_xaxes=True, 
                        subplot_titles=['', 'Carteira Ativa', 'Carteira Inadimplida Arrastada'],
                        vertical_spacing=0.05,
                        row_heights=[0.5, 0.25, 0.25])

    df_uf = df_copy[df_copy[uf_col] == uf]
    
    # Add traces for each 'uf'
    for modalidade in unique_modalidades:
        df_modalidade = df_uf[df_uf[modalidade_col] == modalidade]
        fig.add_trace(
            go.Scatter(
                x=df_modalidade[date_col],
                y=df_modalidade['inadimplencia'],
                mode='lines+markers',
                name=modalidade,
                marker_color=colors[modalidade],
                showlegend=False,
                legendgroup=modalidade,  # Group by modalidade
            ), 
            row=1, col=1
        )
        for i, value_col in enumerate(value_cols):
        # for modalidade in unique_modalidades:
            fig.add_trace(
                go.Bar(
                    x=df_modalidade[date_col],
                    y=df_modalidade[value_col],
                    name=insert_newline(modalidade),
                    marker_color=colors[modalidade],
                    showlegend=(i == 0),  # Show legend only once
                    legendgroup=modalidade,  # Group by modalidade
                    # offsetgroup=modalidade
                ),
                row=i+2, col=1
            )
            
    # Update layout for stacked bars
    fig.update_layout(
        barmode='stack',
        height=800,  # Adjust the height of the figure
        yaxis_title='Inadimplência (%)',
        yaxis2_title=f'Valor ({division} R$)',
        yaxis3_title=f'Valor ({division} R$)',
        title='Inadimplencia e Carteiras por Modalidade',
        legend_title_text='Modalidade',
        legend=dict(
            font=dict(size=10),
            itemwidth=30,
            yanchor='top',
            xanchor='left',
            x=1.02,
            y=1,
            bgcolor='rgba(255,255,255,0)',
            # bordercolor='rgba(0,0,0,0.2)',
            # borderwidth=1
            tracegroupgap=0  # Adjust the item spacing
        )
        
    )
    
    for a in fig.layout.annotations:
        # a['y'] = a['y'] - 0.05
        a['x'] = 0.02
        a['font'] = {'size': 12}
        a['xanchor'] = 'left'
    
    # Ensure x-axis titles are below the respective subplots
    fig.update_xaxes(title_text=date_col, row=3, col=1)
    fig.update_xaxes(tickangle=-45, row=3, col=1)
    
    # Align y-axis titles
    fig.update_layout(yaxis_title_standoff=25)
    fig.update_layout(yaxis2_title_standoff=25)
    fig.update_layout(yaxis3_title_standoff=25)
    
    # Share y-axis title between subplots in rows 2 and 3
    # fig.update_yaxes(title_text="Shared Y-axis Title", row=2, col=1)
    # fig.update_yaxes(title_text="", row=3, col=1)
    
    return fig


def get_top_ufs(df, value_col, n_top_UFs, drop_BR):
    """Retorna as UFs com os maiores valores totais de uma coluna do SCR: 'carteira ativa'
    """
    value_total_per_uf = df.T.groupby(level='uf').sum().sum(axis=1).sort_values(ascending=False)
    if 'BR' in value_total_per_uf:
        value_total_per_uf = value_total_per_uf.drop('BR')
    top_ufs = value_total_per_uf.iloc[:n_top_UFs].index
    if not drop_BR:
        top_ufs = list(top_ufs) + ['BR']
    
    return top_ufs

@st.cache_data
def formatar_scr_para_plot(df, value_cols, **kwargs):
    """Formata o dataframe do SCR para plotar no gráfico de barras.
    
    Args:
    * df: dataframe com os dados do SCR
    * value_cols: coluna(s) com os valores a serem plotados
    * kwargs: argumentos adicionais para a função formatar_scr_para_plot
    
    Returns:
    * df_combined: dataframe com os dados formatados para plotar no gráfico de barras
    """
    if isinstance(value_cols, str):
        value_cols = [value_cols]
        
    top_ufs = get_top_ufs(df, 'carteira ativa', kwargs.get('n_top_UFs', 5), kwargs.get('drop_BR', False))
    kwargs.pop('n_top_UFs', None)
    kwargs.pop('criar_inadimplencia', None)
    
    df_combined = list()
    for value_col in value_cols:
        df_value = _formatar_scr_para_plot_single(df, value_col, top_ufs, **kwargs)
        df_combined.append(df_value)
        
    df_combined = pd.concat(df_combined, axis=1)
    df_combined = df_combined.reset_index()
    
    # print(value_cols)
    if ('carteira_ativa' in value_cols) and ('carteira_inadimplida_arrastada' in value_col):
        df_combined['inadimplencia'] = 100 * df_combined['carteira_inadimplida_arrastada']/ df_combined['carteira_ativa']
    
    return df_combined
    
def _formatar_scr_para_plot_single(df, value_col, 
                                   top_ufs, 
                                   periodicidade='trimestre', trimestre_incompleto_drop = False, 
                                   drop_BR=False, renomear_modalidades_para_siglas=False):
    """retorna um dataframe com os valores de uma coluna do SCR formatados para plotar no gráfico de barras.
    """
    value = df[value_col]

    if renomear_modalidades_para_siglas:
        modalidade_dict = {
            'PF - Cartão de crédito': 'CC',
            'PF - Empréstimo com consignação em folha': 'ECCF',
            'PF - Empréstimo sem consignação em folha': 'ESCF',
            'PF - Habitacional': 'H',
            'PF - Outros créditos': 'OC',
            'PF - Rural e agroindustrial': 'RA',
            'PF - Veículos': 'V'
        }
        value = value.rename(columns=modalidade_dict)

    if periodicidade == 'trimestre':
        if trimestre_incompleto_drop:
            rows_start_drop = (3 - (value.index[0].month - 1) % 3) % 3; #print(rows_start_drop)
            row_end_drop    = -(value.index[-1].month % 3); #print(row_end_drop)
            if row_end_drop == 0: row_end_drop = None # means no drop is needed
            value = value.iloc[rows_start_drop: row_end_drop]
        value = value.resample('QS').sum()

    if ('BR' in value) and drop_BR: value = value.drop('BR', axis=1)

    # Initialize an empty DataFrame to store the combined results
    df_combined = pd.DataFrame()
    top_ufs_na_serie = list()

    # display(value.groupby('uf')[value_col].sum().sort_values(ascending=False))
    
    for period in value.index:
        df_period = value.loc[[period]].T

        df_top = df_period.loc[df_period.index.get_level_values('uf').isin(top_ufs)]
        df_other = df_period.loc[~df_period.index.get_level_values('uf').isin(top_ufs)].groupby(level='modalidade').sum()
        df_other.index = pd.MultiIndex.from_product([['demais UFs'], df_other.index])
        
        # Combine the top ufs and the 'other states' aggregated data
        df_period_combined = pd.concat([df_top, df_other], axis=0).T

        # Append to the combined DataFrame
        df_combined = pd.concat([df_combined, df_period_combined])
    
    df_combined = df_combined.stack(level=[0, 1], future_stack=True)#.reset_index()
    df_combined.name = value_col
    df_combined.index.names = [periodicidade, 'uf', 'modalidade']

    # # ordenando as UFs pelo volume em todo o periodo
    # uf_order = df_combined.groupby('uf')[value_col].sum().sort_values(ascending=False).index
    # uf_order = [uf for uf in uf_order if uf != 'demais UFs']
    # uf_order.append('demais UFs')
    # uf_order
    
    return df_combined
