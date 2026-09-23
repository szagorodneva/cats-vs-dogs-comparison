from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "data" / "comparison.xlsx"
# Настройки сравниваемых объектов.
# При переносе приложения меняются значения здесь, а не логика ниже.
LEFT_NAME = "Котики"
RIGHT_NAME = "Песики"

CRITERION_COLUMN = "Критерий"
LEFT_STATUS_COLUMN = "Статус кошки"
RIGHT_STATUS_COLUMN = "Статус собаки"

# Иконки для краткого отображения статусов в таблице-светофоре.
STATUS_ICONS = {
    "Просто": "✅",
    "Есть затруднения": "⚠️",
    "Очень сложно": "🔴",
    "Зависит от животного": "❔",
}

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
    CRITERION_COLUMN,
    "Что проверяем (бизнес-язык)",
    "Перевод на технический язык",
    "Что ищем в источниках",
    LEFT_STATUS_COLUMN,
    "Возможности кошки",
    "Ограничения кошки",
    "Ссылка на проверку кошки",
    "Источники кошки",
    RIGHT_STATUS_COLUMN,
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
matrix[LEFT_STATUS_COLUMN] = matrix[LEFT_STATUS_COLUMN].str.strip()
matrix[RIGHT_STATUS_COLUMN] = matrix[RIGHT_STATUS_COLUMN].str.strip()
status_methodology["Статус"] = status_methodology["Статус"].str.strip()

#Проверка заполненности и уникальности ID
if matrix["ID"].isna().any():
    st.error("В матрице есть строки без ID")
    st.stop()

if matrix["ID"].duplicated().any():
    st.error("В матрице есть повторяющиеся ID")
    st.stop()

#Получение уникльных статусов и объединение вариантов
left_statuses = set(matrix[LEFT_STATUS_COLUMN].dropna())
right_statuses = set(matrix[RIGHT_STATUS_COLUMN].dropna())
matrix_statuses = left_statuses | right_statuses

#Статусы, разрешенные методикой
allowed_statuses = set(status_methodology["Статус"].dropna())

#Проверка иконок у статусов
statuses_without_icons = allowed_statuses - set(STATUS_ICONS)
if statuses_without_icons:
    st.error("Для некоторых статусов не настроены иконки")
    st.write(statuses_without_icons)
    st.stop()

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

# Готовим компактную таблицу статусов для главной страницы
status_overview = matrix[
    [CRITERION_COLUMN, LEFT_STATUS_COLUMN, RIGHT_STATUS_COLUMN]
].copy()

# Заменяем текстовые статусы на настроенные иконки
status_columns = [LEFT_STATUS_COLUMN, RIGHT_STATUS_COLUMN]

status_overview[status_columns] = (
    status_overview[status_columns].replace(STATUS_ICONS)
)

# Даём колонкам короткие пользовательские названия
status_overview = status_overview.rename(
    columns={
        LEFT_STATUS_COLUMN: LEFT_NAME,
        RIGHT_STATUS_COLUMN: RIGHT_NAME,
    }
)

# Выводим краткое сравнение на главной странице
st.subheader("Сравнение по критериям")

status_legend = " · ".join(
    f"{icon} — {status}"
    for status, icon in STATUS_ICONS.items()
)

st.caption(status_legend)
st.dataframe(status_overview, hide_index=True)

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

