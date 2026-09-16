"""Interface gráfica do simulador de lançamento de objetos."""

from bisect import bisect_left
import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from fisica import ParametrosLancamento, SimuladorProjetil

ESPESSURA_TRAJETORIA = 2.0


class ProjetilApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lançamento de Objetos — Física")
        self.root.geometry("1200x760")
        self.root.minsize(1050, 680)

        self.animacao = None
        self.valores_validos = None

        self.v0_var = tk.DoubleVar(value=30.0)
        self.theta_var = tk.DoubleVar(value=45.0)
        self.y0_var = tk.DoubleVar(value=0.0)
        self.g_var = tk.DoubleVar(value=9.81)

        self._criar_interface()
        self.atualizar_grafico()

    def _criar_interface(self):
        painel = ttk.Frame(self.root, padding=12)
        painel.pack(fill="both", expand=True)

        controles = ttk.Frame(painel, width=320)
        controles.pack(side="left", fill="y", padx=(0, 12))
        controles.pack_propagate(False)

        grafico_frame = ttk.Frame(painel)
        grafico_frame.pack(side="right", fill="both", expand=True)

        ttk.Label(
            controles,
            text="Lançamento de Objetos",
            font=("TkDefaultFont", 15, "bold"),
        ).pack(anchor="w", pady=(0, 14))

        self._adicionar_slider(
            controles, "Velocidade inicial v₀ (m/s)", self.v0_var, 5, 150, 1, 30
        )
        self._adicionar_slider(
            controles, "Ângulo θ (graus)", self.theta_var, 1, 89, 1, 45
        )
        self._adicionar_slider(
            controles, "Altura inicial y₀ (m)", self.y0_var, 0, 50, 1, 0
        )
        self._adicionar_slider(
            controles, "Gravidade g (m/s²)", self.g_var, 1.6, 24.8, 0.01, 9.81
        )

        botoes = ttk.Frame(controles)
        botoes.pack(fill="x", pady=(0, 12))

        ttk.Button(botoes, text="Lançar", command=self.iniciar_animacao).pack(
            side="left", fill="x", expand=True, padx=(0, 5)
        )
        ttk.Button(botoes, text="Parar", command=self.parar_animacao).pack(
            side="left", fill="x", expand=True, padx=(5, 0)
        )

        ttk.Button(
            controles,
            text="Adicionar trajetória",
            command=self.adicionar_trajetoria,
        ).pack(fill="x", pady=(0, 6))
        ttk.Button(
            controles,
            text="Limpar trajetórias",
            command=self.limpar_trajetorias,
        ).pack(fill="x")

        ttk.Separator(controles, orient="horizontal").pack(fill="x", pady=12)
        ttk.Label(
            controles, text="Resultados", font=("TkDefaultFont", 11, "bold")
        ).pack(anchor="w", pady=(0, 7))

        self.resultados_label = ttk.Label(controles, text="", justify="left")
        self.resultados_label.pack(anchor="w")

        ttk.Separator(controles, orient="horizontal").pack(fill="x", pady=12)
        ttk.Label(
            controles,
            text=(
                "As alterações nos controles atualizam a curva e os resultados "
                "automaticamente. O modelo considera ausência de resistência do ar."
            ),
            wraplength=285,
            justify="left",
        ).pack(anchor="w")

        self.fig = Figure(figsize=(8, 5.8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Distância horizontal x (m)")
        self.ax.set_ylabel("Altura y (m)")
        self.ax.grid(True, alpha=0.25)
        self.ax.set_aspect("equal", adjustable="datalim")

        self.trajetoria_atual, = self.ax.plot(
            [], [], linewidth=ESPESSURA_TRAJETORIA, label="Atual"
        )
        self.projetil, = self.ax.plot(
            [],
            [],
            "o",
            color=self.trajetoria_atual.get_color(),
            markersize=8,
            label="Objeto",
        )
        self.velocimetro_textos = []
        self.trajetorias_anteriores = []
        self.dados_trajetorias = []
        self.projeteis_extras = []
        self._atualizar_legenda()
        self._atualizar_velocimetro([0], [self.projetil.get_color()])

        self.canvas = FigureCanvasTkAgg(self.fig, master=grafico_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _adicionar_slider(self, parent, texto, variable, minimo, maximo, passo, valor):
        ttk.Label(parent, text=texto).pack(anchor="w")
        scale = ttk.Scale(
            parent,
            from_=minimo,
            to=maximo,
            variable=variable,
            orient="horizontal",
        )
        scale.pack(fill="x", pady=(2, 0))

        entrada = ttk.Entry(parent, width=12)
        entrada.pack(anchor="w", pady=(2, 10))
        entrada.insert(0, str(valor))

        def sincronizar_entry(_event=None):
            try:
                variable.set(float(entrada.get().replace(",", ".")))
                self._entrada_alterada()
            except ValueError:
                pass

        def sincronizar_scale(_value=None):
            entrada.delete(0, tk.END)
            if passo >= 1:
                entrada.insert(0, f"{variable.get():.0f}")
            else:
                entrada.insert(0, f"{variable.get():.2f}")
            self._entrada_alterada()

        entrada.bind("<Return>", sincronizar_entry)
        entrada.bind("<FocusOut>", sincronizar_entry)
        scale.configure(command=sincronizar_scale)

    def _entrada_alterada(self):
        # Cada alteração em um campo ou slider recalcula a física e redesenha a curva.
        self.atualizar_grafico()

    def ler_parametros(self):
        parametros = ParametrosLancamento(
            velocidade=float(self.v0_var.get()),
            angulo=float(self.theta_var.get()),
            altura=float(self.y0_var.get()),
            gravidade=float(self.g_var.get()),
        )
        parametros.validar()
        return parametros

    def atualizar_grafico(self):
        try:
            parametros = self.ler_parametros()
            simulador = SimuladorProjetil(parametros)
            self.valores_validos = parametros
        except (ValueError, TypeError):
            self.resultados_label.config(
                text="Entrada inválida.\nCorrija os valores dos controles."
            )
            return

        resultado = simulador.calcular_resultados()
        _tempo, x, y = simulador.calcular_trajetoria()
        self.trajetoria_atual.set_data(x, y)
        self.trajetoria_atual.set_label(
            f"{parametros.velocidade:.0f} m/s, {parametros.angulo:.0f}°"
        )
        self.projetil.set_data([x[0]], [y[0]])
        self._atualizar_velocimetro(
            [parametros.velocidade], [self.projetil.get_color()]
        )

        # A escala acompanha os dados para não cortar lançamentos extremos.
        todas_as_trajetorias = [(x, y), *[(x, y) for _, x, y, _, _ in self.dados_trajetorias]]
        maior_x = max(float(trajetoria_x.max()) for trajetoria_x, _ in todas_as_trajetorias)
        maior_y = max(float(trajetoria_y.max()) for _, trajetoria_y in todas_as_trajetorias)

        limite_x = max(1, maior_x * 1.1)
        limite_y = max(1, maior_y * 1.1)
        posicao = self.ax.get_position()
        proporcao_caixa = (
            posicao.width * self.fig.get_figwidth()
        ) / (posicao.height * self.fig.get_figheight())

        # Expande apenas o eixo menor para que a escala igual não corte a curva.
        if limite_x / limite_y > proporcao_caixa:
            limite_y = limite_x / proporcao_caixa
        else:
            limite_x = limite_y * proporcao_caixa

        self.ax.set_xlim(0, limite_x)
        self.ax.set_ylim(0, limite_y)
        # A caixa visual permanece fixa; os limites numéricos se ajustam mantendo
        # a mesma escala física nos dois eixos para preservar o ângulo da curva.
        self.ax.set_aspect("equal", adjustable="datalim")
        self.resultados_label.config(
            text=(
                f"Alcance R: {resultado.alcance:.2f} m\n"
                f"Altura máxima: {resultado.altura_maxima:.2f} m\n"
                f"Tempo de voo: {resultado.tempo_voo:.2f} s\n\n"
                f"v₀ = {parametros.velocidade:.2f} m/s\n"
                f"θ = {parametros.angulo:.2f}°\n"
                f"y₀ = {parametros.altura:.2f} m\n"
                f"g = {parametros.gravidade:.2f} m/s²"
            )
        )
        self._atualizar_legenda()
        self.canvas.draw_idle()

    def _atualizar_legenda(self):
        """Mantém o marcador do objeto acima da linha da trajetória atual."""
        elementos = [self.projetil, self.trajetoria_atual, *self.trajetorias_anteriores]
        self.ax.legend(elementos, [elemento.get_label() for elemento in elementos], loc="best")

    def _atualizar_velocimetro(self, velocidades, cores):
        for texto in self.velocimetro_textos:
            texto.remove()
        self.velocimetro_textos.clear()

        for indice, (velocidade, cor) in enumerate(zip(velocidades, cores), start=1):
            texto = self.ax.text(
                0.03,
                0.97 - (indice - 1) * 0.05,
                f"O{indice}: {velocidade:.2f} m/s",
                color=cor,
                transform=self.ax.transAxes,
                va="top",
                bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "0.7"},
            )
            self.velocimetro_textos.append(texto)

    def iniciar_animacao(self):
        self.parar_animacao()
        self._remover_projeteis_extras()
        try:
            parametros = self.ler_parametros()
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Entrada inválida", str(exc))
            return

        simulador = SimuladorProjetil(parametros)
        tempo_atual, x_atual, y_atual = simulador.calcular_trajetoria(
            quantidade_pontos=240
        )
        velocidades_atual = simulador.calcular_velocidades(tempo_atual)
        trajetorias = [
            (
                tempo_atual,
                x_atual,
                y_atual,
                velocidades_atual,
                self.trajetoria_atual.get_color(),
            ),
            *self.dados_trajetorias,
        ]
        projeteis = [self.projetil]

        for tempo, _, _, _, cor in trajetorias[1:]:
            projetil, = self.ax.plot(
                [],
                [],
                "o",
            color=cor,
                markersize=8,
                alpha=0.9,
                label="_nolegend_",
            )
            self.projeteis_extras.append(projetil)
            projeteis.append(projetil)

        duracao_fisica = max(float(tempo[-1]) for tempo, _, _, _, _ in trajetorias)
        quantidade_frames = 240
        duracao_ms = max(1600, min(7000, int(duracao_fisica * 700)))

        def atualizar(frame):
            fracao = frame / (quantidade_frames - 1)
            tempo_decorrido = duracao_fisica * fracao
            velocidades = []
            for projetil, (tempo, trajetoria_x, trajetoria_y, trajetoria_velocidade, _) in zip(
                projeteis, trajetorias
            ):
                indice = min(bisect_left(tempo, tempo_decorrido), len(tempo) - 1)
                projetil.set_data([trajetoria_x[indice]], [trajetoria_y[indice]])
                velocidades.append(trajetoria_velocidade[indice])
            self._atualizar_velocimetro(
                velocidades, [projetil.get_color() for projetil in projeteis]
            )
            return tuple(projeteis)

        self.animacao = FuncAnimation(
            self.fig,
            atualizar,
            frames=quantidade_frames,
            interval=duracao_ms / quantidade_frames,
            blit=False,
            repeat=False,
        )
        self.canvas.draw()

    def _remover_projeteis_extras(self):
        for projetil in self.projeteis_extras:
            projetil.remove()
        self.projeteis_extras.clear()

    def parar_animacao(self):
        if self.animacao is not None:
            try:
                if self.animacao.event_source is not None:
                    self.animacao.event_source.stop()
            except (AttributeError, RuntimeError):
                pass
            finally:
                self.animacao = None

    def adicionar_trajetoria(self):
        try:
            parametros = self.ler_parametros()
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Entrada inválida", str(exc))
            return

        simulador = SimuladorProjetil(parametros)
        tempo, x, y = simulador.calcular_trajetoria()
        linha, = self.ax.plot(
            x,
            y,
            linewidth=ESPESSURA_TRAJETORIA,
            alpha=1.0,
            label=f"{parametros.velocidade:.0f} m/s, {parametros.angulo:.0f}°",
        )
        self.trajetorias_anteriores.append(linha)
        velocidades = simulador.calcular_velocidades(tempo)
        self.dados_trajetorias.append((tempo, x, y, velocidades, linha.get_color()))
        self._atualizar_legenda()
        self.canvas.draw_idle()

    def limpar_trajetorias(self):
        for linha in self.trajetorias_anteriores:
            linha.remove()
        self.trajetorias_anteriores.clear()
        self.dados_trajetorias.clear()
        self._atualizar_legenda()
        self.canvas.draw_idle()
