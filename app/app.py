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

with st.sidebar: #Texto Acerca de que aparece en la barra desplegable del lado izquierdo
    st.title('Acerca de')
    st.write("""<div style='text-align: justify; text-justify: inter-word; text-align-last: center;'>Doc GPT es tu compañero 
    médico en línea. 
    Nuestro chatbot basado en 
    inteligencia artificial está 
    aquí para brindarte respuestas
    rápidas y confiables a tus 
    preguntas médicas. Aunque no 
    sustituye una consulta médica 
    personalizada, DocGPT cuenta
    con una amplia base de 
    conocimientos 
    actualizada en medicina.  
    Únete a DocGPT y obtén 
    respuestas médicas
    instantáneas. 
    ¡Te acompañamos en el 
    camino hacia la buena salud!</div>""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Subir archivo", accept_multiple_files=False) #Opción para subir mas de un archivo
    if uploaded_file != None:
        st.write("filename:", uploaded_file.name)

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
seguimiento a pacientes con diversas enfermedades, dependiendo de lo que el usuario proporcione como contexto

Para responder las preguntas del usuario utilizar la siguiente información: {langchain_pdf_reader(uploaded_file.name)[0]}

Si el usuario realiza una búsqueda sobre algo diferente a Tamizaje, Diagnóstico o Tratamiento de 
la enfermedad, considere de una manera amable indicarle al usuario que sus funciones son enfocadas
en alguna de las tres categorías mencionadas anteriormente. Responda al usuario amablemente.

"""

if "messages" not in st.session_state: #Si no hay historial de mensajes muestra "¿En que puedo ayudarte?"
    st.session_state["messages"] = [{"role": "assistant", "content": "¿Qué tal, en que puedo ayudarte? Recuerda subir el archivo que gustes que analice :smile:"}]

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