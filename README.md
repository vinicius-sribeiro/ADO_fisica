# Simulador de Lançamento de Projétil — Etapa 2 (Física Analítica e Simulação)

Aplicação acadêmica de Física para simulação de lançamento oblíquo de projéteis, construída em **Python 3 + Pygame**, baseada em equações analíticas exatas.

Nesta segunda etapa, a **física analítica completa, o comportamento da simulação e os controles interativos** foram implementados, utilizando elementos geométricos para o projétil. O carregamento de sprites PNG será realizado na próxima etapa.

## Funcionalidades implementadas nesta etapa

- **Física Analítica Exata**:
  - $x(t) = x_0 + v_0 \cos(\theta) t$
  - $y(t) = y_0 + v_0 \sin(\theta) t - \frac{1}{2} g t^2$
  - $t_{voo} = \frac{v_0 \sin(\theta) + \sqrt{(v_0 \sin(\theta))^2 + 2 g y_0}}{g}$
  - $y_{max} = y_0 + \frac{(v_0 \sin(\theta))^2}{2 g}$
  - $R = x_0 + v_0 \cos(\theta) t_{voo}$
- **Trajetórias Dinâmicas e Preservação**:
  - **Trajetória prevista atual**: linha pontilhada preta atualizada em tempo real ao alterar os sliders.
  - **Trajetória prevista do último lançamento**: linha pontilhada azulada suave preservada após a conclusão do lançamento para comparação direta com novos parâmetros.
  - **Trajetória percorrida**: linha sólida vermelha que acompanha o projétil em tempo físico real e permanece após o impacto no solo.
- **Controles Interativos**:
  - **Lançar**: dispara o projétil baseado no tempo físico contínuo $t$.
  - **Pausar / Continuar**: congela a simulação no instante atual permitindo alterar parâmetros e continuar de onde parou.
  - **Resetar tudo**: restaura todos os parâmetros para os valores padrão e limpa trajetórias e histórico.
  - **Parâmetros**: abre/fecha o HUD com sliders de $v_0$, $\theta$, $y_0$ e $g$.
- **Escala Dinâmica**:
  - A visualização do plano cartesiano adapta sua escala automaticamente para acomodar lançamentos curtos ou longos com divisões numéricas redondas nos eixos.
- **Painel de Resultados em Tempo Real**:
  - Exibe Alcance ($R$), Altura Máxima ($Y_{max}$), Tempo de Voo ($T$) e status da simulação.
- **Histórico de Lançamentos**:
  - Estrutura `historico_trajetorias` preparada com registros de parâmetros, pontos e resultados de cada lançamento.

## Como executar

Dentro da pasta `projectile_sim/`:

```bash
python main.py
```

Ou com o ambiente virtual:

```bash
.\.venv\Scripts\python main.py
```
