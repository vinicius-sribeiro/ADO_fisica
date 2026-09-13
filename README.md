# Simulador de Lançamento de Projétil — Etapa 2 (Física Analítica e Simulação)

Aplicação acadêmica de Física para simulação de lançamento oblíquo de projéteis, construída em **Python 3 + Pygame**, baseada em equações analíticas exatas.

## 🚀 Release v1.0.0

A versão 1.0.0 está disponível para download em: [Releases](https://github.com/vinicius-sribeiro/ADO_fisica/releases/tag/v1.0.0)

### Como usar a release

1. **Acesse a página de releases** do repositório
2. **Baixe o arquivo** `ADO_fisica-v1.0.0.zip` (ou equivalente para seu sistema)
3. **Extraia o arquivo** em uma pasta de sua escolha
4. **Abra o terminal/prompt** na pasta raiz do projeto
5. **Execute o aplicativo** conforme as instruções na seção "Como Executar" abaixo

---

## 📚 Biblioteca de Interface Gráfica

**Pygame** foi escolhido como a biblioteca de interface gráfica principal por:

- **Controle total sobre o renderização**: permite desenhar trajetórias, eixos cartesianos e elementos dinâmicos com precisão
- **Desempenho**: otimizado para aplicações em tempo real com simulações contínuas
- **Compatibilidade**: funciona em Windows, Linux e macOS
- **Comunidade ativa**: documentação ampla e suporte comunitário bem estabelecido
- **Leveza**: não requer dependências pesadas de GUI como Qt ou Tkinter

---

## 🎮 Controles Implementados

| Controle | Função |
|----------|--------|
| **Botão "Lançar"** | Dispara o projétil baseado no tempo físico contínuo |
| **Botão "Pausar / Continuar"** | Congela a simulação no instante atual, permitindo alterar parâmetros e retomar |
| **Botão "Resetar Tudo"** | Restaura todos os parâmetros para valores padrão e limpa trajetórias |
| **Botão "Parâmetros"** | Abre/fecha o HUD com sliders interativos para ajustar: $v_0$ (velocidade inicial), $\theta$ (ângulo), $y_0$ (altura inicial) e $g$ (gravidade) |
| **Sliders** | Permite ajuste em tempo real dos parâmetros com atualização contínua da trajetória prevista |

---

## 📊 Exemplo de Configuração Testada

Configuração padrão utilizada em testes:

| Parâmetro | Valor | Unidade |
|-----------|-------|---------|
| $v_0$ (velocidade inicial) | 20.0 | m/s |
| $\theta$ (ângulo de lançamento) | 45° | graus |
| $y_0$ (altura inicial) | 5.0 | metros |
| $g$ (aceleração gravitacional) | 9.81 | m/s² |

**Resultados Obtidos:**

- **Alcance (R)**: 44.65 metros
- **Altura Máxima (Y_max)**: 15.20 metros
- **Tempo de Voo (T_voo)**: 3.10 segundos

---

## 🔧 Dificuldades Encontradas e Resoluções

### 1. **Atualização em Tempo Real da Trajetória Prevista**
   - **Dificuldade**: Manter a trajetória prevista atualizada enquanto o projétil está em movimento, sem travamento visual
   - **Resolução**: Implementar cálculo separado de pontos de trajetória com limite de samples e cache da última trajetória calculada

### 2. **Escala Dinâmica dos Eixos Cartesianos**
   - **Dificuldade**: Adaptar automaticamente a escala para lançamentos com alcances variados (1 metro até 100+ metros)
   - **Resolução**: Algoritmo de cálculo de escala que encontra divisões "redondas" (10, 20, 50, 100, etc.) baseado nos valores máximos previstos

### 3. **Precisão das Equações Analíticas**
   - **Dificuldade**: Garantir que a simulação física numerada tenha correspondência exata com os valores calculados analiticamente
   - **Resolução**: Validação contínua comparando posição da trajetória percorrida com cálculos de $x(t)$ e $y(t)$ em cada frame

### 4. **Preservação de Trajetórias Múltiplas**
   - **Dificuldade**: Armazenar e renderizar múltiplas trajetórias (prevista atual, prevista anterior, percorrida) sem conflito visual
   - **Resolução**: Sistema de camadas com cores e estilos distintos (preto pontilhado, azul suave, vermelho sólido) e estrutura de dados separada para cada trajetória

### 5. **Pause e Retomada da Simulação**
   - **Dificuldade**: Pausar sem perder estado da simulação e permitir alteração de parâmetros sem resetar
   - **Resolução**: Armazenar tempo absoluto de pausa e ajustar cálculos de tempo relativo ao retomar

---

## Como Executar

Na pasta raiz do projeto:

Crie e ative o ambiente virtual e instale as dependências:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
```

Depois, execute a aplicação:

```bash
python main.py
```

Ou com o ambiente virtual:

```bash
.\.venv\Scripts\python main.py
```
