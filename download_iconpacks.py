import requests
import re
import zipfile
import os
import shutil
import aiohttp
import asyncio
import time
import shutil
from io import BytesIO
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm.asyncio import tqdm
from tqdm import tqdm

def colored_text(text, color_code = 31):
    return f"\033[{color_code}m{text}\033[0m"

def get_terminal_dimensions(align = False):
    terminal_size = shutil.get_terminal_size()
    terminal_width = terminal_size.columns
    terminal_height = terminal_size.lines
    return [terminal_width if not align else terminal_width-8, terminal_height]

cancel_first_line = f' | Escribe "{colored_text("X", 32)}" para terminar Script'
created_by = f' Creado por {colored_text('KilzaNiko', 36)} - IconPack Downloader {colored_text("v1.0.2", 35)} - Pagina: {colored_text("icon-icons.com", 32)}'.center(get_terminal_dimensions()[0] + 9, " ")
created_by_line = (colored_text("-", 36) * (len(created_by) - 9)).center(get_terminal_dimensions()[0], " ")
first_line = ""
divisor = ""
pack_name = ""
cancel_script = False
data_icons_task = None
all_pages = True

#helper de get_data_icon_pack()
def extract_icon_data(href, src):
    # Extraer icon_id del href
    match_href = re.search(r'/[^/]+/([^/]+)/(\d+)$', href)
    if match_href:
        icon_id = match_href.group(2)
    else:
        icon_id = None

    # Extraer icon_pack_id y el nombre del icono del src
    match_src = re.search(r'/(\d+)/[^/]+/[^/]+/([^/]+)\.\w+$', src)
    if match_src:
        icon_pack_id = match_src.group(1)
        icon_name = match_src.group(2)
    else:
        icon_pack_id = None
        icon_name = None

    # Combinar datos en un diccionario
    data = {
        'icon_pack_id': icon_pack_id,
        'icon_id': icon_id,
        'icon_name': icon_name
    }
    return data

# Obtener nombre del pack
def get_pack_name(pack_url):
    match = re.search(r'/pack/([^/]+)/(\d+)', pack_url)
    pack_name = match.group(1).replace("-", " ") if match else "Unknown Pack"
    return pack_name

################### 1. Obtener datos del Pack  #######################################

def parse_page_input(input_str, max_pages):
    page_set = set()
    ranges = input_str.split(',')
    for r in ranges:
        if '-' in r:
            start, end = map(int, r.split('-'))
            if start > end or start < 1 or end > max_pages:
                raise ValueError("Rango de paginas fuera del rango")
            page_set.update(range(start, end + 1))
        else:
            page = int(r)
            if page < 1 or page > max_pages:
                raise ValueError("Paginas fuera del rango")
            page_set.add(page)
    return sorted(page_set)

