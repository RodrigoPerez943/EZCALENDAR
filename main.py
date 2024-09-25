import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from calendar import monthrange
import datetime

indice = 0
indices = []

def solicitar_fechas_eventos():

    global indice
    global indices
    fechas_str = input("Enter the event dates in DD-MM-YYYY format, separated by commas. The format is as follows: 30-5-2024 COTE, 31-5-2024 SDG2, 4-6-2024 CORE ... \n")
    partes = fechas_str.split(" , ")
    colores = ["darkgoldenrod", "darkgreen", "deepskyblue", "fuchsia" , "crimson" , "darkslategray", "forestgreen" , "indigo" , "lightcoral" , "lightskyblue" , "darkgoldenrod", "darkgreen", "deepskyblue", "fuchsia" , "crimson" , "darkslategray", "forestgreen" , "indigo" , "lightcoral" , "lightskyblue"]
    fechas = []
    asignaturas = [] 
    eventos = []

    for parte in partes:
        fecha, asignatura = parte.split(" ")
        fechas.append(fecha)
        asignaturas.append(asignatura)

    for i, fecha_str in enumerate(fechas):
        indice += 1
        indices.append(indice)
        fecha = datetime.datetime.strptime(fecha_str.strip(), "%d-%m-%Y")
        dias_restantes = (datetime.date(fecha.year,fecha.month,fecha.day) - datetime.date.today()).days
        mes_actual = datetime.date.today().month
        dia_actual = datetime.date.today().day

        evento_existente = None

        for a in range(dias_restantes):
            if (dia_actual + 1 <= monthrange(datetime.date.today().year , mes_actual)[1] ):
                dia_actual += 1
            else:
                mes_actual += 1
                dia_actual = 1

            for evento in eventos:
                if evento["dia_del_mes_actual"] == dia_actual and evento["mes"] == mes_actual:
                    evento_existente = evento
                    break

            if evento_existente:
                    evento_existente[f"dia_del_mes_objetivo{indice}"]=fecha.day
                    evento_existente[f"color{indice}"]= colores[i]
                    evento_existente[f"objetivo{indice}"]= asignaturas[i]  + "," + colores[i] + "," + str(dias_restantes - a - 1)
                    evento_existente[f"dias_restantes{indice}"]= dias_restantes - a - 1
                    evento_existente = None
                    continue
            
            nuevo_evento = {
                "dia_del_mes_actual": dia_actual,
                f"dia_del_mes_objetivo{indice}": fecha.day,
                "mes": mes_actual,
                f"objetivo{indice}": asignaturas[i] + "," + colores[i] + "," + str(dias_restantes - a - 1),
                f"dias_restantes{indice}": dias_restantes - a - 1,
                f"color{indice}": colores[i],
                "id": i
            }
            eventos.append(nuevo_evento)
            evento_existente = None

    return eventos

def crear_archivo_json(eventos, nombre_archivo="eventos.json"):
    with open(nombre_archivo, "w") as archivo:
        json.dump(eventos, archivo, indent=4)

eventos = solicitar_fechas_eventos()

def generar_calendario_pdf(eventos, nombre_archivo_pdf="calendario.pdf"):

    global indices
    global indice
    margen_izquierdo = 30
    margen_derecho = 30
    margen_superior = 10
    margen_inferior = 30
    ancho_pagina, alto_pagina = A4
    ancho_util = ancho_pagina - margen_izquierdo - margen_derecho
    alto_util = alto_pagina - margen_superior - margen_inferior
    cell_width = ancho_util / 7

    primer_dia_semana =  datetime.date(2024, eventos[0]["mes"], eventos[0]["dia_del_mes_actual"]).weekday()

    eventos_por_semana = []
    dias_vacios = [{'dia_del_mes_actual': '', 'color': ''}] * primer_dia_semana
    dias_completar_semana = 6 - datetime.date(2024, eventos[-1]["mes"], eventos[-1]["dia_del_mes_actual"]).weekday()
    dias_continuacion = [{'dia_del_mes_actual': '', 'color': ''}]*dias_completar_semana
    eventos_con_dias_vacios = dias_vacios + eventos + dias_continuacion

    for i in range(0, len(eventos_con_dias_vacios), 7):
        eventos_por_semana.append(eventos_con_dias_vacios[i:i+7])

    cell_height = 40 + 12*indice

    altura_total = (len(eventos_por_semana)+1)*cell_height + 20 + 40
    c = canvas.Canvas(nombre_archivo_pdf, pagesize=(ancho_pagina , altura_total))
    c.setFont("Helvetica", 10)

    for semana_index, semana in enumerate(eventos_por_semana):
        for dia_index, evento in enumerate(semana):
            x = margen_izquierdo + dia_index * cell_width
            y = altura_total - margen_superior - (semana_index + 1) * cell_height

            if semana_index == 0:
                c.setFillColor(colors.black)
                c.rect(x, y, cell_width, 20, fill=1)
                c.setFillColor(colors.white)
                dia_semana = ["L", "M", "X", "J", "V", "S", "D"][dia_index]
                c.drawString(x + (cell_width - c.stringWidth(dia_semana))/2, y + 7 , dia_semana)

            c.setFillColor(colors.black)
            c.rect(x, y - cell_height, cell_width, cell_height, stroke=1, fill=0)

            if evento['dia_del_mes_actual']:
                desfaseY = 0
                auxAsignatura = ""
                auxColor = ""
                numeroasgnaturas = 0
                casoEspecial = 5

                for etiqueta in evento:
                    if etiqueta.startswith("objetivo"):
                        asignatura, color , diasrest = evento[etiqueta].split(",")

                        if diasrest == "0":
                            numeroasgnaturas += 1
                            auxAsignatura , auxColor = auxAsignatura + " - " + asignatura , color
                            continue

                        c.setFillColor(color)
                        c.drawString(x + 5, y - 40 - desfaseY, asignatura)
                        desfaseX = c.stringWidth(asignatura)
                        c.setFillColor(colors.black)
                        c.drawString(x + 5 + desfaseX, y - 40 - desfaseY, " - " + diasrest)
                        desfaseY += 12

                if auxColor != "":
                    c.setFillColor(auxColor)
                
                if numeroasgnaturas == 0 or numeroasgnaturas == 1:
                    numeroasgnaturas = 1
                    casoEspecial = 0
                    
                c.setFont("Helvetica-Bold", 12/numeroasgnaturas)   
                c.drawString(x + (cell_width - c.stringWidth(str(evento['dia_del_mes_actual']) + auxAsignatura ))/2, y - 20 + casoEspecial, str(evento['dia_del_mes_actual']) + auxAsignatura )
                c.setFont("Helvetica", 10)
                c.setFillColor(colors.black)
                auxAsignatura = ""
                auxColor = ""
    c.save()

generar_calendario_pdf(eventos)
                