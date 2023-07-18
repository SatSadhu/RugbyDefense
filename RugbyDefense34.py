import sys
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox
from pathlib import Path
# pyright: reportMissingModuleSource=false
import xlsxwriter
import mysql.connector
import datetime
import socket

# Crear ventana principal
root = tk.Tk()
root.title("RugbyDefense")
root.geometry("1366x768")

# Texto 1er tiempo
label = tk.Label(text="1er Tiempo")
label.place(y=0, x=700)

# Crear un widget Treeview
treeview = ttk.Treeview(root, style="Custom.Treeview")
treeview.place(y=20, x=0, width=1366, height=2000)

# Configurar filas y columnas para que se ajusten al tamaño de la ventana
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

# Insertar columnas y filas
treeview["columns"] = ("Tiempo", "Tackles", "Arriba", "Abajo", "H.Interno", "H.Externo", "Adelante LV", "Misma LV",
                       "Atras LV", "Positivo", "Neutro", "Negativo", "Doble Tackle", "Errados")

global tiempo
names_list = []
tiempo_dif = 0

for column in treeview["columns"]:
    treeview.column(column, width=60)

treeview.column("#0", width=160)
treeview.column("Tiempo", width=110)

treeview.heading("#0", text="Jugador")
treeview.heading("Tiempo", text="Tiempo")
treeview.heading("Tackles", text="Tackles")
treeview.heading("Arriba", text="Arriba")
treeview.heading("Abajo", text="Abajo")
treeview.heading("H.Interno", text="H.Interno")
treeview.heading("H.Externo", text="H.Externo")
treeview.heading("Adelante LV", text="Adelante LV")
treeview.heading("Misma LV", text="Misma Linea")
treeview.heading("Atras LV", text="Atras LV")
treeview.heading("Positivo", text="Positivo")
treeview.heading("Neutro", text="Neutro")
treeview.heading("Negativo", text="Negativo")
treeview.heading("Doble Tackle", text="Doble Tackle")
treeview.heading("Errados", text="Errados")

# Definir una variable booleana para llevar registro de si la fila ha sido seleccionada
fila_seleccionada = {}


def main():
    guardado_30_min_ver_hs()
    opciones()
    scrollbar()


def opciones():
    menu = tk.Menu(root)
    root.config(menu=menu)

    menu.add_command(label="Agregar Tiempo", command=agregar_tiempo)

    opciones = tk.Menu(menu, tearoff=0)
    opciones.add_command(label="Agregar Jugadores", command=agregar_jugadores)
    opciones.add_command(label="Sacar Totales", command=total)
    opciones.add_command(label="Sacar Estadisticas", command=total)

    # Base de datos
    opciones2 = tk.Menu(opciones, tearoff=0)
    opciones2.add_command(label="Buscar en Base de Datos", command=base_de_datos_buscar)
    opciones2.add_command(label="Agregar a Base de Datos", command=conseguir)
    # Guardar
    opciones2.add_command(label="Guardar en Excel", command=guardar)

    opciones3 = tk.Menu(opciones, tearoff=0)
    # 2do Tiempo
    opciones3.add_command(label="Ir a 2do tiempo", command=nuevo_2do_tiempo)
    opciones3.add_command(label="Eliminar ultimo Tiempo", command=eliminar_tiempo_final)

    menu.add_cascade(label="Opciones", menu=opciones)
    menu.add_cascade(label="Base de Datos", menu=opciones2)
    menu.add_cascade(label="Tiempo", menu=opciones3)


# Función que se ejecuta al hacer clic con el botón izquierdo
def on_left_click(event):
    global previous_value, fila_seleccionada

    try:
        # Obtener la fila y columna del click
        row = treeview.identify_row(event.y)
        column = treeview.identify_column(event.x)

        # Obtener índice de la columna
        column_index = int(str(column).replace("#", "")) - 1

        # Obtener valor actual y cambiarlo
        valor_actual = treeview.set(row, column_index)

        # Obtener el número de la columna y el valor actual
        col_num = int(str(column).replace("#", ""))
        value = treeview.item(row)["values"][col_num - 1]

        # Verificar si la fila ha sido seleccionada antes
        if row in fila_seleccionada and fila_seleccionada[row]:
            if column == "#1":
                pass
            else:
                try:
                    if treeview.item(row)["text"] != "TOTAL":  # Verificar si no es la fila "Total"
                        value += 1
                except TypeError:
                    pass
        else:
            # Si es el primer click en la fila, marcarla como seleccionada sin cambiar el valor
            fila_seleccionada[row] = True

        # Actualizar el valor en el Treeview
        treeview.set(row, column, value)

        # Guardar el valor actual como el valor anterior
        previous_value = value
    except Exception as e:
        pass


def on_right_click(event):
    global previous_value
    try:
        # Obtener la fila y columna del click
        row = treeview.identify_row(event.y)
        column = treeview.identify_column(event.x)

        # Obtener el número de la columna y el valor actual
        col_num = int(str(column).replace("#", ""))
        value = treeview.item(row)["values"][col_num - 1]

        # Restar 1 al valor actual
        if column == "#1":
            pass
        else:
            try:
                if treeview.item(row)["text"] != "TOTAL":  # Verificar si no es la fila "Total"
                    value -= 1
            except TypeError:
                pass

        # Actualizar el valor en el Treeview
        treeview.set(row, column, value)

        # Guardar el valor actual como el valor anterior
        previous_value = value

    except Exception as e:
        pass


# Vincular la función `column_click` al evento "<Button-1>" y "<Button-3>" en el widget Treeview
treeview.bind("<Button-1>", on_left_click)
treeview.bind("<Button-3>", on_right_click)