async def get_data_icon_pack(pack_url):
    global first_line; global divisor; global pack_name; global all_pages
    data_icons_pack = []
    try_a = False
    
    # Verificar y obtener las URLs de las páginas
    pack_url = await get_url_pages(pack_url)

    urls_a_procesar = []  # Inicializar urls_a_procesar

    clear_console(); 
    print(created_by); print(created_by_line); print(first_line)
    divisor = "-" * (len(first_line)-(9*3)); print(divisor)
    
    if len(pack_url) > 1:
        while True:
            if try_a == True : print(colored_text("[ Opcion inválida]"))
            t_spaginas = f"Se encontraron {len(pack_url)} páginas, elija una opción:"; print(t_spaginas)

            op = [f"{colored_text("1", 32)}. Descargar iconos de todas las páginas",
                  f"{colored_text("2", 32)}. Descargar iconos de páginas específicas",
                  f"{colored_text("C", 32)}. Cambiar pack de iconos",
                  f"{colored_text("X", 32)}. Salir"]

            print(op[0]); print(op[1])
            divisor = "-" * len(t_spaginas); print(divisor)
            print(op[2]); print(op[3])

            opcion = input(f"Ingrese su opción ({colored_text("1", 32)}, {colored_text("2", 32)}, {colored_text("C", 32)} o {colored_text("X", 32)}): ")

            if opcion == 'c': return 'c'
            elif opcion == 'x':
                confirm_exit = input(colored_text("¿Estás seguro de que deseas salir? (S/N): ", 33)).lower()
                if confirm_exit == 's': 
                    clear_console()
                    return 'x'
                elif confirm_exit == 'n': 
                    clear_console(8); continue
            elif opcion not in ["1", "2"]: clear_console(7); try_a = True; continue

            if opcion == '1':
                if try_a: clear_console(8); try_a = False
                elif not try_a: clear_console(7)
                urls_a_procesar = pack_url
                break
            elif opcion == '2':
                if try_a: clear_console(8); try_a = False
                elif not try_a: clear_console(7)
                err = 3
                valid_pages = False
                
                while True:
                    try:
                        max_paginas = len(pack_url)
                        print(f'"{colored_text("C", 32)}" para volver')
                        print(f"Especifique las páginas que desea descargar (no deben ser números mayores a {colored_text(f'{str(max_paginas)} páginas', 33)})")
                        paginas_especificas = input(f'En formato Ex: {colored_text("1,3,5", 32)}, Ex: {colored_text("1-3", 32)} incluso combinarlos Ex: {colored_text("1,3,5-8", 32)}: ')

                        # Parsear la entrada para obtener una lista de páginas únicas y ordenadas
                        paginas_especificas = parse_page_input(paginas_especificas, max_paginas)

                        # Validar que las páginas especificadas están dentro del rango
                        if all(1 <= pagina <= max_paginas for pagina in paginas_especificas):
                            clear_console()
                            first_line = f"{first_line} | Paginas: {colored_text(paginas_especificas, 34)}"; print(first_line)
                            divisor = "-" * (len(first_line)-(9*4)); print(divisor)

                            urls_a_procesar = [pack_url[pagina - 1] for pagina in paginas_especificas]
                            valid_pages = True
                            all_pages = False
                            break
                        else:
                            print(colored_text(f"Algunas páginas especificadas están fuera del rango, ya que el máximo es {max_paginas}.", 33))
                    except ValueError:
                        if err == 3: clear_console(err); err = err + 2
                        else: clear_console(err)
                        if paginas_especificas == "": 
                            i_vacio = f'{colored_text("Entrada Vacia", 31)}. Asegúrese de ingresar NÚMEROS separados por comas. (Ex: 1,3,5-8)'; print(i_vacio)
                            divisor = "-" * (len(i_vacio)-9); print(divisor)
                        elif paginas_especificas.lower() == "c": break
                        else: 
                            i_invalido = f'"{colored_text(paginas_especificas, 31)}" es una entrada inválida. Asegúrese de ingresar NÚMEROS separados por comas o rangos. (Ex: 1,3,5 o 1-3)'; print(i_invalido)
                            divisor = "-" * (len(i_invalido)-9); print(divisor)
                        continue

                if valid_pages: break  # Salir del bucle externo una vez que las páginas específicas se han validado
      
    else: urls_a_procesar = pack_url

    with tqdm(total=len(urls_a_procesar), desc="Obteniendo datos de iconos") as pbar:
        # Procesar cada URL
        for url in urls_a_procesar:
            response = requests.get(url)
            if response.status_code != 200:
                pbar.update(1)
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            icons = soup.select('.icon-preview a')
            for icon in icons:
                img = icon.find('img')
                icon_src = img['src'] if img else None

                icon_data = extract_icon_data(icon['href'], icon_src)
                icon_id_link = {
                    'pack_id': icon_data['icon_pack_id'],
                    'pack_name': pack_name,
                    'icon_id': icon_data['icon_id'],
                    'icon_name': icon_data['icon_name']
                }

                data_icons_pack.append(icon_id_link)
            
            # Actualizar la barra de progreso
            pbar.update(1)
    
    return data_icons_pack

############### Obtener el numero de paginas del pack ################################
def get_max_page(soup):
    """ Extrae el número máximo de página de la navegación actual. """
    pagination = soup.find('nav', {'aria-label': 'Page navigation'})
    if not pagination:
        return 1

    links = pagination.find_all('a', href=True)
    max_page = 1

    for link in links:
        href = link['href']
        if 'page=' in href:
            match = re.search(r'page=(\d+)', href)
            if match:
                page_number = int(match.group(1))
                if page_number > max_page:
                    max_page = page_number

    # Verifica si la última página también está listada
    last_page = pagination.find('li', class_='active')
    if last_page:
        last_page_number = re.search(r'(\d+)', last_page.text)
        if last_page_number:
            max_page = max(max_page, int(last_page_number.group(1)))

    return max_page

