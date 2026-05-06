"""
Gera os 8 notebooks de síntese a partir dos resultados reais dos experimentos.
4 sínteses de análise + 4 sínteses visuais.
Execute APÓS run_experiments.py.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import nbformat as nbf
from pathlib import Path

RESULTS_DIR = Path("experiments_results")
METRICS_DIR = RESULTS_DIR / "metrics"
FIGURES_DIR = RESULTS_DIR / "figures"
SYNTH_DIR   = Path(".")   # sínteses salvas na raiz do projeto


def load_result(nb_id):
    path = METRICS_DIR / f"{nb_id}_results.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def load_all():
    results = {}
    for nb_id in [f'nb{i:02d}' for i in range(1, 29)]:
        d = load_result(nb_id)
        if d:
            results[nb_id] = d
    return results


def best_pauc(data):
    """Extrai melhor pAUC disponível de um resultado de NB."""
    if not data:
        return None
    for key in ['avg_prot_a', 'pauc01']:
        if key in data:
            return float(data[key])
    if 'protocol_a' in data:
        return float(data['protocol_a'].get('pauc01', 0))
    if 'spec' in data:
        return float(data['spec'].get('avg_prot_a', 0))
    if 'models' in data:
        vals = [v.get('pauc01', 0) for v in data['models'].values()
                if isinstance(v, dict)]
        if vals: return float(max(vals))
    if 'model' in data:
        m = data['model']
        if isinstance(m, dict): return float(m.get('pauc01', 0))
    if 'ranking' in data:
        vals = [v.get('pauc01', 0) for v in data['ranking'].values()]
        if vals: return float(max(vals))
    return None


def nb_cell(source):
    return nbf.v4.new_code_cell(source)


def md_cell(source):
    return nbf.v4.new_markdown_cell(source)


def make_notebook(cells):
    nb = nbf.v4.new_notebook()
    nb.cells = cells
    return nb


def save_nb(nb, path):
    with open(path, 'w') as f:
        nbf.write(nb, f)
    print(f"  ✅ Gerado: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# SÍNTESE 1 — EXPLORATÓRIA (NB01-10)
# ═══════════════════════════════════════════════════════════════════════════════

def gen_sintese_1(results):
    cells = [
        md_cell("""# 🔬 SÍNTESE 1 — FASE EXPLORATÓRIA
## Notebooks 1–10 | Evidências e Métricas Reais

> Todos os valores abaixo foram medidos experimentalmente. pAUC@0.1 calculado
> a partir das curvas ROC reais de cada notebook.

---

### Protocolo de Avaliação
- **Métrica principal**: pAUC@FPR0.1 — área parcial sob a ROC na região de baixo falso positivo
- **Limite mínimo**: 0.80 (critério de aprovação)
- **Latência máxima**: 50 ms | **Memória máxima**: 4 MB
- **Validação**: LOSO (Leave-One-Source-Out)
"""),

        nb_cell("""import json, sys, os
sys.path.insert(0, '..')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

METRICS_DIR = Path('experiments_results/metrics')
FIGURES_DIR = Path('experiments_results/figures')

def load(nb_id):
    p = METRICS_DIR / f'{nb_id}_results.json'
    return json.load(open(p)) if p.exists() else {}

# Carrega resultados
nb01 = load('nb01'); nb02 = load('nb02'); nb03 = load('nb03')
nb04 = load('nb04'); nb05 = load('nb05'); nb06 = load('nb06')
nb07 = load('nb07'); nb08 = load('nb08'); nb09 = load('nb09')
nb10 = load('nb10')
print("✅ Resultados carregados")
"""),

        md_cell("## 📊 NB01 — Aprendizado Supervisionado"),
        nb_cell(f"""data = nb01.get('models', {{}})
print("NB01 — Aprendizado Supervisionado")
print("-" * 50)
for model, met in data.items():
    if isinstance(met, dict):
        print(f"  {{met.get('label','?'):25s}} | pAUC@0.1={{met.get('pauc01',0):.4f}} | "
              f"F1={{met.get('f1',0):.4f}} | Lat={{met.get('latency_ms','-'):.1f}}ms | "
              f"Mem={{met.get('memory_mb','-'):.2f}}MB")
"""),

        md_cell("## 📊 NB02 — Não Supervisionado"),
        nb_cell("""data = nb02.get('models', {})
print("NB02 — Não Supervisionado")
print("-" * 50)
for model, met in data.items():
    if isinstance(met, dict):
        print(f"  {met.get('label','?'):25s} | pAUC@0.1={met.get('pauc01',0):.4f} | "
              f"F1={met.get('f1',0):.4f} | Lat={met.get('latency_ms','-')}")
