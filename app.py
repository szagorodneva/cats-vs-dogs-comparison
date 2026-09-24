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

# Колонки с возможностями и ограничениями каждого сравниваемого объекта
LEFT_CAPABILITIES_COLUMN = "Возможности кошки"
LEFT_LIMITATIONS_COLUMN = "Ограничения кошки"

RIGHT_CAPABILITIES_COLUMN = "Возможности собаки"
RIGHT_LIMITATIONS_COLUMN = "Ограничения собаки"

# Колонки с названием критерия и его пояснением.
CRITERION_COLUMN = "Критерий"
QUESTION_COLUMN = "Что проверяем (бизнес-язык)"

# Колонки со ссылками на проверку и источниками
LEFT_CHECK_LINK_COLUMN = "Ссылка на проверку кошки"
LEFT_SOURCES_COLUMN = "Источники кошки"

RIGHT_CHECK_LINK_COLUMN = "Ссылка на проверку собаки"
RIGHT_SOURCES_COLUMN = "Источники собаки"

# Иконки для краткого отображения статусов в таблице-светофоре.
STATUS_ICONS = {
    "Просто": "✅",
    "Есть затруднения": "⚠️",
    "Очень сложно": "🔴",
    "Зависит от животного": "ℹ️",
}

CONCLUSION_COLUMN = "Вывод для будущего владельца"

#Технические таблицы для проверки: True - показать, False - скрыть
SHOW_DEBUG = False


# Заполнение верхнего блока страницы
PROJECT_TITLE = "Котики vs песики"
PPAGE_ICON = "🐾" #иконка вкладки
LEFT_ICON = "🐱"
RIGHT_ICON = "🐶"


PROJECT_DESCRIPTION = (
    "Сравниваем котиков и песиков по условиям содержания, уходу "
    "и совместимости с образом жизни городской семьи"
)

PROJECT_CAPTION = (
    "Как превратить табличного монстра в симпатичный аналитический интерфейс. " 
    "Python, Pandas и Streamlit"
)

KEY_QUESTION = "Подходит ли животное для домашнего содержания?"

LEFT_RESULT = "Домашнее содержание возможно"
RIGHT_RESULT = "Домашнее содержание возможно"

RESULT_NOTE = (
    "При условии, что особенности животного соответствуют "
    "образу жизни и возможностям владельца. Его потребности в пушистости и лапках"
)
#===================================================
#===================================================
#===================================================
#===================================================


st.title(PROJECT_TITLE)
st.write(PROJECT_DESCRIPTION)
st.caption(PROJECT_CAPTION)

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
    LEFT_CAPABILITIES_COLUMN,
    LEFT_LIMITATIONS_COLUMN,
    LEFT_CHECK_LINK_COLUMN,
    LEFT_SOURCES_COLUMN,
    RIGHT_STATUS_COLUMN,
    RIGHT_CAPABILITIES_COLUMN,
    RIGHT_LIMITATIONS_COLUMN,
    RIGHT_CHECK_LINK_COLUMN,
    RIGHT_SOURCES_COLUMN,
    CONCLUSION_COLUMN,
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

#=======================================================
#=======================================================
#=======================================================
#=======================================================

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

# Показываем общий вывод до перехода к отдельным критериям.
st.subheader(KEY_QUESTION)

left_card, right_card = st.columns(2)

with left_card:
    with st.container(border=True):
        st.markdown(f"### {LEFT_ICON} {LEFT_NAME}")
        st.info(LEFT_RESULT, icon="☺️") #.info = нейтральная информация, голубая плашка

with right_card:
    with st.container(border=True):
        st.markdown(f"### {RIGHT_ICON} {RIGHT_NAME}")
        st.info(RIGHT_RESULT, icon="☺️")

st.caption(RESULT_NOTE)

# Выводим краткое сравнение на главной странице
st.subheader("Сравнение по критериям")

status_legend = " · ".join(
    f"{icon} — {status}"
    for status, icon in STATUS_ICONS.items()
)

st.caption(status_legend)
# Объясняем, как открыть подробности выбранного критерия
st.caption(
    "Чтобы открыть подробности, поставьте галочку напротив нужного критерия"
)


# Разрешаем пользователю выбрать один критерий для подробного просмотра
table_event = st.dataframe(
    status_overview,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
)

# Получаем позицию выбранной строки и находим полный критерий в исходной матрице
selected_rows = table_event.selection.rows

if selected_rows:
    selected_position = selected_rows[0]
    selected_criterion = matrix.iloc[selected_position]

    st.markdown(
        f"Выбран критерий: **{selected_criterion[CRITERION_COLUMN]}**"
    )
    st.write(selected_criterion[QUESTION_COLUMN]) #пояснение к критерию

    # Показываем статусы животных по выбранному критерию
    left_status = selected_criterion[LEFT_STATUS_COLUMN]
    right_status = selected_criterion[RIGHT_STATUS_COLUMN]

    left_detail, right_detail = st.columns(2)

    with left_detail.container(border=True):
        st.markdown(f"#### {LEFT_ICON} {LEFT_NAME}")
        st.write(f"{STATUS_ICONS[left_status]} {left_status}")
        st.markdown("**Возможности**")
        st.write(selected_criterion[LEFT_CAPABILITIES_COLUMN])
        st.markdown("**Ограничения**")
        st.write(selected_criterion[LEFT_LIMITATIONS_COLUMN])
        st.markdown("**Ссылка на проверку**")
        st.text(str(selected_criterion[LEFT_CHECK_LINK_COLUMN]))

        st.markdown("**Источники**")
        st.text(str(selected_criterion[LEFT_SOURCES_COLUMN]))

    with right_detail.container(border=True):
        st.markdown(f"#### {RIGHT_ICON} {RIGHT_NAME}")
        st.write(f"{STATUS_ICONS[right_status]} {right_status}")
        st.markdown("**Возможности**")
        st.write(selected_criterion[RIGHT_CAPABILITIES_COLUMN])
        st.markdown("**Ограничения**")
        st.write(selected_criterion[RIGHT_LIMITATIONS_COLUMN])
        st.markdown("**Ссылка на проверку**")
        st.text(str(selected_criterion[RIGHT_CHECK_LINK_COLUMN]))
        st.markdown("**Источники**")
        st.text(str(selected_criterion[RIGHT_SOURCES_COLUMN]))

    # Показываем общий вывод по выбранному критерию
    with st.container(border=True):
        st.markdown("#### Вывод")
        st.write(selected_criterion[CONCLUSION_COLUMN])

# Даем пользователю возможность открыть методику
st.subheader("Дополнительная информация")

with st.expander("Как читать статусы"):
    st.table(status_methodology, hide_index=True)

with st.expander("Правила чтения результатов"):
    st.table(rules_methodology, hide_index=True)

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

