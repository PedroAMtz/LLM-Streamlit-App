import os
import openai
import streamlit as st
import base64
from langchain_reader import langchain_pdf_reader
from dotenv import load_dotenv, find_dotenv
from openai_response import get_completion_from_messages

st.title("ASISTENTE PROPIEDAD INTELECTUAL :robot_face:")

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
    st.write("""<div style='text-align: justify; text-justify: inter-word; text-align-last: center;'>
            Bot asistente en tareas de propiedad intelectual, información sobre patentes
            y conceptos relacionados</div>""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Subir archivo", accept_multiple_files=False) #Opción para subir mas de un archivo
    if uploaded_file != None:
        st.write("filename:", uploaded_file.name)

        system_message = f"""

La Academia de la OMPI es el centro de excelencia en el ámbito de la enseñanza, la formación y el fortalecimiento de capacidades 
en propiedad intelectual (PI) para los Estados miembros de la OMPI, y, en particular, los países en desarrollo, 
los países menos adelantados (PMA) y los países en transición.
La Academia contribuye a crear capacidad humana en materia de PI, que es fundamental para la innovación y la creatividad.
Considerando lo anterior, tu trabajo es ser un asistente virtual enriquecido con información de la OMPI
y la gran mayortía de los proceses que esta organización lleva a cabo, por lo tanto asistiras al usuario 
que usualmente tendrá preguntas respecto a algun concepto relacionado con las actividades de la OMPI
por lo que responderas amablemente y de la mejor manera posible.
Las búsquedas del usuario serán delimitadas con cuatro hashtags i.e. {delimitador}.

Las búsquedas del usuario serán respecto a algún tema en particular que trate la OMPI, como la propiedad intelectual,
derechos de autor, fechas importantes, tratados y entre otros tipos de información a solicitar. 

Para responder las preguntas del usuario es vital utilizar la siguiente información, ya que proporciona un
amplio panorama para las preguntas que pueda tener el usuario, esta es una guía completa de uno
de los cursos de la OMPI por lo que con esto debería ser más que suficiente para contestar: {langchain_pdf_reader(uploaded_file.name)[0]}

Si el usuario realiza una búsqueda sobre algo diferente a alguno de los temas tratados por la OMPI, 
considere de una manera amable indicarle al usuario que sus funciones son enfocadas
en información relevante de las actividades la OMPI. Responda al usuario amablemente.

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