"""),

        md_cell("## 📊 NB03 — Baseline Real (4 Modelos)"),
        nb_cell("""data = nb03.get('models', {})
print("NB03 — Benchmark Real")
print("-" * 60)
header = f"{'Modelo':20s} | {'pAUC@0.1':10s} | {'F1':8s} | {'Lat(ms)':10s} | {'Mem(MB)':8s}"
print(header); print("-"*len(header))
for model, met in data.items():
    if isinstance(met, dict):
        lat = met.get('latency_ms')
        mem = met.get('memory_mb')
        print(f"  {met.get('label','?'):20s} | {met.get('pauc01',0):.4f}     | "
              f"{met.get('f1',0):.4f}   | {lat:.2f} ms   | {mem:.3f} MB" if lat and mem
              else f"  {met.get('label','?'):20s} | {met.get('pauc01',0):.4f}")
"""),

        md_cell("## 📊 NB04-06 — Representações Espectrais"),
        nb_cell("""print("NB04-06 — Representações Espectrais")
print("-" * 55)
for nb_id, nb_data in [('NB04 Mel', nb04), ('NB05 CWT', nb05), ('NB06 STFT', nb06)]:
    m = nb_data.get('model', {})
    ext = nb_data.get('extraction_ms', '?')
    print(f"  {nb_id:15s} | pAUC={m.get('pauc01',0):.4f} | "
          f"Ext={ext:.1f}ms" if isinstance(ext, float)
          else f"  {nb_id:15s} | pAUC={m.get('pauc01',0):.4f}")
"""),

        md_cell("## 📊 NB07-08 — Super-Vetor Híbrido"),
        nb_cell("""print("NB07-08 — Super-Vetor")
for nb_id, nb_data in [('NB07 Mel+MFCC+CWT', nb07), ('NB08 +NMF+Kurt', nb08)]:
    m = nb_data.get('model', {})
    n_feat = m.get('n_features','?')
    print(f"  {nb_id:22s} | pAUC={m.get('pauc01',0):.4f} | Dimensões={n_feat}")
"""),

        md_cell("## 📊 NB09-10 — Validação Cross-Domain e Domain Shift"),
        nb_cell("""print("NB09 — Kaggle Bearings (cross-domain)")
m9 = nb09.get('model', {})
print(f"  pAUC@0.1 = {m9.get('pauc01',0):.4f}")

print("\\nNB10 — Drive Próprio (domain shift severo)")
m10 = nb10.get('model', {})
drop = nb10.get('domain_shift_drop', 0)
ctrl = m10.get('pauc01_controlled', '?')
print(f"  pAUC@0.1 controlado = {ctrl:.4f}" if isinstance(ctrl, float) else f"  pAUC controlado = {ctrl}")
print(f"  pAUC@0.1 cego (Drive) = {m10.get('pauc01',0):.4f}")
print(f"  Queda = {drop:.4f} pp  ← Motivação das 11 Frentes de Melhoria")
"""),

        md_cell("""## 🏆 Resumo Fase 1

| Componente | Decisão | Critério |
|-----------|---------|----------|
| XGBoost | ✅ Campeão supervisionado | Melhor pAUC + Edge-ready |
| CNN proxy | 🔴 Descartado como motor | Lat+Mem fora dos limites |
| OC-SVM | 🔴 Descartado | pAUC < 0.80 |
| Autoencoder | 🔴 Conceito mantido via NMF | Lat+Mem fora dos limites |
| Isolation Forest | 🔴 Descartado | pAUC < 0.80 |
| Mel-Spectrogram | ✅ Representação principal | Melhor integração pipeline |
| CWT | 🔴 Descartado como motor | Lat extração esgota orçamento |
| LOSO | ✅ Protocolo adotado | Única medição justa de generalização |
"""),
    ]

    nb = make_notebook(cells)
    save_nb(nb, SYNTH_DIR / "SINTESE_1_Exploratorio_REAL.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
# SÍNTESE 2 — OTIMIZAÇÃO (NB11-15)
# ═══════════════════════════════════════════════════════════════════════════════

def gen_sintese_2(results):
    cells = [
        md_cell("""# ⚙️ SÍNTESE 2 — FASE DE OTIMIZAÇÃO
## Notebooks 11–15 | Frentes 1–5 | Evidências Reais

---
Frentes de melhoria aplicadas ao pipeline base para aumentar pAUC@0.1
em cenários de domain shift e generalização cross-domain.
"""),

        nb_cell("""import json, sys
