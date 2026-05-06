"""
Métricas de avaliação: pAUC@0.1, F1, AUC, latência real e memória real.
"""
import time
import tracemalloc
import numpy as np
from sklearn.metrics import roc_curve, f1_score, roc_auc_score
from scipy.stats import gamma as scipy_gamma


def pauc_at_fpr(y_true, y_score, max_fpr=0.1):
    """
    Partial AUC normalizada: integra TPR na região FPR ∈ [0, max_fpr].
    Retorna valor em [0, 1].
    """
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)

    if len(np.unique(y_true)) < 2:
        return 0.0

    fpr, tpr, _ = roc_curve(y_true, y_score)

    # Adiciona ponto em max_fpr via interpolação
    interp_tpr = float(np.interp(max_fpr, fpr, tpr))
    mask = fpr <= max_fpr
    fpr_clip = np.append(fpr[mask], max_fpr)
    tpr_clip = np.append(tpr[mask], interp_tpr)

    if len(fpr_clip) < 2:
        return 0.0

    pauc = float(np.trapz(tpr_clip, fpr_clip) / max_fpr)
    return float(np.clip(pauc, 0, 1))


def dcase_score(pauc_supervised, pauc_unsupervised):
    """Score DCASE = média aritmética dos dois protocolos."""
    return (pauc_supervised + pauc_unsupervised) / 2.0


def compute_f1(y_true, y_score, threshold=0.5):
    y_pred = (y_score >= threshold).astype(int)
    return float(f1_score(y_true, y_pred, zero_division=0))


def compute_auc(y_true, y_score):
    if len(np.unique(y_true)) < 2:
        return 0.5
    return float(roc_auc_score(y_true, y_score))


def measure_latency(predict_fn, X_single, n_runs=100):
    """
    Mede latência real de inferência por amostra (ms).
    Aquece o cache com 10 runs antes de medir.
    """
    for _ in range(10):
        predict_fn(X_single)

    times = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        predict_fn(X_single)
        times.append((time.perf_counter() - t0) * 1000)

    return float(np.median(times))


def measure_memory_mb(obj):
    """Estima uso de memória de um objeto (modelo) em MB via pickle size."""
    import pickle, io
    buf = io.BytesIO()
    pickle.dump(obj, buf)
    return buf.tell() / (1024 * 1024)


def fit_gamma_threshold(scores_normal, fpr_target=0.05):
    """
    Ajusta distribuição Gamma aos scores de normalidade e retorna limiar.
    threshold = F_Gamma^{-1}(1 - fpr_target; alpha, beta)
    """
    scores = np.asarray(scores_normal)
    scores = scores[scores > 0]
    if len(scores) < 10:
        return float(np.percentile(scores_normal, 100 * (1 - fpr_target)))

    # MLE dos parâmetros Gamma
    mean = np.mean(scores)
    var  = np.var(scores) + 1e-10
    beta = var / mean
    alpha = mean / beta

    # Percentil (quantil) para FPR alvo
    threshold = scipy_gamma.ppf(1 - fpr_target, a=alpha, scale=beta)
    return float(threshold)


def full_metrics(y_true, y_score, model=None, X_single=None,
                 predict_fn=None, label='model'):
    """
    Computa conjunto completo de métricas para um experimento.
    Retorna dict com pAUC, F1, AUC, latência e memória.
    """
    result = {
        'label': label,
        'pauc01': pauc_at_fpr(y_true, y_score, 0.1),
        'f1':     compute_f1(y_true, y_score),
        'auc':    compute_auc(y_true, y_score),
        'n_test': int(len(y_true)),
        'n_anomaly_test': int(np.sum(y_true)),
    }

    if predict_fn is not None and X_single is not None:
        result['latency_ms'] = measure_latency(predict_fn, X_single)
    elif model is not None and X_single is not None:
        if hasattr(model, 'predict_proba'):
            def fn(x): return model.predict_proba(x)[:, 1]
        elif hasattr(model, 'decision_function'):
            def fn(x): return -model.decision_function(x)
        elif hasattr(model, 'score_samples'):
            def fn(x): return -model.score_samples(x)
        else:
            def fn(x): return model.predict(x).astype(float)
        result['latency_ms'] = measure_latency(fn, X_single)
    else:
        result['latency_ms'] = None

    if model is not None:
        result['memory_mb'] = measure_memory_mb(model)
    else:
        result['memory_mb'] = None

    return result


def summarize_metrics(metrics_list):
    """Agrega lista de dicts de métricas em médias."""
    keys = ['pauc01', 'f1', 'auc', 'latency_ms', 'memory_mb']
    summary = {}
    for k in keys:
        vals = [m[k] for m in metrics_list if m.get(k) is not None]
        if vals:
            summary[k] = float(np.mean(vals))
    return summary