async def fetch_page(session, url):
    async with session.get(url) as response:
        text = await response.text()
        return BeautifulSoup(text, 'html.parser')

def verify_url(url):
    # Verificar si la URL tiene el formato correcto y proviene de "icon-icons.com"
    url_pattern = re.compile(r'^(https://)?icon-icons\.com(/[^/]+)?/pack/[a-zA-Z0-9-+&]+/\d+$')

    if not url_pattern.match(url):
        return False, colored_text('La URL no tiene el formato correcto o no proviene de icon-icons.com' if not url == "" else 'No ha ingresado ningun URL', 33)

    # Ignorar caracteres especiales y caracteres no permitidos en la URL
    base_url = re.sub(r'(&page=\d+)', '', url)
    if not base_url.startswith('https://'): base_url = 'https://' + base_url
    base_url = re.sub(r'^https://www\.', 'https://', base_url)

    return True, base_url

####### Obtener las URL de las paginas ######################
async def get_url_pages(url):
    
    async with aiohttp.ClientSession() as session:
        page_urls = [url]  # Incluir solo la URL base sin el parámetro &page=1
        current_page = 2

        while True:
            current_url = f"{url}&page={current_page}"
            soup = await fetch_page(session, current_url)
            
            # Obtener el número máximo de página desde la navegación
            new_max_page = get_max_page(soup)
            
            # Verificar si hay más páginas para agregar
            if new_max_page >= current_page:
                page_urls.append(current_url)
                current_page += 1
            else:
                break

        # Añadir URLs de las páginas adicionales si no se incluye en el bucle
        for page in range(current_page, new_max_page + 1):
            page_url = f"{url}&page={page}"
            if page_url not in page_urls:
                page_urls.append(page_url)

    return page_urls

################### 2 Generar links de descargar x icono #############################
async def generate_link_download(data_icons_pack, format, resolution='512'):
    base_url = f"https://icon-icons.com/downloadimage.php?id={{icon_id}}&root={{pack_id}}/{format}/{'{resolution}/' if format != 'SVG' else ''}&file={{icon_name}}.{format.lower()}"

    icon_urls = []

    async def generate_url(item):
        url = base_url.format(
            icon_id=item['icon_id'],
            pack_id=item['pack_id'],
            format= format,
            resolution=resolution,
            icon_name=item['icon_name'].replace(' ', '_').lower()
        )
        icon_urls.append(url)
        await asyncio.sleep(0)  # Yield control to the event loop

    tasks = [generate_url(item) for item in data_icons_pack]
    
    # Utiliza tqdm.asyncio.tqdm para la barra de progreso asíncrona
    for task in tqdm(asyncio.as_completed(tasks), desc="Generando enlaces de descarga", total=len(data_icons_pack)):
        await task

    return icon_urls

################### 3 Descargar los iconos ###########################################

async def fetch_icon(session, url, resolutions, max_retries=3):
    for res in resolutions:
        retries = 0
        while retries < max_retries:
            try:
                # Construir la URL con la resolución actual
                resolution_url = url.replace('512', str(res))
                async with session.get(resolution_url) as response:
                    if response.status == 403:
                        retries += 1
                        if retries >= max_retries:
                            break
                        continue  # Reintentar con la misma resolución
                    response.raise_for_status()
                    return await response.read(), resolution_url, res
            except aiohttp.ClientError as e:
                # print(f'Error al procesar la URL del icono: {e}')
                retries += 1
                if retries >= max_retries:
                    break
    # Si ninguna resolución es válida, retorna None
    return None, url, None

