import urllib.parse
import streamlit as st

# 1. Tus datos de prueba (Simulación de tu lista_mvp)
lista_mvp = [
    {"Jugador": "Carlos", "pts_mvp": 25.5},
    {"Jugador": "Ana", "pts_mvp": 22.0},
    {"Jugador": "Luis", "pts_mvp": 19.8},
    {"Jugador": "Marta", "pts_mvp": 15.0},
    {"Jugador": "Pedro", "pts_mvp": 10.2},
]

# 2. Construcción del texto (Tu código original mejorado)
txt_wa = "⭐ *CLASIFICACIÓN MVP* ⭐\n"
for i, res in enumerate(lista_mvp):
    # Simplificado: si i < 3 asigna la medalla, si no, el cuadrado gris
    med = ["🥇", "🥈", "🥉"][i] if i < 3 else "▪️"
    puntos_v = float(res.get("pts_mvp", 0.0))
    txt_wa += f"{med} {i+1}º {res['Jugador']}: *{puntos_v:.1f} pts*\n"
txt_wa += "-----------------------------------\n\n"

# 3. Mostrar la vista previa en Streamlit (Opcional pero recomendado)
st.subheader("Vista previa del mensaje:")
st.text(txt_wa)

# 4. Codificar el texto para que WhatsApp lo entienda en la URL
texto_codificado = urllib.parse.quote(txt_wa)

# Puedes incluir un número de teléfono si quieres enviar a alguien específico (ej: "34600000000")
# Si lo dejas vacío, abrirá WhatsApp para que selecciones el contacto/grupo.
telefono = ""
whatsapp_url = f"https://wa.me/{telefono}?text={texto_codificado}"

# 5. Crear el botón de envío en Streamlit
st.link_button("🚀 Enviar por WhatsApp", whatsapp_url)
