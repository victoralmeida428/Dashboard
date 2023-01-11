import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import json
from dash import dash_table
import plotly.offline as pyo
from dash.dash_table.Format import Format, Group, Scheme, Symbol
import plotly.graph_objects as go
import statistics as st


# importando os dados
url = 'Urina EA - Dez 22 Convertido.csv'
df = pd.read_csv(url, encoding='latin-1', sep='\t')
df['RESP'] = df['RESP'].str.rsplit(" ", n=1, expand=True)[0]
df['RESP'] = df['RESP'].str.replace(',', '.', regex=True)
df['RESP'] = pd.to_numeric(df['RESP'], 'coerce')
df['S1_NOME_SA'] = df['S1_NOME_SA'].replace(to_replace='WAMA', value='Wama')
df['S1_NOME_SA'] = df['S1_NOME_SA'].replace(to_replace='wama', value='Wama')

# criando uma lista para conter as opções que o usuario terá para escolher - estados
analito_select = []
for analito in df['ANALITO'].unique():
    analito_select.append({'label':analito, 'value':analito})

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.themes.GRID]) # Criando a instancia da aplicação
app.layout = html.Div([ # Div geral
                    html.Div( # Div para os dados das estados
                        [
                            # Titulo
                            dbc.Row(
                                dbc.Col(
                                    html.H2(id='title-states') # adicionando uma ID
                                ), style = {'textAlign': 'center', 'paddingTop': '40px', 'paddingBottom': '20px'} # aplicando estilo
                            ),
                            # texto simples + popover
                            dbc.Row(
                                [
                                    dbc.Col( # texto simples
                                        html.Label("Escolha um analito:"), # texto do texto simples
                                        width = 3, # número e coluna que o elemento deve ocupar
                                        align = 'left', # setando o alinhamento do texto
                                        style = {'display': 'inline-block'} # add estido
                                    ),
                                    dbc.Col( # coluna para o popover
                                        html.Div(
                                            [
                                                dbc.Button('+ info', # botão do popover
                                                           outline=True, # colocando contorno no botão
                                                           id = 'popovertarget-estado', # adicionando o id do botão
                                                           style= {'fontFamily': 'Garamond', }, # alterando a fonte do botão
                                                           className="mr-2", # aplicando um tipo de botão do bootstrap
                                                           color="success", # alterando a cor do botão
                                                           size="sm", # alterando o tamanho do botão
                                                          ),
                                                dbc.Popover( # elemento do popover
                                                    [
                                                        # cabeçalho
                                                        dbc.PopoverHeader(id='popover-header-estado'), # id do cabeçalho do popover
                                                        # corpo
                                                        dbc.PopoverBody(
                                                            # add um elemento de markdonw para as marcações funcionarem vindas do texto nodata frame
                                                            dcc.Markdown(
                                                                        id = 'popover-body-estado', # id do markdown
                                                                        style={'textAlign': 'justify',} # deixando o texto no markdown justificado
                                                                        ),
                                                            style= {'overflow': 'auto', 'max-height': '500px'} # deixando o body do popover com uma barra de rolamento e fixando um tamanho máximo
                                                        ),
                                                    ],
                                                    id ='popover-estado', # adicionando um id ao popover
                                                    target = "popovertarget-estado", # definindo o elemento target do popover (tem de ser a id do botão)
                                                    placement='bottom-end', # definindo a posição em que o popover vai popar
                                                    is_open = False, # definindo que o estado inicial do popover é fechado
                                                ),
                                            ]
                                        ),
                                        width = 2, # definindo o número de colunas que o popover deve expandir
                                        align = 'right' # definindo o seu alinhamento na linha
                                    ),
                                ], style = {'paddingLeft': '12%', 'paddingRight': '5%'}, # adicionando um espaçamento para a linha
                                    justify='between' # definindo que as colunas que "sobram" deve ser alocadas entre as colunas
                            ),
                            # linha para o dropdown
                            dbc.Row(
                                dbc.Col( # coluna unica para o dropdown
                                    dcc.Dropdown(id = 'analito-picker', # id do dropdown
                                        value = 'Corpos Cetônicos.', # seta o valor inicial,
                                        options = analito_select, # as opções que vão aparecer no dropdown
                                        clearable = False, # permite remover o valor (acho importante manter false para evitar problemas)
                                        style = {'width': '50%'} # setando que o tamanho do dropdown deve preencher metade do espaço disponível
                                    ),
                                ), style = {'paddingTop': "5px",'paddingLeft': '10%',} # dando um espaçamento entre as linhas
                            ),
                            # grafico de dispersão com linhas
                            dbc.Row(
                                dbc.Col( # coluna para o gráfico de resultado por equipamento
                                    dcc.Graph(id='bar-plot-states'), # adicionado ID para o gráfico de dispersão com linhas
                                    style = {'textAlign': 'center', 'paddingBottom': '60px'} # adicoinado um estilo para a coluna
                                ),
                            ),
                            # grafico de quantidade de participantes por equipamento
                            dbc.Row(
                                dbc.Col(
                                    dcc.Graph(id='equip-states'),
                                    style = {'textAlign': 'center'}
                                ),
                            ),
                        ]
                    ),
])

# Gráfico de barras para um único analito
@app.callback(Output('bar-plot-states', 'figure'),
             [Input('analito-picker', 'value')])