def guardar():
    # Obtener todos los valores de las filas y columnas
    values = []
    for item in treeview.get_children():
        values.append(treeview.item(item)["values"])

    # Obtener los nombres de los jugadores
    player_names = []
    for item in treeview.get_children():
        player_names.append(treeview.item(item)["text"])

    # Crear el archivo xlsx y hoja de trabajo
    if Path('Rugby_Excel_1erT.xlsx').is_file():
        workbook = xlsxwriter.Workbook("Rugby_Excel_2doT.xlsx")
        worksheet = workbook.add_worksheet()
    else:
        workbook = xlsxwriter.Workbook("Rugby_Excel_1erT.xlsx")
        worksheet = workbook.add_worksheet()

    # Escribir el nombre de la columna "JUGADORES" en la celda A1
    worksheet.write(0, 0, "JUGADORES")

    # Escribir los nombres de los jugadores en la primera columna
    for i, player_name in enumerate(player_names):
        worksheet.write(i + 1, 0, player_name)

    # Escribir los encabezados de las columnas en la primera fila
    headers = ["Tiempo", "Tackles", "Arriba", "Abajo", "H.Interno", "H.Externo", "Adelante", "Misma LV", "Atras LV",
               "Positivo LV", "Neutro LV", "Negativo LV", "Doble Tackle", "Errados"]

    for i, header in enumerate(headers):
        worksheet.write(0, i + 1, header)

    # Escribir los valores de las filas y columnas en el archivo xlsx
    for i, row in enumerate(values):
        for j, value in enumerate(row):
            worksheet.write(i + 1, j + 1, str(value))

    # Cerrar el archivo xlsx
    workbook.close()

    # Confirmar que se guardó el archivo correctamente
    messagebox.showinfo("Guardado",
                        "Los datos se han guardado correctamente en\n(Rugby_Excel_1doT.xlsx / Rugby_Excel_2doT.xlsx)")


def agregar_jugadores():
    global entry_dato
    global nueva
    nueva = tk.Toplevel(root)
    nueva.title("Agregar Jugadores")
    nueva.resizable(False, False)
    nueva.geometry("1366x768")

    label = tk.Label(nueva, text="Cantidad de Jugadores")
    label.grid(row=0, column=0)

    entry_dato = tk.StringVar()
    entry = ttk.Entry(nueva, textvariable=entry_dato)
    entry.grid(row=1, column=0)

    boton = ttk.Button(nueva, text="Agregar", command=lambda: entrys(nueva, names))
    boton.grid(row=2, column=0)


names = []


# Función para crear los entrys
def entrys(nueva, names):
    # Crear 5 entrys dentro de un bucle
    for i in range(int(entry_dato.get())):
        # Crear un label con el número del entry
        label = tk.Label(nueva, text=f"Jugador {i + 1}")
        label.grid(row=i, column=3)

        # Crear el entry y guardarlo en la lista de valores
        entry = tk.Entry(nueva)
        entry.grid(row=i, column=4)
        names.append(entry)

    boton = tk.Button(nueva, text="Agregar Jugadores", command=lambda: mostrar_valores(names))
    boton.grid(row=25, column=3, columnspan=2)


# Función para mostrar los valores de los entrys
def mostrar_valores(names):
    # Recorrer la lista de valores y mostrarlos en la consola
    for i, entry in enumerate(names):
        names_list.append(entry.get())
    # Agregar jugadores
    for name in reversed(names_list):
        treeview.insert("", 0, text=name, values=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    nueva.destroy()


def agregar_tiempo():
    guardado_30_min_ejecutar()

    global tiempo
    # Obtener el jugador seleccionado
    item = treeview.focus()
    jugador = treeview.item(item)["text"]

    # Obtener el tiempo a agregar
    tiempo = simpledialog.askstring("Ingresar Tiempo", "Ingrese Tiempo (HH:MM:SS):")

    # Obtener la fila del jugador seleccionado y establecer el tiempo
    for row in treeview.get_children():
        if treeview.item(row)["text"] == jugador:
            # Obtener el tiempo existente
            tiempo_existente = treeview.item(row)["values"][0]

            # Concatenar el tiempo existente con el nuevo tiempo ingresado
            if tiempo == "":
                pass
            else:
                if tiempo_existente == 0:
                    nuevo_tiempo = f"{tiempo}"
                    if nuevo_tiempo == None:
                        nuevo_tiempo.replace("None", "")
                else:
                    nuevo_tiempo = f"{tiempo_existente} / {tiempo}"

                # Actualizar el valor en la tabla
                treeview.set(row, "Tiempo", nuevo_tiempo)
                break


def eliminar_tiempo_final():
    global nuevo_tiempo
    # Obtener el jugador seleccionado
    item = treeview.focus()
    jugador = treeview.item(item)["text"]

    # Obtener la fila del jugador seleccionado y establecer el tiempo
    for row in treeview.get_children():
        if treeview.item(row)["text"] == jugador:
            # Obtener el tiempo existente
            tiempo_existente = treeview.item(row)["values"][0]

            # Si hay más de un tiempo separado por "/", eliminar el último
            try:
                if "/" in tiempo_existente:
                    tiempos = tiempo_existente.split("/")
                    tiempos.pop()
                    nuevo_tiempo = "/".join(tiempos)
                else:
                    nuevo_tiempo = 0

            except TypeError:
                treeview.set(row, "Tiempo", 0)

            # Actualizar el valor en la tabla
            try:
                treeview.set(row, "Tiempo", nuevo_tiempo)
                break
            except UnboundLocalError:
                pass


def total():
    # Obtener todas las filas
    rows = treeview.get_children()
    columns = treeview["columns"]

    # Buscar la fila que contiene la cadena "total" en la columna "Jugadores #0"
    for row in rows:
        if treeview.item(row, "text") == "TOTAL":
            # Eliminar la fila si existe
            treeview.delete(row)

    # Diccionario para almacenar los totales de cada columna
    totals = {}

    # Iterar a través de todas las filas
    for child in treeview.get_children():
        # Obtener valores de la fila actual
        values = treeview.item(child, 'values')

        # Iterar a través de cada columna
        for i, val in enumerate(values):
            # Si la columna no está en el diccionario, inicializar el valor en cero
            if i not in totals:
                totals[i] = 0

            # Sumar el valor actual al total de la columna
            if val:
                if i == 0:
                    pass
                else:
                    totals[i] += int(val)

    # Agregar la fila de totales
    total_values = [totals.get(i, '') for i in range(len(treeview["columns"]))]
    treeview.insert("", tk.END, text="TOTAL", values=total_values)


def scrollbar():
    # Creamos una barra de desplazamiento horizontal y la asociamos al Treeview
    xscrollbar = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=treeview.xview)
    treeview.configure(xscrollcommand=xscrollbar.set)

    # Empaquetamos el Treeview y la barra de desplazamiento
    treeview.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)


