#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Con estas funciones se pueden bajar todos los archivos .xls de
http://www.agduba.org.ar/sector/grilla%20salarial.

Por ejemplo:
>>from scrapers.agd import get_agd_grillasalarial, from_raw_to_tidy
>>get_agd_grillasalarial()
>>from_raw_to_tidy()

Con estos tres comandos se bajan los datos y se les da un formato manejable y
se guardan en tidy_escala_salarial.xlsx
"""
from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup as bs
import re
import time
import dateparser
from glob import glob
import pandas as pd
import itertools as itt
import numpy as np
import os


def get_agd_grillasalarial():
    """
    Download xls files from http://www.agduba.org.ar/sector/grilla%20salarial
    """
    month_list = ['enero' 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre',
                  'diciembre']
    r = requests.get('http://www.agduba.org.ar/sector/grilla%20salarial')
    soup = bs(r.content, 'lxml')
    links = [x['href'] for x in soup.find_all('a') if '.xls' in x['href']]
    links = ['http://www.agduba.org.ar' + x for x in links]
    if not os.path.isdir('raw_data'):
        os.mkdir('raw_data')
    if not os.path.isdir('data'):
        os.mkdir('data')
    for link in links:
        r = requests.get(link)
        if r.status_code == 200:
            fname = 'raw_data/' + link.split('/')[-1]
            with open(fname, 'wb') as f:
                f.write(r.content)
            search = re.search('\d\d\d\d\d\d', fname)
            if search is not None:
                time_text = search.group(0)
                time_stamp = time.strptime(time_text, '%m%Y')
            else:
                search = re.search('(' + '|'.join(month_list) + ')', fname)
                month = search.group(0)
                search = re.search('\d\d\d\d', fname)
                if search is not None:
                    year = search.group(0)
                else:
                    search = re.search('\d\d', fname)
                    year = '20' + search.group(0)
                time_stamp = dateparser.parse(' '.join([month, year]))
                time_stamp = time_stamp.timetuple()
            time_text = time.strftime('%m-%Y', time_stamp)
            fname = 'data/' + time_text + '.xls'
            with open(fname, 'wb') as f:
                f.write(r.content)


def from_raw_to_tidy():
    """
    Reshape the output of get_agd_grillasalarial in tidy format.
    """
    cargos = ['PROFESOR TITULAR', 'PROFESOR ASOCIADO', 'PROFESOR ADJUNTO',
              'JEFE DE TRABAJOS PRACTICOS',  'AYUDANTE DE PRIMERA',
              'AYUDANTE DE SEGUNDA']
    dedicaciones = ['EXCLUSIVA', 'SEMI-EXCLUSIVA', 'PARC/SIMPLE']
    salarios = pd.DataFrame(columns=['Fecha', 'Cargo', 'Dedicacion',
                                     'Antiguedad Años', 'Antiguedad %',
                                     'Sueldo Bruto'])
    for fname in glob('data/*'):
        df = pd.read_excel(fname, header=None)
        date = pd.Timestamp(fname.split('/')[-1].split('.')[0])
        for cargo, dedicacion in itt.product(cargos, dedicaciones):
            plain_view = find_subdata_in_agd_df(df, cargo, dedicacion)
            if plain_view is not None:
                plain_view['Fecha'] = date
                salarios = salarios.append(plain_view, ignore_index=False)
    salarios.to_excel('tidy_escala_salarial.xlsx')


def find_ind_df(df, target):
    """
    Find index and column of cell in dataframe, df, containing target.
    """
    ind = None
    for row in df.index:
        try:
            if target == 'nan':
                ind = np.where(pd.isnull(df.loc[row]))[0][0]
            else:
                ind = np.where(pd.Index(df.loc[row]) == target)[0][0]
            break
        except IndexError:
            row = None
    return row, ind


def find_subdata_in_agd_df(df, cargo, dedicacion):
    """
    Esta funcion extrae una sub tabla dentre de los archivos de AGD que tienen
    un formato poco feliz. Se pude ver cualquiera de los que se descargan con
    la funcion get_agd_grillasalarial()
    """
    cargo_index = df[(df.iloc[:, 0] == cargo)].index[0] + 1
    cargo_view = df.loc[cargo_index:]
    if sum(cargo_view.iloc[:, 0] == dedicacion) == 0:
        return None
    ded_index = cargo_view[(cargo_view.iloc[:, 0] == dedicacion)].index[0]
    ded_view = cargo_view.loc[ded_index + 1:]
    row_ini, brcol = find_ind_df(ded_view, u'BRUTO')
    row_ini += 1
    row_end = find_ind_df(ded_view.iloc[:, brcol], 'nan')[0]
    if row_end is not None:
        row_end -= 1
    else:
        row_end = ded_view.index[-1]
    arow, acol = find_ind_df(ded_view, u'AÑOS')
    plain_view = ded_view.loc[row_ini:row_end, [acol, acol+1, brcol]]
    plain_view = plain_view.copy()
    plain_view = plain_view.rename(columns={brcol: 'Sueldo Bruto',
                                            acol: 'Antiguedad Años',
                                            acol+1: 'Antiguedad %'})
    plain_view['Cargo'] = cargo
    plain_view['Dedicacion'] = dedicacion
    return plain_view