sys.path.insert(0, '..')
from pathlib import Path
METRICS_DIR = Path('experiments_results/metrics')
def load(nb_id): p = METRICS_DIR/f'{nb_id}_results.json'; return json.load(open(p)) if p.exists() else {}
nb11=load('nb11'); nb12=load('nb12'); nb13=load('nb13'); nb14=load('nb14'); nb15=load('nb15')
print("✅ Resultados NB11-15 carregados")
"""),

        md_cell("## Frente 1 — NB11: Regularização L2 + Limiar Gamma"),
        nb_cell("""print("NB11 — Regularização L2")
for k, v in nb11.get('models',{}).items():
    if isinstance(v, dict):
        print(f"  {v.get('label','?'):15s} pAUC={v.get('pauc01',0):.4f}")
print(f"\\nLimiar Gamma calibrado: {nb11.get('gamma_threshold', '?'):.4f}")
"""),

        md_cell("## Frente 2 — NB12: GMM Campeão Não Supervisionado"),
        nb_cell("""print("NB12 — GMM vs Mahalanobis vs CNN")
for k, v in nb12.get('models',{}).items():
    if isinstance(v, dict):
        lat = v.get('latency_ms', '-')
        print(f"  {v.get('label','?'):25s} pAUC={v.get('pauc01',0):.4f} | "
              f"F1={v.get('f1',0):.4f} | Lat={lat:.2f}ms" if isinstance(lat,float)
              else f"  {v.get('label','?'):25s} pAUC={v.get('pauc01',0):.4f}")
"""),

        md_cell("## Frente 3 — NB13: HHT+UKF ← Componente Mais Crítico"),
        nb_cell("""print("NB13 — Impacto do HHT+UKF")
raw = nb13.get('models',{}).get('raw',{})
hht = nb13.get('models',{}).get('hht',{})
gain = nb13.get('pauc_gain', 0)
snr  = nb13.get('snr_gain_db', 0)
print(f"  Sem HHT+UKF: pAUC={raw.get('pauc01',0):.4f}")
print(f"  Com HHT+UKF: pAUC={hht.get('pauc01',0):.4f}")
print(f"  Ganho pAUC: +{gain:.4f} pp")
print(f"  Ganho SNR:  +{snr:.1f} dB")
"""),

        md_cell("## Frente 4 — NB14: Mixup para Domain Shift"),
        nb_cell("""print("NB14 — Mixup (α=0.4)")
no_mix = nb14.get('models',{}).get('no_mixup',{})
mix    = nb14.get('models',{}).get('mixup',{})
gain   = nb14.get('pauc_gain', 0)
print(f"  Sem Mixup: pAUC={no_mix.get('pauc01',0):.4f}")
print(f"  Com Mixup: pAUC={mix.get('pauc01',0):.4f}")
pct = (gain / (no_mix.get('pauc01',1)+1e-10)) * 100
print(f"  Melhoria:  +{gain:.4f} pp ({pct:.1f}%)")
"""),

        md_cell("## Frente 5 — NB15: pAUC@0.1 como Métrica Principal"),
        nb_cell("""print("NB15 — Ranking por pAUC@0.1 vs F1 global")
ranking = nb15.get('ranking', {})
print(f"{'Modelo':15s} | {'pAUC@0.1':10s} | {'F1':8s} | {'AUC':8s}")
print("-" * 50)
for name, met in sorted(ranking.items(), key=lambda x: -x[1].get('pauc01',0)):
    print(f"  {name:15s} | {met.get('pauc01',0):.4f}     | {met.get('f1',0):.4f}   | {met.get('auc',0):.4f}")
print("\\n⚠️  Tiny-AST lidera em F1/AUC mas fica atrás em pAUC@0.1")
"""),
    ]

    nb = make_notebook(cells)
    save_nb(nb, SYNTH_DIR / "SINTESE_2_Otimizacao_REAL.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
# SÍNTESE 3 — VALIDAÇÃO (NB16-21)
# ═══════════════════════════════════════════════════════════════════════════════

def gen_sintese_3(results):
    cells = [
        md_cell("""# ✅ SÍNTESE 3 — FASE DE VALIDAÇÃO
## Notebooks 16–21 | Frentes 6–11 | Evidências Reais

---
Formalização, validação externa e consolidação dos dois protocolos.
"""),

        nb_cell("""import json, sys
sys.path.insert(0, '..')
from pathlib import Path
METRICS_DIR = Path('experiments_results/metrics')
def load(nb_id): p = METRICS_DIR/f'{nb_id}_results.json'; return json.load(open(p)) if p.exists() else {}
nb16=load('nb16'); nb17=load('nb17'); nb18=load('nb18')
nb19=load('nb19'); nb20=load('nb20'); nb21=load('nb21')
print("✅ Resultados NB16-21 carregados")
"""),

        md_cell("## Frente 6 — NB16: Limiar Gamma com FPR Alvo Formal"),
        nb_cell("""print("NB16 — Gamma Thresholds por FPR alvo")
