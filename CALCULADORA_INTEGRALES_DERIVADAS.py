import re
import tkinter as tk
from tkinter import messagebox, simpledialog
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor
)
import plotly.graph_objects as go
import numpy as np

# Transformaciones para permitir 2t -> 2*t y ^ -> **
transformations = standard_transformations + (implicit_multiplication_application, convert_xor)

# ===============================
# FUNCIONES LÓGICAS
# ===============================

def crear_diccionario_simbolos(texto):
    conocidos = {
        'sin', 'cos', 'tan', 'sec', 'csc', 'cot',
        'asin', 'acos', 'atan',
        'sinh', 'cosh', 'tanh',
        'exp', 'ln', 'log', 'sqrt',
        'pi', 'E', 'I'
    }
    ids = set(re.findall(r'[A-Za-z_]\w*', texto))
    ids = {i for i in ids if not i.isdigit()}
    local = {}
    for ident in ids:
        if ident in conocidos:
            continue
        local[ident] = sp.Symbol(ident)
    return local

def insertar_texto(texto):
    entrada.insert(tk.END, texto)
    verificar_expresion()

def limpiar():
    entrada.delete(0, tk.END)
    resultado_var.set("")
    estado_var.set("")

def parsear_expresion(texto):
    local = crear_diccionario_simbolos(texto)
    return parse_expr(texto, local_dict=local, transformations=transformations, evaluate=False)

# === FUNCIONES PASO A PASO ===

def paso_a_paso_derivada():
    try:
        texto = entrada.get()
        expr = parsear_expresion(texto)
        simbolos = list(expr.free_symbols)
        pasos = []
        for v in simbolos:
            deriv = sp.diff(expr, v)
            pasos.append(f"Derivar respecto a {v}: d/d{v}({expr}) = {deriv}")
        resultado_var.set("\n".join(pasos))
    except Exception as e:
        messagebox.showerror("Error", f"Expresión inválida\n{e}")

def paso_a_paso_integral():
    try:
        texto = entrada.get()
        expr = parsear_expresion(texto)
        simbolos = list(expr.free_symbols)
        pasos = []
        for v in simbolos:
            integ = sp.integrate(expr, v)
            pasos.append(f"Integral indefinida respecto a {v}: ∫({expr}) d{v} = {integ} + C")
        resultado_var.set("\n".join(pasos))
    except Exception as e:
        messagebox.showerror("Error", f"Expresión inválida\n{e}")

def paso_a_paso_integral_definida():
    try:
        texto = entrada.get()
        expr = parsear_expresion(texto)
        a = float(limite_inferior.get())
        b = float(limite_superior.get())
        simbolos = list(expr.free_symbols)
        pasos = []
        for v in simbolos:
            integ = sp.integrate(expr, v)
            evaluado = integ.subs(v, b) - integ.subs(v, a)
            paso_str = (
                f"Para {v}:\n"
                f"∫[{a},{b}] ({expr}) d{v} = {integ.subs(v, b)} - {integ.subs(v, a)} = {evaluado}"
            )
            pasos.append(paso_str)
        resultado_var.set("\n\n".join(pasos))
    except Exception as e:
        messagebox.showerror("Error", f"Verifica la función y los límites\n{e}")

# === FUNCIONES PARA SUPERÍNDICES Y SUBÍNDICES ===

def insertar_superindice():
    try:
        n = simpledialog.askstring("Superíndice", "Ingresa el exponente:")
        if n:
            insertar_texto(f"**{n}")
    except Exception:
        messagebox.showerror("Error", "Entrada inválida")

def insertar_subindice():
    try:
        n = simpledialog.askstring("Subíndice", "Ingresa el subíndice:")
        if n:
            insertar_texto(f"_{n}")
    except Exception:
        messagebox.showerror("Error", "Entrada inválida")

# === VALIDACIÓN EN TIEMPO REAL ===

def verificar_expresion(event=None):
    texto = entrada.get()
    if not texto.strip():
        estado_var.set("")
        return
    try:
        parsear_expresion(texto)
        estado_var.set("✅ Expresión válida")
        etiqueta_estado.config(fg="#00ff88")
    except Exception:
        estado_var.set("❌ Error de sintaxis")
        etiqueta_estado.config(fg="#ff4444")

# === FUNCIONES DE GRAFICACIÓN ===

