from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)


# ==============================================================================
# 1. ESTRUCTURA DE DATOS: LA LISTA ENLAZADA (FILA VIRTUAL)
# ==============================================================================
class NodoUsuario:
    def __init__(self, nombre):
        self.nombre = nombre
        self.siguiente = None


class FilaVirtualEnlazada:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.tamaño = 0

    def formar_usuario(self, nombre):
        nuevo_nodo = NodoUsuario(nombre)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo
        self.tamaño += 1

    def dejar_pasar(self):
        if self.cabeza is None:
            return None
        usuario_que_pasa = self.cabeza.nombre
        self.cabeza = self.cabeza.siguiente
        if self.cabeza is None:
            self.cola = None
        self.tamaño -= 1
        return usuario_que_pasa

    def obtener_posicion(self, nombre):
        actual = self.cabeza
        posicion = 1
        while actual:
            if actual.nombre == nombre:
                return posicion
            actual = actual.siguiente
            posicion += 1
        return -1

    def abandonar_fila(self, nombre):
        actual = self.cabeza
        anterior = None
        while actual:
            if actual.nombre == nombre:
                if anterior is None:
                    self.cabeza = actual.siguiente
                    if self.cabeza is None:
                        self.cola = None
                else:
                    anterior.siguiente = actual.siguiente
                    if actual.siguiente is None:
                        self.cola = anterior
                self.tamaño -= 1
                return True
            anterior = actual
            actual = actual.siguiente
        return False


# ==============================================================================
# 2. ALGORITMOS DE ORDENAMIENTO (PANEL DE ADMINISTRADOR)
# ==============================================================================
# Funcion auxiliar para el Bubble Sort (Convierte "A10" en un valor comparable)
def valor_butaca(b):
    return (b[0], int(b[1:]))


def bubble_sort_butacas(arreglo_compras):
    n = len(arreglo_compras)
    for i in range(n):
        for j in range(0, n - i - 1):
            val1 = valor_butaca(arreglo_compras[j]['butaca'])
            val2 = valor_butaca(arreglo_compras[j + 1]['butaca'])
            if val1 > val2:
                arreglo_compras[j], arreglo_compras[j + 1] = arreglo_compras[j + 1], arreglo_compras[j]
    return arreglo_compras


def quick_sort_nombres(arreglo_compras):
    if len(arreglo_compras) <= 1:
        return arreglo_compras
    pivote = arreglo_compras[-1]
    izq = [x for x in arreglo_compras[:-1] if x['nombre'].lower() <= pivote['nombre'].lower()]
    der = [x for x in arreglo_compras[:-1] if x['nombre'].lower() > pivote['nombre'].lower()]
    return quick_sort_nombres(izq) + [pivote] + quick_sort_nombres(der)


# ==============================================================================
# 3. VARIABLES GLOBALES Y CSS BASE
# ==============================================================================
fila_espera = FilaVirtualEnlazada()
zona_pago = []
historial_compras = []

# Crear 30 butacas (Fila A: 1-15, Fila B: 1-15)
butacas_teatro = {f"A{i}": "disponible" for i in range(1, 16)}
butacas_teatro.update({f"B{i}": "disponible" for i in range(1, 16)})

# CSS Global (Ruido, Colores, Fuentes)
CSS_BASE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Arial:wght@400;700&display=swap');

    body {
        background-color: #0d0d0d;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.08'/%3E%3C/svg%3E");
        color: #ffffff;
        font-family: 'Arial', sans-serif;
        margin: 0;
        padding: 0;
    }
    .header {
        background-color: #990000;
        width: 100%;
        padding: 15px 0;
        text-align: center;
        border-bottom: 3px solid #ffcc00;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
    }
    .header h1 {
        font-family: 'UnifrakturMaguntia', cursive;
        color: #000000;
        margin: 0;
        font-size: 40px;
        letter-spacing: 2px;
    }
    .gotico {
        font-family: 'UnifrakturMaguntia', cursive;
    }
    .watermark {
        position: fixed;
        bottom: 10px;
        width: 100%;
        text-align: center;
        font-size: 12px;
        color: rgba(255, 255, 255, 0.3);
    }
    .btn-rojo {
        background-color: #990000;
        color: #ffffff;
        border: 1px solid #ffcc00;
        padding: 10px 20px;
        font-weight: bold;
        cursor: pointer;
        text-transform: uppercase;
        font-family: 'Arial', sans-serif;
    }
    .btn-rojo:hover {
        background-color: #cc0000;
    }
