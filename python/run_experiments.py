"""
Runner de todos os 28 experimentos.
Cada função NB_XX implementa exatamente o que aquele notebook realizou,
mede métricas reais (pAUC, F1, latência, memória) e salva resultados.
Execute: python3 run_experiments.py
"""
import sys, os, json, time, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from pathlib import Path

RESULTS_DIR = Path("experiments_results")
FIGURES_DIR = RESULTS_DIR / "figures"
METRICS_DIR = RESULTS_DIR / "metrics"
MODELS_DIR  = RESULTS_DIR / "models"
for d in [FIGURES_DIR, METRICS_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── Imports dos módulos src ──────────────────────────────────────────────────
from src.data_generator import (generate_dataset, train_test_split_loso,
                                 generate_mimii_snr)
from src.features import (batch_extract, NMFDetector, extract_super_vector,
                           log_mel_spectrogram, mfcc, band_energies, kurtosis)
from src.dsp import hht_ukf, rpca_signal, snr_estimate, emd
from src.models_zoo import (train_xgboost, GMMDetector, MahalanobisDetector,
                              train_ocsvm, train_isolation_forest,
                              train_mlp_cnn_proxy, SimpleAutoencoder,
                              build_tiny_ast_proxy, mixup_augment)
from src.metrics import (pauc_at_fpr, compute_f1, compute_auc, full_metrics,
                          measure_latency, measure_memory_mb, fit_gamma_threshold)
from src.viz import (plot_roc_pauc, plot_metric_bars, plot_signal_and_spectrogram,
                      plot_evolution, plot_ablation, plot_xai_heatmap,
                      plot_latency_memory, save)

RESULTS_ALL = {}
_CURRENT_DATASET = {}

def track_dataset(X, y, meta, X_tr=None, y_tr=None, X_te=None, y_te=None):
    """Registra estatísticas do dataset atual para inclusão automática no JSON."""
    global _CURRENT_DATASET
    if X_tr is None: X_tr, y_tr = X, y
    if X_te is None: X_te, y_te = X, y
    _CURRENT_DATASET = dataset_info(X, y, meta, X_tr, y_tr, X_te, y_te)

def save_result(nb_id, result):
    if _CURRENT_DATASET:
        result['dataset'] = _CURRENT_DATASET
    RESULTS_ALL[nb_id] = result
    out = METRICS_DIR / f"{nb_id}_results.json"
    with open(out, 'w') as f:
        json.dump(result, f, indent=2, default=float)
    print(f"  ✅ Salvo: {out}")


def get_fig_path(nb_id, name):
    return str(FIGURES_DIR / f"{nb_id}_{name}.png")


def dataset_info(X, y, meta, X_tr, y_tr, X_te, y_te):
    """Captura estatísticas do dataset para rastreabilidade no artigo."""
    from collections import Counter
    domain_counts  = Counter(m['domain'] for m in meta)
    machine_key    = 'machine' if 'machine' in meta[0] else 'machine_type'
    machine_counts = Counter(m[machine_key] for m in meta)
    sig_len = int(X.shape[1]) if X.ndim == 2 else 32000
    return {
        'n_total':               int(len(y)),
        'n_normal':              int(np.sum(y == 0)),
        'n_anomaly':             int(np.sum(y == 1)),
        'n_train':               int(len(y_tr)),
        'n_train_normal':        int(np.sum(y_tr == 0)),
        'n_train_anomaly':       int(np.sum(y_tr == 1)),
        'n_test':                int(len(y_te)),
        'n_test_normal':         int(np.sum(y_te == 0)),
        'n_test_anomaly':        int(np.sum(y_te == 1)),
        'machines':              sorted(set(m[machine_key] for m in meta)),
        'domains':               sorted(set(m['domain'] for m in meta)),
        'samples_per_domain':    {k: int(v) for k, v in domain_counts.items()},
        'samples_per_machine':   {k: int(v) for k, v in machine_counts.items()},
        'signal_length_samples': sig_len,
        'signal_duration_s':     round(sig_len / 16000, 2),
        'sample_rate_hz':        16000,
        'source':                'synthetic (sinusoidal+harmonics+pink_noise+fault_signature)',
    }


def smart_split(X, y, meta, test_domain, test_size=0.25, seed=42):
    """
    LOSO se possível; caso contrário usa stratified split.
    Evita sets vazios quando só há um domínio no dataset.
    """
    from sklearn.model_selection import train_test_split as sk_split
    train_idx = [i for i, m in enumerate(meta) if m['domain'] != test_domain]
    test_idx  = [i for i, m in enumerate(meta) if m['domain'] == test_domain]
    if len(train_idx) >= 10 and len(test_idx) >= 5:
        return X[train_idx], y[train_idx], X[test_idx], y[test_idx]
    # Fallback: stratified split
    X_train, X_test, y_train, y_test = sk_split(X, y, test_size=test_size, random_state=seed, stratify=y)
    return X_train, y_train, X_test, y_test


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 1 — EXPLORAÇÃO (NB 01 – 10)
# ═══════════════════════════════════════════════════════════════════════════════

def nb01_supervisionado():
    """NB01: Aprendizado supervisionado — CNN×XGBoost×OC-SVM (sem pré-proc)."""
    print("\n─── NB01: Supervisionado ───")
    X, y, meta = generate_dataset(n_normal=60, n_anomaly=20,
                                   machines=['fan','pump'], domains=['dcase'], seed=1)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='dcase')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)
    # Usa apenas stats simples (sem pipeline DSP ainda)
    def raw_features(signals):
        feats = []
        for s in signals:
            mel = log_mel_spectrogram(s)
            f = np.concatenate([np.mean(mel, 0), np.std(mel, 0),
                                 [kurtosis(s), np.std(s)]])
            feats.append(f)
        return np.array(feats)

    X_tr_f = raw_features(X_tr)
    X_te_f = raw_features(X_te)

    results = {}
    # XGBoost
    model_xgb, sc, scores_xgb = train_xgboost(X_tr_f, y_tr, X_te_f)
    m_xgb = full_metrics(y_te, scores_xgb, model=model_xgb,
                          X_single=X_te_f[:1],
                          predict_fn=lambda x: model_xgb.predict_proba(sc.transform(x))[:,1])
    m_xgb['label'] = 'XGBoost'
    results['xgboost'] = m_xgb

    # MLP proxy CNN (maior latência/memória)
    model_cnn, sc_cnn, scores_cnn = train_mlp_cnn_proxy(X_tr_f, y_tr, X_te_f)
    m_cnn = full_metrics(y_te, scores_cnn, model=model_cnn, X_single=X_te_f[:1],
                          predict_fn=lambda x: model_cnn.predict_proba(sc_cnn.transform(x))[:,1])
    m_cnn['label'] = 'CNN proxy'
    results['cnn'] = m_cnn

    # OC-SVM
    model_svm, sc_svm, scores_svm = train_ocsvm(X_tr_f[y_tr==0], X_te_f)
    m_svm = full_metrics(y_te, scores_svm, model=model_svm, X_single=X_te_f[:1],
                          predict_fn=lambda x: -model_svm.decision_function(sc_svm.transform(x)))
    m_svm['label'] = 'OC-SVM'
    results['ocsvm'] = m_svm

    # Figura
    plot_metric_bars(['XGBoost','CNN proxy','OC-SVM'],
                     [m_xgb['pauc01'], m_cnn['pauc01'], m_svm['pauc01']],
                     title='NB01 — Aprendizado Supervisionado: pAUC@0.1',
                     out_path=get_fig_path('nb01', 'pauc_comparison'))
    plot_roc_pauc(y_te, {'XGBoost': scores_xgb, 'CNN': scores_cnn, 'OC-SVM': scores_svm},
                  title='NB01 — ROC Curves', out_path=get_fig_path('nb01', 'roc'))

    res = {'nb': 'NB01', 'topic': 'Supervisionado', 'models': results}
    save_result('nb01', res)
    return res


