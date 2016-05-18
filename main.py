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

bkio.output_file("docentes.html")
ipc = pd.read_csv('ipc/sanluis.csv', parse_dates=['fecha'])
ipc['ipc'] = 100 * np.cumprod(ipc['ipc']/100 + 1)
salario = pd.read_csv('salarios/docentes.csv', parse_dates=['fecha'])
salario['salario'] = 100 * salario['salario']/salario['salario'][0]


salario_inicial = salario['salario'].values[-1]
canasta_inicial = ipc['ipc'].values[-1]
fecha_comienzo = salario['fecha'].values[-1]
fin_paritarias = pd.Timestamp('2017-03-01')

oferta = [(pd.Timestamp('2016-06-01'), 18), (pd.Timestamp('2016-11-01'), 15)]

proy_salario = sl.proyectar_salarios(salario_inicial,
                                     fecha_comienzo,
                                     fin_paritarias, oferta)

proyeccion_salario = {'Oferta actual de paritarias': proy_salario}

proy_canasta1 = sl.proyectar_canasta(canasta_inicial,
                                     fecha_comienzo,
                                     fin_paritarias, 2.0)

proy_canasta2 = sl.proyectar_canasta(canasta_inicial,
                                     fecha_comienzo,
                                     fin_paritarias, 3.0)

proyeccion_canasta = {'Costo de vida 2% mensual': proy_canasta1,
                      'Costo de vida 3% mensual': proy_canasta2,}

fig1 = sl.crear_figura(ipc, salario, proyeccion_canasta,
                       proyeccion_salario)
fig2 = sl.crear_figura(ipc, salario, proyeccion_canasta,
                       proyeccion_salario, estilo='log')
tab1 = bkm.Panel(child=fig1, title="Lineal")
tab2 = bkm.Panel(child=fig2, title="Logarítmico")

tabs = bkm.Tabs(tabs=[tab1, tab2 ])

TOOLS = [bkm.PanTool(),
         bkm.WheelZoomTool(),
         bkm.BoxZoomTool(),
         bkm.PreviewSaveTool(),
         bkm.HoverTool(tooltips=[('Poder adquisitivo', '$y')], point_policy='snap_to_data'),
         bkm.CrosshairTool(dimensions=['height'])]

colors = ('#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854',
          '#ffd92f', '#e5c494', '#b3b3b3')

fig3 = bkp.Figure(title='Evolución del poder adquisitivo',
                  x_axis_type='datetime', tools=TOOLS)


fig3.line(ipc['fecha'], salario['salario']/ipc['ipc'],
          color=colors[0], legend='Poder adquisitivo normalizado a 11-2011',
          line_width=3)

fig3.circle(ipc['fecha'], salario['salario']/ipc['ipc'],
            color=colors[0], size=6)

i = 2
for key, val in zip(proyeccion_canasta.keys(), proyeccion_canasta.values()):
  fig3.line(val['fecha'],
            proyeccion_salario.values()[0]['salario']/val['canasta'],
            color=colors[i], legend=key, line_width=3, line_dash='dashed')
  i += 1

fig3.plot_height = 540
fig3.plot_width = int((16.0/9.0)*fig3.plot_height)
fig3.border_fill_color = 'whitesmoke'

hline = bkm.Span(location=1, dimension='width', line_color=colors[1],
                 line_width=3, line_alpha=0.7)
fig3.renderers.extend([hline])
box = bkio.VBox(tabs, fig3)


bkp.show(box)
