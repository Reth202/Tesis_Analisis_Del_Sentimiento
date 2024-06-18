# -*- coding: utf-8 -*-
"""Entregable 2 - Integración BD- David.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rfHFUI-gT4ctRUx7N1RJGlA_UGLc0ji3
"""

!pip install streamlit -g
!pip install streamlit-lottie
!pip install Pillow
!pip install gradio
!pip install git+https://github.com/openai/whisper.git
!sudo apt update && sudo apt install ffmpeg
!pip install numpy pandas scikit-learn tensorflow
!pip install librosa
!pip install opensmile
!pip install soundfile
!apt-get install portaudio19-dev
!pip install pyaudio
!pip install resampy
!pip install oracledb

username = "USER_PROYFINAL"
dsn = "dbproyfinal_high"
pw = "UserProyFinal#40_24"
wallet_pw="^&$#7aBcdeFgHiJkLmNpQrStUvWxYz@!%"

from google.colab import drive
drive.mount('/content/drive')

import librosa
from librosa import display

import os
import glob
import pandas as pd
import numpy as np
import subprocess

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig, pipeline
from scipy.special import softmax

import gradio as gr
import whisper
from whisper import load_model
import shutil

from datetime import datetime
import oracledb

!pip install gdown

# Importar la librería necesaria
import gdown

folder_id = '1nWiIFMAw3MpfI5cVSCkvbuW-CNSYbFp9'

# URL para descargar el contenido de la carpeta pública
url = f"https://drive.google.com/drive/folders/{folder_id}"

# Montar el Google Drive (enlace a tu propio Google Drive)
drive.mount('/content/drive')

!gdown --folder https://drive.google.com/drive/folders/1nWiIFMAw3MpfI5cVSCkvbuW-CNSYbFp9?usp=sharing

#gdown.download_folder("https://drive.google.com/drive/folders/1nWiIFMAw3MpfI5cVSCkvbuW-CNSYbFp9?usp=sharing", output="./carpeta_publica", quiet=False, use_cookies=False)

#!chmod +x /content/drive/folders/1nWiIFMAw3MpfI5cVSCkvbuW-CNSYbFp9/Codigo/ColabVersiones/opensmile-3.0.2-linux-x86_64/bin/SMILExtract
#!chmod +r "/content/drive/folders/1nWiIFMAw3MpfI5cVSCkvbuW-CNSYbFp9/Codigo/ColabVersiones/opensmile-3.0.2-linux-x86_64/config/is09-13/IS09_emotion.conf"2

##Cierra la conexion de la base de datos
#conn.close()

def write_db(pfile_name, pupload_date, pfile_size, pclient, pcalldate, pparticipants,  pemployee, pai_value):
    ##Instrucciones para consultar datos de la tabla prueba2
    try:
        insert_datos = '''insert into analisis_sentimientos(file_name,
        upload_date,
        file_size,
        client,
        calldate,
        participants,
        employee,
        ai_value)
        values(:tagfile_name, :tagupload_date, :tagfile_size, :tagclient, :tagcalldate, :tagparticipants,  :tagemployee, :tagai_value)'''
        cur_01.execute(insert_datos,tagfile_name=pfile_name, tagupload_date=pupload_date, tagfile_size=pfile_size, tagclient=pclient, tagcalldate=pcalldate, tagparticipants=pparticipants,  tagemployee=pemployee,tagai_value=pai_value)
    except Exception as err:
        print("Error insertando datos",err)
    else:
        print("Datos insertados correctamente")
        conn.commit()

# Modelo y Tokenizer
MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

def analisis_sentimiento_voz(audio):
    # Convertir el archivo de audio cargado a una ruta utilizable
    audio_path = audio.name
    return "audio"


# Función para escribir el texto del audio
def speech_to_text(audio, company, employee, calldate, participants):
  try:
    model = whisper.load_model("base")
    result = model.transcribe(audio)
    texto = result["text"]
    # Ruta destino del archivo en la carpeta deseada
    dest_path = os.path.join(os.path.basename(audio))
    shutil.move(audio, dest_path)
    AudiosinExtension = os.path.splitext(dest_path)[0]

    file = open(AudiosinExtension+".txt", "w")
    file.write(texto)
    file.close()

    AnalisisSentimientoTexto = analisis_sentimiento_texto(texto, company, employee, calldate, participants)
    #AnalisisSentimientoVoz = analisis_sentimiento_voz(audio)

    return AnalisisSentimientoTexto
  except Exception as e:
    print(f"Error: {e}")
    return f"Se produjo un error: {e}"