def nb02_nao_supervisionado():
    """NB02: Não supervisionado — Autoencoder×Isolation Forest."""
    print("\n─── NB02: Não Supervisionado ───")
    X, y, meta = generate_dataset(n_normal=60, n_anomaly=20,
                                   machines=['fan','pump'], domains=['dcase'], seed=2)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='dcase')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def raw_features(signals):
        return np.array([np.concatenate([np.mean(log_mel_spectrogram(s),0),
                                          np.std(log_mel_spectrogram(s),0)])
                          for s in signals])

    X_tr_f = raw_features(X_tr)
    X_te_f = raw_features(X_te)
    X_normal_f = X_tr_f[y_tr == 0]

    results = {}
    # Autoencoder
    ae = SimpleAutoencoder(n_features=X_tr_f.shape[1], n_latent=32)
    ae.fit(X_normal_f)
    scores_ae = ae.score(X_te_f)
    m_ae = full_metrics(y_te, scores_ae, X_single=X_te_f[:1],
                         predict_fn=ae.predict_fn)
    m_ae['label'] = 'Autoencoder'
    results['autoencoder'] = m_ae

    # Isolation Forest
    model_if, sc_if, scores_if = train_isolation_forest(X_normal_f, X_te_f)
    m_if = full_metrics(y_te, scores_if, model=model_if, X_single=X_te_f[:1],
                         predict_fn=lambda x: -model_if.decision_function(sc_if.transform(x)))
    m_if['label'] = 'Isolation Forest'
    results['isolation_forest'] = m_if

    plot_metric_bars(['Autoencoder','Isolation Forest'],
                     [m_ae['pauc01'], m_if['pauc01']],
                     title='NB02 — Não Supervisionado: pAUC@0.1',
                     out_path=get_fig_path('nb02', 'pauc_comparison'))
    plot_roc_pauc(y_te, {'Autoencoder': scores_ae, 'IF': scores_if},
                  title='NB02 — ROC', out_path=get_fig_path('nb02', 'roc'))

    res = {'nb': 'NB02', 'topic': 'Não Supervisionado', 'models': results}
    save_result('nb02', res)
    return res


def nb03_baseline_real():
    """NB03: Baseline com múltiplos domínios — XGBoost×GRU×LSTM-AE×Tiny-AST."""
    print("\n─── NB03: Baseline Real ───")
    X, y, meta = generate_dataset(n_normal=50, n_anomaly=15,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii'], seed=3)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='mimii')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats(sigs): return np.array([extract_super_vector(s) for s in sigs])
    X_tr_f = feats(X_tr); X_te_f = feats(X_te)

    results = {}
    # XGBoost
    m_xgb, sc, sc_xgb = train_xgboost(X_tr_f, y_tr, X_te_f)
    res_xgb = full_metrics(y_te, sc_xgb, model=m_xgb, X_single=X_te_f[:1])
    res_xgb['label'] = 'XGBoost'
    results['xgboost'] = res_xgb

    # MLP GRU proxy
    model_gru, sc_gru, scores_gru = train_mlp_cnn_proxy(X_tr_f, y_tr, X_te_f,
                                                          hidden=(128, 64))
    res_gru = full_metrics(y_te, scores_gru, model=model_gru, X_single=X_te_f[:1])
    res_gru['label'] = 'GRU proxy'
    results['gru'] = res_gru

    # Autoencoder (LSTM-AE proxy)
    ae = SimpleAutoencoder(X_tr_f.shape[1], n_latent=24)
    ae.fit(X_tr_f[y_tr==0])
    scores_ae = ae.score(X_te_f)
    res_ae = full_metrics(y_te, scores_ae, X_single=X_te_f[:1], predict_fn=ae.predict_fn)
    res_ae['label'] = 'LSTM-AE'
    results['lstm_ae'] = res_ae

    # Tiny-AST proxy
    model_ast, sc_ast, scores_ast = build_tiny_ast_proxy(X_tr_f, y_tr, X_te_f)
    res_ast = full_metrics(y_te, scores_ast, model=model_ast, X_single=X_te_f[:1])
    res_ast['label'] = 'Tiny-AST'
    results['tiny_ast'] = res_ast

    labs = ['XGBoost','GRU','LSTM-AE','Tiny-AST']
    paucs = [results[k]['pauc01'] for k in ['xgboost','gru','lstm_ae','tiny_ast']]
    lats = [results[k].get('latency_ms',0) or 0 for k in ['xgboost','gru','lstm_ae','tiny_ast']]
    mems = [results[k].get('memory_mb',0) or 0 for k in ['xgboost','gru','lstm_ae','tiny_ast']]

    plot_metric_bars(labs, paucs, title='NB03 — Benchmark Real: pAUC@0.1',
                     out_path=get_fig_path('nb03', 'pauc'))
    plot_latency_memory(labs, lats, mems, out_path=get_fig_path('nb03', 'lat_mem'))
    # (sem plot_roc_pauc aqui — scores já não estão em memória separada)

    res = {'nb': 'NB03', 'topic': 'Baseline Real', 'models': results}
    save_result('nb03', res)
    return res


def _nb_representation(nb_id, topic, rep_type, seed):
    """Helper genérico para NB04/05/06 (representações espectrais)."""
    print(f"\n─── {nb_id}: Representação {rep_type} ───")
    X, y, meta = generate_dataset(n_normal=50, n_anomaly=15,
                                   machines=['fan','pump'],
                                   domains=['dcase'], seed=seed)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='dcase')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    from src.features import (log_mel_spectrogram, mfcc, stft_features,
                               cwt_approx, kurtosis, band_energies)
    import time

    def get_feats(sigs, rtype):
        feats, lat = [], []
        for s in sigs:
            t0 = time.perf_counter()
            if rtype == 'mel':
                mel = log_mel_spectrogram(s)
                f = np.concatenate([np.mean(mel,0), np.std(mel,0)])
            elif rtype == 'cwt':
                cwt = cwt_approx(s, n_scales=32)
                f = np.concatenate([np.mean(cwt,0), np.std(cwt,0)])
            elif rtype == 'stft':
                st = stft_features(s)
                f = np.concatenate([np.mean(st,0)[:128], np.std(st,0)[:128]])
            lat.append((time.perf_counter()-t0)*1000)
            feats.append(f)
        return np.array(feats), float(np.median(lat))

    X_tr_f, lat_tr = get_feats(X_tr, rep_type)
    X_te_f, lat_te = get_feats(X_te, rep_type)

    model, sc, scores = train_xgboost(X_tr_f, y_tr, X_te_f)
    metrics = full_metrics(y_te, scores, model=model, X_single=X_te_f[:1])
    metrics['extraction_latency_ms'] = lat_te
    metrics['label'] = rep_type.upper()

    plot_roc_pauc(y_te, {rep_type.upper(): scores},
                  title=f'{nb_id} — {rep_type.upper()} ROC',
                  out_path=get_fig_path(nb_id.lower(), 'roc'))

    # Figura do espectrograma
    sample_normal = X_te[y_te == 0][0]
    sample_anomaly = X_te[y_te == 1][0] if np.any(y_te == 1) else sample_normal
    plot_signal_and_spectrogram(sample_normal, title=f'{nb_id} — Normal',
                                 out_path=get_fig_path(nb_id.lower(), 'normal'))
    plot_signal_and_spectrogram(sample_anomaly, title=f'{nb_id} — Anomalia',
                                 out_path=get_fig_path(nb_id.lower(), 'anomaly'))

    res = {'nb': nb_id, 'topic': topic,
           'model': metrics, 'extraction_ms': lat_te}
    save_result(nb_id.lower(), res)
    return res


def nb04_mel(): return _nb_representation('NB04', 'Mel-Spectrogram', 'mel', 4)
def nb05_cwt(): return _nb_representation('NB05', 'CWT', 'cwt', 5)
def nb06_stft(): return _nb_representation('NB06', 'STFT', 'stft', 6)


def nb07_hibrido_v1():
    """NB07: Fusão Mel+MFCC+CWT."""
    print("\n─── NB07: Híbrido v1 (Mel+MFCC+CWT) ───")
    X, y, meta = generate_dataset(n_normal=50, n_anomaly=15,
                                   machines=['fan','pump','slider'],
                                   domains=['dcase'], seed=7)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='dcase')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats(sigs):
        return np.array([extract_super_vector(s, include_cwt=True) for s in sigs])
    X_tr_f = feats(X_tr); X_te_f = feats(X_te)

    model, sc, scores = train_xgboost(X_tr_f, y_tr, X_te_f)
    metrics = full_metrics(y_te, scores, model=model, X_single=X_te_f[:1])
    metrics['label'] = 'Mel+MFCC+CWT'
    metrics['n_features'] = int(X_tr_f.shape[1])

    plot_roc_pauc(y_te, {'Mel+MFCC+CWT': scores},
                  title='NB07 — Híbrido v1', out_path=get_fig_path('nb07', 'roc'))

    res = {'nb': 'NB07', 'topic': 'Híbrido v1', 'model': metrics}
    save_result('nb07', res)
    return res