async def download_icons_to_zip(icon_urls):
    global first_line; global divisor; global all_pages
    # Extraer pack_id y generar el nombre del archivo ZIP
    pack_id = re.search(r'root=(\d+)', icon_urls[0]).group(1)
    now = datetime.now()
    current_time = now.strftime('%Y-%m-%d %Hh%Mm%Ss')
    zip_filename = f'IconPack {pack_name} {pack_id} {current_time}.zip'
    
    # Crear un archivo ZIP en memoria
    zip_buffer = BytesIO()
    failed_icons = []
    resolution_changes = []

    # Obtener resoluciones disponibles para los iconos
    available_resolutions = [512, 256, 128, 64, 32, 16]  # Ejemplo de resoluciones

    async with aiohttp.ClientSession() as session:
        # Inicializar la barra de progreso
        total_icons = len(icon_urls)
        with tqdm(total=len(icon_urls), desc="Descargando iconos") as pbar:
            # Crear una lista de tareas para descargar iconos
            tasks = [fetch_icon(session, url, available_resolutions) for url in icon_urls]
            # Ejecutar las tareas concurrentemente y esperar a que todas terminen
            results = await asyncio.gather(*tasks)

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for content, url, used_resolution in results:
                    if content is None:
                        failed_icons.append(url)
                        continue

                    # Extraer el nombre del archivo del URL
                    file_name = url.split('/')[-1]

                    # Limpiar el nombre del archivo
                    clean_name = re.sub(r'&file=|_icon_\d+', '', file_name)
                    clean_name = clean_name.replace('_', '-')  # Aquí se reemplazan los guiones bajos por guiones
                    clean_name = clean_name.replace(' ', '-')  # Aquí se reemplazan los espacios por guiones

                    # Verificar si el archivo ya existe en el ZIP y ajustar el nombre si es necesario
                    original_name, ext = os.path.splitext(clean_name)
                    counter = 1
                    while clean_name in zip_file.namelist():
                        clean_name = f"{original_name}_{counter}{ext}"
                        counter += 1

                    # Agregar el archivo al ZIP
                    zip_file.writestr(clean_name, content)

                    # Registrar si se usó una resolución diferente
                    if used_resolution and str(used_resolution) != '512':
                        resolution_changes.append((clean_name, used_resolution))

                    # Actualizar la barra de progreso
                    pbar.update(1)

    # Guardar el archivo ZIP en el disco
    with open(zip_filename, 'wb') as f:
        f.write(zip_buffer.getvalue())

    clear_console()
    first_line = f"{first_line} | Total de iconos: {colored_text(total_icons, 34)}"; print(created_by); print(created_by_line); print(first_line)

    divisor = "-" * (len(first_line)-(9*4 if all_pages else 9*5)); print(divisor)
    t_nfile = f'Todos los iconos se han descargado y comprimido en {colored_text(zip_filename, 32)}'
    divisor = f'{colored_text("-", 32)}' * (len(t_nfile)-9); print(divisor)
    print(t_nfile)
    print(divisor)

    if failed_icons:
        t_failed_icons = f'{colored_text("Algunos iconos no se pudieron descargar debido a formatos, resoluciones no disponibles o el icono esta corrupto:")} '
        divisor = f'{colored_text("-", 31)}' * (len(t_failed_icons)-9); print(divisor)
        print(t_failed_icons)
        for icon_url in failed_icons:
            print(f'  {icon_url}')
        print(divisor)
    if resolution_changes:
        t_resolution_changes = f'{colored_text("Los iconos se descargaron en una resolución diferente a la solicitada:", 35)}'
        divisor = f'{colored_text("-", 35)}' * (len(t_resolution_changes)-9); print(divisor)
        print(t_resolution_changes)
        for name, resolution in resolution_changes:
            print(f'  {name} - Resolución: {resolution}px')
        print(divisor)

######################################################################################

def get_available_formats_and_resolutions(soup):
    """ Extrae los formatos y resoluciones de icono disponibles de la estructura HTML. """
    formats = []
    resolutions = []

    # Extraer formatos
    tab_elements = soup.select('ul.nav-tabs li a')
    resolution_elements = soup.select('div.tab-pane.active button.size-selector')
    
    total_steps = len(tab_elements) + len(resolution_elements)
    
    with tqdm(total=total_steps, desc="Obteniendo formato y resoluciones disponibles para los iconos.", leave=False) as pbar:
        # Extraer formatos
        for tab in tab_elements:
            format_text = tab.get_text()
            if format_text:
                formats.append(format_text.upper())
            pbar.update(1)

        # Extraer resoluciones
        for button in resolution_elements:
            resolution_text = button.get_text().strip()
            if resolution_text.endswith('px'):
                resolutions.append(resolution_text[:-2])  # Elimina 'px'
            pbar.update(1)

    return formats, resolutions

