import streamlit as st
import numpy as np
import pandas as pd
from collections import Counter
import plotly.express as px
import io

st.set_page_config(page_title="Dice Path Simulator", layout="wide")

st.title("Симуляция пути пользователей по клеткам")

st.markdown("""
Можно задать вероятности граней «нечестного» кубика и общее количество пользователей.
""")

# -------------------------------
# Задаём вероятности бросков
# -------------------------------

# реальные данные по количеству бросков и вероятностям
throw_probs_dict = {
    1:0.1018,
2:0.0501999999999999,
3:0.106,
4:0.0624,
5:0.0483,
6:0.0684,
7:0.0316,
8:0.0371,
9:0.0280000000000001,
10:0.0248999999999999,
11:0.0233,
12:0.0212,
13:0.0192,
14:0.0180999999999999,
15:0.0139,
16:0.0164,
17:0.0157,
18:0.0147,
19:0.0139,
20:0.0135,
21:0.0129,
22:0.0125,
23:0.0123,
24:0.00960000000000003,
25:0.012,
26:0.012,
27:0.00990000000000002,
28:0.0116,
29:0.0102,
30:0.00939999999999999,
31:0.00739999999999999,
32:0.0086,
33:0.00810000000000002,
34:0.00889999999999999,
35:0.00730000000000001,
36:0.00699999999999999,
37:0.00659999999999999,
38:0.0064,
39:0.005,
40:0.0058,
41:0.00539999999999999,
42:0.005,
43:0.0048,
44:0.0044,
45:0.0042,
46:0.0033,
47:0.0038,
48:0.0035,
49:0.0033,
50:0.00309999999999999,
51:0.0026,
52:0.0028,
53:0.0027,
54:0.0026,
55:0.0022,
56:0.0025,
57:0.0025,
58:0.0025,
59:0.0023,
60:0.0026,
61:0.0024,
62:0.0023,
63:0.0018,
64:0.0017,
65:0.0014,
66:0.0012,
67:0.001,
68:0.0009,
69:0.0008,
70:0.0006,
71:0.000700000000000001,
72:0.000499999999999999,
73:0.0005,
74:0.0005,
75:0.000300000000000001,
76:0.0004,
77:0.000399999999999999,
78:0.000300000000000001,
79:0.000299999999999999,
80:0.0002,
81:0.0003,
82:0.0002,
83:0.0002,
84:0.0002,
85:0.0002,
86:0.0002,
87:9.99999999999998E-05,
88:0.0002,
89:0.0001,
90:0.0002,
91:0.0001,
92:0.0001,
93:9.99999999999998E-05,
94:0.0001,
95:0.0001,
96:9.99999999999998E-05,
97:0,
98:0.0001,
99:0.0001,
100:0,
101:9.99999999999999E-05,
102:0,
103:9.99999999999999E-05,
104:0,
105:0.0001,
106:0,
107:9.99999999999999E-05,
108:0,
109:0,
110:0.0001,
111:0,
112:0,
113:0,
114:0.0001,
115:0,
116:0,
117:0,
118:0,
119:0.0001,
}

throw_probs_dict = {k: v for k, v in throw_probs_dict.items()}

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
        cell_data[cell_data.index <= 150].reset_index(),
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


    