def nb08_nmf():
    """NB08: Super-Vetor completo com erro NMF."""
    print("\n─── NB08: Super-Vetor + NMF ───")
    X, y, meta = generate_dataset(n_normal=60, n_anomaly=20,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase'], seed=8)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='dcase')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    from src.features import log_mel_spectrogram
    def get_mel_matrix(sigs):
        mats = []
        for s in sigs:
            mel = log_mel_spectrogram(s)
            mats.append(np.mean(np.abs(mel), 0))
        return np.array(mats)

    mel_tr = get_mel_matrix(X_tr)
    nmf = NMFDetector(n_components=8)
    nmf.fit(mel_tr[y_tr==0])

    def feats(sigs):
        out = []
        for s in sigs:
            mel = log_mel_spectrogram(s)
            mel_mean = np.abs(mel).mean(0, keepdims=True)
            err = float(nmf.reconstruction_error(mel_mean)[0])
            out.append(extract_super_vector(s, nmf_error=err))
        return np.array(out)

    X_tr_f = feats(X_tr); X_te_f = feats(X_te)

    model, sc, scores = train_xgboost(X_tr_f, y_tr, X_te_f)
    metrics = full_metrics(y_te, scores, model=model, X_single=X_te_f[:1])
    metrics['label'] = 'Mel+MFCC+NMF+Kurtosis'
    metrics['n_features'] = int(X_tr_f.shape[1])

    plot_roc_pauc(y_te, {'Super-Vetor+NMF': scores},
                  title='NB08 — Super-Vetor com NMF', out_path=get_fig_path('nb08', 'roc'))

    res = {'nb': 'NB08', 'topic': 'Super-Vetor+NMF', 'model': metrics}
    save_result('nb08', res)
    return res


def nb09_kaggle():
    """NB09: Validação cross-domain com Kaggle Bearings (domínio 'kaggle')."""
    print("\n─── NB09: Kaggle Bearings ───")
    X, y, meta = generate_dataset(n_normal=50, n_anomaly=15,
                                   machines=['slider'],
                                   domains=['dcase','kaggle'], seed=9)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='kaggle')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats(sigs): return np.array([extract_super_vector(s) for s in sigs])
    X_tr_f = feats(X_tr); X_te_f = feats(X_te)

    model, sc, scores = train_xgboost(X_tr_f, y_tr, X_te_f)
    metrics = full_metrics(y_te, scores, model=model, X_single=X_te_f[:1])
    metrics['label'] = 'XGBoost cross-domain'

    plot_roc_pauc(y_te, {'XGBoost (Kaggle)': scores},
                  title='NB09 — Cross-Domain: Kaggle Bearings',
                  out_path=get_fig_path('nb09', 'roc'))

    res = {'nb': 'NB09', 'topic': 'Kaggle Bearings', 'model': metrics}
    save_result('nb09', res)
    return res


def nb10_drive_proprio():
    """NB10: Teste cego Drive Próprio — domain shift severo."""
    print("\n─── NB10: Drive Próprio (Domain Shift) ───")
    # Treino: dcase + mimii; Teste: drive (smartphone, mais ruído)
    X, y, meta = generate_dataset(n_normal=50, n_anomaly=15,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii','drive'],
                                   domain_shift=True, snr_db=0, seed=10)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='drive')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats(sigs): return np.array([extract_super_vector(s) for s in sigs])
    X_tr_f = feats(X_tr); X_te_f = feats(X_te)

    model, sc, scores = train_xgboost(X_tr_f, y_tr, X_te_f)
    metrics = full_metrics(y_te, scores, model=model, X_single=X_te_f[:1])
    metrics['label'] = 'XGBoost (Drive - blind)'

    # Também mede no ambiente controlado para comparação
    X_ctrl = X[np.array([m['domain'] != 'drive' for m in meta])]
    y_ctrl = y[np.array([m['domain'] != 'drive' for m in meta])]
    if len(y_ctrl) > 10:
        scores_ctrl = model.predict_proba(sc.transform(feats(X_ctrl)))[:,1]
        metrics['pauc01_controlled'] = pauc_at_fpr(y_ctrl, scores_ctrl)
    else:
        metrics['pauc01_controlled'] = metrics['pauc01']

    plot_roc_pauc(y_te, {'XGBoost Blind': scores},
                  title='NB10 — Domain Shift: Drive Próprio',
                  out_path=get_fig_path('nb10', 'roc'))

    res = {'nb': 'NB10', 'topic': 'Drive Próprio Domain Shift',
           'model': metrics,
           'domain_shift_drop': metrics['pauc01_controlled'] - metrics['pauc01']}
    save_result('nb10', res)
    return res


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 2 — OTIMIZAÇÃO (NB 11 – 15)
# ═══════════════════════════════════════════════════════════════════════════════

def nb11_l2_gamma():
    """NB11: Frente 1 — Regularização L2 + limiar Gamma."""
    print("\n─── NB11: Frente 1 — L2 + Gamma ───")
    X, y, meta = generate_dataset(n_normal=60, n_anomaly=20,
                                   machines=['fan','pump'],
                                   domains=['dcase','mimii'], seed=11)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='mimii')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats(sigs): return np.array([extract_super_vector(s) for s in sigs])
    X_tr_f = feats(X_tr); X_te_f = feats(X_te)

    results = {}
    for lam in [0.0, 0.1, 1.0]:
        m, sc, sc_scores = train_xgboost(X_tr_f, y_tr, X_te_f, reg_lambda=lam)
        met = full_metrics(y_te, sc_scores, model=m, X_single=X_te_f[:1])
        met['label'] = f'λ={lam}'
        results[f'lambda_{lam}'] = met

    # Limiar Gamma
    m_best, sc_best, sc_best_scores = train_xgboost(X_tr_f, y_tr, X_te_f, reg_lambda=1.0)
    scores_normal = sc_best_scores[y_te == 0] if np.any(y_te==0) else sc_best_scores[:5]
    tau = fit_gamma_threshold(scores_normal, fpr_target=0.05)

    plot_metric_bars([f'λ={l}' for l in [0.0,0.1,1.0]],
                     [results[f'lambda_{l}']['pauc01'] for l in [0.0,0.1,1.0]],
                     title='NB11 — Efeito da Regularização L2',
                     out_path=get_fig_path('nb11', 'l2_effect'))

    res = {'nb':'NB11','topic':'Frente 1 — L2+Gamma','models':results,
           'gamma_threshold':tau}
    save_result('nb11', res)
    return res


def nb12_gmm():
    """NB12: Frente 2 — GMM vs Mahalanobis (campeão não supervisionado)."""
    print("\n─── NB12: Frente 2 — GMM ───")
    X, y, meta = generate_dataset(n_normal=60, n_anomaly=20,
                                   machines=['fan','pump','slider'],
                                   domains=['dcase','mimii'], seed=12)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='mimii')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats(sigs): return np.array([extract_super_vector(s) for s in sigs])
    X_tr_f = feats(X_tr); X_te_f = feats(X_te)
    X_normal = X_tr_f[y_tr == 0]

    results = {}
    # GMM
    gmm = GMMDetector(n_components=5)
    gmm.fit(X_normal)
    scores_gmm = gmm.score(X_te_f)
    m_gmm = full_metrics(y_te, scores_gmm, X_single=X_te_f[:1], predict_fn=gmm.predict_fn)
    m_gmm['label'] = 'GMM (k=5)'
    results['gmm'] = m_gmm

    # Mahalanobis
    mah = MahalanobisDetector()
    mah.fit(X_normal)
    scores_mah = mah.score(X_te_f)
    m_mah = full_metrics(y_te, scores_mah, X_single=X_te_f[:1], predict_fn=mah.predict_fn)
    m_mah['label'] = 'Mahalanobis'
    results['mahalanobis'] = m_mah

    # CNN descartada
    model_cnn, _, scores_cnn = train_mlp_cnn_proxy(X_tr_f, y_tr, X_te_f)
    m_cnn = full_metrics(y_te, scores_cnn, model=model_cnn, X_single=X_te_f[:1])
    m_cnn['label'] = 'CNN (descartada)'
    results['cnn'] = m_cnn

    plot_metric_bars(['GMM','Mahalanobis','CNN'],
                     [m_gmm['pauc01'], m_mah['pauc01'], m_cnn['pauc01']],
                     title='NB12 — Frente 2: Campeão Não Supervisionado',
                     out_path=get_fig_path('nb12', 'comparison'))
    plot_roc_pauc(y_te, {'GMM':scores_gmm,'Mahalanobis':scores_mah,'CNN':scores_cnn},
                  title='NB12 — ROC', out_path=get_fig_path('nb12','roc'))

    res = {'nb':'NB12','topic':'Frente 2 — GMM','models':results}
    save_result('nb12', res)
    return res