async def get_formats_and_resolutions_from_page(first_icon_url):
    async with aiohttp.ClientSession() as session:
        soup = await fetch_page(session, first_icon_url)
        return get_available_formats_and_resolutions(soup)

######################################################################################

async def get_first_icon_url(pack_url):
    with tqdm(total=1, desc="Obteniendo la URL del primer icono", leave=False) as pbar:
        async with aiohttp.ClientSession() as session:
            try:
                soup = await fetch_page(session, pack_url)
                icon_element = soup.select_one('.icon-preview a')
                if icon_element:
                    icon_relative_url = icon_element['href']
                    icon_url = f"https://icon-icons.com{icon_relative_url if icon_relative_url.startswith('/') else '/' + icon_relative_url}"
                    pbar.update(1)
                    return icon_url
                else:
                    print("No se encontró el primer icono.")
                    pbar.update(1)
                    return None
            except aiohttp.ClientError as e:
                print(f'Error al procesar la URL del pack: {e}')
                pbar.update(1)
                return None

def clear_console(cant = 0):
    if cant == 0: return os.system('cls' if os.name == 'nt' else 'clear')
    # Imprimir líneas en blanco para sobrescribir el contenido actual
    for _ in range(cant):
        os.system('cls' if os.name == 'nt' else 'clear')

