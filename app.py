from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "data" / "comparison.xlsx"

st.set_page_config(
    page_title = 'Котики и песики',
    page_icon = '🐱❔🐶',
    layout = 'wide',
)

st.title('Котики vs песики')
st.write('Как превратить табличного монстра в симпатичный аналитический интерфейс')
st.caption('Демонстрационный проект на Python, Pandas и Streamlit')

try:
    matrix = pd.read_excel(DATA_FILE, sheet_name='Матрица', header=1)
except FileNotFoundError:
    st.error(f'Файл {DATA_FILE} не найден. ')
    st.stop()
except ValueError:
    st.error(f'Файл {DATA_FILE} не содержит лист "Матрица".')
    st.stop()

st.subheader('Проверка загрузки данных')
st.write(f'Загружено критериев: {len(matrix)}')
st.dataframe(matrix.head())

