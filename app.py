import streamlit as st
import numpy as np
import pandas as pd
from collections import Counter
import plotly.express as px
import io

st.set_page_config(page_title="Dice Path Simulator", layout="wide")

st.title("Симуляция пути пользователей по клеткам")

st.markdown("""
Это симуляция, учитывающая весь путь пользователя по клеткам.  
Можно задать вероятности граней «нечестного» кубика и общее количество пользователей.
""")

# -------------------------------
# Задаём вероятности бросков
# -------------------------------

# Твои реальные данные по количеству бросков и вероятностям
# Можно зашить напрямую:
throw_probs_dict = {
    1: 0.1348,
    2: 0.0964,
    3: 0.0053,
    4: 0.0597,
    5: 0.0882,
    6: 0.0395,
    7: 0.0426,
    8: 0.0481,
    9: 0.0275,
    10: 0.0315,
    11: 0.0327,
    12: 0.0217,
    13: 0.0241,
    14: 0.0241,
    15: 0.0171,
    16: 0.0187,
    17: 0.0189,
    18: 0.0146,
    19: 0.0158,
    20: 0.0156,
    21: 0.0125,
22: 0.0136,
23: 0.0134,
24: 0.0112,
25: 0.0122,
26: 0.012,
27: 0.0107,
28: 0.0105,
29: 0.0093,
30: 0.0077,
31: 0.0079,
32: 0.0075,
33: 0.0064,
34: 0.0064,
35: 0.0061,
36: 0.0052,
37: 0.0051,
38: 0.0049,
39: 0.0042,
40: 0.0043,
41: 0.0038,
42: 0.0033,
43: 0.0033,
44: 0.0031,
45: 0.0026,
46: 0.0026,
47: 0.0025,
48: 0.0022,
49: 0.002,
50: 0.0019,
51: 0.0017,
52: 0.0016,
53: 0.0016,
54: 0.0013,
55: 0.0012,
56: 0.0012,
57: 0.001,
58: 0.0011,
59: 0.0009,
60: 0.0008,
61: 0.0008,
62: 0.0008,
63: 0.0007,
64: 0.0006,
65: 0.0007,
66: 0.0005,
67: 0.0006,
68: 0.0005,
69: 0.0004,
70: 0.0005,
71: 0.0004,
72: 0.0003,
73: 0.0003,
74: 0.0004,
75: 0.0002,
76: 0.0003,
77: 0.0003,
78: 0.0002,
79: 0.0002,
80: 0.0002
}
# Оставим только до 20 бросков
throw_probs_dict = {k: v for k, v in throw_probs_dict.items() if k <= 80}

# -------------------------------
# Интерфейс ввода
# -------------------------------

st.subheader("Задайте параметры")

# Кубик
default_probs = [0.1, 0.15, 0.3, 0.1, 0.3, 0.05]
face_probs = []

cols = st.columns(6)
for i in range(6):
    prob = cols[i].number_input(
        f"Грань {i+1}",
        value=float(default_probs[i]),
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        format="%.4f"
    )
    face_probs.append(prob)

if abs(sum(face_probs) - 1.0) > 1e-6:
    st.error(f"Сумма вероятностей граней должна быть равна 1. Сейчас: {sum(face_probs):.4f}")
    st.stop()

# Пользователи
n_users_total = st.number_input(
    "Введите общее количество пользователей",
    min_value=1,
    value=2730000,
    step=1000
)

run_button = st.button("Запустить симуляцию")

if run_button:

    st.write("Считаем...")

    faces = np.arange(1, 7)

    # Посчитаем пользователей, которые завершили ровно N бросков
    users_by_throw_count = {
        n_throws: int(round(prob * n_users_total, 0))
        for n_throws, prob in throw_probs_dict.items()
    }

    # Храним счетчик всех посещений клеток
    cell_counter = Counter()

    for n_throws, n_users in users_by_throw_count.items():
        if n_users == 0:
            continue

        # Симулируем броски
        rolls = np.random.choice(
            faces,
            size=(n_users, n_throws),
            p=face_probs
        )

        # Кумулятивная сумма по строкам = путь каждого пользователя
        cum_positions = np.cumsum(rolls, axis=1)

        # Все позиции всех пользователей
        all_positions = cum_positions.flatten()

        # Засчитываем визиты на все клетки
        cell_counter.update(all_positions)

    # В красивую таблицу
    st.subheader("Распределение пользователей по клеткам")

    st.dataframe(cell_data)
    
    # Кнопка для скачивания
    csv = cell_data.reset_index().to_csv(index=False).encode("utf-8")
    
    st.download_button(
        label="Скачать CSV",
        data=csv,
        file_name="visited_cells.csv",
        mime="text/csv",
    )
    cell_data = pd.DataFrame.from_dict(cell_counter, orient='index', columns=['users_passed'])
    cell_data.index.name = 'cell'
    cell_data = cell_data.sort_index()
    cell_data['percent_users'] = (cell_data['users_passed'] / n_users_total) * 100
    total_users = cell_data['users_passed'].sum()
    st.write(f"Всего игр: {total_users}")
    games_per_user = round(total_users/n_users_total,2)
    st.write(f"Игр на пользователя: {games_per_user}")

    # ----------------------------
    # График посещений
    # ----------------------------
    
    fig = px.bar(
        cell_data[cell_data.index <= 200].reset_index(),
        x='cell',
        y='users_passed',
        labels={'cell': 'Клетка', 'users_passed': 'Количество пользователей'},
        title="Посещённые клетки пользователями",
        color="users_passed",  # цвет по количеству пользователей
        color_continuous_scale="Viridis",  # цветовая шкала
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    st.success("Симуляция завершена!")


    
