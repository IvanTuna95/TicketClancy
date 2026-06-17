from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# ==============================================================================
# 1. ESTRUCTURA DE DATOS: LA LISTA ENLAZADA (FILA VIRTUAL)
# ==============================================================================
# Aquí creamos los Nodos. Cada persona que entra a la página es un "Nodo".
class NodoUsuario:
    def __init__(self, nombre):
        self.nombre = nombre
        self.siguiente = None # El puntero mágico que conecta con el de atrás

class FilaVirtualEnlazada:
    def __init__(self):
        self.cabeza = None # El primero de la fila
        self.cola = None   # El último de la fila
        self.tamaño = 0    # Cuántos hay formados

    # Método para formar a alguien (Insertar al final)
    def formar_usuario(self, nombre):
        nuevo_nodo = NodoUsuario(nombre)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo
        self.tamaño += 1

    # Método para dejar pasar al primero (Eliminar al inicio)
    def dejar_pasar(self):
        if self.cabeza is None:
            return None
        usuario_que_pasa = self.cabeza.nombre
        self.cabeza = self.cabeza.siguiente # Rompemos el enlace y el 2do pasa a ser el 1ro
        if self.cabeza is None:
            self.cola = None
        self.tamaño -= 1
        return usuario_que_pasa

    # Para saber en qué posición está alguien específico
    def obtener_posicion(self, nombre):
        actual = self.cabeza
        posicion = 1
        while actual:
            if actual.nombre == nombre:
                return posicion
            actual = actual.siguiente
            posicion += 1
        return -1


# ==============================================================================
# 2. ALGORITMOS DE ORDENAMIENTO (PANEL DE ADMINISTRADOR)
# ==============================================================================
# Estos algoritmos reciben el arreglo final de las compras para organizarlo.

# BUBBLE SORT: Ordena el arreglo basándose en el número de butaca.
# Es visual y didáctico para datos numéricos pequeños.
def bubble_sort_butacas(arreglo_compras):
    n = len(arreglo_compras)
    for i in range(n):
        for j in range(0, n - i - 1):
            # Comparamos el valor de la "butaca"
            if arreglo_compras[j]['butaca'] > arreglo_compras[j + 1]['butaca']:
                # Intercambiamos si están en el orden equivocado
                arreglo_compras[j], arreglo_compras[j + 1] = arreglo_compras[j + 1], arreglo_compras[j]
    return arreglo_compras

# QUICK SORT: Ordena el arreglo alfabéticamente por el nombre del usuario.
# Usa la técnica de "Divide y Vencerás" usando un pivote.
def quick_sort_nombres(arreglo_compras):
    if len(arreglo_compras) <= 1:
        return arreglo_compras
    pivote = arreglo_compras[-1]
    # Comparamos strings alfabéticamente
    izq = [x for x in arreglo_compras[:-1] if x['nombre'].lower() <= pivote['nombre'].lower()]
    der = [x for x in arreglo_compras[:-1] if x['nombre'].lower() > pivote['nombre'].lower()]
    
    return quick_sort_nombres(izq) + [pivote] + quick_sort_nombres(der)


# ==============================================================================
# 3. VARIABLES GLOBALES (El cerebro del Teatro de la República)
# ==============================================================================
fila_espera = FilaVirtualEnlazada()
zona_pago = [] # Arreglo que soporta un MÁXIMO de 3 personas simultáneas
historial_compras = [] # Arreglo de diccionarios para el Administrador

# Creamos 20 butacas simuladas para el Teatro
butacas_teatro = {i: "disponible" for i in range(1, 21)}


# ==============================================================================
# 4. LÓGICA DE LA PÁGINA WEB (RUTAS FLASK)
# ==============================================================================

# Función clave: Mueve a la gente de la Lista Enlazada a la Zona de Pago (Max 3)
def actualizar_flujo():
    while len(zona_pago) < 3 and fila_espera.cabeza is not None:
        afortunado = fila_espera.dejar_pasar()
        zona_pago.append(afortunado)

# RUTA 1: Pantalla de Bienvenida (Registro)
@app.route('/', methods=['GET', 'POST'])
def inicio():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        # Formamos al usuario en la Lista Enlazada
        fila_espera.formar_usuario(nombre)
        return redirect(url_for('espera', nombre=nombre))
    
    html = """
    <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
        <h1>🎭 Teatro de la República (Querétaro)</h1>
        <h2>Sistema de Boletos Exclusivo</h2>
        <form method="POST">
            <input type="text" name="nombre" placeholder="Ingresa tu nombre" required style="padding: 10px; font-size: 16px;">
            <button type="submit" style="padding: 10px; font-size: 16px; background-color: #28a745; color: white;">Unirse a la Fila</button>
        </form>
    </div>
    """
    return render_template_string(html)