for k, v in nb16.get('thresholds', {}).items():
    print(f"  FPR alvo={v.get('fpr_target',0):.2f} | τ={v.get('threshold',0):.4f} | F1={v.get('f1',0):.4f}")
print(f"  pAUC@0.1 = {nb16.get('pauc01',0):.4f}")
"""),

        md_cell("## Frente 7 — NB17: Protocolo A/B + Outlier Exposure"),
        nb_cell("""print("NB17 — Separação Protocolo A / Protocolo B")
for k, v in nb17.get('models', {}).items():
    if isinstance(v, dict):
        print(f"  {v.get('label','?'):35s} pAUC={v.get('pauc01',0):.4f}")
"""),

        md_cell("## Frente 8 — NB18: Arena Não Supervisionada Final"),
        nb_cell("""print("NB18 — Arena: GMM vs Mahalanobis vs Isolation Forest")
for k, v in nb18.get('models', {}).items():
    if isinstance(v, dict):
        lat = v.get('latency_ms', '-')
        mem = v.get('memory_mb', '-')
        approved = "✅" if v.get('pauc01',0) >= 0.80 else "🔴"
        print(f"  {approved} {v.get('label','?'):25s} pAUC={v.get('pauc01',0):.4f} | "
              f"Lat={lat:.2f}ms | Mem={mem:.3f}MB" if isinstance(lat,float) and isinstance(mem,float)
              else f"  {approved} {v.get('label','?'):25s} pAUC={v.get('pauc01',0):.4f}")
"""),

        md_cell("## Frente 9 — NB19: Pré-Treino e Augmentation"),
        nb_cell("""print("NB19 — Pré-Treino + Augmentation (cross-domain Kaggle)")
for k, v in nb19.get('models', {}).items():
    if isinstance(v, dict):
        print(f"  {v.get('label','?'):35s} pAUC={v.get('pauc01',0):.4f}")
"""),

        md_cell("## Frente 10 — NB20: XAI — Hotspots e Bandas Espectrais"),
        nb_cell("""print("NB20 — XAI: Hotspots Temporais")
for h in nb20.get('hotspots', []):
    print(f"  H{h['rank']} @ {h['time_s']:.3f}s | Intensidade={h['intensity']:.4f}")

print("\\nNB20 — XAI: Ativação por Banda de Frequência")
bands = nb20.get('band_activations', {})
for band, val in bands.items():
    bar = "█" * int(val * 200)
    print(f"  {band:5s}: {val:.4f}  {bar}")
"""),

        md_cell("## Frente 11 — NB21: Consolidação LOSO Multi-Domínio"),
        nb_cell("""print("NB21 — Frente 11: Resultado LOSO por Domínio")
print(f"{'Domínio':12s} | {'Prot.A':8s} | {'Prot.B':8s} | {'Score DCASE':12s}")
print("-" * 50)
for dom, v in nb21.get('per_domain', {}).items():
    pa = v.get('prot_a',0); pb = v.get('prot_b',0); dc = v.get('dcase_score',0)
    print(f"  {dom:12s} | {pa:.4f}   | {pb:.4f}   | {dc:.4f}")
print(f"  {'MÉDIA':12s} | {nb21.get('avg_prot_a',0):.4f}   | {nb21.get('avg_prot_b',0):.4f}   | {nb21.get('avg_dcase_score',0):.4f}")
"""),
    ]

    nb = make_notebook(cells)
    save_nb(nb, SYNTH_DIR / "SINTESE_3_Validacao_REAL.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
# SÍNTESE 4 — CONFRONTAMENTO (NB22-28)
# ═══════════════════════════════════════════════════════════════════════════════

def gen_sintese_4(results):
    cells = [
        md_cell("""# 💎 SÍNTESE 4 — FASE DE CONFRONTAMENTO
## Notebooks 22–28 | DIAMOND CRISTAL CLEAN | Evidências Reais

---
Especificação final, ablation study e veredito definitivo da arquitetura.
"""),

        nb_cell("""import json, sys
sys.path.insert(0, '..')
from pathlib import Path
METRICS_DIR = Path('experiments_results/metrics')
def load(nb_id): p = METRICS_DIR/f'{nb_id}_results.json'; return json.load(open(p)) if p.exists() else {}
nb22=load('nb22'); nb23=load('nb23'); nb24=load('nb24')
nb25=load('nb25'); nb26=load('nb26'); nb27=load('nb27'); nb28=load('nb28')
print("✅ Resultados NB22-28 carregados")
"""),

        md_cell("## NB22-23 — Arquitetura Campeã: Protocolos A e B"),
        nb_cell("""print("NB22 — Arquitetura Campeã")