def nb13_hht_ukf():
    """NB13: Frente 3 — Pipeline HHT+UKF como pré-processador."""
    print("\n─── NB13: Frente 3 — HHT+UKF ───")
    X, y, meta = generate_dataset(n_normal=60, n_anomaly=20,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii'], seed=13)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='mimii')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    import time

    def feats_raw(sigs):
        return np.array([extract_super_vector(s) for s in sigs])

    def feats_hht(sigs):
        out, snr_gains = [], []
        for s in sigs:
            t0 = time.perf_counter()
            s_clean, snr_gain = hht_ukf(s, n_imfs=4, n_sifting=6)
            snr_gains.append(snr_gain)
            out.append(extract_super_vector(s_clean))
        return np.array(out), float(np.mean(snr_gains))

    X_tr_f_raw = feats_raw(X_tr)
    X_te_f_raw = feats_raw(X_te)

    # Sem HHT
    m_raw, sc_raw, sc_raw_s = train_xgboost(X_tr_f_raw, y_tr, X_te_f_raw)
    met_raw = full_metrics(y_te, sc_raw_s, model=m_raw, X_single=X_te_f_raw[:1])
    met_raw['label'] = 'Sem HHT+UKF'

    # Com HHT
    X_tr_f_hht, snr_tr = feats_hht(X_tr)
    X_te_f_hht, snr_te = feats_hht(X_te)
    m_hht, sc_hht, sc_hht_s = train_xgboost(X_tr_f_hht, y_tr, X_te_f_hht)
    met_hht = full_metrics(y_te, sc_hht_s, model=m_hht, X_single=X_te_f_hht[:1])
    met_hht['label'] = 'Com HHT+UKF'
    met_hht['snr_gain_db'] = snr_te

    # Figura comparativa
    plot_metric_bars(['Sem HHT+UKF','Com HHT+UKF'],
                     [met_raw['pauc01'], met_hht['pauc01']],
                     title='NB13 — Frente 3: Impacto do HHT+UKF',
                     out_path=get_fig_path('nb13','hht_impact'))
    plot_roc_pauc(y_te, {'Sem HHT':sc_raw_s,'Com HHT':sc_hht_s},
                  title='NB13 — ROC', out_path=get_fig_path('nb13','roc'))

    # Figura sinal limpo vs bruto
    s_ex = X_te[0]
    s_clean, _ = hht_ukf(s_ex)
    plot_signal_and_spectrogram(s_ex, title='NB13 — Sinal Bruto',
                                 out_path=get_fig_path('nb13','raw_signal'))
    plot_signal_and_spectrogram(s_clean, title='NB13 — Sinal Limpo (HHT+UKF)',
                                 out_path=get_fig_path('nb13','clean_signal'))

    res = {'nb':'NB13','topic':'Frente 3 — HHT+UKF',
           'models':{'raw':met_raw,'hht':met_hht},
           'snr_gain_db': snr_te,
           'pauc_gain': met_hht['pauc01'] - met_raw['pauc01']}
    save_result('nb13', res)
    return res


def nb14_mixup():
    """NB14: Frente 4 — Data augmentation Mixup (α=0.4)."""
    print("\n─── NB14: Frente 4 — Mixup ───")
    X, y, meta = generate_dataset(n_normal=60, n_anomaly=20,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii','drive'],
                                   domain_shift=True, snr_db=0, seed=14)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='drive')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats_hht(sigs):
        out = []
        for s in sigs:
            s_clean, _ = hht_ukf(s, n_imfs=3, n_sifting=5)
            out.append(extract_super_vector(s_clean))
        return np.array(out)

    X_tr_f = feats_hht(X_tr); X_te_f = feats_hht(X_te)

    # Sem Mixup
    m_no, sc_no, sc_no_s = train_xgboost(X_tr_f, y_tr, X_te_f, use_mixup=False)
    met_no = full_metrics(y_te, sc_no_s, model=m_no, X_single=X_te_f[:1])
    met_no['label'] = 'Sem Mixup'

    # Com Mixup
    m_mix, sc_mix, sc_mix_s = train_xgboost(X_tr_f, y_tr, X_te_f,
                                              use_mixup=True, alpha=0.4)
    met_mix = full_metrics(y_te, sc_mix_s, model=m_mix, X_single=X_te_f[:1])
    met_mix['label'] = 'Com Mixup (α=0.4)'

    plot_metric_bars(['Sem Mixup','Com Mixup'],
                     [met_no['pauc01'], met_mix['pauc01']],
                     title='NB14 — Frente 4: Impacto do Mixup (Cross-Domain)',
                     out_path=get_fig_path('nb14','mixup_impact'))
    plot_roc_pauc(y_te, {'Sem Mixup':sc_no_s,'Com Mixup':sc_mix_s},
                  title='NB14 — ROC', out_path=get_fig_path('nb14','roc'))

    res = {'nb':'NB14','topic':'Frente 4 — Mixup',
           'models':{'no_mixup':met_no,'mixup':met_mix},
           'pauc_gain': met_mix['pauc01'] - met_no['pauc01']}
    save_result('nb14', res)
    return res


