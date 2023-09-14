import os
import openai
import streamlit as st
import base64
from langchain_reader import langchain_pdf_reader
from dotenv import load_dotenv, find_dotenv
from openai_response import get_completion_from_messages

st.title("ASISTENTE MÉDICO :robot_face::medical_symbol:")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)


_ = load_dotenv(find_dotenv())
openai.api_key = os.environ["OPENAI_API_KEY"]

delimitador = "####"

system_message = f"""

Eres un asistente médico especializado creado para proporcionar información relevante.
considerando ciertos archivos que el usuario cargará como su contexto.
El usuario es médico, le preguntará sobre la enfermedad proporcionada ya que su contexto puede variar.
Como si fueras un médico especialista basado en guías clínicas,
Tendrás una conversación con un especialista de la salud.
Las búsquedas del usuario serán delimitadas con cuatro hashtags, i.e. {delimitador}.

Las búsquedas del usuario serán respecto al enfoque de alguna o todas de 
las siguientes categorías: Tamizaje, Diagnóstico y Tratamiento.
Estas categorías sirven como guía clínica para el usuario al momento de dar 
seguimiento a pacientes, en este caso particular a pacientes con diabetes mellitus.

Para responder las preguntas del usuario utilizar la siguiente información: {langchain_pdf_reader("GPC_DM.pdf")[0]}

Si el usuario realiza una búsqueda sobre algo diferente a Tamizaje, Diagnóstico o Tratamiento de 
la enfermedad, considere de una manera amable indicarle al usuario que sus funciones son enfocadas
en alguna de las tres categorías mencionadas anteriormente. Responda al usuario amablemente.

"""


if "messages" not in st.session_state: #Si no hay historial de mensajes muestra "¿En que puedo ayudarte?"
    st.session_state["messages"] = [{"role": "assistant", "content": "¿Qué tal, en que puedo ayudarte? :smile:"}]

for msg in st.session_state.messages: 
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(): #Asigna el input del usuario en la pagina a la variable prompt
    if not openai.api_key: #Si no detecta la api envía:
        st.info("Actualmente no se encuentra conectada la API de GPT")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt}) #Agrega el prompt al historial "messages"
    st.chat_message("user").write(prompt) #Muestra el prompt en la pagina para mostrar lo que el usuario preguntó
    

    mensaje_usuario = prompt
    messages =  [  
    {'role':'system', 
    'content':system_message},    
    {'role':'user', 
    'content': f"{delimitador}{mensaje_usuario}{delimitador}"},  
    ] 
    response = get_completion_from_messages(messages)
    try:
        final_response = response.split(delimitador)[-1].strip()
    except Exception as e:
        final_response = "Lo siento, tengo problemas en este momento, intente hacer otra pregunta."
    
    msg = response
    st.session_state.messages.append(msg) #Agrega el mensaje de gpt al historial 
    st.chat_message("assistant").write(msg.content) #Muestra el mensaje de gpt en la página 