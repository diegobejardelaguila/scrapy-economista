from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('yourbrother-app-93a4561dc72e.json', scope)
client = gspread.authorize(creds)


# Abrir la hoja de cálculo por su ID y seleccionar la hoja de trabajo
spreadsheet_id = '1T0xgH2KSOULfgOm1KUtkF2YwPoWj-xhp1Pd2JWFKUmw'
sheet_name = 'lista'
sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)


# Obtener las cabeceras (encabezados de columna)
headers = sheet.row_values(1)  # La primera fila contiene las cabeceras
print("Cabeceras:", headers)

service = ChromeService()
driver = webdriver.Chrome(service=service)

url = "https://empresite.eleconomista.es/Actividad/FABRICA-TEXTIL/provincia/BARCELONA/"
driver.get(url)

# Esperar hasta que el elemento deseado esté presente (timeout de 10 segundos)
wait = WebDriverWait(driver, 10)
try:
    cookies_modal = wait.until(EC.presence_of_element_located((By.ID, 'didomi-notice-agree-button')))
    # Cerrar el modal de cookies
    driver.execute_script("arguments[0].click()", cookies_modal)
except:
    pass  # El modal de cookies no apareció o ya fue cerrado


page_count = 4



while page_count <= 40:
    print(page_count)
    url_paginator = f"{url}PgNum-{page_count}/"
    driver.get(url_paginator)

    wait = WebDriverWait(driver, 10)
    elementos_li = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'resultado_pagina')))


    # Iterar a través de los elementos li
    for elemento_li in elementos_li:
        direccion_formateada = ""
        correo_electronico = ""
        numero_telefono = ""
        nombre_empresa = ""
        
        # Obtener el nombre de la empresa
        nombre_empresa = elemento_li.find_element(By.CLASS_NAME, "title03").text

        boton_ver_empresa = elemento_li.find_element(By.XPATH, ".//button[contains(text(), 'Ver empresa')]")
        link = boton_ver_empresa.get_attribute("onclick")
        # Extraer la parte del enlace desde el atributo onclick
        url_part = link.split("'")[1]
        url_completa = f"https://empresite.eleconomista.es/{url_part}"
        print(url_completa)

        driver.execute_script("window.open('{}', '_blank');".format(url_completa))

        # Cambiar a la nueva pestaña
        ventanas = driver.window_handles
        driver.switch_to.window(ventanas[1])  # Cambiar a la segunda pestaña (índice 1)

        try:
    
            wait_direccion = WebDriverWait(driver, 10)
            elemento_direccion = wait_direccion.until(EC.presence_of_element_located((By.XPATH, "//span[@id='situation'][1]")))
            # Obtener los elementos de la dirección individualmente
            pais = elemento_direccion.find_element(By.CLASS_NAME, "country-name").text
            calle = elemento_direccion.find_element(By.CLASS_NAME, "street-address").text
            localidad = elemento_direccion.find_element(By.CLASS_NAME, "locality").text
            codigo_postal = elemento_direccion.find_element(By.CLASS_NAME, "postal-code").text
            region = elemento_direccion.find_element(By.CLASS_NAME, "region").text

            # Formatear la dirección según el formato deseado
            direccion_formateada = f"{calle}, {localidad}, {codigo_postal}, {region}, {pais}"
            print("Dirección:", direccion_formateada)

            # Realizar operaciones adicionales si es necesario

        except Exception as e_direccion:
            print("Error al obtener la dirección:")


        try:
            # Esperar hasta que el elemento <a> con el correo electrónico esté visible
            wait = WebDriverWait(driver, 10)
            elemento_email = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'mailto:')]/span[@class='email']")))
            correo_electronico = elemento_email.text
            print("Correo electrónico:", correo_electronico)

        except Exception as e:
            print("Error en la empresa - No se pudo obtener correo:")

        try:
            # Buscar el elemento <span> con el número de teléfono
            elemento_tel = driver.find_element(By.XPATH, "//span[@class='tel']")
            numero_telefono = elemento_tel.text
            print("Número de teléfono:", numero_telefono)

            # Realizar operaciones adicionales si es necesario

        except Exception as e:
            print("Error en la empresa - No se pudo obtener teléfono:")

        finally:
            # Insertar la información en la hoja de cálculo
            fila = [nombre_empresa, direccion_formateada, correo_electronico, numero_telefono]
            sheet.append_row(fila)

            # Cerrar la pestaña actual
            driver.close()

            # Cambiar de nuevo a la primera pestaña
            driver.switch_to.window(ventanas[0])
    page_count += 1

# Cerrar el navegador al final del bucle
driver.quit()