</style>
"""


# ==============================================================================
# 4. LÓGICA DE LA PÁGINA WEB (RUTAS FLASK)
# ==============================================================================
def actualizar_flujo():
    while len(zona_pago) < 3 and fila_espera.cabeza is not None:
        afortunado = fila_espera.dejar_pasar()
        zona_pago.append(afortunado)


# RUTA 1: Pagina Principal (Grid de Eventos)
@app.route('/')
def inicio():
    tarjetas_html = ""
    # Tarjeta 1 (Activa)
    tarjetas_html += """
    <div style="border: 2px solid #ffcc00; background-color: #1a1a1a; padding: 20px; margin: 15px; cursor: pointer; transition: 0.3s;" onclick="window.location.href='/registro'">
        <h2 class="gotico" style="color: #ffcc00; margin-top: 0;">Patricio Rey y sus Redonditos de Ricota Homenaje</h2>
        <p>Lugar: Teatro de la Republica, Queretaro</p>
        <p>Hora: 9:00 pm</p>
        <button class="btn-rojo" style="width: 100%;">Comprar Boletos</button>
    </div>
    """
    # Tarjetas 2 a 8 (Proximamente)
    for _ in range(7):
        tarjetas_html += """
        <div style="border: 2px solid #333; background-color: #111; padding: 20px; margin: 15px; text-align: center; color: #555;">
            <h2 class="gotico">Proximamente</h2>
            <p>Evento por confirmar</p>
        </div>
        """

    html = CSS_BASE + f"""
   <div class="header">
    
    <h1>TicketClancy</h1>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; max-width: 900px; margin: 40px auto;">
        {tarjetas_html}
    </div>
    <div class="watermark">Gracias por usar Clancy Systems</div>
    """
    return render_template_string(html)


# RUTA 2: Registro de Usuario
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        fila_espera.formar_usuario(nombre)
        return redirect(url_for('espera', nombre=nombre))

    html = CSS_BASE + """
    <div class="header"><h1>TicketClancy</h1></div>
    <div style="max-width: 500px; margin: 80px auto; border: 2px solid #990000; background-color: #1a1a1a; padding: 30px; text-align: center;">
        <h2 class="gotico" style="color: #ffcc00;">Informacion del Evento</h2>
        <p>Patricio Rey y sus Redonditos de Ricota Homenaje</p>
        <p>Teatro de la Republica, Queretaro | 9:00 pm</p>
        <hr style="border-color: #333; margin: 20px 0;">
        <form method="POST">
            <label style="display: block; margin-bottom: 10px;">Ingresa tu nombre para continuar:</label>
            <input type="text" name="nombre" required style="width: 90%; padding: 10px; background-color: #000; color: #fff; border: 1px solid #555; margin-bottom: 20px; font-size: 16px;">
            <button type="submit" class="btn-rojo" style="width: 95%;">Ingresar a Seleccion</button>
        </form>
    </div>
    <div class="watermark">Gracias por usar Clancy Systems</div>
    """
    return render_template_string(html)


# RUTA 3: Fila Virtual
@app.route('/espera/<nombre>')
def espera(nombre):
    actualizar_flujo()
    if nombre in zona_pago:
        return redirect(url_for('comprar', nombre=nombre))

    posicion = fila_espera.obtener_posicion(nombre)

    html = CSS_BASE + f"""
    <head><meta http-equiv="refresh" content="3"></head>
    <div class="header"><h1>TicketClancy</h1></div>
    <div style="text-align: center; margin-top: 100px;">
        <h1 class="gotico" style="color: #ffcc00; font-size: 50px;">Estas en la fila virtual...</h1>
        <p style="color: #990000; font-size: 24px; font-weight: bold;">Posicion: #{posicion}</p>
        <p style="font-size: 18px; color: #fff;">Por favor espera a que sea tu turno, no salgas ni recargues la pagina</p>
    </div>
    <div class="watermark">Gracias por usar Clancy Systems</div>
    """
    return render_template_string(html)


# RUTA 4: Zona de Compra (Imagen de fondo literal con botones superpuestos)
@app.route('/comprar/<nombre>', methods=['GET', 'POST'])
def comprar(nombre):
    if nombre not in zona_pago:
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        butaca_elegida = request.form.get('butaca')
        if butacas_teatro[butaca_elegida] == "disponible":
            butacas_teatro[butaca_elegida] = "ocupada"
            historial_compras.append({"nombre": nombre, "butaca": butaca_elegida})
            zona_pago.remove(nombre)
            actualizar_flujo()
            return redirect(url_for('confirmacion', nombre=nombre, butaca=butaca_elegida))

    # Diccionario con las coordenadas de cada boton sobre la imagen.
    # Los valores "top" y "left" estan en porcentajes.
    # Aqui vas a modificar los numeros para que los botones cuadren perfecto sobre tu foto.
    coordenadas = {
        # Ala Izquierda (B exterior, A interior)
        "B1": {"top": "20%", "left": "15%"}, "A1": {"top": "20%", "left": "25%"},
        "B2": {"top": "32%", "left": "12%"}, "A2": {"top": "32%", "left": "22%"},
        "B3": {"top": "44%", "left": "10%"}, "A3": {"top": "44%", "left": "20%"},
        "B4": {"top": "56%", "left": "11%"}, "A4": {"top": "56%", "left": "21%"},
        "B5": {"top": "68%", "left": "14%"}, "A5": {"top": "68%", "left": "24%"},

        # Centro (A mas cerca del escenario arriba, B mas lejos abajo)
        "A6": {"top": "75%", "left": "32%"}, "B6": {"top": "88%", "left": "32%"},
        "A7": {"top": "77%", "left": "41%"}, "B7": {"top": "90%", "left": "41%"},
        "A8": {"top": "78%", "left": "50%"}, "B8": {"top": "91%", "left": "50%"},
        "A9": {"top": "77%", "left": "59%"}, "B9": {"top": "90%", "left": "59%"},
        "A10": {"top": "75%", "left": "68%"}, "B10": {"top": "88%", "left": "68%"},

        # Ala Derecha (A interior, B exterior)
        "A11": {"top": "20%", "left": "75%"}, "B11": {"top": "20%", "left": "85%"},
        "A12": {"top": "32%", "left": "78%"}, "B12": {"top": "32%", "left": "88%"},
        "A13": {"top": "44%", "left": "80%"}, "B13": {"top": "44%", "left": "90%"},
        "A14": {"top": "56%", "left": "79%"}, "B14": {"top": "56%", "left": "89%"},
        "A15": {"top": "68%", "left": "76%"}, "B15": {"top": "68%", "left": "86%"},
    }

    botones_html = ""
    for asiento, coords in coordenadas.items():
        estado = butacas_teatro[asiento]
        # Colores de TicketClancy con un poco de transparencia para que se funda con la foto
        color_fondo = "rgba(40, 167, 69, 0.9)" if estado == "disponible" else "rgba(153, 0, 0, 0.9)"
        color_texto = "#ffffff"
        borde = "2px solid #fff" if estado == "disponible" else "2px solid #330000"
        disabled = "" if estado == "disponible" else "disabled"
        cursor = "pointer" if estado == "disponible" else "not-allowed"

        # Cada boton se posiciona de manera absoluta sobre la imagen usando top y left
        botones_html += f"""
        <button name='butaca' value='{asiento}' 
            style='position: absolute; top: {coords["top"]}; left: {coords["left"]}; transform: translate(-50%, -50%);
            width: 45px; height: 35px; background-color: {color_fondo}; color: {color_texto}; 
            border: {borde}; border-radius: 4px; font-size: 12px; font-weight: bold; cursor: {cursor}; 
            transition: transform 0.1s;' 
            onmouseover='if(!this.disabled)this.style.transform=\"translate(-50%, -50%) scale(1.1)\"' 
            onmouseout='this.style.transform=\"translate(-50%, -50%) scale(1)\"' {disabled}>
            {asiento}
        </button>
        """

    html = CSS_BASE + f"""
    <div class="header">
        <h1>TicketClancy</h1>
        <a href="/salir/{nombre}" style="position: absolute; right: 20px;"><button class="btn-rojo">Cancelar y Regresar</button></a>
    </div>

    <div style="text-align: center; margin-top: 20px;">
        <h2 style="color: #ffcc00; font-size: 28px; margin-bottom: 5px;">Selecciona tu Butaca, {nombre}</h2>
        <div style="display: flex; justify-content: center; gap: 20px; color: #ccc; font-size: 14px; margin-top: 10px;">
            <span style="display: flex; align-items: center; gap: 5px;"><div style="width: 15px; height: 15px; background-color: #28a745; border-radius: 3px;"></div> Disponible</span>
            <span style="display: flex; align-items: center; gap: 5px;"><div style="width: 15px; height: 15px; background-color: #990000; border-radius: 3px;"></div> Ocupado</span>
        </div>
    </div>

    <form method="POST" style="position: relative; width: 800px; height: 500px; margin: 30px auto; background-image: url('/static/mapa.png'); background-size: 100% 100%; background-position: center; border: 2px solid #555; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.8);">
        {botones_html}
        <div style="position: absolute; top: 30%; left: 50%; transform: translate(-50%, -50%); width: 350px; height: 90px; background: linear-gradient(180deg, #2a2a2a 0%, #0a0a0a 100%); border: 2px solid #990000; border-radius: 8px; display: flex; justify-content: center; align-items: center; box-shadow: 0 5px 15px rgba(0,0,0,0.6);">
    <h2 class="gotico" style="color: #ffffff; margin: 0; letter-spacing: 8px; font-size: 38px; text-shadow: 2px 2px 5px #000000;">Escenario</h2>