async def download_icons_main():
    global first_line
    global divisor
    global data_icons_task  # Referencia a la tarea en paralelo
    global pack_name

    while True:
        clear_console()
        print(created_by)
        print(created_by_line)
        print(f'{cancel_first_line[3:]}')
        divisor = "-" * len(cancel_first_line[3:]); print(divisor)
        pack_url = input("Ingresa el enlace del pack de iconos: ")
        
        if pack_url.lower() == 'x':
            confirm_exit = input(colored_text("¿Estás seguro de que deseas salir? (S/N): ", 33)).lower()
            if confirm_exit == 's':
                clear_console()
                print(colored_text("Saliendo del script...", 34)); time.sleep(0.5); clear_console(); return
            else: clear_console(); continue
        
        # Verificar si la URL es válida
        result, pack_url_verifed = verify_url(pack_url)
        if not result: print(pack_url_verifed); input("Presiona Enter para continuar..."); continue
        
        pack_name = get_pack_name(pack_url_verifed)

        try:
            if data_icons_task: # Cancelar la tarea en paralelo si existe
                data_icons_task.cancel()
                try:
                    await data_icons_task
                except asyncio.CancelledError:
                    print("Tarea en paralelo cancelada.")
            
            # Crear nueva tarea en paralelo
            data_icons_task = asyncio.create_task(get_data_icon_pack(pack_url_verifed))
            
            first_icon_url = await get_first_icon_url(pack_url_verifed)
            
            clear_console()
            first_line = f"Pack de iconos: {colored_text(pack_name, 34)}"; print(created_by); print(created_by_line); print(first_line)
            divisor = "-" * (len(first_line)-9); print(divisor)
            
            if first_icon_url:
                try:
                    formats, resolutions = await get_formats_and_resolutions_from_page(first_icon_url)
                    
                    if not formats: print("No se encontraron formatos disponibles."); continue
                    
                    while True:
                        t_sformat = "Seleccione un formato:"; print(t_sformat)
                        for i, fmt in enumerate(formats, start=1):
                            print(f"{colored_text(i, 32)}. {fmt}")
                        divisor = "-" * len(t_sformat); print(divisor)
                        print(f"{colored_text('C', 32)}. Cambiar pack de iconos")
                        print(f"{colored_text('X', 32)}. Salir")
                        
                        format_choice = input("Ingrese el número del formato deseado: ").lower()
                        
                        if format_choice == 'c':
                            clear_console()
                            break
                        elif format_choice == 'x':
                            confirm_exit = input(colored_text("¿Estás seguro de que deseas salir? (S/N): ", 33)).lower()
                            if confirm_exit == 's': 
                                clear_console()
                                print(colored_text("Saliendo del script...", 34)); time.sleep(0.5); clear_console(); return 
                            else: 
                                clear_console()
                                print(created_by); print(created_by_line); print(first_line); print(divisor)
                                continue
                        elif format_choice.isdigit() and 1 <= int(format_choice) <= len(formats):
                            chosen_format = formats[int(format_choice) - 1]
                            clear_console()
                            first_line = f"{first_line} | Formato: {colored_text(chosen_format, 34)}"; print(created_by); print(created_by_line); print(first_line)
                            divisor = "-" * (len(first_line)-(9*2)); print(divisor)
                            break
                        else:
                            clear_console(); print(created_by); print(created_by_line); print(first_line); 
                            divisor = "-" * (len(first_line)-9); print(divisor)
                            print(colored_text("[ Selección inválida. ]")); 
                    
                    if format_choice == 'c': continue
                    
                    chosen_resolution = ""
                    resolution_choice = ""
                    if chosen_format in ['PNG', 'ICO']:
                        while True:
                            t_sresolution = "Seleccione una resolución:"; print(t_sresolution)
                            for i, res in enumerate(resolutions, start=1):
                                print(f"{colored_text(i, 32)}. {res} px")
                            divisor = "-" * len(t_sresolution); print(divisor)
                            print(f"{colored_text('C', 32)}. Cambiar pack de iconos")
                            print(f"{colored_text('X', 32)}. Salir")
                            
                            resolution_choice = input("Ingrese el número de la resolución deseada: ").lower()
                            
                            if resolution_choice == 'c':
                                clear_console()
                                break
                            elif resolution_choice == 'x':
                                confirm_exit = input(colored_text("¿Estás seguro de que deseas salir? (S/N): ", 33)).lower()
                                if confirm_exit == 's': 
                                    clear_console()
                                    print(colored_text("Saliendo del script...", 34)); time.sleep(0.5); clear_console(); return 
                                else: 
                                    clear_console()
                                    print(created_by); print(created_by_line); print(first_line); print(divisor)
                                    continue
                            elif resolution_choice.isdigit() and 1 <= int(resolution_choice) <= len(resolutions):
                                chosen_resolution = resolutions[int(resolution_choice) - 1]
                                clear_console()
                                first_line = f"{first_line} | Resolución: {colored_text(chosen_resolution, 34)} px"; print(created_by); print(created_by_line); print(first_line)
                                divisor = "-" * (len(first_line)-(9*3)); print(divisor)
                                break
                            else: clear_console(); print(created_by); print(created_by_line); print(first_line); print(divisor); print(colored_text("[ Selección inválida. ]")); 
                    
                    if resolution_choice == 'c': continue
                    elif chosen_format == 'ICNS': chosen_resolution = '512'
                    
                    # Esperar a que la tarea asíncrona se complete
                    print(f'{colored_text("Obteniendo datos y páginas del pack de iconos...", 32)}')
                    data_icons = await data_icons_task
                    
                    if data_icons == 'c': clear_console(); continue
                    elif data_icons == 'x': clear_console(2); return

                    icon_urls = await generate_link_download(data_icons, chosen_format, chosen_resolution)
                    await download_icons_to_zip(icon_urls)
                    divisor = colored_text("-", 33) * (get_terminal_dimensions()[0]); print(divisor)
                    d_otro = input(f"{colored_text("¿Deseas descargar otro pack? (S/N): ", 33)}").lower()
                    if d_otro == "s": clear_console(); continue
                    else: clear_console(2); return
                    
                except aiohttp.ClientError as e:
                    print(f'{colored_text("Error al procesar la URL del icono: {e}}")}')
            else:
                print(f"{colored_text("No se pudo obtener la URL del primer icono o el link está incorrecto.")}")
        except ValueError as e:
            print(f'Error: {e}')

if __name__ == "__main__":#
    asyncio.run(download_icons_main())

# Rojo: 31
# Verde: 32
# Amarillo: 33
# Azul: 34
# Magenta: 35
# Cyan: 36
# Blanco: 37