# Relatório — Interface Gráfica Interativa para Lançamento de Objetos

## Instalação

### Pré-requisitos

- **Python 3.10+** (recomendado).
- **Git** (recomendado para clonar o repositório).
- **Tkinter**:
  - Em Windows e macOS, normalmente já vem com a instalação oficial do Python.
  - Em distribuições Linux, pode ser necessário instalar separadamente (exemplo Debian/Ubuntu):
    ```bash
    sudo apt-get install python3-tk
    ```

### Clonar o repositório

```bash
git clone https://github.com/NiWYZin/Fisica_Extensiva.git
cd Fisica_Extensiva
```

> Execute os comandos e rode o projeto **a partir da raiz do repositório** (pasta que contém `main.py`).

### Criar e ativar ambiente virtual

#### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Windows (CMD)

```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

#### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Instalar bibliotecas necessárias

Este projeto usa `numpy` e `matplotlib` no código, além de `tkinter` (biblioteca padrão do Python, quando disponível no sistema).

#### Opção recomendada (requirements.txt)

```bash
pip install -r requirements.txt
```

#### Opção manual

```bash
pip install numpy matplotlib
```

## Execução

O ponto de entrada do projeto é o arquivo **`main.py`**.

### Via terminal

Com o ambiente virtual ativado e na raiz do repositório:

```bash
python main.py
```

> Em alguns ambientes Linux/macOS, o comando pode ser `python3 main.py`.

### Via IDE

#### VS Code

1. Abra a pasta do repositório (`File > Open Folder...`).
2. Selecione o interpretador da `.venv` (`Ctrl+Shift+P` → `Python: Select Interpreter`).
3. Abra `main.py`.
4. Execute pelo botão **Run Python File** ou com `F5`.

#### PyCharm

1. Abra o projeto pela pasta do repositório.
2. Configure o interpretador para a `.venv` (Settings/Preferences → Python Interpreter).
3. Crie/edite uma Run Configuration apontando para `main.py`.
4. Execute a configuração.

## 1. Biblioteca escolhida

Foi utilizada a combinação de **Tkinter** e **Matplotlib**. O Tkinter foi escolhido para construir a interface gráfica e os controles interativos, enquanto o Matplotlib foi incorporado à janela para representar a trajetória e realizar a animação dos objetos. Essa abordagem atende ao requisito técnico de separar a interface gráfica da visualização e não exige um framework web.

## 2. Controles implementados

A aplicação permite alterar interativamente:

- velocidade inicial `v₀`, entre 5 e 150 m/s;
- ângulo de lançamento `θ`, entre 1° e 89°;
- altura inicial `y₀`, entre 0 e 50 m;
- aceleração da gravidade `g`, entre 1,6 e 24,8 m/s².

Cada parâmetro possui um slider e um campo numérico para entrada direta. A gravidade é informada manualmente, permitindo testar diferentes valores dentro do intervalo definido.

As alterações atualizam automaticamente o gráfico e os valores numéricos de alcance horizontal, altura máxima e tempo de voo. O gráfico também exibe um velocímetro em m/s, com a velocidade instantânea de cada objeto identificada por cor.

### Visual da interface e trajetória

![image1](image1)

Legenda: interface gráfica da aplicação durante a simulação, com os controles de lançamento e a trajetória parabólica renderizada no gráfico.

## 3. Fundamentação e cálculos

A trajetória é calculada diretamente pelas expressões analíticas do lançamento de objetos sem resistência do ar. O programa utiliza:

`x(t) = x₀ + v₀ cos(θ)t`

`y(t) = y₀ + v₀ sin(θ)t − (1/2)gt²`

O tempo de voo é obtido pela raiz positiva da equação `y(t)=0`, e a altura máxima é calculada pela expressão correspondente. O alcance horizontal é calculado pela posição horizontal no instante final.

Não é utilizada integração numérica, em conformidade com a atividade.

## 4. Exemplo de configuração

Foi usada a configuração:

- `v₀ = 30,00 m/s`
- `θ = 45,00°`
- `y₀ = 0,00 m`
- `g = 9,81 m/s²`

Resultados aproximados:

- **Alcance horizontal:** 91,74 m
- **Altura máxima:** 22,94 m
- **Tempo de voo:** 4,32 s

Esses valores são recalculados automaticamente sempre que um parâmetro é alterado.

## 5. Dificuldades e soluções

A principal questão de implementação foi manter a atualização da interface e da curva de forma imediata sem precisar reiniciar a aplicação. Para isso, os controles acionam uma função de atualização que recalcula os resultados e os pontos da trajetória a cada alteração.

A animação foi implementada separadamente da função de cálculo: ao clicar em “Lançar”, vários objetos percorrem simultaneamente suas respectivas trajetórias, usando o mesmo tempo físico de referência. Assim, cada objeto mantém a velocidade inicial e os parâmetros da configuração que originou sua curva.

Também foi implementado tratamento de entradas inválidas. Valores fora dos intervalos definidos são rejeitados e apresentados ao usuário como erro de entrada, evitando que o programa seja encerrado por uma exceção não tratada.

Como funcionalidade adicional, a aplicação permite preservar trajetórias anteriores na mesma área de plotagem para comparação entre configurações diferentes. Ao clicar em “Lançar”, todos os objetos, incluindo os das trajetórias anteriores, são animados simultaneamente e sincronizados pelo tempo físico.

## 6. Verificação dos requisitos

Os controles exigidos, a atualização em tempo real, os resultados numéricos, a animação, os rótulos dos eixos, a escala física consistente e o tratamento de entradas inválidas estão implementados. A física está separada da interface nos módulos `fisica.py` e `interface.py`, enquanto `main.py` contém o ponto de entrada. O cálculo usa exclusivamente as fórmulas analíticas, sem integração numérica.