def analisis_sentimiento_texto(text, company, employee, calldate, participants):
  text = preprocess(text)
  encoded_input = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
  output = model(**encoded_input)
  scores = output.logits[0].detach().numpy()
  scores = softmax(scores)
  ranking = np.argsort(scores)[::-1]
  labels_scores = []
  for i in range(scores.shape[0]):
    label = config.id2label[ranking[i]]
    score = scores[ranking[i]]
    labels_scores.append(f"{label}: {np.round(float(score), 4)}")
  return "\n".join(labels_scores)

def analisis_sentimiento_texto_DANIELA(text, company, employee, calldate, participants):
  # se separa el texto por lineas para hacer la separación
  lineas = text.split('\n')
  # Lista para almacenar las líneas del cliente
  lineas_cliente = []

  # Variable para indicar si estamos dentro de un diálogo del cliente
  es_dialogo = False

  # Itera sobre las líneas del archivo
  for linea in lineas:
      if es_dialogo and linea != "":
          lineas_cliente.append(linea.strip())

      # Verifica si la línea actual es dicha por el cliente
      if linea.startswith(employee):
          es_dialogo = True
      elif linea == '':
          es_dialogo = False

  # Imprimir el contenido en bloques de 15 líneas
  bloque_size = 15
  total_lineas = len(lineas_cliente)
  valores = []
  for i in range(0, total_lineas, bloque_size):
    parrafo = ''
    bloque = lineas_cliente[i:i + bloque_size]
    for linea in bloque:
        parrafo = parrafo + ' ' + linea.strip()
    neg, neu, pos = analizar(parrafo)
    valores.append([neg, neu, pos])

  pneg, pneu, ppos = np.mean(valores, axis=0)
  satisfaccion = clasificar_satisfaccion(pneg, pneu, ppos)
  return satisfaccion

def analizar(texto):
  # creación del pipeline cargando el modelo preentrenado
  pipe = pipeline(
      model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
      top_k=None)
  # obtención de la predicción
  evaluacion = pipe(texto)[0]

  # procesamiento de la respuesta del modelo
  if evaluacion[0]['label']=='negative': neg = evaluacion[0]['score']
  elif evaluacion[0]['label']=='positive': pos = evaluacion[0]['score']
  else: neu = evaluacion[0]['score']

  if evaluacion[1]['label']=='negative': neg = evaluacion[1]['score']
  elif evaluacion[1]['label']=='positive': pos = evaluacion[1]['score']
  else: neu = evaluacion[1]['score']

  if evaluacion[2]['label']=='negative': neg = evaluacion[2]['score']
  elif evaluacion[2]['label']=='positive': pos = evaluacion[2]['score']
  else: neu = evaluacion[2]['score']

  return (neg, neu, pos)

# Definir los límites de cada categoría
def clasificar_satisfaccion(negativo, neutro, positivo):
    if positivo >= 0.8:
        return "Muy satisfecho"
    elif positivo >= 0.6:
        return "Satisfecho"
    elif neutro >= 0.4:
        return "Neutral"
    elif negativo >= 0.6:
        return "Muy insatisfecho"
    elif negativo >= 0.4:
        return "Insatisfecho"
    else:
        return "Neutral"


styles = {
     "body": {
        "background-color": "white",
        "margin": "0",
        "padding": "0",
        "height": "100vh",
        "display": "flex",
        "justify-content": "center",
        "align-items": "center"
    },
    ".gradio-container": {
        "background-color": "white",
        "width": "100%",
        "height": "100%",
        "display": "flex",
        "justify-content": "center",
        "align-items": "center"
    },
    ".lg.primary.svelte-cmf5ev": {
        "background-color": "#5AAAF0",
        "color": "white",
        "font-size": "16px",
        "border-radius": "125px",
        "margin": "0px 10px"
    },
     ".lg.secondary.svelte-cmf5ev": {
        "background-color": "#B5B7CF",
        "color": "white",
        "font-weight": "bold",
        "font-size": "16px",
        "padding": "10px 20px",
        "border-radius": "125px",
        "margin": "20px 10px"
     },
    ".svelte-1bvc1p0 th": {
        "background-color": "#5AAAF0",
        "color": "white",
        "font-weight": "bold",
        "font-size": "14px",
        "border": "1px solid #ddd",
        "text-align": "center"
    },
    ".svelte-1bvc1p0 td": {
        "background-color": "white",
        "color": "black",
        "border": "1px solid #ddd",
        "text-align": "center"
    },
     ".block.svelte-12cmxck": {
        "background-color": "white",
        "color": "black",
        "text-align": "center",
        "border": "1px solid white"
    },
     ".svelte-1b6s6s": {
         "display": "inline-block",
         "background-color": "white",
         "color": "black",
         "border": "1px solid black"
    },
     ".svelte-j5bxrl": {
         "color": "#B5B7CF",
         "background-color": "#B5B7CF",
         "border": "1px solid black"
    },
     ".svelte-j5bxrl svg": {
         "color": "#B5B7CF",
         "margin-right": "10px"
    },
     ".wrap": {
        "color": "black"
    },
     ".or": {
         "color": "black"
    },
     ".svelte-1gfkn6j": {
         "color": "black"
    },
     ".svelte-sa48pu.stretch":{
         "background-color": "white",
         "border": "1px solid white",
         "align-items": "center",
         "justify-content": "center"
    },
     ".svelte-iyf88w": {
         "border": "1px solid white"
    },
     ".svelte-1f354aw textarea": {
         "border": "1px solid black",
         "background-color": "#B5B7CF",
         "font-weight": "bold",
         "color": "black"
    },
     ".svelte-vt1mxs": {
         "padding": "0"
    },
     "#component-231": {
         "margin-top": "10px"
    },
     ".svelte-vt1mxs gap": {
         "padding": "0"
     }
}


