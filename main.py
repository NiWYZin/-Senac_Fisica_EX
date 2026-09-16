"""Ponto de entrada da aplicação de lançamento de objetos.

Dependências:
    pip install matplotlib numpy

Execução:
    python main.py
"""

import tkinter as tk
from tkinter import ttk

from fisica import (
    ParametrosLancamento,
    ResultadoLancamento,
    SimuladorProjetil,
    calcular_resultados,
    calcular_trajetoria,
)
from interface import ProjetilApp


def main():
    root = tk.Tk()

    style = ttk.Style()
    try:
        style.theme_use("vista")
    except tk.TclError:
        pass

    ProjetilApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