def nb15_pauc_metric():
    """NB15: Frente 5 — Adoção de pAUC@0.1 como métrica principal."""
    print("\n─── NB15: Frente 5 — pAUC@0.1 como métrica principal ───")
    X, y, meta = generate_dataset(n_normal=60, n_anomaly=20,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii'], seed=15)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='mimii')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats_hht(sigs):
        return np.array([extract_super_vector(hht_ukf(s,3,5)[0]) for s in sigs])

    X_tr_f = feats_hht(X_tr); X_te_f = feats_hht(X_te)

    # Compara modelos nas duas métricas
    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler()
    X_tr_sc = sc.fit_transform(X_tr_f)
    X_te_sc  = sc.transform(X_te_f)

    model_xgb, _, scores_xgb = train_xgboost(X_tr_f, y_tr, X_te_f)
    model_ast, _, scores_ast = build_tiny_ast_proxy(X_tr_f, y_tr, X_te_f)
    gmm_d = GMMDetector(n_components=5)
    gmm_d.fit(X_tr_f[y_tr==0])
    scores_gmm = gmm_d.score(X_te_f)

    ranking = {
        'XGBoost': {'pauc01': pauc_at_fpr(y_te, scores_xgb),
                    'f1':     compute_f1(y_te, scores_xgb),
                    'auc':    compute_auc(y_te, scores_xgb)},
        'Tiny-AST': {'pauc01': pauc_at_fpr(y_te, scores_ast),
                     'f1':     compute_f1(y_te, scores_ast),
                     'auc':    compute_auc(y_te, scores_ast)},
        'GMM':  {'pauc01': pauc_at_fpr(y_te, scores_gmm),
                 'f1':     compute_f1(y_te, scores_gmm),
                 'auc':    compute_auc(y_te, scores_gmm)},
    }

    plot_metric_bars(list(ranking.keys()),
                     [ranking[k]['pauc01'] for k in ranking],
                     metric_name='pAUC@0.1',
                     title='NB15 — Ranking por pAUC@0.1 (vs F1 global)',
                     out_path=get_fig_path('nb15','pauc_ranking'))

    res = {'nb':'NB15','topic':'Frente 5 — pAUC@0.1','ranking':ranking}
    save_result('nb15', res)
    return res


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 3 — VALIDAÇÃO (NB 16 – 21)
# ═══════════════════════════════════════════════════════════════════════════════

def nb16_gamma_fpr():
    """NB16: Frente 6 — Limiar Gamma com FPR alvo formalizado."""
    print("\n─── NB16: Frente 6 — Gamma Threshold ───")
    X, y, meta = generate_dataset(n_normal=70, n_anomaly=20,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii'], seed=16)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='mimii')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats_hht(sigs):
        return np.array([extract_super_vector(hht_ukf(s,3,5)[0]) for s in sigs])

    X_tr_f = feats_hht(X_tr); X_te_f = feats_hht(X_te)
    gmm = GMMDetector(n_components=5)
    gmm.fit(X_tr_f[y_tr==0])
    scores = gmm.score(X_te_f)

    # Diferentes alvos de FPR
    results = {}
    for fpr_t in [0.01, 0.05, 0.10]:
        normal_scores = scores[y_te==0] if np.any(y_te==0) else scores[:5]
        tau = fit_gamma_threshold(normal_scores, fpr_target=fpr_t)
        y_pred = (scores >= tau).astype(int)
        met = {'fpr_target': fpr_t, 'threshold': tau,
               'pauc01': pauc_at_fpr(y_te, scores),
               'f1': compute_f1(y_te, scores, threshold=tau)}
        results[f'fpr_{fpr_t}'] = met

    plot_roc_pauc(y_te, {'GMM+Gamma': scores},
                  title='NB16 — Frente 6: Gamma Threshold',
                  out_path=get_fig_path('nb16','roc'))

    res = {'nb':'NB16','topic':'Frente 6 — Gamma FPR','thresholds':results,
           'pauc01': pauc_at_fpr(y_te, scores)}
    save_result('nb16', res)
    return res


def nb17_outlier_exposure():
    """NB17: Frente 7 — Outlier Exposure + separação Protocolo A/B."""
    print("\n─── NB17: Frente 7 — Outlier Exposure + Protocolo A/B ───")
    # Simula exposição a anomalias de fonte externa (DCASE como outliers)
    X, y, meta = generate_dataset(n_normal=60, n_anomaly=20,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii','drive'],
                                   domain_shift=True, snr_db=3, seed=17)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='drive')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats_hht(sigs):
        return np.array([extract_super_vector(hht_ukf(s,3,5)[0]) for s in sigs])

    X_tr_f = feats_hht(X_tr); X_te_f = feats_hht(X_te)

    results = {}
    # Protocolo A: Supervisionado (XGBoost)
    m_a, sc_a, sc_a_s = train_xgboost(X_tr_f, y_tr, X_te_f, use_mixup=True)
    met_a = full_metrics(y_te, sc_a_s, model=m_a, X_single=X_te_f[:1])
    met_a['label'] = 'Protocolo A (XGBoost)'
    results['protocol_a'] = met_a

    # Protocolo B: Não supervisionado (GMM)
    gmm = GMMDetector(n_components=5)
    # Inclui alguns exemplos de anomalia DCASE como outlier exposure
    X_normal = X_tr_f[y_tr==0]
    X_outlier = X_tr_f[y_tr==1][:10]  # exposição a outliers
    X_exposure = np.vstack([X_normal, X_outlier * 0.3])  # exposição suave
    gmm.fit(X_exposure)
    sc_b_s = gmm.score(X_te_f)
    met_b = full_metrics(y_te, sc_b_s, X_single=X_te_f[:1], predict_fn=gmm.predict_fn)
    met_b['label'] = 'Protocolo B (GMM+OutlierExp)'
    results['protocol_b'] = met_b

    plot_metric_bars(['Protocolo A','Protocolo B'],
                     [met_a['pauc01'], met_b['pauc01']],
                     title='NB17 — Frente 7: Protocolo A vs B (Drive Próprio)',
                     out_path=get_fig_path('nb17','ab_comparison'))
    plot_roc_pauc(y_te, {'Prot.A (XGB)':sc_a_s,'Prot.B (GMM)':sc_b_s},
                  title='NB17 — ROC', out_path=get_fig_path('nb17','roc'))

    res = {'nb':'NB17','topic':'Frente 7 — Protocolos A/B','models':results}
    save_result('nb17', res)
    return res


def nb18_arena_nao_sup():
    """NB18: Frente 8 — Arena não supervisionada: GMM vs Mahalanobis vs IF."""
    print("\n─── NB18: Frente 8 — Arena Não Supervisionada ───")
    X, y, meta = generate_dataset(n_normal=70, n_anomaly=20,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii'], seed=18)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='mimii')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats_hht(sigs):
        return np.array([extract_super_vector(hht_ukf(s,3,5)[0]) for s in sigs])

    X_tr_f = feats_hht(X_tr); X_te_f = feats_hht(X_te)
    X_normal = X_tr_f[y_tr==0]

    results = {}
    # GMM
    gmm = GMMDetector(n_components=5)
    gmm.fit(X_normal)
    sc_gmm = gmm.score(X_te_f)
    met_gmm = full_metrics(y_te, sc_gmm, X_single=X_te_f[:1], predict_fn=gmm.predict_fn)
    met_gmm['label'] = 'GMM (k=5)'
    results['gmm'] = met_gmm

    # Mahalanobis
    mah = MahalanobisDetector()
    mah.fit(X_normal)
    sc_mah = mah.score(X_te_f)
    met_mah = full_metrics(y_te, sc_mah, X_single=X_te_f[:1], predict_fn=mah.predict_fn)
    met_mah['label'] = 'Mahalanobis'
    results['mahalanobis'] = met_mah

    # Isolation Forest
    m_if, sc_if, sc_if_s = train_isolation_forest(X_normal, X_te_f)
    met_if = full_metrics(y_te, sc_if_s, model=m_if, X_single=X_te_f[:1])
    met_if['label'] = 'Isolation Forest'
    results['isolation_forest'] = met_if

    labs = ['GMM','Mahalanobis','IF']
    paucs = [met_gmm['pauc01'], met_mah['pauc01'], met_if['pauc01']]
    lats = [met_gmm.get('latency_ms',0) or 0,
            met_mah.get('latency_ms',0) or 0,
            met_if.get('latency_ms',0) or 0]
    mems = [met_gmm.get('memory_mb',0) or 0,
            met_mah.get('memory_mb',0) or 0,
            met_if.get('memory_mb',0) or 0]

    plot_metric_bars(labs, paucs, title='NB18 — Arena Não Supervisionada: pAUC@0.1',
                     out_path=get_fig_path('nb18','arena'))
    plot_roc_pauc(y_te, {'GMM':sc_gmm,'Mah':sc_mah,'IF':sc_if_s},
                  title='NB18 — ROC', out_path=get_fig_path('nb18','roc'))

    res = {'nb':'NB18','topic':'Frente 8 — Arena Não Sup','models':results}
    save_result('nb18', res)
    return res


def nb19_pretrain_aug():
    """NB19: Frente 9 — Pré-treino com dados externos + augmentation."""
    print("\n─── NB19: Frente 9 — Pré-Treino + Augmentation ───")
    X, y, meta = generate_dataset(n_normal=60, n_anomaly=20,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii','kaggle'],
                                   snr_db=3, seed=19)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='kaggle')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats_hht(sigs):
        return np.array([extract_super_vector(hht_ukf(s,3,5)[0]) for s in sigs])

    X_tr_f = feats_hht(X_tr); X_te_f = feats_hht(X_te)

    # Sem augmentation
    m_no, _, sc_no_s = train_xgboost(X_tr_f, y_tr, X_te_f, use_mixup=False)
    met_no = full_metrics(y_te, sc_no_s, model=m_no, X_single=X_te_f[:1])
    met_no['label'] = 'Sem Augmentation'

    # Com Mixup
    m_mix, _, sc_mix_s = train_xgboost(X_tr_f, y_tr, X_te_f, use_mixup=True)
    met_mix = full_metrics(y_te, sc_mix_s, model=m_mix, X_single=X_te_f[:1])
    met_mix['label'] = 'Com Mixup'

    # Tiny-AST como gerador de embeddings (função XAI)
    model_ast, _, scores_ast = build_tiny_ast_proxy(X_tr_f, y_tr, X_te_f)
    met_ast = full_metrics(y_te, scores_ast, model=model_ast, X_single=X_te_f[:1])
    met_ast['label'] = 'Tiny-AST (auxiliar XAI)'

    plot_metric_bars(['Sem Aug','Com Mixup','Tiny-AST (aux)'],
                     [met_no['pauc01'], met_mix['pauc01'], met_ast['pauc01']],
                     title='NB19 — Frente 9: Pré-Treino e Augmentation',
                     out_path=get_fig_path('nb19','pretrain'))

    res = {'nb':'NB19','topic':'Frente 9 — Pré-Treino+Aug',
           'models':{'no_aug':met_no,'mixup':met_mix,'tiny_ast_xai':met_ast}}
    save_result('nb19', res)
    return res


def nb20_xai():
    """NB20: Frente 10 — XAI: heatmap, hotspots e bandas."""
    print("\n─── NB20: Frente 10 — XAI ───")
    X, y, meta = generate_dataset(n_normal=50, n_anomaly=15,
                                   machines=['fan','slider'],
                                   domains=['dcase'], seed=20)
    X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_domain='dcase')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def feats_hht(sigs):
        return np.array([extract_super_vector(hht_ukf(s,3,5)[0]) for s in sigs])

    X_tr_f = feats_hht(X_tr); X_te_f = feats_hht(X_te)

    model, sc, scores = train_xgboost(X_tr_f, y_tr, X_te_f, use_mixup=True)
    metrics = full_metrics(y_te, scores, model=model, X_single=X_te_f[:1])

    # Pega amostra anômala para XAI
    anomaly_idx = np.where(y_te == 1)[0]
    if len(anomaly_idx) > 0:
        s_anom = X_te[anomaly_idx[0]]
    else:
        s_anom = X_te[0]

    s_clean, _ = hht_ukf(s_anom, n_imfs=3, n_sifting=5)

    # Gera activation map (proxy: variância ao longo do tempo)
    mel = log_mel_spectrogram(s_clean)
    activation = np.var(mel, axis=1)
    activation = (activation - activation.min()) / (activation.max() - activation.min() + 1e-8)

    # Top-3 hotspots
    from scipy.signal import find_peaks
    hop = 256; sr = 16000
    times = np.arange(len(activation)) * hop / sr
    peaks, props = find_peaks(activation, height=0.3, distance=5)
    if len(peaks) == 0:
        peaks = np.argsort(activation)[-3:]
    top3 = peaks[np.argsort(activation[peaks])[-3:]]

    hotspots = [{'rank': i+1, 'time_s': float(times[p]),
                  'intensity': float(activation[p])}
                 for i, p in enumerate(sorted(top3, key=lambda x: -activation[x]))]

    # Bandas espectrais
    el, em, eh = band_energies(s_clean)
    bands = {'low': float(el), 'mid': float(em), 'high': float(eh)}

    plot_xai_heatmap(s_clean, activation, title='NB20 — XAI Heatmap (Anomalia)',
                      out_path=get_fig_path('nb20','xai_heatmap'))

    res = {'nb':'NB20','topic':'Frente 10 — XAI','model':metrics,
           'hotspots':hotspots,'band_activations':bands}
    save_result('nb20', res)
    return res