</div>
    </form>

    <div class="watermark">Gracias por usar Clancy Systems</div>
    """
    return render_template_string(html)

# RUTA 5: Confirmacion de Compra
@app.route('/confirmacion/<nombre>/<butaca>')
def confirmacion(nombre, butaca):
    html = CSS_BASE + f"""
    <div class="header"><h1>TicketClancy</h1></div>
    <div style="max-width: 600px; margin: 80px auto; border: 2px solid #ffcc00; background-color: #1a1a1a; padding: 40px; text-align: center;">
        <h1 class="gotico" style="color: #28a745;">Gracias por tu compra</h1>
        <hr style="border-color: #333;">
        <h2 style="color: #ffcc00;">Resumen de tu compra</h2>
        <div style="text-align: left; margin-left: 20%; font-size: 18px; line-height: 1.8;">
            <p><strong>Comprador:</strong> {nombre}</p>
            <p><strong>Artista:</strong> Patricio Rey y sus Redonditos de Ricota Homenaje</p>
            <p><strong>Recinto:</strong> Teatro de la Republica</p>
            <p><strong>Hora:</strong> 9:00 pm</p>
            <p><strong>Asiento Asignado:</strong> <span style="color: #ffcc00; font-weight: bold; font-size: 24px;">{butaca}</span></p>
        </div>
        <br>
        <a href="/"><button class="btn-rojo" style="width: 80%; padding: 15px; font-size: 18px;">Volver a la pagina principal</button></a>
    </div>
    <div class="watermark">Gracias por usar Clancy Systems</div>
    """
    return render_template_string(html)


# RUTA 6: Abandonar Fila (Oculta)
@app.route('/salir/<nombre>')
def salir(nombre):
    if nombre in zona_pago:
        zona_pago.remove(nombre)
    else:
        fila_espera.abandonar_fila(nombre)
    actualizar_flujo()
    return redirect(url_for('inicio'))


# RUTA 7: Panel de Administrador
@app.route('/admin')
def admin():
    filtro = request.args.get('orden', 'original')
    datos_mostrar = historial_compras.copy()

    if filtro == 'butaca':
        datos_mostrar = bubble_sort_butacas(datos_mostrar)
    elif filtro == 'alfabetico':
        datos_mostrar = quick_sort_nombres(datos_mostrar)

    tabla_html = ""
    for dato in datos_mostrar:
        tabla_html += f"<tr style='border-bottom: 1px solid #333;'><td style='padding: 15px;'>{dato['nombre']}</td><td style='padding: 15px; color: #ffcc00;'>{dato['butaca']}</td></tr>"

    html = CSS_BASE + f"""
    <div class="header"><h1>TicketClancy - Panel Admin</h1></div>
    <div style="text-align: center; margin-top: 50px;">
        <h2 class="gotico" style="color: #fff; font-size: 36px;">Registro de Ventas</h2>
        <div style="margin-bottom: 30px; display: flex; justify-content: center; gap: 15px;">
            <a href="/admin?orden=original"><button class="btn-rojo" style="background-color: #333; border-color: #555;">Orden Original</button></a>
            <a href="/admin?orden=butaca"><button class="btn-rojo">Ordenar por Butaca (Bubble)</button></a>
            <a href="/admin?orden=alfabetico"><button class="btn-rojo" style="border-color: #fff;">Ordenar A-Z (Quick)</button></a>
        </div>
        <table style="margin: 0 auto; width: 70%; font-size: 20px; border-collapse: collapse; background-color: #111; border: 2px solid #990000;">
            <tr style="background-color: #990000; color: #000;">
                <th style="padding: 15px; font-family: 'UnifrakturMaguntia', cursive;">Nombre del Comprador</th>
                <th style="padding: 15px; font-family: 'UnifrakturMaguntia', cursive;">Numero de Butaca</th>
            </tr>
            {tabla_html}
        </table>
    </div>
    """
    return render_template_string(html)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