def mostrar_grafica():
    try:
        texto = entrada.get()
        expr = parsear_expresion(texto)
        simbolos = list(expr.free_symbols)
        if not simbolos:
            messagebox.showerror("Error", "La función no tiene variables para graficar")
            return

        rango_str = simpledialog.askstring("Rango de graficación",
                                           "Ingresa el rango como mínimo,máximo (ej: -10,10):")
        if not rango_str:
            return
        min_r, max_r = map(float, rango_str.split(','))

        for var in simbolos:
            x_vals = np.linspace(min_r, max_r, 500)
            y_vals = [float(expr.subs(var, v)) for v in x_vals]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name=str(expr)))
            fig.update_layout(title=f"Gráfica de {expr} respecto a {var}",
                              xaxis_title=str(var),
                              yaxis_title="f("+str(var)+")",
                              template="plotly_dark")
            fig.show()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo graficar la función\n{e}")

# ===============================
# INTERFAZ GRÁFICA
# ===============================

ventana = tk.Tk()
ventana.title("Calculadora de Derivadas e Integrales")
ventana.geometry("440x650")
ventana.config(bg="#2c2f33")

tk.Label(ventana, text="🧮 Calculadora de Cálculo Simbólico",
         bg="#2c2f33", fg="white", font=("Arial", 14, "bold")).pack(pady=10)

entrada = tk.Entry(ventana, font=("Consolas", 16), justify="center", width=32)
entrada.pack(pady=10)
entrada.bind("<KeyRelease>", verificar_expresion)

estado_var = tk.StringVar()
etiqueta_estado = tk.Label(ventana, textvariable=estado_var,
                           bg="#2c2f33", fg="white", font=("Arial", 10, "italic"))
etiqueta_estado.pack()

frame_botones = tk.Frame(ventana, bg="#23272a")
frame_botones.pack(pady=5)

botones = [
    "x", "sin(x)", "cos(x)", "tan(x)", "exp(x)", "ln(x)",
    "pi", "E", "+", "-", "*", "/", "(", ")"
]

fila = 0
col = 0
for b in botones:
    tk.Button(frame_botones, text=b, width=6, height=2, bg="#99aab5", fg="black",
              command=lambda t=b: insertar_texto(t)).grid(row=fila, column=col, padx=3, pady=3)
    col += 1
    if col > 4:
        col = 0
        fila += 1

frame_extras = tk.Frame(ventana, bg="#2c2f33")
frame_extras.pack(pady=5)

tk.Button(frame_extras, text="xⁿ (superior)", bg="#7289da", fg="white", width=14, height=2,
          command=insertar_superindice).grid(row=0, column=0, padx=5)
tk.Button(frame_extras, text="xₙ (inferior)", bg="#43b581", fg="white", width=14, height=2,
          command=insertar_subindice).grid(row=0, column=1, padx=5)

frame_operaciones = tk.Frame(ventana, bg="#2c2f33")
frame_operaciones.pack(pady=10)

tk.Button(frame_operaciones, text="Derivada", bg="#7289da", fg="white", width=12, height=2,
          command=paso_a_paso_derivada).grid(row=0, column=0, padx=5)
tk.Button(frame_operaciones, text="Integral", bg="#43b581", fg="white", width=12, height=2,
          command=paso_a_paso_integral).grid(row=0, column=1, padx=5)
tk.Button(frame_operaciones, text="Integral definida", bg="#faa61a", fg="white", width=15, height=2,
          command=paso_a_paso_integral_definida).grid(row=0, column=2, padx=5)
tk.Button(frame_operaciones, text="Mostrar gráfica", bg="#ff5555", fg="white", width=15, height=2,
          command=mostrar_grafica).grid(row=1, column=1, padx=5, pady=5)

frame_limites = tk.Frame(ventana, bg="#2c2f33")
frame_limites.pack(pady=5)

tk.Label(frame_limites, text="Límite inferior:", bg="#2c2f33", fg="white").grid(row=0, column=0)
limite_inferior = tk.Entry(frame_limites, width=5)
limite_inferior.grid(row=0, column=1, padx=5)

tk.Label(frame_limites, text="Límite superior:", bg="#2c2f33", fg="white").grid(row=0, column=2)
limite_superior = tk.Entry(frame_limites, width=5)
limite_superior.grid(row=0, column=3, padx=5)

resultado_var = tk.StringVar()
tk.Label(ventana, textvariable=resultado_var, bg="#23272a", fg="#00ff88",
         font=("Consolas", 14), wraplength=380, justify="center").pack(pady=15)

tk.Button(ventana, text="Limpiar", bg="#99aab5", width=12, command=limpiar).pack(pady=5)

ventana.mainloop()