def nb21_consolidacao():
    """NB21: Frente 11 — Consolidação multicritério (Arena Final)."""
    print("\n─── NB21: Frente 11 — Consolidação Final ───")
    X, y, meta = generate_dataset(n_normal=80, n_anomaly=25,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii','kaggle','drive'],
                                   domain_shift=True, snr_db=3, seed=21)

    pauc_per_domain, all_models = {}, {}
    for test_dom in ['dcase','mimii','kaggle','drive']:
        X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_dom)
        track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)
        if len(y_te) == 0 or len(np.unique(y_te)) < 2:
            continue

        def feats_hht(sigs):
            return np.array([extract_super_vector(hht_ukf(s,3,5)[0]) for s in sigs])

        X_tr_f = feats_hht(X_tr); X_te_f = feats_hht(X_te)
        X_normal = X_tr_f[y_tr==0]

        # Protocolo A
        m_a, sc_a, sc_a_s = train_xgboost(X_tr_f, y_tr, X_te_f, use_mixup=True)
        pa_a = pauc_at_fpr(y_te, sc_a_s)

        # Protocolo B
        gmm = GMMDetector(n_components=5)
        gmm.fit(X_normal)
        sc_b_s = gmm.score(X_te_f)
        pa_b = pauc_at_fpr(y_te, sc_b_s)

        pauc_per_domain[test_dom] = {'prot_a': pa_a, 'prot_b': pa_b,
                                      'dcase_score': (pa_a+pa_b)/2}
        all_models[test_dom] = {'lat_ms_a': full_metrics(y_te,sc_a_s,model=m_a,X_single=X_te_f[:1]).get('latency_ms'),
                                 'mem_mb_a': measure_memory_mb(m_a)}

    # Médias globais
    avg_a  = np.mean([v['prot_a'] for v in pauc_per_domain.values()])
    avg_b  = np.mean([v['prot_b'] for v in pauc_per_domain.values()])
    avg_dc = np.mean([v['dcase_score'] for v in pauc_per_domain.values()])

    domains = list(pauc_per_domain.keys())
    pa_vals = [pauc_per_domain[d]['prot_a'] for d in domains]
    pb_vals = [pauc_per_domain[d]['prot_b'] for d in domains]

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9,5))
    ax.set_facecolor('#161b22')
    x = np.arange(len(domains))
    ax.bar(x-0.2, pa_vals, 0.35, label='Protocolo A', color='#2ea043', alpha=0.85)
    ax.bar(x+0.2, pb_vals, 0.35, label='Protocolo B', color='#1f6feb', alpha=0.85)
    ax.axhline(0.80, color='#f0883e', ls='--', lw=1.5, label='Limite mínimo 0.80')
    ax.set_xticks(x); ax.set_xticklabels([d.upper() for d in domains])
    ax.set_ylim(0,1.05); ax.set_ylabel('pAUC@0.1')
    ax.set_title('NB21 — Frente 11: LOSO Multi-Domínio', fontsize=12, fontweight='bold',
                 color='#f0f6fc')
    ax.legend(fontsize=9)
    ax.grid(True, axis='y', alpha=0.3)
    fig.patch.set_facecolor('#0d1117')
    from src.viz import save
    save(fig, get_fig_path('nb21','loso_consolidation'))

    res = {'nb':'NB21','topic':'Frente 11 — Consolidação',
           'per_domain':pauc_per_domain,
           'avg_prot_a': float(avg_a), 'avg_prot_b': float(avg_b),
           'avg_dcase_score': float(avg_dc)}
    save_result('nb21', res)
    return res


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 4 — CONFRONTAMENTO (NB 22 – 28)
# ═══════════════════════════════════════════════════════════════════════════════

def nb22_champion_arch():
    """NB22: Especificação da arquitetura campeã (clean)."""
    print("\n─── NB22: Arquitetura Campeã ───")
    X, y, meta = generate_dataset(n_normal=80, n_anomaly=25,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii'], seed=22)
    X_tr, y_tr, X_te, y_te = train_test_split_loso(X, y, meta, 'mimii')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def pipeline_a(sigs):
        out = []
        for s in sigs:
            s_clean, _ = hht_ukf(s, n_imfs=4, n_sifting=8)
            mel = log_mel_spectrogram(s_clean)
            mel_mean = np.abs(mel).mean(0, keepdims=True)
            out.append(extract_super_vector(s_clean))
        return np.array(out)

    X_tr_f = pipeline_a(X_tr); X_te_f = pipeline_a(X_te)

    m_a, sc_a, sc_a_s = train_xgboost(X_tr_f, y_tr, X_te_f, use_mixup=True,
                                        n_estimators=100, max_depth=3, reg_lambda=1.0)
    met_a = full_metrics(y_te, sc_a_s, model=m_a, X_single=X_te_f[:1])
    met_a['label'] = 'Protocolo A — DIAMOND CRISTAL CLEAN'

    gmm = GMMDetector(n_components=5)
    gmm.fit(X_tr_f[y_tr==0])
    sc_b_s = gmm.score(X_te_f)
    met_b = full_metrics(y_te, sc_b_s, X_single=X_te_f[:1], predict_fn=gmm.predict_fn)
    met_b['label'] = 'Protocolo B — DIAMOND CRISTAL CLEAN'

    plot_roc_pauc(y_te, {'Prot.A (XGB)':sc_a_s,'Prot.B (GMM)':sc_b_s},
                  title='NB22 — Arquitetura Campeã: ROC',
                  out_path=get_fig_path('nb22','champion_roc'))

    res = {'nb':'NB22','topic':'Arquitetura Campeã',
           'protocol_a':met_a,'protocol_b':met_b}
    save_result('nb22', res)
    return res


def nb23_champion_clean():
    """NB23: Implementação limpa e documentada da arquitetura campeã."""
    print("\n─── NB23: Champion Clean ───")
    # Replica NB22 com seed diferente para validação cruzada interna
    X, y, meta = generate_dataset(n_normal=80, n_anomaly=25,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii'], seed=230)
    X_tr, y_tr, X_te, y_te = train_test_split_loso(X, y, meta, 'mimii')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def full_pipeline(sigs):
        return np.array([extract_super_vector(hht_ukf(s,4,8)[0]) for s in sigs])

    X_tr_f = full_pipeline(X_tr); X_te_f = full_pipeline(X_te)
    m_a, sc, sc_a_s = train_xgboost(X_tr_f, y_tr, X_te_f,
                                      use_mixup=True, n_estimators=100, max_depth=3, reg_lambda=1.0)
    met_a = full_metrics(y_te, sc_a_s, model=m_a, X_single=X_te_f[:1])

    gmm = GMMDetector(n_components=5)
    gmm.fit(X_tr_f[y_tr==0])
    sc_b_s = gmm.score(X_te_f)
    met_b = full_metrics(y_te, sc_b_s, X_single=X_te_f[:1], predict_fn=gmm.predict_fn)

    plot_roc_pauc(y_te, {'XGBoost':sc_a_s,'GMM':sc_b_s},
                  title='NB23 — Champion Clean: Validação Cruzada',
                  out_path=get_fig_path('nb23','clean_roc'))

    res = {'nb':'NB23','topic':'Champion Clean',
           'protocol_a':met_a,'protocol_b':met_b}
    save_result('nb23', res)
    return res


def nb24_veredito_inicial():
    """NB24: Veredito inicial com métricas finais."""
    print("\n─── NB24: Veredito Final (inicial) ───")
    X, y, meta = generate_dataset(n_normal=80, n_anomaly=25,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii','kaggle'],
                                   snr_db=3, seed=24)
    results = {}
    for test_dom in ['dcase','mimii','kaggle']:
        X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_dom)
        track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)
        if len(y_te) < 5 or len(np.unique(y_te)) < 2:
            continue

        def fp(sigs):
            return np.array([extract_super_vector(hht_ukf(s,4,8)[0]) for s in sigs])

        X_tr_f = fp(X_tr); X_te_f = fp(X_te)
        m_a, _, sc_a_s = train_xgboost(X_tr_f, y_tr, X_te_f, use_mixup=True)
        gmm = GMMDetector(5); gmm.fit(X_tr_f[y_tr==0])
        sc_b_s = gmm.score(X_te_f)
        results[test_dom] = {
            'prot_a': pauc_at_fpr(y_te, sc_a_s),
            'prot_b': pauc_at_fpr(y_te, sc_b_s),
        }

    res = {'nb':'NB24','topic':'Veredito Inicial','per_domain':results}
    save_result('nb24', res)
    return res


