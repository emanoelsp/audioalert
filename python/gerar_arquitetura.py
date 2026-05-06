"""
Diagrama de arquitetura nível artigo acadêmico — AudioAlert AAD Pipeline
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

# ── Paleta acadêmica ──────────────────────────────────────────────────
BG       = '#FAFAFA'
DARK     = '#1A1A2E'
BLUE     = '#2563EB'
BLUE_LT  = '#DBEAFE'
TEAL     = '#0D9488'
TEAL_LT  = '#CCFBF1'
AMBER    = '#D97706'
AMBER_LT = '#FEF3C7'
RED      = '#DC2626'
RED_LT   = '#FEE2E2'
GRAY     = '#6B7280'
GRAY_LT  = '#F3F4F6'
GREEN    = '#16A34A'
GREEN_LT = '#DCFCE7'
PURPLE   = '#7C3AED'
PURPLE_LT= '#EDE9FE'
LINE     = '#374151'

fig = plt.figure(figsize=(18, 24), facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_facecolor(BG)
ax.set_xlim(0, 18)
ax.set_ylim(0, 24)
ax.axis('off')

# ── Helpers ───────────────────────────────────────────────────────────

def box(ax, x, y, w, h, fc, ec, lw=1.5, radius=0.25, zorder=3):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle=f"round,pad=0,rounding_size={radius}",
                          fc=fc, ec=ec, lw=lw, zorder=zorder)
    ax.add_patch(rect)

def label(ax, x, y, txt, fs=9, color=DARK, weight='normal', ha='center', va='center', style='normal'):
    ax.text(x, y, txt, fontsize=fs, color=color, fontweight=weight,
            ha=ha, va=va, fontstyle=style, zorder=5,
            fontfamily='DejaVu Sans')

def arrow(ax, x1, y1, x2, y2, color=GRAY, lw=1.8, style='->', headw=0.18, headl=0.25):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=f'->, head_width={headw}, head_length={headl}',
                                color=color, lw=lw),
                zorder=4)

def section_label(ax, x, y, txt, color):
    ax.text(x, y, txt, fontsize=7.2, color=color, fontweight='bold',
            ha='left', va='center', zorder=5,
            fontstyle='italic', fontfamily='DejaVu Sans')

def badge(ax, x, y, txt, fc, ec, fs=7):
    box(ax, x - 0.5, y - 0.17, 1.0, 0.34, fc=fc, ec=ec, lw=1.2, radius=0.15)
    label(ax, x, y, txt, fs=fs, color=ec, weight='bold')

def divider(ax, y, color='#D1D5DB', lw=0.8):
    ax.plot([0.5, 17.5], [y, y], color=color, lw=lw, ls='--', zorder=2)

# ═══════════════════════════════════════════════════════════════════════
# TÍTULO
# ═══════════════════════════════════════════════════════════════════════
box(ax, 0.3, 22.8, 17.4, 1.0, fc='#1E3A5F', ec='#1E3A5F', lw=0, radius=0.3)
label(ax, 9, 23.38,
      'Acoustic Anomaly Detection (AAD) — Final Pipeline Architecture',
      fs=14, color='white', weight='bold')
label(ax, 9, 23.05,
      'Protocolo Dual LOSO · DCASE + MIMII + Kaggle + Drive Próprio · Edge/TinyML-Ready',
      fs=8.5, color='#93C5FD', style='italic')

# ═══════════════════════════════════════════════════════════════════════
# 0. FONTES DE DADOS
# ═══════════════════════════════════════════════════════════════════════
Y_SRC = 21.4
box(ax, 0.3, Y_SRC, 17.4, 1.1, fc=GRAY_LT, ec=GRAY, lw=1.5, radius=0.3)
section_label(ax, 0.55, Y_SRC + 0.92, '① FONTES DE DADOS (Multi-Source)', GRAY)

sources = [
    ('DCASE 2025\nTask 2', BLUE, BLUE_LT),
    ('MIMII\nDataset', TEAL, TEAL_LT),
    ('Kaggle\nBearings', AMBER, AMBER_LT),
    ('Drive\nPróprio', PURPLE, PURPLE_LT),
]
xs = [2.1, 5.8, 9.5, 13.2]
for (name, ec, fc), x in zip(sources, xs):
    box(ax, x - 1.45, Y_SRC + 0.08, 2.9, 0.72, fc=fc, ec=ec, lw=1.3, radius=0.2)
    label(ax, x, Y_SRC + 0.44, name, fs=8, color=ec, weight='bold')

# label direito — protocolo LOSO
box(ax, 14.8, Y_SRC + 0.12, 2.7, 0.62, fc='#FEF3C7', ec=AMBER, lw=1.3, radius=0.2)
label(ax, 16.15, Y_SRC + 0.43, 'Protocolo\nLOSO', fs=7.8, color=AMBER, weight='bold')

# seta para próximo bloco
arrow(ax, 9, Y_SRC, 9, Y_SRC - 0.28)

# ═══════════════════════════════════════════════════════════════════════
# 1. PRÉ-PROCESSAMENTO
# ═══════════════════════════════════════════════════════════════════════
Y_PRE = 19.55
box(ax, 0.3, Y_PRE, 17.4, 1.55, fc='#EFF6FF', ec=BLUE, lw=2.0, radius=0.3)
section_label(ax, 0.55, Y_PRE + 1.37, '② PRÉ-PROCESSAMENTO & DENOISING', BLUE)

# HHT block
box(ax, 0.65, Y_PRE + 0.08, 7.5, 1.0, fc=BLUE_LT, ec=BLUE, lw=1.4, radius=0.25)
label(ax, 4.4, Y_PRE + 0.82, 'HHT  ·  Hilbert-Huang Transform', fs=9.5, color=BLUE, weight='bold')
label(ax, 4.4, Y_PRE + 0.57,
      'Decomposição EMD → IMFs adaptativas (sinal não-estacionário)',
      fs=7.8, color=DARK)
label(ax, 4.4, Y_PRE + 0.32,
      'Remove tendências de baixa frequência e artefatos de captura',
      fs=7.5, color=GRAY)

# seta HHT → UKF
arrow(ax, 8.15, Y_PRE + 0.58, 9.15, Y_PRE + 0.58, color=BLUE, headw=0.12, headl=0.18)

# UKF block
box(ax, 9.15, Y_PRE + 0.08, 7.6, 1.0, fc=BLUE_LT, ec=BLUE, lw=1.4, radius=0.25)
label(ax, 12.95, Y_PRE + 0.82, 'UKF  ·  Unscented Kalman Filter', fs=9.5, color=BLUE, weight='bold')
label(ax, 12.95, Y_PRE + 0.57,
      'Rastreamento não-linear de estado → filtragem de ruído sigma-point',
      fs=7.8, color=DARK)
label(ax, 12.95, Y_PRE + 0.32,
      'Ganho: +5.7 dB SNR médio sobre o sinal bruto',
      fs=7.5, color=GRAY)

# badge SNR
badge(ax, 16.0, Y_PRE + 0.08 + 1.0 + 0.07, '+5.7 dB SNR', fc='#DCFCE7', ec=GREEN)

arrow(ax, 9, Y_PRE, 9, Y_PRE - 0.28)

# ═══════════════════════════════════════════════════════════════════════
# 2. SEGMENTAÇÃO
# ═══════════════════════════════════════════════════════════════════════
Y_SEG = 18.5
box(ax, 0.3, Y_SEG, 17.4, 0.78, fc=GRAY_LT, ec=GRAY, lw=1.5, radius=0.25)
section_label(ax, 0.55, Y_SEG + 0.63, '③ SEGMENTAÇÃO', GRAY)

box(ax, 3.0, Y_SEG + 0.07, 12.0, 0.52, fc='white', ec=GRAY, lw=1.2, radius=0.2)
label(ax, 9.0, Y_SEG + 0.335,
      'Janelas Deslizantes (Sliding Windows)  ·  hop=50%  ·  Normalização por janela',
      fs=8.5, color=DARK)

arrow(ax, 9, Y_SEG, 9, Y_SEG - 0.28)

# ═══════════════════════════════════════════════════════════════════════
# 3. EXTRAÇÃO DE FEATURES
# ═══════════════════════════════════════════════════════════════════════
Y_FEA = 15.45
box(ax, 0.3, Y_FEA, 17.4, 2.77, fc='#F0FDF4', ec=GREEN, lw=2.0, radius=0.3)
section_label(ax, 0.55, Y_FEA + 2.58, '④ EXTRAÇÃO DE FEATURES  →  SUPER-VECTOR', GREEN)

feat_blocks = [
    {
        'x': 0.65, 'w': 3.2,
        'title': 'Mel / log-Mel',
        'sub': '64 bins · 128 frames\nlog-compressão',
        'note': 'Representação\nbase do espectro',
        'fc': GREEN_LT, 'ec': GREEN,
    },
    {
        'x': 4.05, 'w': 3.3,
        'title': 'RPCA',
        'sub': 'Componente esparsa\n(transientes)',
        'note': 'Separa padrão estável\ndo raro/impulsivo',
        'fc': TEAL_LT, 'ec': TEAL,
    },
    {
        'x': 7.55, 'w': 3.3,
        'title': 'MFCC',
        'sub': '13 coef. + Δ + ΔΔ\n+ estatísticas',
        'note': 'Envelope timbral\ncompacto',
        'fc': BLUE_LT, 'ec': BLUE,
    },
    {
        'x': 11.05, 'w': 3.35,
        'title': 'NMF',
        'sub': 'Erro de reconstrução\nn_components=16',
        'note': 'Score de desvio\nda normalidade',
        'fc': AMBER_LT, 'ec': AMBER,
    },
    {
        'x': 14.6, 'w': 3.1,
        'title': 'Tiny-AST (aux)',
        'sub': 'Embeddings de\npré-treino acústico',
        'note': 'XAI · não classifica\ndiretamente',
        'fc': PURPLE_LT, 'ec': PURPLE,
    },
]

for fb in feat_blocks:
    box(ax, fb['x'], Y_FEA + 0.62, fb['w'], 1.88,
        fc=fb['fc'], ec=fb['ec'], lw=1.4, radius=0.22)
    label(ax, fb['x'] + fb['w']/2, Y_FEA + 2.22,
          fb['title'], fs=9.2, color=fb['ec'], weight='bold')
    label(ax, fb['x'] + fb['w']/2, Y_FEA + 1.82,
          fb['sub'], fs=7.5, color=DARK)
    # note box
    box(ax, fb['x'] + 0.15, Y_FEA + 0.72, fb['w'] - 0.3, 0.62,
        fc='white', ec=fb['ec'], lw=0.8, radius=0.15)
    label(ax, fb['x'] + fb['w']/2, Y_FEA + 1.03,
          fb['note'], fs=7.0, color=GRAY)

# Super-Vector bar
box(ax, 0.65, Y_FEA + 0.08, 17.05, 0.46,
    fc='#1E3A5F', ec='#1E3A5F', lw=0, radius=0.18)
label(ax, 9.18, Y_FEA + 0.31,
      'CONCATENAÇÃO  →  SUPER-VECTOR  (features normalizadas por z-score)',
      fs=8.5, color='white', weight='bold')

# setas feature blocks → supervector
for fb in feat_blocks:
    cx = fb['x'] + fb['w']/2
    arrow(ax, cx, Y_FEA + 0.62, cx, Y_FEA + 0.54, color='#374151', headw=0.08, headl=0.12)

arrow(ax, 9, Y_FEA, 9, Y_FEA - 0.28)

# ═══════════════════════════════════════════════════════════════════════
# 4. PROTOCOLO DUAL
# ═══════════════════════════════════════════════════════════════════════
Y_MOD = 12.55
box(ax, 0.3, Y_MOD, 17.4, 2.62, fc='#FAFAFA', ec=LINE, lw=2.0, radius=0.3)
section_label(ax, 0.55, Y_MOD + 2.44, '⑤ PROTOCOLO DUAL DE DECISÃO', LINE)

# ── Protocolo A (Supervisionado)
box(ax, 0.55, Y_MOD + 0.08, 8.25, 2.18, fc='#EFF6FF', ec=BLUE, lw=2.2, radius=0.28)
label(ax, 4.68, Y_MOD + 2.02,
      'PROTOCOLO A  —  Supervisionado', fs=10, color=BLUE, weight='bold')
label(ax, 4.68, Y_MOD + 1.72,
      'Requer rótulos de falha no treino (labels known)', fs=7.8, color=GRAY, style='italic')

# XGBoost
box(ax, 0.75, Y_MOD + 0.95, 7.85, 0.65, fc=BLUE_LT, ec=BLUE, lw=1.3, radius=0.2)
label(ax, 4.68, Y_MOD + 1.36,
      'XGBoost  ·  n_estimators=300  ·  max_depth=6  ·  Mixup α=0.4  ·  Outlier Exposure',
      fs=8, color=BLUE, weight='bold')
label(ax, 4.68, Y_MOD + 1.1,
      'LOSO cross-validation  ·  pAUC@0.1 como função de perda guia',
      fs=7.5, color=DARK)

# Threshold Gamma A
box(ax, 0.75, Y_MOD + 0.18, 7.85, 0.62, fc='white', ec=BLUE, lw=1.0, radius=0.2)
label(ax, 4.68, Y_MOD + 0.6,
      'Threshold: Distribuição Gamma  ·  FPR-alvo 5%  ·  EVT/POT calibração',
      fs=8, color=DARK)
label(ax, 4.68, Y_MOD + 0.36,
      'Score proxy DCASE = pAUC × F1 × AUC  —  penalizado por latência e memória',
      fs=7.5, color=GRAY)

# métricas A
for txt, xm, ym in [
    ('pAUC@0.1\n0.94', 1.55, Y_MOD + 2.3),
    ('Latência\n15 ms', 3.55, Y_MOD + 2.3),
    ('<1 MB\nRAM', 5.55, Y_MOD + 2.3),
    ('Score DCASE\n0.948', 7.4, Y_MOD + 2.3),
]:
    box(ax, xm - 0.7, Y_MOD + 2.26 - 0.02, 1.4, 0.36,
        fc=GREEN_LT, ec=GREEN, lw=1.0, radius=0.12)
    label(ax, xm, Y_MOD + 2.44, txt, fs=6.8, color=GREEN, weight='bold')

# ── Protocolo B (Não-supervisionado)
box(ax, 9.2, Y_MOD + 0.08, 8.25, 2.18, fc='#FFF7ED', ec=AMBER, lw=2.2, radius=0.28)
label(ax, 13.33, Y_MOD + 2.02,
      'PROTOCOLO B  —  Não-Supervisionado', fs=10, color=AMBER, weight='bold')
label(ax, 13.33, Y_MOD + 1.72,
      'Treina apenas com dados normais (DCASE-like, domínio cego)', fs=7.8, color=GRAY, style='italic')

# GMM
box(ax, 9.4, Y_MOD + 0.95, 7.85, 0.65, fc=AMBER_LT, ec=AMBER, lw=1.3, radius=0.2)
label(ax, 13.33, Y_MOD + 1.36,
      'GMM  ·  n_components=8  ·  covariance=full  ·  log-likelihood score',
      fs=8, color=AMBER, weight='bold')
label(ax, 13.33, Y_MOD + 1.1,
      'Mahalanobis + Gamma (baseline)  ·  Isolation Forest + Gamma (ref.)',
      fs=7.5, color=DARK)

# Threshold Gamma B
box(ax, 9.4, Y_MOD + 0.18, 7.85, 0.62, fc='white', ec=AMBER, lw=1.0, radius=0.2)
label(ax, 13.33, Y_MOD + 0.6,
      'Threshold: Distribuição Gamma  ·  FPR-alvo 5%  ·  EVT/POT calibração',
      fs=8, color=DARK)
label(ax, 13.33, Y_MOD + 0.36,
      'Treino somente normal  ·  anomalia apenas em validação/teste  ·  anti-vazamento',
      fs=7.5, color=GRAY)

# métricas B
for txt, xm in [
    ('pAUC@0.1\n0.88', 10.25),
    ('Latência\n20 ms', 12.1),
    ('0.8 MB\nRAM', 13.95),
    ('Score DCASE\n0.892', 15.95),
]:
    box(ax, xm - 0.7, Y_MOD + 2.26 - 0.02, 1.4, 0.36,
        fc=GREEN_LT, ec=GREEN, lw=1.0, radius=0.12)
    label(ax, xm, Y_MOD + 2.44, txt, fs=6.8, color=GREEN, weight='bold')

# linha divisória entre protocolos
ax.plot([9.05, 9.05], [Y_MOD + 0.18, Y_MOD + 2.2], color=LINE, lw=1.5, ls='--', zorder=4)
label(ax, 9.05, Y_MOD + 1.17, 'ou', fs=9, color=GRAY, weight='bold')

arrow(ax, 4.68, Y_MOD, 4.68, Y_MOD - 0.28, color=BLUE)
arrow(ax, 13.33, Y_MOD, 13.33, Y_MOD - 0.28, color=AMBER)

# ═══════════════════════════════════════════════════════════════════════
# 5. XAI
# ═══════════════════════════════════════════════════════════════════════
Y_XAI = 11.25
box(ax, 0.3, Y_XAI, 17.4, 1.02, fc=PURPLE_LT, ec=PURPLE, lw=1.8, radius=0.28)
section_label(ax, 0.55, Y_XAI + 0.86, '⑥ EXPLICABILIDADE (XAI)', PURPLE)

box(ax, 2.0, Y_XAI + 0.08, 6.5, 0.62, fc='white', ec=PURPLE, lw=1.1, radius=0.2)
label(ax, 5.25, Y_XAI + 0.39,
      'Heatmap espectral  ·  Tiny-AST → regiões de ativação (hotspot)',
      fs=8, color=DARK)

box(ax, 9.3, Y_XAI + 0.08, 6.5, 0.62, fc='white', ec=PURPLE, lw=1.1, radius=0.2)
label(ax, 12.55, Y_XAI + 0.39,
      'Ablation study por canal  ·  importância de feature via XGBoost',
      fs=8, color=DARK)

arrow(ax, 4.68, Y_XAI, 4.68, Y_XAI - 0.28, color=PURPLE)
arrow(ax, 13.33, Y_XAI, 13.33, Y_XAI - 0.28, color=PURPLE)

# ═══════════════════════════════════════════════════════════════════════
# 6. SAÍDA / DECISÃO
# ═══════════════════════════════════════════════════════════════════════
Y_OUT = 9.68
box(ax, 0.3, Y_OUT, 17.4, 1.3, fc='#F0FDF4', ec=GREEN, lw=2.2, radius=0.28)
section_label(ax, 0.55, Y_OUT + 1.13, '⑦ DECISÃO & SAÍDA', GREEN)

box(ax, 1.2, Y_OUT + 0.1, 6.0, 0.82, fc=GREEN_LT, ec=GREEN, lw=1.5, radius=0.22)
label(ax, 4.2, Y_OUT + 0.62, 'NORMAL', fs=11, color=GREEN, weight='bold')
label(ax, 4.2, Y_OUT + 0.33, 'Score < Threshold Gamma', fs=7.8, color=DARK)

ax.plot([9.0, 9.0], [Y_OUT + 0.12, Y_OUT + 0.88], color=LINE, lw=1.0, ls=':')
label(ax, 9.0, Y_OUT + 0.51, 'vs', fs=9, color=GRAY)

box(ax, 10.8, Y_OUT + 0.1, 6.0, 0.82, fc=RED_LT, ec=RED, lw=1.5, radius=0.22)
label(ax, 13.8, Y_OUT + 0.62, 'ANOMALIA', fs=11, color=RED, weight='bold')
label(ax, 13.8, Y_OUT + 0.33, 'Score ≥ Threshold Gamma  ·  alerta acionado', fs=7.8, color=DARK)

# ═══════════════════════════════════════════════════════════════════════
# 7. ABLATION STUDY — resultados chave
# ═══════════════════════════════════════════════════════════════════════
Y_ABL = 8.0
divider(ax, Y_ABL + 1.5)
box(ax, 0.3, Y_ABL, 17.4, 1.42, fc=GRAY_LT, ec=GRAY, lw=1.5, radius=0.28)
section_label(ax, 0.55, Y_ABL + 1.25, '⑧ ABLATION STUDY — Contribuição de cada bloco (pAUC@0.1, Protocolo A)', GRAY)

ablations = [
    ('Baseline\n(Mel only)', '0.71'),
    ('+ RPCA', '0.76'),
    ('+ MFCC', '0.80'),
    ('+ NMF', '0.85'),
    ('+ HHT+UKF', '0.90'),
    ('+ Tiny-AST\n(aux emb.)', '0.92'),
    ('+ Mixup\n+ OE', '0.94'),
]
n = len(ablations)
xs_abl = np.linspace(1.3, 16.7, n)
for i, ((name, val), x) in enumerate(zip(ablations, xs_abl)):
    ec_col = BLUE if i < n - 1 else GREEN
    fc_col = BLUE_LT if i < n - 1 else GREEN_LT
    box(ax, x - 1.05, Y_ABL + 0.08, 2.1, 1.0, fc=fc_col, ec=ec_col, lw=1.2, radius=0.18)
    label(ax, x, Y_ABL + 0.82, name, fs=7.2, color=ec_col, weight='bold')
    label(ax, x, Y_ABL + 0.36, val, fs=10.5, color=ec_col, weight='bold')
    if i < n - 1:
        arrow(ax, x + 1.05, Y_ABL + 0.58, x + 1.2, Y_ABL + 0.58,
              color=GRAY, headw=0.09, headl=0.14)

# ═══════════════════════════════════════════════════════════════════════
# 8. TABELA COMPARATIVA FINAL
# ═══════════════════════════════════════════════════════════════════════
Y_TAB = 5.95
divider(ax, Y_TAB + 1.9)
box(ax, 0.3, Y_TAB, 17.4, 1.85, fc='white', ec=LINE, lw=1.5, radius=0.28)
section_label(ax, 0.55, Y_TAB + 1.68, '⑨ COMPARATIVO FINAL DE MODELOS AVALIADOS', LINE)

headers = ['Modelo', 'Regime', 'pAUC@0.1', 'Score DCASE', 'Latência', 'RAM', 'Status']
col_xs  = [1.55,     4.05,     6.35,       8.85,          11.1,       13.0,  15.0]
row_data = [
    ('XGBoost',        'Superv.',    '0.94', '0.948', '15 ms',  '<1 MB',  '★ CAMPEÃO A', GREEN,  GREEN_LT),
    ('GMM + Gamma',    'Não-sup.',   '0.88', '0.892', '20 ms',  '0.8 MB', '★ CAMPEÃO B', AMBER,  AMBER_LT),
    ('Mahalanobis',    'Não-sup.',   '0.82', '0.841', '18 ms',  '0.6 MB', 'Baseline',    GRAY,   GRAY_LT),
    ('LSTM-AE',        'Não-sup.',   '0.74', '0.770', '120 ms', '8 MB',   '✗ Descartado',RED,    RED_LT),
    ('CNN',            'Superv.',    '0.79', '0.810', '85 ms',  '12 MB',  '✗ Descartado',RED,    RED_LT),
]

# header
for h, x in zip(headers, col_xs):
    label(ax, x, Y_TAB + 1.48, h, fs=7.8, color=DARK, weight='bold')

ax.plot([0.5, 17.5], [Y_TAB + 1.35, Y_TAB + 1.35], color=LINE, lw=0.8)

row_ys = [1.12, 0.88, 0.65, 0.42, 0.19]
for row, ry in zip(row_data, row_ys):
    model, regime, pauc, sdcase, lat, ram, status, ec, fc = row
    # highlight row
    box(ax, 0.4, Y_TAB + ry - 0.12, 17.2, 0.26, fc=fc, ec='none', lw=0, radius=0.1)
    vals = [model, regime, pauc, sdcase, lat, ram, status]
    for v, x in zip(vals, col_xs):
        c = ec if v == status else DARK
        w = 'bold' if v == status else 'normal'
        label(ax, x, Y_TAB + ry, v, fs=7.5, color=c, weight=w)

# ═══════════════════════════════════════════════════════════════════════
# 9. EDGE / TINYML SUMMARY
# ═══════════════════════════════════════════════════════════════════════
Y_EDGE = 4.3
divider(ax, Y_EDGE + 1.5)
box(ax, 0.3, Y_EDGE, 17.4, 1.45, fc='#1E3A5F', ec='#1E3A5F', lw=0, radius=0.28)
section_label(ax, 0.55, Y_EDGE + 1.28, '⑩ REQUISITOS EDGE / TinyML  —  Deploy-Ready', '#93C5FD')

edge_items = [
    ('Protocolo A\n(XGBoost)', 'pAUC 0.94\nScore 0.948', '15 ms\ninfluência', '<1 MB\nRAM', BLUE_LT, BLUE),
    ('Protocolo B\n(GMM)', 'pAUC 0.88\nScore 0.892', '20 ms\ninfluência', '0.8 MB\nRAM', AMBER_LT, AMBER),
]
offsets = [1.2, 5.5]
labels_e = ['Acurácia', 'Latência', 'Memória']
for (name, acc, lat, mem, fc_e, ec_e), ox in zip(edge_items, offsets):
    box(ax, ox, Y_EDGE + 0.1, 3.8, 1.12, fc=fc_e, ec=ec_e, lw=1.3, radius=0.22)
    label(ax, ox + 1.9, Y_EDGE + 0.96, name, fs=8, color=ec_e, weight='bold')
    label(ax, ox + 0.95, Y_EDGE + 0.5, acc, fs=7.8, color=DARK)
    label(ax, ox + 1.9, Y_EDGE + 0.5, lat, fs=7.8, color=DARK)
    label(ax, ox + 2.85, Y_EDGE + 0.5, mem, fs=7.8, color=DARK)

# checklist Edge
checks = [
    '✔  Sem GPU (inference CPU-only)',
    '✔  Sem framework pesado (sklearn + scipy)',
    '✔  Exportável: joblib / ONNX',
    '✔  TinyML: quantização INT8 compatível',
    '✔  Reprodutível: seed=42, LOSO congelado',
    '✔  Anti-vazamento: teste nunca visto no treino',
]
cx_base = 10.5
for i, chk in enumerate(checks):
    row_x = cx_base + (i % 2) * 3.6
    row_y = Y_EDGE + 0.95 - (i // 2) * 0.38
    label(ax, row_x, row_y, chk, fs=7.5, color='#93C5FD', ha='left')

# ═══════════════════════════════════════════════════════════════════════
# 10. RODAPÉ
# ═══════════════════════════════════════════════════════════════════════
Y_FOOT = 0.15
box(ax, 0.3, Y_FOOT, 17.4, 4.0, fc=GRAY_LT, ec=GRAY, lw=1.0, radius=0.28)

# legenda de cores
legend_items = [
    ('Pré-processamento', BLUE, BLUE_LT),
    ('Features', GREEN, GREEN_LT),
    ('Protocolo A — Superv.', BLUE, BLUE_LT),
    ('Protocolo B — Não-sup.', AMBER, AMBER_LT),
    ('XAI', PURPLE, PURPLE_LT),
    ('Saída Normal', GREEN, GREEN_LT),
    ('Saída Anomalia', RED, RED_LT),
]

label(ax, 0.7, Y_FOOT + 3.72, 'Legenda de cores:', fs=8, color=DARK, weight='bold', ha='left')
lx = 0.7
for leg_name, ec_l, fc_l in legend_items:
    box(ax, lx, Y_FOOT + 3.3, 0.3, 0.25, fc=fc_l, ec=ec_l, lw=1.2, radius=0.08)
    label(ax, lx + 0.55, Y_FOOT + 3.42, leg_name, fs=7.3, color=DARK, ha='left')
    lx += 2.35

# notas técnicas
notes = [
    ('Dados:', 'DCASE 2025 Task 2  ·  MIMII Dataset  ·  Kaggle Bearings  ·  Drive Próprio (áudios de campo)'),
    ('Protocolo:', 'LOSO — Leave-One-Source-Out  ·  treino e teste nunca compartilham fonte'),
    ('Métricas:', 'pAUC@0.1 (primary)  ·  F1-score  ·  AUC-ROC  ·  Score DCASE proxy'),
    ('Threshold:', 'Distribuição Gamma ajustada por FPR-alvo de 5%  ·  EVT/POT para calibração de cauda'),
    ('Ablação:', 'Cada bloco testado isoladamente em NB27 — contribuição individual auditável'),
    ('Reprodução:', 'seed=42  ·  sklearn >= 1.3  ·  librosa >= 0.10  ·  PyEMD  ·  filterpy'),
]
ny = Y_FOOT + 2.92
for title, text in notes:
    label(ax, 0.7, ny, title, fs=7.5, color=DARK, weight='bold', ha='left')
    label(ax, 2.15, ny, text, fs=7.5, color=GRAY, ha='left')
    ny -= 0.42

# autoria
label(ax, 9.0, Y_FOOT + 0.22,
      'Emanoel Spanhol  ·  Pós-Graduação IA Aplicada  ·  UniSENAI  ·  2025–2026  ·  emanoelsp@gmail.com',
      fs=7.8, color=GRAY, style='italic')

# ═══════════════════════════════════════════════════════════════════════
# SETAS DE FLUXO PRINCIPAIS (conectam blocos)
# ═══════════════════════════════════════════════════════════════════════
main_arrows = [
    # dados → pré-proc
    (9, Y_SRC, 9, Y_PRE + 1.55),
    # pré-proc → seg
    (9, Y_PRE, 9, Y_SEG + 0.78),
    # seg → feature
    (9, Y_SEG, 9, Y_FEA + 2.77),
    # feature → protocolo
    (9, Y_FEA, 9, Y_MOD + 2.62),
    # protocolo → xai
    (4.68, Y_MOD, 4.68, Y_XAI + 1.02),
    (13.33, Y_MOD, 13.33, Y_XAI + 1.02),
    # xai → saida
    (4.68, Y_XAI, 4.68, Y_OUT + 1.3),
    (13.33, Y_XAI, 13.33, Y_OUT + 1.3),
]
# (already drawn inline above — skip to avoid double arrows)

plt.savefig('arquitetura_pipeline.png', dpi=180, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
print('✅ arquitetura_pipeline.png gerada com sucesso!')
