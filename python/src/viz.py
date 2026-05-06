"""
Funções de visualização padronizadas para todos os experimentos.
Tema escuro, estilo DCASE/paper.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.metrics import roc_curve
from src.metrics import pauc_at_fpr

DARK_BG    = '#0d1117'
PANEL_BG   = '#161b22'
GREEN      = '#2ea043'
RED        = '#da3633'
BLUE       = '#1f6feb'
ORANGE     = '#f0883e'
PURPLE     = '#8b949e'
YELLOW     = '#e3b341'
WHITE      = '#f0f6fc'

plt.rcParams.update({
    'figure.facecolor': DARK_BG,
    'axes.facecolor':   PANEL_BG,
    'text.color':       WHITE,
    'axes.labelcolor':  WHITE,
    'xtick.color':      PURPLE,
    'ytick.color':      PURPLE,
    'axes.edgecolor':   '#30363d',
    'grid.color':       '#30363d',
    'grid.alpha':       0.5,
    'font.family':      'DejaVu Sans',
    'axes.titlecolor':  WHITE,
    'legend.frameon':   False,
    'legend.labelcolor': WHITE,
})


def save(fig, path, dpi=120):
    fig.savefig(path, dpi=dpi, bbox_inches='tight',
                facecolor=DARK_BG, edgecolor='none')
    plt.close(fig)
    return path


# ─── ROC + pAUC ──────────────────────────────────────────────────────────────

def plot_roc_pauc(y_true, y_scores_dict, title='ROC Curve', out_path=None):
    """Plota curvas ROC + região pAUC@0.1 para múltiplos modelos."""
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_facecolor(PANEL_BG)
    colors = [GREEN, BLUE, ORANGE, PURPLE, YELLOW, RED]

    for (label, y_score), color in zip(y_scores_dict.items(), colors):
        fpr, tpr, _ = roc_curve(y_true, y_score)
        pauc = pauc_at_fpr(y_true, y_score)
        ax.plot(fpr, tpr, color=color, lw=2,
                label=f'{label}  pAUC={pauc:.3f}')

    # Região pAUC@0.1
    ax.axvline(0.1, color=RED, ls='--', lw=1.2, alpha=0.7, label='FPR=0.10')
    ax.fill_betweenx([0, 1], 0, 0.1, alpha=0.06, color=RED)
    ax.plot([0,1],[0,1], color=PURPLE, ls=':', lw=1)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    if out_path:
        save(fig, out_path)
    return fig


# ─── Barras de métricas ───────────────────────────────────────────────────────

def plot_metric_bars(labels, values, metric_name='pAUC@0.1',
                     threshold=0.80, title='', out_path=None, colors=None):
    """Barras horizontais comparando modelos numa métrica."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_facecolor(PANEL_BG)
    if colors is None:
        colors = [GREEN if v >= threshold else RED for v in values]

    bars = ax.barh(labels, values, color=colors, alpha=0.85, edgecolor='none')
    ax.axvline(threshold, color=ORANGE, ls='--', lw=1.5,
               label=f'Limite mínimo {threshold}')
    for bar, val in zip(bars, values):
        ax.text(min(val + 0.01, 0.98), bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', ha='left', color=WHITE, fontsize=9)
    ax.set_xlabel(metric_name)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlim(0, 1.1)
    ax.legend(fontsize=9)
    ax.grid(True, axis='x', alpha=0.3)
    if out_path:
        save(fig, out_path)
    return fig


# ─── Espectrograma + sinal ────────────────────────────────────────────────────

def plot_signal_and_spectrogram(signal, sr=16000, n_fft=512, hop=256,
                                 title='Signal & Spectrogram', out_path=None,
                                 anomaly_region=None):
    """Plota sinal + espectrograma Log-Mel com região de anomalia destacada."""
    from src.features import log_mel_spectrogram
    mel = log_mel_spectrogram(signal)
    t = np.arange(len(signal)) / sr
    t_mel = np.arange(mel.shape[0]) * hop / sr

    fig, axes = plt.subplots(2, 1, figsize=(10, 6))
    for ax in axes:
        ax.set_facecolor(PANEL_BG)

    # Sinal
    axes[0].plot(t, signal, color=BLUE, lw=0.8, alpha=0.9)
    if anomaly_region:
        axes[0].axvspan(*anomaly_region, alpha=0.2, color=RED, label='Anomalia')
        axes[0].legend(fontsize=9)
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title(title, fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3)

    # Espectrograma
    im = axes[1].pcolormesh(t_mel, np.arange(mel.shape[1]),
                             mel.T, cmap='inferno', shading='auto')
    if anomaly_region:
        axes[1].axvspan(*anomaly_region, alpha=0.2, color=RED)
    axes[1].set_xlabel('Tempo (s)')
    axes[1].set_ylabel('Mel Band')
    plt.colorbar(im, ax=axes[1], label='Log-Mel Energy')
    plt.tight_layout()
    if out_path:
        save(fig, out_path)
    return fig


# ─── Evolução das métricas ────────────────────────────────────────────────────

def plot_evolution(nb_labels, pauc_values, f1_values=None,
                   title='Evolução das Métricas por Notebook', out_path=None):
    """Linha de evolução de pAUC (e F1) ao longo dos notebooks."""
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_facecolor(PANEL_BG)
    x = np.arange(len(nb_labels))

    ax.plot(x, pauc_values, color=GREEN, marker='o', lw=2, ms=7,
            label='pAUC@0.1', zorder=3)
    if f1_values is not None:
        ax.plot(x, f1_values, color=BLUE, marker='s', lw=2, ms=6,
                ls='--', label='F1-Score', zorder=3)
    ax.axhline(0.80, color=ORANGE, ls='--', lw=1.5, alpha=0.8,
               label='Limite mínimo 0.80')
    ax.fill_between(x, pauc_values, 0.80,
                    where=np.array(pauc_values) >= 0.80,
                    alpha=0.1, color=GREEN)

    for xi, pv in zip(x, pauc_values):
        ax.annotate(f'{pv:.2f}', (xi, pv), textcoords='offset points',
                    xytext=(0, 8), ha='center', fontsize=8, color=GREEN)

    ax.set_xticks(x)
    ax.set_xticklabels(nb_labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel('Score')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if out_path:
        save(fig, out_path)
    return fig


# ─── Ablation study ──────────────────────────────────────────────────────────

def plot_ablation(components, pauc_full, pauc_ablated, out_path=None):
    """Barras de impacto de cada componente no ablation study."""
    deltas = [pauc_full - p for p in pauc_ablated]
    colors = [RED if d >= 0.05 else ORANGE if d >= 0.02 else GREEN for d in deltas]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_facecolor(PANEL_BG)
    bars = ax.barh(components, deltas, color=colors, alpha=0.85, edgecolor='none')
    for bar, d in zip(bars, deltas):
        ax.text(d + 0.001, bar.get_y() + bar.get_height()/2,
                f'−{d:.3f}', va='center', ha='left', color=WHITE, fontsize=9)
    ax.axvline(0, color=WHITE, lw=0.8, alpha=0.5)
    ax.set_xlabel('Queda de pAUC@0.1 ao remover componente')
    ax.set_title(f'Ablation Study — Referência pAUC@0.1 = {pauc_full:.3f}',
                 fontsize=12, fontweight='bold')
    ax.grid(True, axis='x', alpha=0.3)
    legend = [
        mpatches.Patch(color=RED,    label='Crítico (≥0.05)'),
        mpatches.Patch(color=ORANGE, label='Importante (0.02-0.04)'),
        mpatches.Patch(color=GREEN,  label='Leve (<0.02)'),
    ]
    ax.legend(handles=legend, fontsize=9)
    plt.tight_layout()
    if out_path:
        save(fig, out_path)
    return fig


# ─── XAI Heatmap ─────────────────────────────────────────────────────────────

def plot_xai_heatmap(signal, activation_map, sr=16000, n_mel=64,
                     title='XAI Saliency Heatmap', out_path=None):
    """Plota espectrograma com heatmap de ativação XAI."""
    from src.features import log_mel_spectrogram
    mel = log_mel_spectrogram(signal)
    if len(mel) == 0:
        return None

    T = min(mel.shape[0], len(activation_map))
    act = activation_map[:T]
    act_2d = np.outer(act, np.ones(n_mel)).T  # (n_mel, T)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax in axes:
        ax.set_facecolor(PANEL_BG)

    im1 = axes[0].pcolormesh(np.arange(T), np.arange(n_mel),
                               mel[:T].T, cmap='inferno', shading='auto')
    axes[0].set_title('Log-Mel Spectrogram', fontsize=11, fontweight='bold')
    axes[0].set_xlabel('Frame'); axes[0].set_ylabel('Mel Band')
    plt.colorbar(im1, ax=axes[0])

    im2 = axes[1].pcolormesh(np.arange(T), np.arange(n_mel),
                               act_2d[:, :T], cmap='hot', shading='auto', alpha=0.85)
    axes[1].set_title('XAI Activation Heatmap', fontsize=11, fontweight='bold')
    axes[1].set_xlabel('Frame'); axes[1].set_ylabel('Mel Band')
    plt.colorbar(im2, ax=axes[1])
    fig.suptitle(title, fontsize=13, fontweight='bold', color=WHITE)
    plt.tight_layout()
    if out_path:
        save(fig, out_path)
    return fig


# ─── Latência e Memória ───────────────────────────────────────────────────────

def plot_latency_memory(labels, latencies, memories, limit_lat=50, limit_mem=4,
                        out_path=None):
    """Scatter plot: latência vs memória com zonas de Edge e Cloud."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_facecolor(PANEL_BG)

    # Zona Edge
    ax.axvspan(0, limit_lat, ymin=0, ymax=limit_mem/max(memories+[limit_mem*1.5]),
               alpha=0.07, color=GREEN, label='Zona Edge OK')
    ax.axvline(limit_lat, color=ORANGE, ls='--', lw=1.5, alpha=0.8)
    ax.axhline(limit_mem, color=ORANGE, ls='--', lw=1.5, alpha=0.8)

    colors = [GREEN if (l <= limit_lat and m <= limit_mem) else RED
              for l, m in zip(latencies, memories)]
    ax.scatter(latencies, memories, c=colors, s=120, zorder=5, alpha=0.9)
    for label, x, y in zip(labels, latencies, memories):
        ax.annotate(label, (x, y), fontsize=8, color=WHITE,
                    xytext=(5, 5), textcoords='offset points')

    ax.set_xlabel('Latência de Inferência (ms)')
    ax.set_ylabel('Memória do Modelo (MB)')
    ax.set_title('Eficiência Computacional: Latência × Memória', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    plt.tight_layout()
    if out_path:
        save(fig, out_path)
    return fig