css_styles = "\n".join([f"{selector} {{{' '.join([f'{prop}: {value};' for prop, value in props.items()])}}}" for selector, props in styles.items()])

with gr.Blocks(css=css_styles, theme=gr.themes.Monochrome()) as webpage:
    markdown_text = """
                  <div style='text-align: center; font-size: 36px; color: Black'; font-weight: bold>
                  Calls Sentiment Analysis
                  </div>
                  """
    gr.Markdown(markdown_text)

    #Crear boton cargar archivo, buscar y tabla de resultados
    new_text_file_button = gr.Button("Upload .txt or .wav file", variant="primary")

    # Create the components for the text file
    upload_text = gr.Group(visible=False)

    # Funcion que se ejecuta al cargar un archivo
    def on_upload_submit(file, company, employee, calldate, participants):
      # Verificar que se haya subido un archivo
      if file:
        # Verificar si el archivo es un texto
        if ((file.name).find('.txt') != -1):
          with open(file.name, 'r') as f:
            content = f.read()
          valor = analisis_sentimiento_texto_DANIELA(content, company, employee, calldate, participants)
          write_db(pfile_name=file.name, pupload_date=datetime.now().date(), pfile_size=100, pclient=company, pcalldate=calldate, pparticipants=int(participants),  pemployee=employee, pai_value=valor)
          return valor
        # Verificar si el archivo es un audio
        elif ((file.name).find('.wav') != -1):
          audio_a_texto = speech_to_text(file, company, employee, calldate, participants)
          write_db(pfile_name=file.name, pupload_date=datetime.now().date(), pfile_size=100, pclient=company, pcalldate=calldate, pparticipants=int(participants),  pemployee=employee, pai_value=audio_a_texto)
          return audio_a_texto
        else:
          return "El archivo cargado no tiene formato .txt o .wav."
      else:
        return "No se ha seleccionado ningún archivo."

    with upload_text:
        with gr.Row():
            file_input = gr.File(label="Select a File", file_count="single", file_types=[".txt", ".wav" ], interactive=True)
            with gr.Row():
                company_input = gr.Textbox(label="Client")
                employee_input = gr.Textbox(label="Employee")
            with gr.Row():
                calldate_input = gr.Textbox(label="Call date (YYYY-MM-DD)")
                participants_input = gr.Textbox(label="Participants")
            with gr.Row():
                close_button = gr.Button("Close", variant="secondary")
                upload_text_button = gr.Button("Upload", variant="primary")

            upload_text_button.click(on_upload_submit, inputs=[file_input, company_input, employee_input, calldate_input, participants_input], outputs=[gr.Textbox(label="Sentiment Analysis", lines=10)])
            #add_table_data = {"Date uploaded":now.date(), "File Name": file.name, "Size": file.size, "Call Date": calldate, "Employee": employee, "Company": company, "Participants": participants, "AI Value":analsis_texto}
            #file_table.add_row(add_table_data)
            close_button.click(lambda: gr.update(visible=False), inputs=[], outputs=[upload_text])

    new_text_file_button.click(lambda: gr.update(visible=True), inputs=[], outputs=[upload_text])

    file_table = gr.Dataframe(headers=["Date uploaded", "File Name", "Size", "Call Date", "Employee", "Company", "Participants", "AI Value"],
                              datatype=["date", "str", "number", "date", "str", "str", "number", "str"],
                              row_count=1)

webpage.launch()