for prot, key in [('Protocolo A', 'protocol_a'), ('Protocolo B', 'protocol_b')]:
    met = nb22.get(key, {})
    lat = met.get('latency_ms')
    mem = met.get('memory_mb')
    print(f"  {prot}: pAUC={met.get('pauc01',0):.4f} | "
          + (f"Lat={lat:.2f}ms | Mem={mem:.3f}MB" if lat and mem else ""))

print("\\nNB23 — Validação Cruzada da Arquitetura Campeã")
for prot, key in [('Protocolo A', 'protocol_a'), ('Protocolo B', 'protocol_b')]:
    met = nb23.get(key, {})
    print(f"  {prot}: pAUC={met.get('pauc01',0):.4f}")
"""),

        md_cell("## NB25 — MIMII Multi-SNR: Limites Operacionais"),
        nb_cell("""print("NB25 — MIMII Sweep: SNR × pAUC@0.1")
print(f"{'SNR (dB)':12s} | {'Protocolo A':12s} | {'Protocolo B':12s} | {'Aprovado?':10s}")
print("-" * 55)
for k, v in nb25.get('per_snr', {}).items():
    snr = v.get('snr_db','?')
    pa  = v.get('prot_a', 0)
    pb  = v.get('prot_b', 0)
    ok_a = "✅" if pa >= 0.80 else "🔴"
    ok_b = "✅" if pb >= 0.80 else "🔴"
    print(f"  {snr:+3d} dB      | {ok_a} {pa:.4f}    | {ok_b} {pb:.4f}    |")
print("\\n⚠️  Limite operacional: Prot.B falha quando SNR < -3 dB sem rótulos")
"""),

        md_cell("## NB27 — Ablation Study: Importância dos Componentes"),
        nb_cell("""print("NB27 — Ablation Study")
ablation = nb27.get('ablation', {})
pauc_full = nb27.get('pauc_full', 0)
print(f"  Referência (completo): pAUC={pauc_full:.4f}")
print("-" * 60)
sorted_abl = sorted(ablation.items(), key=lambda x: -x[1].get('delta',0))
for name, v in sorted_abl:
    if name == 'Referência (completo)': continue
    delta = v.get('delta', 0)
    impact = "🔴 Crítico" if delta >= 0.05 else ("🟡 Importante" if delta >= 0.02 else "🟢 Leve")
    print(f"  {impact:15s} | {name:25s} | Δ pAUC = -{delta:.4f}")
"""),

        md_cell("## NB28 — DIAMOND CRISTAL CLEAN: Resultado Final"),
        nb_cell("""print("NB28 — Resultado Final DIAMOND CRISTAL CLEAN")
spec = nb28.get('spec', {})
print(f"  pAUC@0.1 Protocolo A (média LOSO): {spec.get('avg_prot_a',0):.4f}")
print(f"  pAUC@0.1 Protocolo B (média LOSO): {spec.get('avg_prot_b',0):.4f}")
print(f"  Score DCASE (médio):               {spec.get('avg_dcase_score',0):.4f}")
lat = spec.get('avg_latency_ms_a')
mem = spec.get('avg_memory_mb_a')
if lat: print(f"  Latência Prot.A (média):            {lat:.2f} ms ({'✅' if lat<50 else '🔴'})")
if mem: print(f"  Memória Prot.A (média):             {mem:.3f} MB ({'✅' if mem<4 else '🔴'})")
print("\\n📋 Hiperparâmetros:")
for k, v in spec.get('hyperparams', {}).items():
    print(f"  {k:25s} = {v}")
"""),
    ]

    nb = make_notebook(cells)
    save_nb(nb, SYNTH_DIR / "SINTESE_4_Confrontamento_REAL.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
# SÍNTESES VISUAIS
# ═══════════════════════════════════════════════════════════════════════════════

def _visual_setup_cell():
    return nb_cell("""import json, sys, numpy as np
sys.path.insert(0, '..')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

METRICS_DIR = Path('experiments_results/metrics')
FIGURES_DIR = Path('experiments_results/figures')

plt.rcParams.update({
    'figure.facecolor':'#0d1117','axes.facecolor':'#161b22',
    'text.color':'#f0f6fc','axes.labelcolor':'#f0f6fc',
    'xtick.color':'#8b949e','ytick.color':'#8b949e',
    'axes.edgecolor':'#30363d','grid.color':'#30363d','grid.alpha':0.5,
})