def obtener_direccion_ip():
    global direccion_ip_solucion
    hostname = socket.gethostname()
    direccion_ip = socket.gethostbyname(hostname)
    return direccion_ip


# Llamar a la función para obtener la dirección IP
direccion_ip_solucion = obtener_direccion_ip()


def nuevo_2do_tiempo():
    global tiempo_dif
    tiempo_dif = 1

    msg = messagebox.askyesno("Cambiar a 2do Tiempo", "Esta seguro que desea cambiar al 2do Tiempo?"
                                                      "\nTodos los datos del 1er Tiempo seran borrados")
    if msg:
        treeview.delete(*treeview.get_children())

        # Creamos una conexión a la base de datos
        cnx = mysql.connector.connect(user='user', password=f'passwd', host=f"192.168.0.13", database=f"database")
        cursor = cnx.cursor()

        cursor.execute("SELECT Jugador FROM rugby")

        datos_jugador = cursor.fetchall()

        for fila in reversed(datos_jugador):
            treeview.insert("", 0, text=fila, values=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

        # Cerramos la conexión
        cursor.close()
        cnx.close()

        names_list.clear()
        names.clear()


mensaje_mostrado = False


def mensaje_info():
    global mensaje_mostrado
    global msgg
    if not mensaje_mostrado:
        mensaje_mostrado = True
        msgg = messagebox.askyesno("Mensaje",
                                   "Los datos se estan por perder,\nGuardaste los datos en la Base de Datos?",
                                   default="no")

    if not msgg:
        conseguir()

    elif msgg:
        sys.exit()


# Vincular la función `conseguir` al evento "<Destroy>" de la ventana principal
root.bind("<Destroy>", lambda event: mensaje_info())

control = False


def guardado_30_min_ver_hs():
    global horaMas30
    global hora_actual
    global control

    if control == False:
        hora_actual = datetime.datetime.now().time()
        control = True

    horaMas30 = (datetime.datetime.combine(datetime.date.today(), hora_actual) +
                 datetime.timedelta(minutes=30)).time()
    guardado_30_min_ejecutar()


def guardado_30_min_ejecutar():
    global control
    hora_actual_2 = datetime.datetime.now().time()
    if hora_actual_2 >= horaMas30:
        conseguir()
        control = False
        guardado_30_min_ver_hs()
    else:
        pass


def base_de_datos_buscar():
    global database_papa_psswd
    global database_papa_user_and_database
    if tiempo_dif == 0:
        database_papa_psswd = 'passwd'
        database_papa_user_and_database = 'dtbase'
    elif tiempo_dif == 1:
        database_papa_psswd = 'passwd'
        database_papa_user_and_database = 'dtbase'

    # Creamos una conexión a la base de datos
    cnx = mysql.connector.connect(user=f'user', password=f'passwd', host=f"192.168.0.13",
                                  database=f'{database_papa_user_and_database}')
    cursor = cnx.cursor()

    cursor.execute(
        "SELECT Tiempo, Tackles, Arriba, Abajo, Hinterno, Hexterno, AdelanteLV, MismaLinea, AtrasLV, Positivo, Neutro, Negativo, DobleTackle, Errados FROM rugby")

    datos = cursor.fetchall()

    cursor.execute("SELECT Jugador FROM rugby")

    datos2 = cursor.fetchall()

    treeview.delete(*treeview.get_children())

    for fila, fila2 in zip(datos, datos2):
        treeview.insert('', tk.END, values=fila, text=fila2)

    # Cerramos la conexión
    cursor.close()
    cnx.close()


def conseguir():
    # suma el primero[] ----> va cambiando de jugador
    # suma el segundo[] ----> va cambiando la columna
    global database_papa_psswd
    global database_papa_user_and_database
    if tiempo_dif == 0:
        database_papa_psswd = 'psswd'
        database_papa_user_and_database = 'dtbase'
    elif tiempo_dif == 1:
        database_papa_psswd = 'kali'
        database_papa_user_and_database = 'dtbase'

    def decimoquinto_jugador():
        try:
            list = [f"{treeview.item(treeview.get_children()[14])['text']}",
                    f"{treeview.item(treeview.get_children()[14])['values'][0]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][1]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][2]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][3]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][4]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][5]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][6]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][7]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][8]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][9]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][10]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][11]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][12]}",
                    f"{treeview.item(treeview.get_children()[14])['values'][13]}"]
            return list
        except IndexError:
            pass

    def decimosexto_jugador():
        try:
            list = [f"{treeview.item(treeview.get_children()[15])['text']}",
                    f"{treeview.item(treeview.get_children()[15])['values'][0]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][1]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][2]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][3]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][4]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][5]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][6]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][7]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][8]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][9]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][10]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][11]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][12]}",
                    f"{treeview.item(treeview.get_children()[15])['values'][13]}"]
            return list
        except IndexError:
            pass

    def decimoseptimo_jugador():
        try:
            list = [f"{treeview.item(treeview.get_children()[16])['text']}",
                    f"{treeview.item(treeview.get_children()[16])['values'][0]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][1]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][2]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][3]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][4]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][5]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][6]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][7]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][8]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][9]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][10]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][11]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][12]}",
                    f"{treeview.item(treeview.get_children()[16])['values'][13]}"]
            return list
        except IndexError:
            pass

    def decimooctavo_jugador():
        try:
            list = [f"{treeview.item(treeview.get_children()[17])['text']}",
                    f"{treeview.item(treeview.get_children()[17])['values'][0]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][1]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][2]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][3]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][4]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][5]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][6]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][7]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][8]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][9]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][10]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][11]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][12]}",
                    f"{treeview.item(treeview.get_children()[17])['values'][13]}"]
            return list
        except IndexError:
            pass

    def decimonoveno_jugador():
        try:
            list = [f"{treeview.item(treeview.get_children()[18])['text']}",
                    f"{treeview.item(treeview.get_children()[18])['values'][0]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][1]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][2]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][3]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][4]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][5]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][6]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][7]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][8]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][9]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][10]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][11]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][12]}",
                    f"{treeview.item(treeview.get_children()[18])['values'][13]}"]
            return list
        except IndexError:
            pass

    def vigecimo_jugador():
        try:
            list = [f"{treeview.item(treeview.get_children()[19])['text']}",
                    f"{treeview.item(treeview.get_children()[19])['values'][0]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][1]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][2]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][3]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][4]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][5]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][6]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][7]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][8]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][9]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][10]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][11]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][12]}",
                    f"{treeview.item(treeview.get_children()[19])['values'][13]}"]
            return list
        except IndexError:
            pass

    def vigecimoprimer_jugador():
        try:
            list = [f"{treeview.item(treeview.get_children()[20])['text']}",
                    f"{treeview.item(treeview.get_children()[20])['values'][0]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][1]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][2]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][3]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][4]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][5]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][6]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][7]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][8]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][9]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][10]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][11]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][12]}",
                    f"{treeview.item(treeview.get_children()[20])['values'][13]}"]
            return list
        except IndexError:
            pass

    def vigecimosegundo_jugador():
        try:
            list = [f"{treeview.item(treeview.get_children()[21])['text']}",
                    f"{treeview.item(treeview.get_children()[21])['values'][0]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][1]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][2]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][3]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][4]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][5]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][6]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][7]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][8]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][9]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][10]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][11]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][12]}",
                    f"{treeview.item(treeview.get_children()[21])['values'][13]}"]
            return list
        except IndexError:
            pass

    def vigecimotercer_jugador():
        try:
            list = [f"{treeview.item(treeview.get_children()[22])['text']}",
                    f"{treeview.item(treeview.get_children()[22])['values'][0]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][1]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][2]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][3]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][4]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][5]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][6]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][7]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][8]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][9]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][10]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][11]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][12]}",
                    f"{treeview.item(treeview.get_children()[22])['values'][13]}"]
            return list
        except IndexError:
            pass

    def total():
        try:
            list = [f"{treeview.item(treeview.get_children()[23])['text']}",
                    f"{treeview.item(treeview.get_children()[23])['values'][0]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][1]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][2]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][3]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][4]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][5]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][6]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][7]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][8]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][9]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][10]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][11]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][12]}",
                    f"{treeview.item(treeview.get_children()[23])['values'][13]}"]
            return list
        except IndexError:
            pass

    diccionario = {
        f"primer_jugador": [f"{treeview.item(treeview.get_children()[0])['text']}",
                            f"{treeview.item(treeview.get_children()[0])['values'][0]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][1]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][2]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][3]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][4]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][5]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][6]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][7]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][8]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][9]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][10]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][11]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][12]}",
                            f"{treeview.item(treeview.get_children()[0])['values'][13]}"],

        f"segundo_jugador": [f"{treeview.item(treeview.get_children()[1])['text']}",
                             f"{treeview.item(treeview.get_children()[1])['values'][0]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][1]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][2]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][3]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][4]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][5]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][6]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][7]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][8]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][9]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][10]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][11]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][12]}",
                             f"{treeview.item(treeview.get_children()[1])['values'][13]}"],

        f"tercer_jugador": [f"{treeview.item(treeview.get_children()[2])['text']}",
                            f"{treeview.item(treeview.get_children()[2])['values'][0]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][1]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][2]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][3]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][4]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][5]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][6]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][7]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][8]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][9]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][10]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][11]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][12]}",
                            f"{treeview.item(treeview.get_children()[2])['values'][13]}"],

        f"cuarto_jugador": [f"{treeview.item(treeview.get_children()[3])['text']}",
                            f"{treeview.item(treeview.get_children()[3])['values'][0]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][1]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][2]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][3]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][4]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][5]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][6]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][7]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][8]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][9]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][10]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][11]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][12]}",
                            f"{treeview.item(treeview.get_children()[3])['values'][13]}"],

        f"quinto_jugador": [f"{treeview.item(treeview.get_children()[4])['text']}",
                            f"{treeview.item(treeview.get_children()[4])['values'][0]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][1]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][2]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][3]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][4]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][5]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][6]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][7]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][8]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][9]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][10]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][11]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][12]}",
                            f"{treeview.item(treeview.get_children()[4])['values'][13]}"],

        f"sexto_jugador": [f"{treeview.item(treeview.get_children()[5])['text']}",
                           f"{treeview.item(treeview.get_children()[5])['values'][0]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][1]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][2]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][3]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][4]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][5]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][6]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][7]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][8]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][9]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][10]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][11]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][12]}",
                           f"{treeview.item(treeview.get_children()[5])['values'][13]}"],

        f"septimo_jugador": [f"{treeview.item(treeview.get_children()[6])['text']}",
                             f"{treeview.item(treeview.get_children()[6])['values'][0]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][1]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][2]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][3]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][4]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][5]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][6]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][7]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][8]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][9]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][10]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][11]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][12]}",
                             f"{treeview.item(treeview.get_children()[6])['values'][13]}"],

        f"octavo_jugador": [f"{treeview.item(treeview.get_children()[7])['text']}",
                            f"{treeview.item(treeview.get_children()[7])['values'][0]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][1]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][2]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][3]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][4]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][5]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][6]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][7]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][8]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][9]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][10]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][11]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][12]}",
                            f"{treeview.item(treeview.get_children()[7])['values'][13]}"],

        f"noveno_jugador": [f"{treeview.item(treeview.get_children()[8])['text']}",
                            f"{treeview.item(treeview.get_children()[8])['values'][0]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][1]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][2]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][3]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][4]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][5]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][6]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][7]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][8]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][9]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][10]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][11]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][12]}",
                            f"{treeview.item(treeview.get_children()[8])['values'][13]}"],

        f"decimo_jugador": [f"{treeview.item(treeview.get_children()[9])['text']}",
                            f"{treeview.item(treeview.get_children()[9])['values'][0]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][1]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][2]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][3]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][4]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][5]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][6]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][7]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][8]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][9]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][10]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][11]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][12]}",
                            f"{treeview.item(treeview.get_children()[9])['values'][13]}"],

        f"onceavo_jugador": [f"{treeview.item(treeview.get_children()[10])['text']}",
                             f"{treeview.item(treeview.get_children()[10])['values'][0]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][1]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][2]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][3]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][4]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][5]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][6]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][7]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][8]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][9]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][10]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][11]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][12]}",
                             f"{treeview.item(treeview.get_children()[10])['values'][13]}"],

        f"doceavo_jugador": [f"{treeview.item(treeview.get_children()[11])['text']}",
                             f"{treeview.item(treeview.get_children()[11])['values'][0]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][1]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][2]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][3]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][4]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][5]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][6]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][7]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][8]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][9]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][10]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][11]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][12]}",
                             f"{treeview.item(treeview.get_children()[11])['values'][13]}"],

        f"treceavo_jugador": [f"{treeview.item(treeview.get_children()[12])['text']}",
                              f"{treeview.item(treeview.get_children()[12])['values'][0]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][1]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][2]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][3]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][4]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][5]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][6]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][7]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][8]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][9]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][10]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][11]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][12]}",
                              f"{treeview.item(treeview.get_children()[12])['values'][13]}"],

        f"decimocuarto_jugador": [f"{treeview.item(treeview.get_children()[13])['text']}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][0]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][1]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][2]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][3]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][4]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][5]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][6]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][7]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][8]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][9]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][10]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][11]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][12]}",
                                  f"{treeview.item(treeview.get_children()[13])['values'][13]}"],

        f"decimoquinto_jugador": decimoquinto_jugador(),

        f"decimosexto_jugador": decimosexto_jugador(),

        f"decimoseptimo_jugador": decimoseptimo_jugador(),

        f"decimooctavo_jugador": decimooctavo_jugador(),

        f"decimonoveno_jugador": decimonoveno_jugador(),

        f"vigesimo_jugador": vigecimo_jugador(),

        f"vigesimoprimero_jugador": vigecimoprimer_jugador(),

        f"vigesimosegundo_jugador": vigecimosegundo_jugador(),

        f"vigesimotercero_jugador": vigecimotercer_jugador(),

        f"total": total()
    }

    # Creamos una conexión a la base de datos
    cnx = mysql.connector.connect(user=f'user', password=f'passwd', host=f"192.168.0.13",
                                  database=f'{database_papa_user_and_database}')
    cursor = cnx.cursor()

    cursor.execute("set sql_safe_updates=0;")
    cursor.execute("delete from rugby;")

    datos = cursor.fetchall()
    global query24

    query = f'insert into rugby values ("{diccionario["primer_jugador"][0]}", "{diccionario["primer_jugador"][1]}", "{diccionario["primer_jugador"][2]}", "{diccionario["primer_jugador"][3]}", "{diccionario["primer_jugador"][4]}", "{diccionario["primer_jugador"][5]}", "{diccionario["primer_jugador"][6]}", "{diccionario["primer_jugador"][7]}", "{diccionario["primer_jugador"][8]}", "{diccionario["primer_jugador"][9]}", "{diccionario["primer_jugador"][10]}", "{diccionario["primer_jugador"][11]}", "{diccionario["primer_jugador"][12]}", "{diccionario["primer_jugador"][13]}", "{diccionario["primer_jugador"][14]}");'
    query2 = f'insert into rugby values ("{diccionario["segundo_jugador"][0]}", "{diccionario["segundo_jugador"][1]}", "{diccionario["segundo_jugador"][2]}", "{diccionario["segundo_jugador"][3]}", "{diccionario["segundo_jugador"][4]}", "{diccionario["segundo_jugador"][5]}", "{diccionario["segundo_jugador"][6]}", "{diccionario["segundo_jugador"][7]}", "{diccionario["segundo_jugador"][8]}", "{diccionario["segundo_jugador"][9]}", "{diccionario["segundo_jugador"][10]}", "{diccionario["segundo_jugador"][11]}", "{diccionario["segundo_jugador"][12]}", "{diccionario["segundo_jugador"][13]}", "{diccionario["segundo_jugador"][14]}");'
    query3 = f'insert into rugby values ("{diccionario["tercer_jugador"][0]}", "{diccionario["tercer_jugador"][1]}", "{diccionario["tercer_jugador"][2]}", "{diccionario["tercer_jugador"][3]}", "{diccionario["tercer_jugador"][4]}", "{diccionario["tercer_jugador"][5]}", "{diccionario["tercer_jugador"][6]}", "{diccionario["tercer_jugador"][7]}", "{diccionario["tercer_jugador"][8]}", "{diccionario["tercer_jugador"][9]}", "{diccionario["tercer_jugador"][10]}", "{diccionario["tercer_jugador"][11]}", "{diccionario["tercer_jugador"][12]}", "{diccionario["tercer_jugador"][13]}", "{diccionario["tercer_jugador"][14]}");'
    query4 = f'insert into rugby values ("{diccionario["cuarto_jugador"][0]}", "{diccionario["cuarto_jugador"][1]}", "{diccionario["cuarto_jugador"][2]}", "{diccionario["cuarto_jugador"][3]}", "{diccionario["cuarto_jugador"][4]}", "{diccionario["cuarto_jugador"][5]}", "{diccionario["cuarto_jugador"][6]}", "{diccionario["cuarto_jugador"][7]}", "{diccionario["cuarto_jugador"][8]}", "{diccionario["cuarto_jugador"][9]}", "{diccionario["cuarto_jugador"][10]}", "{diccionario["cuarto_jugador"][11]}", "{diccionario["cuarto_jugador"][12]}", "{diccionario["cuarto_jugador"][13]}", "{diccionario["cuarto_jugador"][14]}");'
    query5 = f'insert into rugby values ("{diccionario["quinto_jugador"][0]}", "{diccionario["quinto_jugador"][1]}", "{diccionario["quinto_jugador"][2]}", "{diccionario["quinto_jugador"][3]}", "{diccionario["quinto_jugador"][4]}", "{diccionario["quinto_jugador"][5]}", "{diccionario["quinto_jugador"][6]}", "{diccionario["quinto_jugador"][7]}", "{diccionario["quinto_jugador"][8]}", "{diccionario["quinto_jugador"][9]}", "{diccionario["quinto_jugador"][10]}", "{diccionario["quinto_jugador"][11]}", "{diccionario["quinto_jugador"][12]}", "{diccionario["quinto_jugador"][13]}", "{diccionario["quinto_jugador"][14]}");'
    query6 = f'insert into rugby values ("{diccionario["sexto_jugador"][0]}", "{diccionario["sexto_jugador"][1]}", "{diccionario["sexto_jugador"][2]}", "{diccionario["sexto_jugador"][3]}", "{diccionario["sexto_jugador"][4]}", "{diccionario["sexto_jugador"][5]}", "{diccionario["sexto_jugador"][6]}", "{diccionario["sexto_jugador"][7]}", "{diccionario["sexto_jugador"][8]}", "{diccionario["sexto_jugador"][9]}", "{diccionario["sexto_jugador"][10]}", "{diccionario["sexto_jugador"][11]}", "{diccionario["sexto_jugador"][12]}", "{diccionario["sexto_jugador"][13]}", "{diccionario["sexto_jugador"][14]}");'
    query7 = f'insert into rugby values ("{diccionario["septimo_jugador"][0]}", "{diccionario["septimo_jugador"][1]}", "{diccionario["septimo_jugador"][2]}", "{diccionario["septimo_jugador"][3]}", "{diccionario["septimo_jugador"][4]}", "{diccionario["septimo_jugador"][5]}", "{diccionario["septimo_jugador"][6]}", "{diccionario["septimo_jugador"][7]}", "{diccionario["septimo_jugador"][8]}", "{diccionario["septimo_jugador"][9]}", "{diccionario["septimo_jugador"][10]}", "{diccionario["septimo_jugador"][11]}", "{diccionario["septimo_jugador"][12]}", "{diccionario["septimo_jugador"][13]}", "{diccionario["septimo_jugador"][14]}");'
    query8 = f'insert into rugby values ("{diccionario["octavo_jugador"][0]}", "{diccionario["octavo_jugador"][1]}", "{diccionario["octavo_jugador"][2]}", "{diccionario["octavo_jugador"][3]}", "{diccionario["octavo_jugador"][4]}", "{diccionario["octavo_jugador"][5]}", "{diccionario["octavo_jugador"][6]}", "{diccionario["octavo_jugador"][7]}", "{diccionario["octavo_jugador"][8]}", "{diccionario["octavo_jugador"][9]}", "{diccionario["octavo_jugador"][10]}", "{diccionario["octavo_jugador"][11]}", "{diccionario["octavo_jugador"][12]}", "{diccionario["octavo_jugador"][13]}", "{diccionario["octavo_jugador"][14]}");'
    query9 = f'insert into rugby values ("{diccionario["noveno_jugador"][0]}", "{diccionario["noveno_jugador"][1]}", "{diccionario["noveno_jugador"][2]}", "{diccionario["noveno_jugador"][3]}", "{diccionario["noveno_jugador"][4]}", "{diccionario["noveno_jugador"][5]}", "{diccionario["noveno_jugador"][6]}", "{diccionario["noveno_jugador"][7]}", "{diccionario["noveno_jugador"][8]}", "{diccionario["noveno_jugador"][9]}", "{diccionario["noveno_jugador"][10]}", "{diccionario["noveno_jugador"][11]}", "{diccionario["noveno_jugador"][12]}", "{diccionario["noveno_jugador"][13]}", "{diccionario["noveno_jugador"][14]}");'
    query10 = f'insert into rugby values ("{diccionario["decimo_jugador"][0]}", "{diccionario["decimo_jugador"][1]}", "{diccionario["decimo_jugador"][2]}", "{diccionario["decimo_jugador"][3]}", "{diccionario["decimo_jugador"][4]}", "{diccionario["decimo_jugador"][5]}", "{diccionario["decimo_jugador"][6]}", "{diccionario["decimo_jugador"][7]}", "{diccionario["decimo_jugador"][8]}", "{diccionario["decimo_jugador"][9]}", "{diccionario["decimo_jugador"][10]}", "{diccionario["decimo_jugador"][11]}", "{diccionario["decimo_jugador"][12]}", "{diccionario["decimo_jugador"][13]}", "{diccionario["decimo_jugador"][14]}");'
    query11 = f'insert into rugby values ("{diccionario["onceavo_jugador"][0]}", "{diccionario["onceavo_jugador"][1]}", "{diccionario["onceavo_jugador"][2]}", "{diccionario["onceavo_jugador"][3]}", "{diccionario["onceavo_jugador"][4]}", "{diccionario["onceavo_jugador"][5]}", "{diccionario["onceavo_jugador"][6]}", "{diccionario["onceavo_jugador"][7]}", "{diccionario["onceavo_jugador"][8]}", "{diccionario["onceavo_jugador"][9]}", "{diccionario["onceavo_jugador"][10]}", "{diccionario["onceavo_jugador"][11]}", "{diccionario["onceavo_jugador"][12]}", "{diccionario["onceavo_jugador"][13]}", "{diccionario["onceavo_jugador"][14]}");'
    query12 = f'insert into rugby values ("{diccionario["doceavo_jugador"][0]}", "{diccionario["doceavo_jugador"][1]}", "{diccionario["doceavo_jugador"][2]}", "{diccionario["doceavo_jugador"][3]}", "{diccionario["doceavo_jugador"][4]}", "{diccionario["doceavo_jugador"][5]}", "{diccionario["doceavo_jugador"][6]}", "{diccionario["doceavo_jugador"][7]}", "{diccionario["doceavo_jugador"][8]}", "{diccionario["doceavo_jugador"][9]}", "{diccionario["doceavo_jugador"][10]}", "{diccionario["doceavo_jugador"][11]}", "{diccionario["doceavo_jugador"][12]}", "{diccionario["doceavo_jugador"][13]}", "{diccionario["doceavo_jugador"][14]}");'
    query13 = f'insert into rugby values ("{diccionario["treceavo_jugador"][0]}", "{diccionario["treceavo_jugador"][1]}", "{diccionario["treceavo_jugador"][2]}", "{diccionario["treceavo_jugador"][3]}", "{diccionario["treceavo_jugador"][4]}", "{diccionario["treceavo_jugador"][5]}", "{diccionario["treceavo_jugador"][6]}", "{diccionario["treceavo_jugador"][7]}", "{diccionario["treceavo_jugador"][8]}", "{diccionario["treceavo_jugador"][9]}", "{diccionario["treceavo_jugador"][10]}", "{diccionario["treceavo_jugador"][11]}", "{diccionario["treceavo_jugador"][12]}", "{diccionario["treceavo_jugador"][13]}", "{diccionario["treceavo_jugador"][14]}");'
    query14 = f'insert into rugby values ("{diccionario["decimocuarto_jugador"][0]}", "{diccionario["decimocuarto_jugador"][1]}", "{diccionario["decimocuarto_jugador"][2]}", "{diccionario["decimocuarto_jugador"][3]}", "{diccionario["decimocuarto_jugador"][4]}", "{diccionario["decimocuarto_jugador"][5]}", "{diccionario["decimocuarto_jugador"][6]}", "{diccionario["decimocuarto_jugador"][7]}", "{diccionario["decimocuarto_jugador"][8]}", "{diccionario["decimocuarto_jugador"][9]}", "{diccionario["decimocuarto_jugador"][10]}", "{diccionario["decimocuarto_jugador"][11]}", "{diccionario["decimocuarto_jugador"][12]}", "{diccionario["decimocuarto_jugador"][13]}", "{diccionario["decimocuarto_jugador"][14]}");'

    queries = [query, query2, query3, query4, query5, query6, query7, query8, query9, query10, query11, query12,
               query13, query14]

    for q in queries:
        cursor.execute(q)

    try:
        query15 = f'insert into rugby values ("{diccionario["decimoquinto_jugador"][0]}", "{diccionario["decimoquinto_jugador"][1]}", "{diccionario["decimoquinto_jugador"][2]}", "{diccionario["decimoquinto_jugador"][3]}", "{diccionario["decimoquinto_jugador"][4]}", "{diccionario["decimoquinto_jugador"][5]}", "{diccionario["decimoquinto_jugador"][6]}", "{diccionario["decimoquinto_jugador"][7]}", "{diccionario["decimoquinto_jugador"][8]}", "{diccionario["decimoquinto_jugador"][9]}", "{diccionario["decimoquinto_jugador"][10]}", "{diccionario["decimoquinto_jugador"][11]}", "{diccionario["decimoquinto_jugador"][12]}", "{diccionario["decimoquinto_jugador"][13]}", "{diccionario["decimoquinto_jugador"][14]}");'
        cursor.execute(query15)
    except TypeError:
        pass

    try:
        query16 = f'insert into rugby values ("{diccionario["decimosexto_jugador"][0]}", "{diccionario["decimosexto_jugador"][1]}", "{diccionario["decimosexto_jugador"][2]}", "{diccionario["decimosexto_jugador"][3]}", "{diccionario["decimosexto_jugador"][4]}", "{diccionario["decimosexto_jugador"][5]}", "{diccionario["decimosexto_jugador"][6]}", "{diccionario["decimosexto_jugador"][7]}", "{diccionario["decimosexto_jugador"][8]}", "{diccionario["decimosexto_jugador"][9]}", "{diccionario["decimosexto_jugador"][10]}", "{diccionario["decimosexto_jugador"][11]}", "{diccionario["decimosexto_jugador"][12]}", "{diccionario["decimosexto_jugador"][13]}", "{diccionario["decimosexto_jugador"][14]}");'
        cursor.execute(query16)
    except TypeError:
        pass

    try:
        query17 = f'insert into rugby values ("{diccionario["decimoseptimo_jugador"][0]}", "{diccionario["decimoseptimo_jugador"][1]}", "{diccionario["decimoseptimo_jugador"][2]}", "{diccionario["decimoseptimo_jugador"][3]}", "{diccionario["decimoseptimo_jugador"][4]}", "{diccionario["decimoseptimo_jugador"][5]}", "{diccionario["decimoseptimo_jugador"][6]}", "{diccionario["decimoseptimo_jugador"][7]}", "{diccionario["decimoseptimo_jugador"][8]}", "{diccionario["decimoseptimo_jugador"][9]}", "{diccionario["decimoseptimo_jugador"][10]}", "{diccionario["decimoseptimo_jugador"][11]}", "{diccionario["decimoseptimo_jugador"][12]}", "{diccionario["decimoseptimo_jugador"][13]}", "{diccionario["decimoseptimo_jugador"][14]}");'
        cursor.execute(query17)
    except TypeError:
        pass

    try:
        query18 = f'insert into rugby values ("{diccionario["decimooctavo_jugador"][0]}", "{diccionario["decimooctavo_jugador"][1]}", "{diccionario["decimooctavo_jugador"][2]}", "{diccionario["decimooctavo_jugador"][3]}", "{diccionario["decimooctavo_jugador"][4]}", "{diccionario["decimooctavo_jugador"][5]}", "{diccionario["decimooctavo_jugador"][6]}", "{diccionario["decimooctavo_jugador"][7]}", "{diccionario["decimooctavo_jugador"][8]}", "{diccionario["decimooctavo_jugador"][9]}", "{diccionario["decimooctavo_jugador"][10]}", "{diccionario["decimooctavo_jugador"][11]}", "{diccionario["decimooctavo_jugador"][12]}", "{diccionario["decimooctavo_jugador"][13]}", "{diccionario["decimooctavo_jugador"][14]}");'
        cursor.execute(query18)
    except TypeError:
        pass

    try:
        query19 = f'insert into rugby values ("{diccionario["decimonoveno_jugador"][0]}", "{diccionario["decimonoveno_jugador"][1]}", "{diccionario["decimonoveno_jugador"][2]}", "{diccionario["decimonoveno_jugador"][3]}", "{diccionario["decimonoveno_jugador"][4]}", "{diccionario["decimonoveno_jugador"][5]}", "{diccionario["decimonoveno_jugador"][6]}", "{diccionario["decimonoveno_jugador"][7]}", "{diccionario["decimonoveno_jugador"][8]}", "{diccionario["decimonoveno_jugador"][9]}", "{diccionario["decimonoveno_jugador"][10]}", "{diccionario["decimonoveno_jugador"][11]}", "{diccionario["decimonoveno_jugador"][12]}", "{diccionario["decimonoveno_jugador"][13]}", "{diccionario["decimonoveno_jugador"][14]}");'
        cursor.execute(query19)
    except TypeError:
        pass

    try:
        query20 = f'insert into rugby values ("{diccionario["vigesimo_jugador"][0]}", "{diccionario["vigesimo_jugador"][1]}", "{diccionario["vigesimo_jugador"][2]}", "{diccionario["vigesimo_jugador"][3]}", "{diccionario["vigesimo_jugador"][4]}", "{diccionario["vigesimo_jugador"][5]}", "{diccionario["vigesimo_jugador"][6]}", "{diccionario["vigesimo_jugador"][7]}", "{diccionario["vigesimo_jugador"][8]}", "{diccionario["vigesimo_jugador"][9]}", "{diccionario["vigesimo_jugador"][10]}", "{diccionario["vigesimo_jugador"][11]}", "{diccionario["vigesimo_jugador"][12]}", "{diccionario["vigesimo_jugador"][13]}", "{diccionario["vigesimo_jugador"][14]}");'
        cursor.execute(query20)
    except TypeError:
        pass

    try:
        query21 = f'insert into rugby values ("{diccionario["vigesimoprimero_jugador"][0]}", "{diccionario["vigesimoprimero_jugador"][1]}", "{diccionario["vigesimoprimero_jugador"][2]}", "{diccionario["vigesimoprimero_jugador"][3]}", "{diccionario["vigesimoprimero_jugador"][4]}", "{diccionario["vigesimoprimero_jugador"][5]}", "{diccionario["vigesimoprimero_jugador"][6]}", "{diccionario["vigesimoprimero_jugador"][7]}", "{diccionario["vigesimoprimero_jugador"][8]}", "{diccionario["vigesimoprimero_jugador"][9]}", "{diccionario["vigesimoprimero_jugador"][10]}", "{diccionario["vigesimoprimero_jugador"][11]}", "{diccionario["vigesimoprimero_jugador"][12]}", "{diccionario["vigesimoprimero_jugador"][13]}", "{diccionario["vigesimoprimero_jugador"][14]}");'
        cursor.execute(query21)
    except TypeError:
        pass

    try:
        query22 = f'insert into rugby values ("{diccionario["vigesimosegundo_jugador"][0]}", "{diccionario["vigesimosegundo_jugador"][1]}", "{diccionario["vigesimosegundo_jugador"][2]}", "{diccionario["vigesimosegundo_jugador"][3]}", "{diccionario["vigesimosegundo_jugador"][4]}", "{diccionario["vigesimosegundo_jugador"][5]}", "{diccionario["vigesimosegundo_jugador"][6]}", "{diccionario["vigesimosegundo_jugador"][7]}", "{diccionario["vigesimosegundo_jugador"][8]}", "{diccionario["vigesimosegundo_jugador"][9]}", "{diccionario["vigesimosegundo_jugador"][10]}", "{diccionario["vigesimosegundo_jugador"][11]}", "{diccionario["vigesimosegundo_jugador"][12]}", "{diccionario["vigesimosegundo_jugador"][13]}", "{diccionario["vigesimosegundo_jugador"][14]}");'
        cursor.execute(query22)
    except TypeError:
        pass

    try:
        query23 = f'insert into rugby values ("{diccionario["vigesimotercero_jugador"][0]}", "{diccionario["vigesimotercero_jugador"][1]}", "{diccionario["vigesimotercero_jugador"][2]}", "{diccionario["vigesimotercero_jugador"][3]}", "{diccionario["vigesimotercero_jugador"][4]}", "{diccionario["vigesimotercero_jugador"][5]}", "{diccionario["vigesimotercero_jugador"][6]}", "{diccionario["vigesimotercero_jugador"][7]}", "{diccionario["vigesimotercero_jugador"][8]}", "{diccionario["vigesimotercero_jugador"][9]}", "{diccionario["vigesimotercero_jugador"][10]}", "{diccionario["vigesimotercero_jugador"][11]}", "{diccionario["vigesimotercero_jugador"][12]}", "{diccionario["vigesimotercero_jugador"][13]}", "{diccionario["vigesimotercero_jugador"][14]}");'
        cursor.execute(query23)
    except TypeError:
        pass

    try:
        query24 = f'insert into rugby values ("{diccionario["Total"][0]}", "{diccionario["Total"][1]}", "{diccionario["Total"][2]}", "{diccionario["Total"][3]}", "{diccionario["Total"][4]}", "{diccionario["Total"][5]}", "{diccionario["Total"][6]}", "{diccionario["Total"][7]}", "{diccionario["Total"][8]}", "{diccionario["Total"][9]}", "{diccionario["Total"][10]}", "{diccionario["Total"][11]}", "{diccionario["Total"][12]}", "{diccionario["Total"][13]}", "{diccionario["Total"][14]}");'
        cursor.execute(query24)
    except KeyError:
        pass

    cnx.commit()

    # Cerramos la conexión
    cursor.close()
    cnx.close()

    tk.messagebox.showinfo("Mensaje", "Agregado a Base de Datos")


if __name__ == "__main__":
    main()

root.mainloop()

