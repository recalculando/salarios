import pandas as pd
import numpy as np
from bokeh.io import output_server, vplot
import bokeh.models as bkm
from bokeh.plotting import figure, output_file, show
from bokeh.charts import Line

import datetime

ipc = pd.read_csv('ipc_sanluis.csv', parse_dates=['fecha'])
ipc['ipc_sanluis'] = 100 * np.cumprod(ipc['ipc_sanluis']/100 + 1)
salario = pd.read_csv('salarios_docentes.csv', parse_dates=['fecha'])
salario['docentes UBA'] = 100 * salario['docentes UBA']/salario['docentes UBA'][0]
ultimo = salario['fecha'].values[-1]
fin_paritarias = pd.Timestamp('2017-03-01')
agregado = pd.date_range(freq='m', start=pd.Timestamp(ultimo), end=fin_paritarias)
#agregado += pd.Timedelta('1 day') - pd.Timedelta('1 M')
oferta = [[(pd.Timestamp('2016-05-01'), 18), (pd.Timestamp('2016-11-01'), 15)],]

a = oferta[0]

proyectado = pd.DataFrame({'fecha': agregado})
s = np.zeros_like(proyectado.values, dtype=np.float).flatten()

for i, mes in enumerate(proyectado['fecha']):
  if i == 0:
    s[i] = salario['docentes UBA'].values[-1]
    continue
  b = False
  for _ in a:
    if mes == _[0]:
      print (mes)
      s[i] = s[i-1] * (1 + _[1]/100)
      b = True
      continue
  if b: continue
  s[i] = s[i-1]




output_file("example.html", title="example")





TOOLS = [bkm.PanTool(),
         bkm.WheelZoomTool(),
         bkm.BoxZoomTool(),
         bkm.HoverTool(tooltips=[('Fecha', '$x'), ('Monto', '$y')])]



s1 = figure(title='primero', x_axis_type='datetime', tools=TOOLS)

s1.line(ipc['fecha'], ipc['ipc_sanluis'], color='navy',
        legend='Costo de Vida', line_width=2)

s1.circle(ipc['fecha'], ipc['ipc_sanluis'], color='navy', size=8)

s1.line(salario['fecha'], salario['docentes UBA'], color='green',
        legend='Salario', line_width=2)

s1.circle(salario['fecha'], salario['docentes UBA'], color='green', size=8)

TOOLS = [bkm.PanTool(),
         bkm.WheelZoomTool(),
         bkm.BoxZoomTool(),
         bkm.HoverTool(tooltips=[('Fecha', '$x'), ('Monto', '$y')]),]

s2 = figure(title='primero', x_axis_type='datetime', tools=TOOLS)
s2.line(ipc['fecha'], salario['docentes UBA']/ipc['ipc_sanluis'], color='navy')

p = vplot(s1, s2)
show(p)

"""
numeroDeMesesEtimados = 8
# Hacemos el indice acumulado de inflacion. Se considera el mes de septiembre de 2011 como la referencia y que la inflacion aplica al costo de vida del mes siguiente
InflacionReferida = [100]
for inflacion in IPC_SanLuis:
    InflacionReferida = InflacionReferida + [InflacionReferida[-1]*(1+inflacion/100)]

InflacionReferida = InflacionReferida[1:]

#Separamos los datos hasta donde hay datos de inflacion
indice_FechasSinProyeccion=indice_Fechas[:-numeroDeMesesEtimados]
InflacionReferidaSinProyeccion = InflacionReferida[:-numeroDeMesesEitmados]
sueldoReferidoSinProyeccion = sueldoReferido[:-numeroDeMesesEtimados]
SalarioRealSinProyeccion = [(dato[0]/dato[1]-1)*100 for dato in zip (sueldoReferidoSinProyeccion,InflacionReferidaSinProyeccion)]
sueldoReferidoProyeccionActual = sueldoReferido[-numeroDeMesesEtimados:]



# Hacemos tres proyecciones para abril en adelante, una con 3% de inflacion, otra con 1,5 y otra con 0.5
proyeccion1 = 3.
proyeccion2 = 2.
proyeccion3 = 0

indiceFechasProyeccion = indice_Fechas[-numeroDeMesesEtimados:]
InflacionProyeccion_1 = [InflacionReferidaSinProyeccion[-1]]
InflacionProyeccion_2 = [InflacionReferidaSinProyeccion[-1]]
InflacionProyeccion_3 = [InflacionReferidaSinProyeccion[-1]]
for value in indiceFechasProyeccion:
    InflacionProyeccion_1 = InflacionProyeccion_1 + [InflacionProyeccion_1[-1]*(1+proyeccion1/100)]
    InflacionProyeccion_2 = InflacionProyeccion_2 + [InflacionProyeccion_2[-1]*(1+proyeccion2/100)]
    InflacionProyeccion_3 = InflacionProyeccion_3 + [InflacionProyeccion_3[-1]*(1+proyeccion3/100)]

SalarioRealProyeccion_1 = [(dato[0]/dato[1]-1)*100 for dato in zip (sueldoReferidoProyeccionActual,InflacionProyeccion_1)]
SalarioRealProyeccion_2 = [(dato[0]/dato[1]-1)*100 for dato in zip (sueldoReferidoProyeccionActual,InflacionProyeccion_2)]
SalarioRealProyeccion_3 = [(dato[0]/dato[1]-1)*100 for dato in zip (sueldoReferidoProyeccionActual,InflacionProyeccion_3)]



evoluciones, ax = plt.subplots(figsize=(20, 10))
ind = np.arange(len(sueldoReferido))
plt.plot(sueldoReferidoSinProyeccion, label='Evolucion sueldo')
plt.plot(ind[-numeroDeMesesEtimados:]-1,sueldoReferidoProyeccionActual, label='propuesta actual paritaria (15+15)')
plt.plot(ind[-numeroDeMesesEtimados-1:],InflacionProyeccion_1, label='proyeccion inflacion '+str(proyeccion1)+'% mensual (actual)')
plt.plot(ind[-numeroDeMesesEtimados-1:],InflacionProyeccion_2, label='proyeccion inflacion '+str(proyeccion2)+'% mensual (generosa)')
plt.plot(ind[-numeroDeMesesEtimados-1:],InflacionProyeccion_3, label='proyeccion inflacion '+str(proyeccion3)+'% mensual (necesaria)')
plt.plot(InflacionReferidaSinProyeccion, label='Evolucion costo de vida')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.grid(True)
plt.xticks(ind, indice_Fechas, rotation='vertical')

comparativo = plt.figure(figsize=(20, 10))
referencia = [0 for value in sueldoReferido]

plt.plot(SalarioRealSinProyeccion, label='Poder adquisitivo respecto a Octubre 2011')
plt.plot(ind[-numeroDeMesesEtimados:]-1,SalarioRealProyeccion_1, label='Poder adquisitivo propuesta 15+15 proyeccion inflacion '+str(proyeccion1)+'%)')
plt.plot(ind[-numeroDeMesesEtimados:]-1,SalarioRealProyeccion_2, label='Poder adquisitivo propuesta 15+15 proyeccion inflacion '+str(proyeccion2)+'%)')
plt.plot(ind[-numeroDeMesesEtimados:]-1,SalarioRealProyeccion_3, label='Poder adquisitivo propuesta 15+15 proyeccion inflacion '+str(proyeccion3)+'%)')
plt.plot(referencia, 'r--', label='Referencia')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.xticks(ind, indice_Fechas, rotation='vertical')


plt.show()
"""