def load(nb_id):
    p = METRICS_DIR/f'{nb_id}_results.json'
    return json.load(open(p)) if p.exists() else {}

def best_pauc(data):
    for key in ['avg_prot_a','pauc01']:
        if key in data: return float(data[key])
    if 'protocol_a' in data: return float(data['protocol_a'].get('pauc01',0))
    if 'spec' in data: return float(data['spec'].get('avg_prot_a',0))
    if 'models' in data:
        vals = [v.get('pauc01',0) for v in data['models'].values() if isinstance(v,dict)]
        if vals: return float(max(vals))
    if 'model' in data:
        m = data['model']
        if isinstance(m,dict): return float(m.get('pauc01',0))
    if 'ranking' in data:
        vals = [v.get('pauc01',0) for v in data['ranking'].values()]
        if vals: return float(max(vals))
    return 0.0

all_data = {f'nb{i:02d}': load(f'nb{i:02d}') for i in range(1,29)}
print(f"✅ {sum(1 for v in all_data.values() if v)} resultados carregados")
""")


def gen_visual_1(results):
    cells = [
        md_cell("# 📊 SÍNTESE VISUAL 1 — Benchmark Completo de pAUC@0.1"),
        _visual_setup_cell(),
        nb_cell("""# Coleta pAUC de todos os notebooks
nbs = [f'nb{i:02d}' for i in range(1,29)]
pauc_vals = [best_pauc(all_data[nb]) for nb in nbs]
labels = [nb.upper() for nb in nbs]

fig, ax = plt.subplots(figsize=(16, 6))
colors = ['#2ea043' if p >= 0.80 else '#da3633' for p in pauc_vals]
bars = ax.bar(labels, pauc_vals, color=colors, alpha=0.85, edgecolor='none')
ax.axhline(0.80, color='#f0883e', ls='--', lw=2, label='Limite mínimo 0.80')
for bar, val in zip(bars, pauc_vals):
    if val > 0:
        ax.text(bar.get_x()+bar.get_width()/2, val+0.01, f'{val:.2f}',
                ha='center', va='bottom', fontsize=7, color='white')
ax.set_ylim(0, 1.1); ax.set_ylabel('pAUC@0.1')
ax.set_title('Benchmark Completo: pAUC@0.1 por Notebook (NB01–NB28)', fontsize=13, fontweight='bold')
ax.legend(fontsize=10); ax.grid(True, axis='y', alpha=0.4)
plt.xticks(rotation=45, ha='right', fontsize=8)
plt.tight_layout()
plt.savefig('experiments_results/figures/visual1_pauc_all.png', dpi=130,
            bbox_inches='tight', facecolor='#0d1117')
plt.show()
print(f"Notebooks acima do limite 0.80: {sum(1 for p in pauc_vals if p>=0.80)}/28")
"""),
    ]
    nb = make_notebook(cells)
    save_nb(nb, SYNTH_DIR / "SINTESE_VISUAL_1_Benchmark_REAL.ipynb")


def gen_visual_2(results):
    cells = [
        md_cell("# 📊 SÍNTESE VISUAL 2 — Latência e Memória por Modelo"),
        _visual_setup_cell(),
        nb_cell("""# Coleta latência e memória de modelos-chave
nb01=load('nb01'); nb03=load('nb03'); nb12=load('nb12')
nb22=load('nb22'); nb27=load('nb27')

model_data = {}
for key, nb_d in [('nb01',nb01),('nb03',nb03)]:
    for k, v in nb_d.get('models',{}).items():
        if isinstance(v,dict) and v.get('latency_ms') and v.get('memory_mb'):
            model_data[v.get('label',k)] = {'lat': v['latency_ms'], 'mem': v['memory_mb'],
                                              'pauc': v.get('pauc01',0)}

# Adiciona protocolos finais
for prot, key in [('XGBoost (Prot.A)','protocol_a'),('GMM (Prot.B)','protocol_b')]:
    met = nb22.get(key, {})
    if met.get('latency_ms') and met.get('memory_mb'):
        model_data[prot] = {'lat': met['latency_ms'], 'mem': met['memory_mb'],
                             'pauc': met.get('pauc01',0)}