def nb25_veredito_mimii_snr():
    """NB25: Veredito V2 — MIMII multi-SNR (-6, 0, +6 dB)."""
    print("\n─── NB25: Veredito MIMII Multi-SNR ───")
    results = {}
    for snr in [-6, 0, 6]:
        X, y, meta = generate_dataset(n_normal=60, n_anomaly=20,
                                       machines=['fan','pump','slider'],
                                       domains=['dcase','mimii'], snr_db=snr, seed=25)
        X_tr, y_tr, X_te, y_te = train_test_split_loso(X, y, meta, 'mimii')
        track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)
        if len(y_te) < 5 or len(np.unique(y_te)) < 2:
            continue

        def fp(sigs):
            return np.array([extract_super_vector(hht_ukf(s,4,8)[0]) for s in sigs])
        X_tr_f = fp(X_tr); X_te_f = fp(X_te)
        m_a, _, sc_a_s = train_xgboost(X_tr_f, y_tr, X_te_f, use_mixup=True)
        gmm = GMMDetector(5); gmm.fit(X_tr_f[y_tr==0])
        sc_b_s = gmm.score(X_te_f)
        results[f'snr_{snr}'] = {
            'snr_db': snr,
            'prot_a': pauc_at_fpr(y_te, sc_a_s),
            'prot_b': pauc_at_fpr(y_te, sc_b_s),
        }

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8,5))
    ax.set_facecolor('#161b22')
    snrs = [-6,0,6]
    pa = [results[f'snr_{s}']['prot_a'] for s in snrs if f'snr_{s}' in results]
    pb = [results[f'snr_{s}']['prot_b'] for s in snrs if f'snr_{s}' in results]
    ax.plot(snrs[:len(pa)], pa, 'o-', color='#2ea043', lw=2, ms=8, label='Protocolo A')
    ax.plot(snrs[:len(pb)], pb, 's--', color='#1f6feb', lw=2, ms=8, label='Protocolo B')
    ax.axhline(0.80, color='#f0883e', ls='--', lw=1.5, label='Limite mínimo 0.80')
    ax.set_xlabel('SNR (dB)'); ax.set_ylabel('pAUC@0.1')
    ax.set_title('NB25 — MIMII Multi-SNR: Protocolo A vs B', fontsize=12,
                 fontweight='bold', color='#f0f6fc')
    ax.legend(fontsize=9); ax.grid(True, alpha=0.3); ax.set_ylim(0,1.05)
    fig.patch.set_facecolor('#0d1117')
    from src.viz import save
    save(fig, get_fig_path('nb25','snr_sweep'))

    res = {'nb':'NB25','topic':'Veredito MIMII Multi-SNR','per_snr':results}
    save_result('nb25', res)
    return res


def nb26_sintese_evolucao():
    """NB26: Síntese da evolução — mapa de contribuição de todas as técnicas."""
    print("\n─── NB26: Síntese da Evolução ───")
    # Coleta pAUC principal de cada NB dos resultados salvos
    nb_pauc = {}
    for nb_id in [f'nb{i:02d}' for i in range(1,22)]:
        path = METRICS_DIR / f"{nb_id}_results.json"
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            # Extrai melhor pAUC disponível
            p = None
            if 'models' in data:
                ps = [v.get('pauc01') for v in data['models'].values()
                      if isinstance(v, dict) and v.get('pauc01')]
                if ps: p = max(ps)
            elif 'model' in data:
                m = data['model']
                p = m.get('pauc01') if isinstance(m, dict) else None
            elif 'protocol_a' in data:
                p = data['protocol_a'].get('pauc01')
            elif 'ranking' in data:
                p = max(v.get('pauc01',0) for v in data['ranking'].values())
            elif 'avg_prot_a' in data:
                p = data['avg_prot_a']
            elif 'pauc01' in data:
                p = data['pauc01']
            if p: nb_pauc[nb_id] = float(p)

    if nb_pauc:
        labels = list(nb_pauc.keys())
        vals   = list(nb_pauc.values())
        plot_evolution(labels, vals, title='NB26 — Evolução pAUC@0.1 (NB01–NB21)',
                       out_path=get_fig_path('nb26','evolution'))

    res = {'nb':'NB26','topic':'Síntese da Evolução','pauc_per_nb':nb_pauc}
    save_result('nb26', res)
    return res


def nb27_ablation():
    """NB27: Ablation Study — impacto de cada componente."""
    print("\n─── NB27: Ablation Study ───")
    X, y, meta = generate_dataset(n_normal=80, n_anomaly=25,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii'], seed=27)
    X_tr, y_tr, X_te, y_te = train_test_split_loso(X, y, meta, 'mimii')
    track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)

    def eval_config(sigs_tr, y_tr, sigs_te, y_te, use_hht=True, use_mfcc=True,
                    use_nmf=True, use_mixup=True, use_kurtosis=True, use_l2=True):
        feats = []
        for s in list(sigs_tr) + list(sigs_te):
            if use_hht:
                s, _ = hht_ukf(s, n_imfs=4, n_sifting=8)
            mel = log_mel_spectrogram(s)
            mel_mean = np.mean(mel, 0); mel_std = np.std(mel, 0)
            parts = [mel_mean, mel_std]
            if use_mfcc:
                from src.features import mfcc as mfcc_fn, delta
                mc = mfcc_fn(mel)
                parts += [np.mean(mc,0), np.std(mc,0), np.mean(delta(mc),0)]
            if use_nmf:
                parts.append([np.mean(np.abs(mel))])
            if use_kurtosis:
                el,em,eh = band_energies(s)
                parts.append([kurtosis(s), el, em, eh])
            feats.append(np.concatenate([np.atleast_1d(p) for p in parts]))
        n_tr = len(sigs_tr)
        X_tr_f = np.array(feats[:n_tr]); X_te_f = np.array(feats[n_tr:])

        lam = 1.0 if use_l2 else 0.0
        m, _, sc_s = train_xgboost(X_tr_f, y_tr, X_te_f,
                                    use_mixup=use_mixup, reg_lambda=lam)
        return pauc_at_fpr(y_te, sc_s)

    configs = [
        ('Referência (completo)', dict(use_hht=True,use_mfcc=True,use_nmf=True,
                                        use_mixup=True,use_kurtosis=True,use_l2=True)),
        ('Sem HHT+UKF',  dict(use_hht=False,use_mfcc=True,use_nmf=True,use_mixup=True,use_kurtosis=True,use_l2=True)),
        ('Sem MFCC',     dict(use_hht=True,use_mfcc=False,use_nmf=True,use_mixup=True,use_kurtosis=True,use_l2=True)),
        ('Sem NMF',      dict(use_hht=True,use_mfcc=True,use_nmf=False,use_mixup=True,use_kurtosis=True,use_l2=True)),
        ('Sem Mixup',    dict(use_hht=True,use_mfcc=True,use_nmf=True,use_mixup=False,use_kurtosis=True,use_l2=True)),
        ('Sem Kurtosis', dict(use_hht=True,use_mfcc=True,use_nmf=True,use_mixup=True,use_kurtosis=False,use_l2=True)),
        ('Sem L2',       dict(use_hht=True,use_mfcc=True,use_nmf=True,use_mixup=True,use_kurtosis=True,use_l2=False)),
    ]

    pauc_vals, comp_names = [], []
    for name, cfg in configs:
        p = eval_config(X_tr, y_tr, X_te, y_te, **cfg)
        pauc_vals.append(p)
        comp_names.append(name)
        print(f"    {name}: pAUC={p:.4f}")

    pauc_full = pauc_vals[0]
    pauc_ablated = pauc_vals[1:]
    comps_ablated = comp_names[1:]

    plot_ablation(comps_ablated, pauc_full, pauc_ablated,
                  out_path=get_fig_path('nb27','ablation'))

    ablation_dict = {n: {'pauc01': float(p), 'delta': float(pauc_full - p)}
                     for n, p in zip(comp_names, pauc_vals)}

    res = {'nb':'NB27','topic':'Ablation Study','ablation':ablation_dict,
           'pauc_full':float(pauc_full)}
    save_result('nb27', res)
    return res


