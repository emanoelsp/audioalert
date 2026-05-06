"""
Script para gerar a image.png atualizada com as 4 fases do projeto.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(16, 9))
fig.patch.set_facecolor('#0d1117')

gs = GridSpec(3, 4, figure=fig, hspace=0.55, wspace=0.3,
              top=0.88, bottom=0.08, left=0.04, right=0.97)

# ── Título principal
fig.text(0.5, 0.95, 'AudioAlert — Deteccao Acustica de Anomalias: Sintese Completa dos 28 Notebooks',
         ha='center', va='top', color='white', fontsize=13, fontweight='bold')
fig.text(0.5, 0.91,
         'Emanoel Spanhol · Pós-Graduação IA Aplicada · UniSENAI · 2025-2026  |  '
         'Dados: DCASE + MIMII + Kaggle + Drive Próprio  |  Protocolo: LOSO',
         ha='center', va='top', color='#8b949e', fontsize=8.5, style='italic')

# ─────────────────────────────────────────────────────────────────────
# FAIXA SUPERIOR: 4 fases como blocos coloridos
# ─────────────────────────────────────────────────────────────────────
fases = [
    {
        'col': 0, 'title': '[1] FASE 1: EXPLORACAO',
        'subtitle': 'Notebooks 1 - 10',
        'color': '#1f6feb', 'facecolor': '#0f2d4a',
        'items': [
            'NB1: Supervisionado (CNN/XGBoost/OC-SVM)',
            'NB2: Nao-Supervisionado (Autoenc./IF)',
            'NB3: Baseline real (4 modelos)',
            'NB4: Mel-Spectrogram (64 bins) [OK]',
            'NB5: CWT Wavelet [X] descartada (45ms)',
            'NB6: STFT [X] preterida',
            'NB7: Fusao Mel+MFCC+CWT',
            'NB8: +NMF (erro reconstrucao) [OK]',
            'NB9: Kaggle Bearings (dados reais)',
            'NB10: Drive Proprio -> domain shift!',
        ],
        'result': 'Campeao: XGBoost\nRepresentacao: Mel+MFCC+NMF\nDescarte: CNN (85ms/12MB),\nOC-SVM (pAUC 0.52),\nAutoenc. (120ms/8MB),\nCWT (45ms), STFT'
    },
    {
        'col': 1, 'title': '[2] FASE 2: OTIMIZACAO',
        'subtitle': 'Notebooks 11 - 15',
        'color': '#9e6a03', 'facecolor': '#2e1d00',
        'items': [
            'NB11 F1: L2 (lambda=1.0) + Gamma',
            'NB12 F2: CNN->aux | GMM [OK]',
            'NB13 F3: HHT+UKF [OK] (+5.7dB SNR)',
            'NB14 F4: Mixup alpha=0.4 [OK]',
            'NB15 F5: pAUC@0.1 (DCASE) [OK]',
        ],
        'result': 'Adicoes ao pipeline:\n- HHT+UKF (pre-proc.)\n- GMM (nao-sup.)\n- Mixup + pAUC\nDescarte: CNN motor\n(85ms/12MB),\nF1 como metrica unica'
    },
    {
        'col': 2, 'title': '[3] FASE 3: VALIDACAO',
        'subtitle': 'Notebooks 16 - 21',
        'color': '#2ea043', 'facecolor': '#0a2e14',
        'items': [
            'NB16 F6: Gamma+FPR 5% [OK]',
            'NB17 F7: Outlier Exposure DCASE',
            'NB18 F8: Arena GMM vs Mah vs IF',
            'NB19 F9: Tiny-AST -> auxiliar XAI',
            'NB20 F10: XAI (Heatmap+Hotspot) [OK]',
            'NB21 F11: Consolidacao final [OK]',
        ],
        'result': 'Protocolo Dual:\nA: XGBoost (superv.)\nB: GMM (nao-superv.)\nDescarte: LSTM-AE\n(120ms/8MB), IF\n(pAUC 0.71), threshold\nfixo'
    },
    {
        'col': 3, 'title': '[4] FASE 4: CONFRONTAMENTO',
        'subtitle': 'Notebooks 22 - 28',
        'color': '#da3633', 'facecolor': '#2e0a0a',
        'items': [
            'NB22-23: Arquitetura Campea limpa',
            'NB24: Veredito A vs B',
            'NB25: MIMII multi-SNR (-6,0,+6dB)',
            'NB26: Sintese Evolucao NB1-25',
            'NB27: Ablation Study (cada peca)',
            'NB28: DIAMOND CRISTAL CLEAN [OK]',
        ],
        'result': 'DIAMOND CRISTAL CLEAN:\nA: pAUC 0.94 | 15ms | <1MB\nB: pAUC 0.88 | 20ms | 0.8MB\nScore DCASE: 0.948/0.892\nEdge TinyML-Ready [OK]'
    },
]

for fase in fases:
    col = fase['col']
    color = fase['color']

    # Cabeçalho da fase
    ax_header = fig.add_subplot(gs[0, col])
    ax_header.set_facecolor(fase['facecolor'])
    for spine in ax_header.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(2)
    ax_header.set_xticks([]); ax_header.set_yticks([])

    ax_header.text(0.5, 0.78, fase['title'], transform=ax_header.transAxes,
                   ha='center', va='center', color=color, fontsize=10.5, fontweight='bold')
    ax_header.text(0.5, 0.45, fase['subtitle'], transform=ax_header.transAxes,
                   ha='center', va='center', color='white', fontsize=9.5)
    ax_header.text(0.5, 0.15, f'{len(fase["items"])} experimentos', transform=ax_header.transAxes,
                   ha='center', va='center', color='#8b949e', fontsize=8)

    # Itens da fase
    ax_items = fig.add_subplot(gs[1, col])
    ax_items.set_facecolor('#161b22')
    for spine in ax_items.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(1.5)
    ax_items.set_xticks([]); ax_items.set_yticks([])

    for i, item in enumerate(fase['items']):
        ypos = 1.0 - (i + 0.7) / (len(fase['items']) + 0.5)
        item_color = '#da3633' if '🔴' in item else (color if '✅' in item else '#8b949e')
        marker = '▸'
        ax_items.text(0.05, ypos, f'{marker} {item}', transform=ax_items.transAxes,
                     ha='left', va='center', color=item_color, fontsize=7.5)

    # Resultado
    ax_result = fig.add_subplot(gs[2, col])
    ax_result.set_facecolor(fase['facecolor'])
    for spine in ax_result.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(2)
    ax_result.set_xticks([]); ax_result.set_yticks([])
    ax_result.text(0.5, 0.5, fase['result'], transform=ax_result.transAxes,
                   ha='center', va='center', color='white', fontsize=7.5,
                   fontweight='bold', multialignment='center')

# Setas entre fases (na faixa superior)
ax_fig = fig.add_axes([0, 0, 1, 1], zorder=10)
ax_fig.set_facecolor('none')
ax_fig.axis('off')

arrow_y = 0.73  # posição vertical das setas no espaço normalizado da figura
for x_arrow in [0.30, 0.55, 0.77]:
    ax_fig.annotate('', xy=(x_arrow + 0.01, arrow_y), xytext=(x_arrow - 0.005, arrow_y),
                   xycoords='figure fraction', textcoords='figure fraction',
                   arrowprops=dict(arrowstyle='->', color='white', lw=2.5))

# Linha de timeline (eixo inferior)
ax_timeline = fig.add_axes([0.04, 0.03, 0.93, 0.025], zorder=5)
ax_timeline.set_facecolor('#0d1117')
ax_timeline.axis('off')
ax_timeline.set_xlim(0, 28)

colors_tl = ['#1f6feb'] * 10 + ['#9e6a03'] * 5 + ['#2ea043'] * 6 + ['#da3633'] * 7
for nb in range(28):
    ax_timeline.barh(0, 0.85, left=nb + 0.1, color=colors_tl[nb], height=0.7, alpha=0.85)
    ax_timeline.text(nb + 0.525, 0, str(nb + 1), ha='center', va='center',
                    color='white', fontsize=6, fontweight='bold')

ax_timeline.text(5, -0.7, 'Notebooks 1-10\n(Exploração)', ha='center', color='#1f6feb', fontsize=7)
ax_timeline.text(12.5, -0.7, 'Notebooks 11-15\n(Otimização)', ha='center', color='#9e6a03', fontsize=7)
ax_timeline.text(18.5, -0.7, 'Notebooks 16-21\n(Validação)', ha='center', color='#2ea043', fontsize=7)
ax_timeline.text(24.5, -0.7, 'Notebooks 22-28\n(Confrontamento)', ha='center', color='#da3633', fontsize=7)
ax_timeline.set_ylim(-1.2, 1.2)

# Métricas finais no rodapé
fig.text(0.5, 0.0,
         'pAUC@0.1: 0.94 (sup.) / 0.88 (nao-sup.)  |  Latencia: 15ms / 20ms  |  Memoria: <1MB / 0.8MB  |  '
         'Score DCASE: 0.948 / 0.892  |  Edge-Ready: TinyML [OK]',
         ha='center', va='bottom', color='#2ea043', fontsize=8.5, fontweight='bold')

plt.savefig('image.png', dpi=150, bbox_inches='tight', facecolor='#0d1117')
print('✅ image.png gerada com sucesso!')