if model_data:
    labels = list(model_data.keys())
    lats = [model_data[l]['lat'] for l in labels]
    mems = [model_data[l]['mem'] for l in labels]
    paucs = [model_data[l]['pauc'] for l in labels]

    fig, ax = plt.subplots(figsize=(9,6))
    scatter_colors = ['#2ea043' if (l<=50 and m<=4) else '#da3633'
                      for l,m in zip(lats,mems)]
    sc = ax.scatter(lats, mems, c=scatter_colors, s=120, zorder=5, alpha=0.9)
    ax.axvline(50, color='#f0883e', ls='--', lw=1.5, alpha=0.8, label='Lat≤50ms')
    ax.axhline(4,  color='#f0883e', ls=':',  lw=1.5, alpha=0.8, label='Mem≤4MB')
    for lbl, x, y, p in zip(labels, lats, mems, paucs):
        ax.annotate(f'{lbl}\\npAUC={p:.2f}', (x,y), fontsize=7.5,
                    xytext=(6,6), textcoords='offset points', color='white')
    ax.set_xlabel('Latência (ms)'); ax.set_ylabel('Memória (MB)')
    ax.set_title('Eficiência: Latência × Memória por Modelo', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9); ax.grid(True,alpha=0.3)
    plt.tight_layout()
    plt.savefig('experiments_results/figures/visual2_latency_memory.png', dpi=130,
                bbox_inches='tight', facecolor='#0d1117')
    plt.show()
else:
    print("Dados de latência/memória insuficientes — verifique se os experimentos rodaram.")
"""),
    ]
    nb = make_notebook(cells)
    save_nb(nb, SYNTH_DIR / "SINTESE_VISUAL_2_Latencia_Memoria_REAL.ipynb")


def gen_visual_3(results):
    cells = [
        md_cell("# 📊 SÍNTESE VISUAL 3 — pAUC@0.1 × Score DCASE × Multi-SNR"),
        _visual_setup_cell(),
        nb_cell("""# Score DCASE por domínio (NB28)
nb28 = load('nb28')
spec = nb28.get('spec', {})
per_domain = spec.get('per_domain', {})

if per_domain:
    domains = list(per_domain.keys())
    pa = [per_domain[d].get('prot_a_pauc',0) for d in domains]
    pb = [per_domain[d].get('prot_b_pauc',0) for d in domains]
    dc = [per_domain[d].get('dcase_score',0) for d in domains]

    x = np.arange(len(domains))
    fig, axes = plt.subplots(1,2,figsize=(14,5))
    for ax in axes: ax.set_facecolor('#161b22')

    axes[0].bar(x-0.25, pa, 0.25, label='Protocolo A', color='#2ea043', alpha=0.85)
    axes[0].bar(x,      dc, 0.25, label='Score DCASE', color='#f0883e', alpha=0.85)
    axes[0].bar(x+0.25, pb, 0.25, label='Protocolo B', color='#1f6feb', alpha=0.85)
    axes[0].axhline(0.80,color='white',ls='--',lw=1.2,alpha=0.6)
    axes[0].set_xticks(x); axes[0].set_xticklabels([d.upper() for d in domains])
    axes[0].set_ylim(0,1.05); axes[0].set_ylabel('pAUC@0.1')
    axes[0].set_title('NB28 — Score Final por Domínio (LOSO)', fontsize=11, fontweight='bold')
    axes[0].legend(fontsize=9); axes[0].grid(True,axis='y',alpha=0.3)

    # Multi-SNR
    nb25 = load('nb25')
    snr_data = nb25.get('per_snr', {})
    if snr_data:
        snrs = sorted([v.get('snr_db',0) for v in snr_data.values()])
        pa25 = [v.get('prot_a',0) for v in sorted(snr_data.values(), key=lambda x:x.get('snr_db',0))]
        pb25 = [v.get('prot_b',0) for v in sorted(snr_data.values(), key=lambda x:x.get('snr_db',0))]
        axes[1].plot(snrs, pa25, 'o-', color='#2ea043', lw=2, ms=8, label='Protocolo A')
        axes[1].plot(snrs, pb25, 's--', color='#1f6feb', lw=2, ms=8, label='Protocolo B')
        axes[1].axhline(0.80,color='#f0883e',ls='--',lw=1.5,label='Limite 0.80')
        axes[1].set_xlabel('SNR (dB)'); axes[1].set_ylabel('pAUC@0.1')
        axes[1].set_title('NB25 — MIMII Multi-SNR', fontsize=11, fontweight='bold')
        axes[1].legend(fontsize=9); axes[1].grid(True,alpha=0.3); axes[1].set_ylim(0,1.05)

    fig.patch.set_facecolor('#0d1117')
    plt.tight_layout()
    plt.savefig('experiments_results/figures/visual3_dcase_snr.png', dpi=130,
                bbox_inches='tight', facecolor='#0d1117')
    plt.show()
else:
    print("Dados NB28 não disponíveis — rode NB28 primeiro.")
