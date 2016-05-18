# -*- coding: utf-8 -*-
"""
Módulo básico (por ahora sólo funcional) para realizar los gráficos
"""
import pandas as pd
import numpy as np
import bokeh.models as bkm
import bokeh.plotting as bkp

def proyectar_salarios(salario, fecha_comienzo, fecha_fin, oferta):
  """
  Función que genera una proyección sobre el salario.

  Parámetros
  ----------

  salario : float
      El último salario dato

  fecha_comienzo : pandas Timestamp
      Fecha de comienzo de proyección (usualmente coincidente con la
      fecha del último salario dato)

  fecha_fin : pandas Timestamp
      Última fecha contemplada por paritaria

  oferta : List
      Una lista de tuplas, donde el primer elemento de la tupla es la
      fecha en la que se cobra el aumento y la segunda es el
      porcentaje de aumento

  Returns
  -------

  proyectado : pandas DataFrame
      Un Dataframe con fechas y valores de la proyección
  """
  fechas = pd.date_range(freq='m', start=fecha_comienzo, end=fecha_fin)
  fechas += pd.Timedelta('1 day') # Porque si no da el último día del mes
  s = np.zeros_like(fechas.values, dtype=np.float).flatten()

  for i, mes in enumerate(fechas):
    if i == 0:
      s0 = salario
    else:
      s0 = s[i-1]
    b = False
    for of in oferta:
      if mes == of[0]:
        s[i] = s0 * (1 + of[1]/100.0)
        b = True
        continue
    if not b: s[i] = s0

  proyectado = pd.DataFrame({'fecha': fechas,
                             'salario': s})
  return proyectado

def proyectar_canasta(canasta, fecha_comienzo, fecha_fin, porcentaje):
  """
  Función que genera una proyección sobre el costo de vida.

  Parámetros
  ----------

  canasta : float
      La última canasta

  fecha_comienzo : pandas Timestamp
      Fecha de comienzo de proyección (usualmente coincidente con la
      fecha de la última canasta dato)

  fecha_fin : pandas Timestamp
      Última fecha contemplada por proyección de inflación

  porcentaje : float
      Porcentaje de inflación mensual

  Returns
  -------

  proyectado : pandas DataFrame
      Un Dataframe con fechas y valores de la proyección
  """
  fechas = pd.date_range(freq='m', start=fecha_comienzo, end=fecha_fin)
  fechas += pd.Timedelta('1 day') # Porque si no da el último día del mes
  s = np.zeros_like(fechas.values, dtype=np.float).flatten()


  for i, _ in enumerate(fechas):
    if i == 0:
      s0 = canasta
    else:
      s0 = s[i-1]
    s[i] = s0 * (1 + porcentaje/100.0)

  proyectado = pd.DataFrame({'fecha': fechas,
                             'canasta': s})
  return proyectado

def crear_figura(canasta, salario, proyeccion_canasta, proyeccion_salario,
                 estilo='lin'):
  """
  Crea una figura de bokeh

  Parámetros
  ----------

  canasta : pandas DataFrame
      La canasta a considerar

  salario : pandas DataFrame
      El salario histórico

  proyeccion_salario : pandas DataFrame
      La proyección del salario con la propuesta de paritarias

  proyeccion_canasta : pandas DataFrame
      La proyección de la canasta básica

  estilo : {'lin', 'log'}
      Estilo lineal o logarítmico del gráfico

  Returns
  -------

  fig : bokeh Figure
      La figura que resulta
  """

  colors = ('#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854',
           '#ffd92f', '#e5c494', '#b3b3b3')

  TOOLS = [bkm.PanTool(),
           bkm.WheelZoomTool(),
           bkm.BoxZoomTool(),
           bkm.HoverTool(tooltips=[('Fecha', '$x'), ('Monto', '$y')])]


  if estilo == 'lin':
    fig = bkp.figure(title='Salario normalizado',
                     x_axis_type='datetime', tools=TOOLS)
  elif estilo == 'log':
    fig = bkp.figure(title='Salario normalizado',
                     x_axis_type='datetime', tools=TOOLS,
                     y_axis_type='log')
  else:
    raise ValueError('Opción {0} no encontrada'.format(estilo))
  fig.plot_height = 540
  fig.plot_width = 960

  fig.line(canasta['fecha'], canasta['ipc'], color=colors[0],
           legend='Costo de Vida (IPC San Luis)', line_width=3)

  fig.circle(canasta['fecha'], canasta['ipc'], color=colors[0], size=6)

  fig.line(salario['fecha'], salario['salario'], color=colors[1],
           legend='Salario', line_width=3)

  fig.circle(salario['fecha'], salario['salario'], color=colors[1], size=6)

  fig.line(proyeccion_salario['fecha'], proyeccion_salario['salario'], color=colors[2],
           legend='Paritarias Salario', line_width=3, line_dash='dashed')

  fig.line(proyeccion_canasta['fecha'], proyeccion_canasta['canasta'],
           color=colors[3], legend='Proyección Costo de Vida', line_width=3,
           line_dash='dashed')

  fig.legend[0].location = 'top_left'

  return fig
