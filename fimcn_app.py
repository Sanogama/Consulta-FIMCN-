import streamlit as st
import csv
import re
from collections import defaultdict

st.title("📄 Consulta FIMCN")


def limpiar_valor(v):
    if isinstance(v, list):
        return ", ".join(v)
    if isinstance(v, str):
        return v.strip()
    return ""


def procesar_hojas_conteo(texto):
    """
    Convierte:
    '4 (2), 7, 8, 4 (3)'
    en:
    { '4': 5, '7': 1, '8': 1 }
    """
    conteo = defaultdict(int)

    if not texto:
        return conteo

    # Detectar patrones tipo "4 (2)"
    patrones = re.findall(r"(\d+)\s*\((\d+)\)", texto)

    usados = []

    for num, rep in patrones:
        conteo[num] += int(rep)
        usados.append(f"{num} ({rep})")

    # Quitar los ya procesados
    texto_restante = texto
    for u in usados:
        texto_restante = texto_restante.replace(u, "")

    # Detectar números normales
    numeros = re.findall(r"\d+", texto_restante)

    for n in numeros:
        conteo[n] += 1

    return conteo


def cargar_datos():
    datos_temp = defaultdict(lambda: {"nombre": "", "registros": []})

    try:
        with open("Nomina.csv", newline="", encoding="utf-8-sig") as archivo:
            lector = csv.DictReader(archivo)

            lector.fieldnames = [
                campo.strip() if campo else "" for campo in lector.fieldnames
            ]

            for fila in lector:
                fila = {
                    (k.strip() if k else ""): limpiar_valor(v)
                    for k, v in fila.items()
                }

                num_per = fila.get("Num. Per", "").strip()
                nombre = fila.get("Nombre", "").strip()
                fecha = fila.get("Fecha", "").strip()
                num_hojas = fila.get("Núm hojas", "").strip()

                if not num_per or not fecha:
                    continue

                if nombre:
                    datos_temp[num_per]["nombre"] = nombre

                datos_temp[num_per]["registros"].append({
                    "fecha": fecha,
                    "num_hojas": num_hojas
                })

        # 🔥 PROCESAR POR PERSONA
        datos_final = {}

        for num_per, info in datos_temp.items():
            fechas_dict = defaultdict(lambda: defaultdict(int))

            for reg in info["registros"]:
                fecha = reg["fecha"]
                hojas = reg["num_hojas"]

                conteo = procesar_hojas_conteo(hojas)

                for hoja, cantidad in conteo.items():
                    fechas_dict[fecha][hoja] += cantidad

            registros_finales = []

            for fecha, hojas_dict in fechas_dict.items():
                resultado = []

                for hoja in sorted(hojas_dict.keys(), key=int):
                    cantidad = hojas_dict[hoja]

                    if cantidad > 1:
                        resultado.append(f"{hoja} ({cantidad})")
                    else:
                        resultado.append(hoja)

                registros_finales.append({
                    "fecha": fecha,
                    "num_hojas": ", ".join(resultado)
                })

            datos_final[num_per] = {
                "nombre": info["nombre"],
                "registros": registros_finales
            }

    except FileNotFoundError:
        st.error("No se encontró el archivo Nomina.csv")
        return {}

    return datos_final


# 🚀 APP
datos = cargar_datos()

if datos:
    num_buscar = st.text_input("Ingresa el Número de Personal")

    if num_buscar:
        num_buscar = num_buscar.strip()

        if num_buscar in datos:
            st.success("Resultado encontrado")

            st.write("**Número de Personal:**", num_buscar)

            if datos[num_buscar]["nombre"]:
                st.write("**Nombre:**", datos[num_buscar]["nombre"])

            st.write("**Fechas en las que aparece:**")

            for registro in datos[num_buscar]["registros"]:
                texto = f"- {registro['fecha']}"
                if registro["num_hojas"]:
                    texto += f" | Núm hojas: {registro['num_hojas']}"
                st.write(texto)

        else:
            st.error("Ese número de personal no existe.")