def update_bar_plot_states(selected_analito):
    filtroanalito = df['ANALITO'] == selected_analito
    equip = []
    moda = []
    for equipamento in df['S1_NOME_SA'].unique():
        filtroequip = df['S1_NOME_SA'] == equipamento
        equip.append(equipamento)
        filtrado = df[filtroanalito & filtroequip]
        try:
            md = filtrado.RESP.mode().values[0]
        except:
            md = np.nan
        moda.append(md)

    df_tratado = {"Equipamento": equip, 'Moda': moda}
    df_tratado = pd.DataFrame(df_tratado)
    df_tratado.dropna(how='any', axis=0, inplace=True)
    df_tratado = df_tratado.sort_values(by='Moda', ascending=False)
    fig = px.bar(data_frame= df_tratado, # data frame com os dados
            x = 'Equipamento', # coluna para os dados do eixo x
            y = 'Moda', # coluna para os dados do eixo y
            color='Moda',
            hover_name = 'Equipamento', # coluna para setar o titulo do hover
            text='Moda'
            )
    fig.update_layout(xaxis = dict(linecolor='rgba(0,0,0,1)', # adicionando linha em y = 0
                                    tickmode = 'array', # alterando o modo dos ticks
                                    tickvals = df_tratado['Equipamento'], # setando o valor do tick de x
                                    ticktext = df_tratado['Equipamento']), # setando o valor do tick de x
                     yaxis = dict(title = 'Moda dos Resultados',  # alterando o titulo do eixo y
                                  linecolor='rgba(0,0,0,1)', # adicionando linha em x = 0
                                  tickformat=False, # removendo a formatação no eixo y
                                  ),
                      title_text = 'Moda do reporte do analito ' + selected_analito,  # adicionando titulo ao gráfico
                      title_x = 0.5, # reposicionando o titulo para que ele fique ono centro do gráfico
                     )
    return fig

# Quantidade de participantes por equipamento
@app.callback(Output('equip-states', 'figure'),
             [Input('analito-picker', 'value')])
def update_scatter_states(selected_analito):
    filtroanalito = df['ANALITO'] == selected_analito
    equip = []
    quantidade = []
    for equipamento in df['S1_NOME_SA'].unique():
        filtroequip = df['S1_NOME_SA'] == equipamento
        equip.append(equipamento)
        filtrado = df[filtroanalito & filtroequip]
        qtd = filtrado.S1_NOME_SA.value_counts().sum()
        quantidade.append(qtd)

    df_tratado = {"Equipamento": equip, 'Qtd': quantidade}
    df_tratado = pd.DataFrame(df_tratado)
    df_tratado.dropna(how='any', axis=0, inplace=True)
    df_tratado = df_tratado.sort_values(by='Qtd', ascending=False)
    fig = px.bar(
                data_frame= df_tratado, # o data frame contendo os dados
                x = 'Equipamento', # a coluna para os dados de x
                y = 'Qtd', # a coluna para os dados de y
                color = 'Qtd', # a coluna para diferenciar as séries com cores diferentes
                hover_name = 'Qtd', # o nome que aparece ao passar o nome
                text='Qtd'
                )
    fig.update_layout(xaxis = dict(linecolor='rgba(0,0,0,1)', # adicionando linha em y = 0
                                    tickmode = 'array', # alterando o modo dos ticks
                                    tickvals = df_tratado['Equipamento'], # setando o valor do tick de x
                                    ticktext = df_tratado['Equipamento']), # setando o valor do tick de x
                     yaxis = dict(title = 'Quantidade de Participantes',  # alterando o titulo do eixo y
                                  linecolor='rgba(0,0,0,1)', # adicionando linha em x = 0
                                  tickvals = df_tratado['Qtd'], # setando o valor do tick de x
                                  ticktext = df_tratado['Qtd']
                                  ),
                      title_text = 'Quantidade de Participantes por Equipamento ' + selected_analito,  # adicionando titulo ao gráfico
                      title_x = 0.5, # reposicionando o titulo para que ele fique ono centro do gráfico
                     )
    fig.update_yaxes(showticklabels=False)
    return fig

# Botao para o popover dos estados
@app.callback(Output("popover-estado", "is_open"),
            [Input('popovertarget-estado',"n_clicks")],
            [State("popover-estado", "is_open")])
def toggle_popover_estado(n, is_open):
    if n:
        return not is_open
    return is_open

'''# Conteudo do body para o popover do estado
@app.callback(Output('popover-body-estado', 'children'),
             [Input('state-picker', 'value')])
def update_pop_over_body_estado(selected_state):
    return df_texto_estados[df_texto_estados['Estado'] == selected_state]['Texto']'''


# Header para o popover do estado
@app.callback(Output('popover-header-estado', 'children'),
             [Input('analito-picker', 'value')])
def update_pop_over_header_estado(selected_state):
    return str(selected_state)

# Titulo da Div para os estados
@app.callback(Output('title-states', 'children'),
             [Input('analito-picker', 'value')])
def update_graficos_estado(selected_state):
    return "Análise dos Resultados de Urina EA para o Analito " + str(selected_state)


# Rodando a aplicação através de um servidor
if __name__ == '__main__':
    app.run_server(debug = True, use_reloader = False)
