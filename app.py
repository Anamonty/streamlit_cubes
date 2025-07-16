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
    1:0.1326,
2:0.0314,
3:0.0553,
4:0.0809,
5:0.0504,
6:0.075,
7:0.0409,
8:0.0427999999999999,
9:0.0317,
10:0.0347,
11:0.0253,
12:0.0234,
13:0.0215,
14:0.0202000000000001,
15:0.0155,
16:0.0178,
17:0.0169,
18:0.0158,
19:0.0151,
20:0.0145,
21:0.0138,
22:0.0134,
23:0.013,
24:0.0098,
25:0.0127,
26:0.0123,
27:0.0098,
28:0.0113,
29:0.00969999999999999,
30:0.0092,
31:0.0074,
32:0.0082,
33:0.00750000000000001,
34:0.0086,
35:0.00650000000000001,
36:0.00609999999999999,
37:0.00559999999999999,
38:0.0054,
39:0.00420000000000001,
40:0.0048,
41:0.0042,
42:0.0039,
43:0.0037,
44:0.0034,
45:0.0032,
46:0.0025,
47:0.0028,
48:0.0026,
49:0.0024,
50:0.0021,
51:0.0017,
52:0.0019,
53:0.0018,
54:0.0016,
55:0.0013,
56:0.0014,
57:0.0013,
58:0.0012,
59:0.001,
60:0.000999999999999999,
61:0.0009,
62:0.0009,
63:0.0008,
64:0.0008,
65:0.000699999999999999,
66:0.000700000000000001,
67:0.0006,
68:0.0006,
69:0.0005,
70:0.0005,
71:0.0005,
72:0.000399999999999999,
73:0.000300000000000001,
74:0.000399999999999999,
75:0.0003,
76:0.0004,
77:0.0003,
78:0.0003,
79:0.000200000000000001,
80:0.0002,
81:0.0003,
82:0.0002,
83:0.0002,
84:0.0002,
85:9.99999999999998E-05,
86:0.0002,
87:0.0002,
88:9.99999999999998E-05,
89:0.0002,
90:0.0001,
91:0.0001,
92:0.0001,
93:9.99999999999998E-05,
94:0.0001,
95:0.0001,
96:0.0001,
97:0.0001,
98:9.99999999999998E-05,
99:0,
100:0.0001,
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
    cell_data = pd.DataFrame.from_dict(cell_counter, orient='index', columns=['users_passed'])
    cell_data.index.name = 'cell'
    cell_data = cell_data.sort_index()
    cell_data['percent_users'] = (cell_data['users_passed'] / n_users_total) * 100
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


    