# RUTA 2: Fila Virtual (Con Auto-Refresh cada 3 segundos)
@app.route('/espera/<nombre>')
def espera(nombre):
    actualizar_flujo() # Checamos si ya hay espacio en los 3 lugares
    
    # Si el usuario ya avanzó a la zona de pago, lo mandamos a comprar
    if nombre in zona_pago:
        return redirect(url_for('comprar', nombre=nombre))
    
    posicion = fila_espera.obtener_posicion(nombre)
    
    html = f"""
    <head><meta http-equiv="refresh" content="3"></head> 
    <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
        <h1>⏳ Fila Virtual</h1>
        <h2>Hola {nombre}, estás en la posición: <strong style="color: red; font-size: 40px;">#{posicion}</strong></h2>
        <p>El sistema se actualiza automáticamente. No cierres la ventana.</p>
        <p><em>Personas comprando actualmente: {len(zona_pago)}/3</em></p>
    </div>
    """
    return render_template_string(html)

# RUTA 3: Zona de Compra (Mapa de Butacas)
@app.route('/comprar/<nombre>', methods=['GET', 'POST'])
def comprar(nombre):
    if nombre not in zona_pago:
        return redirect(url_for('inicio'))
        
    if request.method == 'POST':
        butaca_elegida = int(request.form.get('butaca'))
        if butacas_teatro[butaca_elegida] == "disponible":
            # Cambiamos estado y guardamos en historial
            butacas_teatro[butaca_elegida] = "ocupada"
            historial_compras.append({"nombre": nombre, "butaca": butaca_elegida})
            # Lo sacamos de la zona de pago para liberar el lugar a otro
            zona_pago.remove(nombre)
            actualizar_flujo()
            return f"<h1 style='text-align:center; color:green; margin-top:50px;'>¡Boleto {butaca_elegida} comprado con éxito, {nombre}! 🎉</h1>"

    # Generar el HTML de las butacas
    botones_butacas = ""
    for num, estado in butacas_teatro.items():
        color = "green" if estado == "disponible" else "red"
        disabled = "" if estado == "disponible" else "disabled"
        botones_butacas += f"<button name='butaca' value='{num}' style='background-color:{color}; color:white; margin:5px; padding:15px;' {disabled}>Butaca {num}</button>"

    html = f"""
    <div style="text-align: center; margin-top: 20px; font-family: sans-serif;">
        <h1>🎟️ ¡Es tu turno, {nombre}!</h1>
        <h2>Selecciona tu butaca (Max 3 personas aquí)</h2>
        <form method="POST" style="max-width: 400px; margin: 0 auto;">
            {botones_butacas}
        </form>
    </div>
    """
    return render_template_string(html)

# RUTA 4: Panel del Administrador (Para presumir los algoritmos de Sort)
@app.route('/admin')
def admin():
    filtro = request.args.get('orden', 'original')
    
    # Copiamos el arreglo para no alterar el original directamente
    datos_mostrar = historial_compras.copy()
    
    # Aplicamos los algoritmos según el botón que presione el profesor
    if filtro == 'butaca':
        datos_mostrar = bubble_sort_butacas(datos_mostrar)
    elif filtro == 'alfabetico':
        datos_mostrar = quick_sort_nombres(datos_mostrar)

    tabla_html = ""
    for dato in datos_mostrar:
        tabla_html += f"<tr><td>{dato['nombre']}</td><td>{dato['butaca']}</td></tr>"

    html = f"""
    <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
        <h1>🔒 Panel de Administrador</h1>
        <div style="margin-bottom: 20px;">
            <a href="/admin?orden=original"><button style="padding:10px;">Orden de Llegada</button></a>
            <a href="/admin?orden=butaca"><button style="padding:10px; background-color:orange;">Ordenar por Butaca (Bubble Sort)</button></a>
            <a href="/admin?orden=alfabetico"><button style="padding:10px; background-color:lightblue;">Ordenar A-Z (Quick Sort)</button></a>
        </div>
        <table border="1" style="margin: 0 auto; width: 50%; font-size: 18px; border-collapse: collapse;">
            <tr><th>Nombre del Comprador</th><th>Número de Butaca</th></tr>
            {tabla_html}
        </table>
    </div>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)