def nb28_diamond_final():
    """NB28: DIAMOND CRISTAL CLEAN — especificação final com hiperparâmetros."""
    print("\n─── NB28: DIAMOND CRISTAL CLEAN Final ───")
    # Protocolo LOSO completo com todos os 4 domínios
    X, y, meta = generate_dataset(n_normal=80, n_anomaly=25,
                                   machines=['fan','pump','slider','valve'],
                                   domains=['dcase','mimii','kaggle','drive'],
                                   domain_shift=True, snr_db=3, seed=28)

    per_domain, lats_a, mems_a = {}, [], []
    for test_dom in ['dcase','mimii','kaggle','drive']:
        X_tr, y_tr, X_te, y_te = smart_split(X, y, meta, test_dom)
        track_dataset(X, y, meta, X_tr, y_tr, X_te, y_te)
        if len(y_te) < 5 or len(np.unique(y_te)) < 2:
            continue

        def full_pipe(sigs):
            return np.array([extract_super_vector(hht_ukf(s,4,8)[0]) for s in sigs])

        X_tr_f = full_pipe(X_tr); X_te_f = full_pipe(X_te)

        m_a, sc_a, sc_a_s = train_xgboost(X_tr_f, y_tr, X_te_f,
                                            use_mixup=True, n_estimators=100,
                                            max_depth=3, reg_lambda=1.0)
        gmm = GMMDetector(n_components=5); gmm.fit(X_tr_f[y_tr==0])
        sc_b_s = gmm.score(X_te_f)

        met_a = full_metrics(y_te, sc_a_s, model=m_a, X_single=X_te_f[:1])
        met_b = full_metrics(y_te, sc_b_s, X_single=X_te_f[:1], predict_fn=gmm.predict_fn)

        per_domain[test_dom] = {
            'prot_a_pauc': met_a['pauc01'],
            'prot_b_pauc': met_b['pauc01'],
            'dcase_score': (met_a['pauc01'] + met_b['pauc01']) / 2,
            'latency_ms_a': met_a.get('latency_ms'),
            'memory_mb_a': met_a.get('memory_mb'),
        }
        if met_a.get('latency_ms'): lats_a.append(met_a['latency_ms'])
        if met_a.get('memory_mb'): mems_a.append(met_a['memory_mb'])

    avg_a  = np.mean([v['prot_a_pauc'] for v in per_domain.values()])
    avg_b  = np.mean([v['prot_b_pauc'] for v in per_domain.values()])
    avg_dc = np.mean([v['dcase_score'] for v in per_domain.values()])

    plot_metric_bars(list(per_domain.keys()),
                     [per_domain[d]['dcase_score'] for d in per_domain],
                     metric_name='Score DCASE',
                     title='NB28 — DIAMOND CRISTAL CLEAN: Score Final por Domínio',
                     out_path=get_fig_path('nb28','final_score'))

    spec = {
        'architecture': 'DIAMOND CRISTAL CLEAN',
        'hyperparams': {
            'hht_n_imfs': 4, 'hht_n_sifting': 8, 'ukf_obs_var': 0.05,
            'mel_bins': 64, 'mfcc_n': 13, 'nmf_components': 8,
            'xgb_n_estimators': 100, 'xgb_max_depth': 3, 'xgb_lambda': 1.0,
            'mixup_alpha': 0.4, 'gmm_components': 5, 'gamma_fpr_target': 0.05,
        },
        'avg_prot_a': float(avg_a),
        'avg_prot_b': float(avg_b),
        'avg_dcase_score': float(avg_dc),
        'avg_latency_ms_a': float(np.mean(lats_a)) if lats_a else None,
        'avg_memory_mb_a': float(np.mean(mems_a)) if mems_a else None,
        'per_domain': per_domain,
    }

    res = {'nb':'NB28','topic':'DIAMOND CRISTAL CLEAN Final','spec':spec}
    save_result('nb28', res)
    return res


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

EXPERIMENTS = [
    ('NB01', nb01_supervisionado),
    ('NB02', nb02_nao_supervisionado),
    ('NB03', nb03_baseline_real),
    ('NB04', nb04_mel),
    ('NB05', nb05_cwt),
    ('NB06', nb06_stft),
    ('NB07', nb07_hibrido_v1),
    ('NB08', nb08_nmf),
    ('NB09', nb09_kaggle),
    ('NB10', nb10_drive_proprio),
    ('NB11', nb11_l2_gamma),
    ('NB12', nb12_gmm),
    ('NB13', nb13_hht_ukf),
    ('NB14', nb14_mixup),
    ('NB15', nb15_pauc_metric),
    ('NB16', nb16_gamma_fpr),
    ('NB17', nb17_outlier_exposure),
    ('NB18', nb18_arena_nao_sup),
    ('NB19', nb19_pretrain_aug),
    ('NB20', nb20_xai),
    ('NB21', nb21_consolidacao),
    ('NB22', nb22_champion_arch),
    ('NB23', nb23_champion_clean),
    ('NB24', nb24_veredito_inicial),
    ('NB25', nb25_veredito_mimii_snr),
    ('NB26', nb26_sintese_evolucao),
    ('NB27', nb27_ablation),
    ('NB28', nb28_diamond_final),
]


def run_all(start_from=1, stop_at=28):
    """Executa todos os experimentos em sequência."""
    print("=" * 60)
    print("  DIAMOND CRISTAL CLEAN — Pipeline Experimental Completo")
    print(f"  Rodando NB{start_from:02d} até NB{stop_at:02d}")
    print("=" * 60)

    t_total = time.time()
    failed = []
    for nb_label, fn in EXPERIMENTS:
        nb_num = int(nb_label[2:])
        if nb_num < start_from or nb_num > stop_at:
            continue
        t0 = time.time()
        try:
            fn()
            elapsed = time.time() - t0
            print(f"  ✅ {nb_label} concluído em {elapsed:.1f}s")
        except Exception as e:
            print(f"  ❌ {nb_label} ERRO: {e}")
            import traceback; traceback.print_exc()
            failed.append(nb_label)

    print("\n" + "=" * 60)
    print(f"  Concluído em {time.time()-t_total:.1f}s")
    if failed:
        print(f"  ⚠️  Falhas: {failed}")
    else:
        print("  🎉 Todos os experimentos concluídos com sucesso!")

    # Salva sumário global
    summary_path = RESULTS_DIR / "summary_all_experiments.json"
    with open(summary_path, 'w') as f:
        json.dump(RESULTS_ALL, f, indent=2, default=float)
    print(f"  📊 Sumário salvo em: {summary_path}")
    return RESULTS_ALL


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--from', dest='start', type=int, default=1)
    parser.add_argument('--to',   dest='stop',  type=int, default=28)
    parser.add_argument('--nb',   dest='nb',    type=int, default=None,
                        help='Rodar apenas um NB específico')
    args = parser.parse_args()

    if args.nb:
        run_all(start_from=args.nb, stop_at=args.nb)
    else:
        run_all(start_from=args.start, stop_at=args.stop)
