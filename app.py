import os
import streamlit as st
import base64
from openai import OpenAI

# Función para convertir imagen a base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Configuración de la página
st.set_page_config(page_title="Museo del Arte Perdido ", layout="centered", initial_sidebar_state="collapsed")
st.title(" Museo del Arte ")
st.markdown("Explora el misterio detrás de cada imagen. La IA actuará como un **curador experto** que analiza su origen, técnica y significado oculto.")

# Ingreso de API Key
ke = st.text_input(' Ingresa tu Clave de OpenAI', type="password")
if ke:
    os.environ['OPENAI_API_KEY'] = ke
else:
    st.warning("Por favor ingresa tu clave de OpenAI para continuar.")

# Inicializa cliente OpenAI
api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key) if api_key else None

# Subir imagen
uploaded_file = st.file_uploader("📷 Sube una imagen para analizar", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("Vista previa de la imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Opción para contexto adicional
show_details = st.toggle(" Añadir detalles o contexto histórico", value=False)
additional_details = ""
if show_details:
    additional_details = st.text_area(
        "Describe la imagen o añade información sobre su procedencia:",
        placeholder="Ejemplo: Esta pintura fue encontrada en una galería abandonada en París...",
        disabled=not show_details
    )

# Botón de análisis
analyze_button = st.button("🔍 Analizar como Curador de Arte")

# Análisis
if uploaded_file is not None and api_key and analyze_button:
    with st.spinner("Analizando obra... 🧠🎨"):
        base64_image = encode_image(uploaded_file)
        
        prompt_text = (
            "Eres un curador experto del Museo del Arte Perdido. "
            "Analiza la imagen y ofrece una descripción detallada y poética en español. "
            "Incluye su posible época, estilo artístico, materiales, significado simbólico y emoción transmitida."
        )

        if show_details and additional_details:
            prompt_text += f"\n\nContexto adicional proporcionado por el usuario:\n{additional_details}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ],
            }
        ]

        try:
            full_response = ""
            message_placeholder = st.empty()

            for completion in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000,
                stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown("###  Análisis del Curador:\n" + full_response)

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
else:
    if not uploaded_file and analyze_button:
        st.warning("Por favor sube una imagen antes de analizar.")
    if not api_key:
        st.warning("Por favor ingresa tu clave de API.")
