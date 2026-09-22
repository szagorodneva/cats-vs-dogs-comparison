from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "data" / "comparison.xlsx"

#Технические таблицы для проверки: True - показать, False - скрыть
SHOW_DEBUG = False

#Настройки страницы в браузере
st.set_page_config(
    page_title = 'Котики и песики',
    page_icon = '🐱❔🐶',
    layout = 'wide',
)
#Заголовок и описание проекта
st.title('Котики vs песики')
st.write('Как превратить табличного монстра в симпатичный аналитический интерфейс')
st.caption('Демонстрационный проект на Python, Pandas и Streamlit')

#Загрузка всех листов Excel
try:
    info = pd.read_excel(DATA_FILE, sheet_name='info', header=None)
    matrix = pd.read_excel(DATA_FILE, sheet_name='Матрица', header=1)
    methodology = pd.read_excel (DATA_FILE, sheet_name='Методика', header=None)

#Вывод ошибки, если отсутстивует файл либо на нем нет нужных листов
except FileNotFoundError:
    st.error(f'Файл {DATA_FILE} не найден')
    st.stop()
except ValueError:
    st.error(
        "В Excel-файле отсутствует один из обязательных листов: "
        "info, Матрица или Методика"
    )
    st.stop()

#Колонки, по которым приложение строит сравнение
required_columns = {
    "ID",
    "Критерий",
    "Что проверяем (бизнес-язык)",
    "Перевод на технический язык",
    "Что ищем в источниках",
    "Статус кошки",
    "Возможности кошки",
    "Ограничения кошки",
    "Ссылка на проверку кошки",
    "Источники кошки",
    "Статус собаки",
    "Возможности собаки",
    "Ограничения собаки",
    "Ссылка на проверку собаки",
    "Источники собаки",
    "Вывод для будущего владельца",
}

#Проверка наличия обязательных колонок
missing_columns = required_columns - set(matrix.columns)
if missing_columns:
    st.error("В матрице отсутствуют обязательные колонки")
    st.write(missing_columns)
    st.stop()

#Справочник статусов из листа Методика, перенос первой строки в заголовок и удаление из списка
# строка 5 содержит заголовки, строки 6–9 — четыре статуса.
status_methodology = methodology.iloc[4:9].copy()
status_methodology.columns = status_methodology.iloc[0]
status_methodology = status_methodology.iloc[1:]
status_methodology = status_methodology.reset_index(drop=True)

#Удаление лишних пробелов в названиеях статусов
matrix["Статус кошки"] = matrix["Статус кошки"].str.strip()
matrix["Статус собаки"] = matrix["Статус собаки"].str.strip()
status_methodology["Статус"] = status_methodology["Статус"].str.strip()

#Проверка заполненности и уникальности ID
if matrix["ID"].isna().any():
    st.error("В матрице есть строки без ID")
    st.stop()

if matrix["ID"].duplicated().any():
    st.error("В матрице есть повторяющиеся ID")
    st.stop()

#Получение уникльных статусов и объединение вариантов
cat_statuses = set(matrix["Статус кошки"].dropna())
dog_statuses = set(matrix["Статус собаки"].dropna())
matrix_statuses = cat_statuses | dog_statuses

#Статусы, разрешенные методикой
allowed_statuses = set(status_methodology["Статус"].dropna())

#Проверка на сответствие статусов матрицы и справочника
unknown_statuses = matrix_statuses - allowed_statuses
if unknown_statuses:
    st.error("В матрице найдены статусы, которых нет в методике")
    st.write(unknown_statuses)
    st.stop()

#Правила чтения из листа Методика, первая строка = заголовок
# строка 11 содержит заголовки, строки 12–18 — семь правил.
rules_methodology = methodology.iloc[10:18, 0:2].copy() 
rules_methodology.columns = rules_methodology.iloc[0]
rules_methodology = rules_methodology.iloc[1:]
rules_methodology = rules_methodology.reset_index(drop=True)

data_description = info.iloc[1,0]

#Техничесние выводы для проверки загрузки и обработки данных
if SHOW_DEBUG:
    st.subheader("Проверка загрузки данных")

    st.write(f"Загружено критериев: {len(matrix)}")
    st.dataframe(matrix.head())

    st.write("Описание данных:")
    st.write(data_description)

    st.write("Справочник статусов:")
    st.dataframe(status_methodology)

    st.write("Правила чтения:")
    st.dataframe(rules_methodology)

