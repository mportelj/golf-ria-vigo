import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- PARES OFICIALES PROPORCIONADOS POR EL USUARIO ---
PAR_RIA_VIGO = {
    1: 4, 2: 5, 3: 3, 4: 4, 5: 4, 6: 5, 7: 3, 8: 4, 9: 4,  # Ida
    10: 4, 11: 3, 12: 4, 13: 3, 14: 5, 15: 4, 16: 5, 17: 4, 18: 5 # Vuelta
}

def get_connection():
    return sqlite3.connect('golf_ria_vigo_final.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jugadores 
                 (nombre TEXT PRIMARY KEY, partidos INTEGER DEFAULT 0, puntos_mvp INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS historial 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, pareja_a TEXT, pareja_b TEXT, 
                  resultado_a INTEGER, resultado_b INTEGER, mvp TEXT)''')
    conn.commit()

init_db()

def calcular_puntos_hoyo(s1, s2, s3, s4, hoyo_num):
    par = PAR_RIA_VIGO[hoyo_num]
    pts_a, pts_b = 0, 0
    mvp_inc = {"p1": 0, "p2": 0, "p3": 0, "p4": 0}

    # 1. Identificar Mejores y Peores scores de cada pareja
    best_a, worst_a = (s1, s2) if s1 <= s2 else (s2, s1)
    best_b, worst_b = (s3, s4) if s3 <= s4 else (s4, s3)

    # 2. Puntos por Match Play (Scratch)
    # Mejor Bola: +2 puntos al MVP del que la hace
    if best_a < best_b: 
        pts_a += 1
        mvp_inc["p1" if s1 == best_a else "p2"] += 2
    elif best_b < best_a: 
        pts_b += 1
        mvp_inc["p3" if s3 == best_b else "p4"] += 2

    # Peor Bola: +1 punto al MVP del que la salva
    if worst_a < worst_b: 
        pts_a += 1
        mvp_inc["p1" if s1 == worst_a else "p2"] += 1
    elif worst_b < worst_a: 
        pts_b += 1
        mvp_inc["p3" if s3 == worst_b else "p4"] += 1

    # 3. Bonos por Birdie y Eagle (1 y 2 puntos extra respectivamente)
    scores = [s1, s2, s3, s4]
    p_ids = ["p1", "p2", "p3", "p4"]
    for i, s in enumerate(scores):
        if s == par - 1: # BIRDIE
            mvp_inc[p_ids[i]] += 1 # +1 MVP
            if i < 2: pts_a += 1   # +1 Bando A
            else: pts_b += 1       # +1 Bando B
        elif s <= par - 2: # EAGLE
            mvp_inc[p_ids[i]] += 2 # +2 MVP
            if i < 2: pts_a += 2   # +2 Bando A
            else: pts_b += 2       # +2 Bando B
            
    return pts_a, pts_b, mvp_inc

# --- INTERFAZ ---
st.set_page_config(page_title="Golf Ría de Vigo", page_icon="🏌️‍♂️")
st.title("🏌️‍♂️ Match Play: Ría de Vigo")

menu = st.sidebar.radio("Navegación", ["Partido", "Clasificación MVP", "Historial"])

if menu == "Partido":
    if 'game' not in st.session_state:
        st.subheader("Configurar Partido")
        col1, col2 = st.columns(2)
        p1 = col1.text_input("Pareja A - Jugador 1")
        p2 = col1.text_input("Pareja A - Jugador 2")
        p3 = col2.text_input("Pareja B - Jugador 1")
        p4 = col2.text_input("Pareja B - Jugador 2")
        start_h = st.selectbox("Salida por el hoyo:", [1, 10])
        
        if st.button("🏁 Iniciar Match"):
            st.session_state.game = {
                'players': [p1, p2, p3, p4], 'hoyo': start_h,
                'score_a': 0, 'score_b': 0,
                'mvp': {p1: 0, p2: 0, p3: 0, p4: 0}, 'logs': []
            }
            st.rerun()
    else:
        g = st.session_state.game
        par = PAR_RIA_VIGO[g['hoyo']]
        st.subheader(f"Hoyo {g['hoyo']} (Par {par})")
        
        c = st.columns(4)
        s = [c[i].number_input(f"{g['players'][i]}", 1, 12, par) for i in range(4)]

        if st.button("➕ Anotar Hoyo"):
            pa, pb, minc = calcular_puntos_hoyo(s[0], s[1], s[2], s[3], g['hoyo'])
            g['logs'].append({'h': g['hoyo'], 'pts': (pa, pb), 'mvp': minc})
            g['score_a'] += pa
            g['score_b'] += pb
            for i, p in enumerate(g['players']):
                g['mvp'][p] += minc[f"p{i+1}"]
            
            g['hoyo'] = g['hoyo'] + 1 if g['hoyo'] < 18 else 1
            st.rerun()

        st.metric("Marcador Actual", f"A: {g['score_a']}  |  B: {g['score_b']}")
        
        c_undo, c_save = st.columns(2)
        if c_undo.button("🔙 Deshacer"):
            if g['logs']:
                last = g['logs'].pop()
                g['score_a'] -= last['pts'][0]
                g['score_b'] -= last['pts'][1]
                for i, p in enumerate(g['players']):
                    g['mvp'][p] -= last['mvp'][f"p{i+1}"]
                g['hoyo'] = last['hoyo']
                st.rerun()

        if c_save.button("💾 Guardar y Finalizar"):
            conn = get_connection()
            cur = conn.cursor()
            mvp_match = max(g['mvp'], key=g['mvp'].get)
            cur.execute("INSERT INTO historial (fecha, pareja_a, pareja_b, resultado_a, resultado_b, mvp) VALUES (?,?,?,?,?,?)",
                      (datetime.now().strftime("%d/%m/%Y"), f"{g['players'][0]}/{g['players'][1]}", f"{g['players'][2]}/{g['players'][3]}", g['score_a'], g['score_b'], mvp_match))
            for p, pts in g['mvp'].items():
                cur.execute("INSERT OR IGNORE INTO jugadores (nombre) VALUES (?)", (p,))
                cur.execute("UPDATE jugadores SET partidos = partidos + 1, puntos_mvp = puntos_mvp + ? WHERE nombre = ?", (pts, p))
            conn.commit()
            del st.session_state.game
            st.success("¡Partido Guardado!")
            st.balloons()

elif menu == "Clasificación MVP":
    st.header("🏆 Ranking Acumulado")
    df = pd.read_sql_query("SELECT nombre as Jugador, partidos as PJ, puntos_mvp as Puntos FROM jugadores ORDER BY puntos_mvp DESC", get_connection())
    st.dataframe(df, use_container_width=True)

elif menu == "Historial":
    st.header("📜 Historial de Partidos")
    df = pd.read_sql_query("SELECT * FROM historial ORDER BY id DESC", get_connection())
    st.table(df)