"""),
    ]
    nb = make_notebook(cells)
    save_nb(nb, SYNTH_DIR / "SINTESE_VISUAL_3_DCASE_SNR_REAL.ipynb")


def gen_visual_4(results):
    cells = [
        md_cell("# 📊 SÍNTESE VISUAL 4 — Resumo Final: Evolução + Ablation + Comparativo"),
        _visual_setup_cell(),
        nb_cell("""# Evolução pAUC@0.1 ao longo dos NB
nbs = [f'nb{i:02d}' for i in range(1,29)]
pauc_vals = [best_pauc(all_data[nb]) for nb in nbs]
labels = [nb.upper() for nb in nbs]

fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor('#0d1117')

# 1) Linha de evolução
ax1 = fig.add_subplot(2, 2, (1,2))
ax1.set_facecolor('#161b22')
x = np.arange(len(labels))
ax1.plot(x, pauc_vals, color='#2ea043', marker='o', lw=2, ms=5, zorder=3)
ax1.fill_between(x, pauc_vals, 0.80,
                  where=np.array(pauc_vals)>=0.80, alpha=0.1, color='#2ea043')
ax1.axhline(0.80,color='#f0883e',ls='--',lw=1.5,alpha=0.8,label='Limite 0.80')
ax1.set_xticks(x); ax1.set_xticklabels(labels, rotation=60, ha='right', fontsize=7)
ax1.set_ylim(0,1.05); ax1.set_ylabel('pAUC@0.1')
ax1.set_title('Evolução pAUC@0.1: NB01 → NB28', fontsize=12, fontweight='bold')
ax1.legend(fontsize=9); ax1.grid(True,alpha=0.3)

# 2) Ablation
nb27 = load('nb27')
ablation = nb27.get('ablation', {})
pauc_full = nb27.get('pauc_full', 0)
if ablation:
    comps = [k for k in ablation if k != 'Referência (completo)']
    deltas = [ablation[k].get('delta',0) for k in comps]
    colors_ab = ['#da3633' if d>=0.05 else '#f0883e' if d>=0.02 else '#2ea043' for d in deltas]
    ax2 = fig.add_subplot(2, 2, 3)
    ax2.set_facecolor('#161b22')
    short_comps = [c.replace('Sem ','') for c in comps]
    ax2.barh(short_comps, deltas, color=colors_ab, alpha=0.85)
    ax2.set_xlabel('Δ pAUC@0.1')
    ax2.set_title(f'Ablation Study (ref={pauc_full:.3f})', fontsize=11, fontweight='bold')
    ax2.grid(True,axis='x',alpha=0.3)

# 3) Final comparison
nb28 = load('nb28')
spec = nb28.get('spec', {})
ax3 = fig.add_subplot(2, 2, 4)
ax3.set_facecolor('#161b22')
final_models = ['Prot.A\\n(XGBoost)', 'Prot.B\\n(GMM)', 'DCASE\\nScore']
final_vals = [spec.get('avg_prot_a',0), spec.get('avg_prot_b',0), spec.get('avg_dcase_score',0)]
bars3 = ax3.bar(final_models, final_vals, color=['#2ea043','#1f6feb','#f0883e'], alpha=0.9)
ax3.axhline(0.80,color='white',ls='--',lw=1.2,alpha=0.6,label='Limite 0.80')
for bar, val in zip(bars3, final_vals):
    ax3.text(bar.get_x()+bar.get_width()/2, val+0.01, f'{val:.3f}',
             ha='center', va='bottom', color='white', fontsize=11, fontweight='bold')
ax3.set_ylim(0,1.1); ax3.set_title('DIAMOND CRISTAL CLEAN\\nResultado Final (LOSO)', fontsize=11, fontweight='bold')
ax3.legend(fontsize=9); ax3.grid(True,axis='y',alpha=0.3)

plt.tight_layout(pad=2)
plt.savefig('experiments_results/figures/visual4_resumo_final.png', dpi=130,
            bbox_inches='tight', facecolor='#0d1117')
plt.show()
print("✅ Resumo visual completo gerado")
"""),
    ]
    nb = make_notebook(cells)
    save_nb(nb, SYNTH_DIR / "SINTESE_VISUAL_4_Resumo_Final_REAL.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 55)
    print("  Gerando Sínteses a partir dos resultados reais...")
    print("=" * 55)
    results = load_all()
    print(f"  {len(results)} notebooks com resultados encontrados.\n")

    gen_sintese_1(results)
    gen_sintese_2(results)
    gen_sintese_3(results)
    gen_sintese_4(results)
    gen_visual_1(results)
    gen_visual_2(results)
    gen_visual_3(results)
    gen_visual_4(results)

    print("\n✅ 8 sínteses geradas com sucesso!")
    print("   Abra no Jupyter: jupyter notebook")
