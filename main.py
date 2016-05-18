# -*- coding: utf-8 -*-
"""
Script de ejemplo
"""

import pandas as pd
import bokeh.io as bkio
import bokeh.plotting as bkp
import bokeh.models as bkm
import numpy as np
import salarios as sl

bkio.output_file("ejemplo.html")
ipc = pd.read_csv('ipc/sanluis.csv', parse_dates=['fecha'])
ipc['ipc'] = 100 * np.cumprod(ipc['ipc']/100 + 1)
salario = pd.read_csv('salarios/docentes.csv', parse_dates=['fecha'])
salario['salario'] = 100 * salario['salario']/salario['salario'][0]


salario_inicial = salario['salario'].values[-1]
canasta_inicial = ipc['ipc'].values[-1]
fecha_comienzo = salario['fecha'].values[-1]
fin_paritarias = pd.Timestamp('2017-03-01')

oferta = [(pd.Timestamp('2016-06-01'), 18), (pd.Timestamp('2016-11-01'), 15)]

proyeccion_salario = sl.proyectar_salarios(salario_inicial,
                                           fecha_comienzo,
                                           fin_paritarias, oferta)

proyeccion_canasta = sl.proyectar_canasta(canasta_inicial,
                                          fecha_comienzo,
                                          fin_paritarias, 3.0)

fig1 = sl.crear_figura(ipc, salario, proyeccion_canasta,
                       proyeccion_salario)
fig2 = sl.crear_figura(ipc, salario, proyeccion_canasta,
                       proyeccion_salario, estilo='log')
tab1 = bkm.Panel(child=fig1, title="Lineal")
tab2 = bkm.Panel(child=fig2, title="Logarítmico")

tabs = bkm.Tabs(tabs=[tab1, tab2 ])
bkp.show(tabs)
