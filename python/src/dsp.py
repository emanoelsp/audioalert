"""
Módulo DSP: RPCA, EMD (HHT) e Filtro de Kalman (UKF simplificado).
"""
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import argrelmax, argrelmin


# ─── RPCA (Robust PCA via IALM) ─────────────────────────────────────────────

def rpca(M, lam=None, tol=1e-7, max_iter=100):
    """
    Decompõe M = L + S onde L é low-rank e S é esparso.
    Retorna (L, S)
    """
    m, n = M.shape
    if lam is None:
        lam = 1.0 / np.sqrt(max(m, n))

    L = np.zeros_like(M)
    S = np.zeros_like(M)
    Y = np.zeros_like(M)
    mu = 1.25 / np.linalg.norm(M, 2)
    mu_bar = mu * 1e7
    rho = 1.5

    for _ in range(max_iter):
        # Update L (singular value thresholding)
        U, s, Vt = np.linalg.svd(M - S + Y / mu, full_matrices=False)
        s_thresh = np.maximum(s - 1/mu, 0)
        L = U @ np.diag(s_thresh) @ Vt

        # Update S (soft thresholding)
        temp = M - L + Y / mu
        S = np.sign(temp) * np.maximum(np.abs(temp) - lam/mu, 0)

        # Update Y (dual variable)
        residual = M - L - S
        Y += mu * residual
        mu = min(rho * mu, mu_bar)

        if np.linalg.norm(residual, 'fro') / (np.linalg.norm(M, 'fro') + 1e-10) < tol:
            break

    return L, S


def rpca_signal(signal, n_components=64):
    """Aplica RPCA num sinal 1D convertendo em matriz de Hankel."""
    N = len(signal)
    n_rows = n_components
    n_cols = N - n_rows + 1
    if n_cols < 2:
        return signal.copy(), np.zeros_like(signal)

    # Matriz de Hankel
    M = np.array([signal[i:i+n_cols] for i in range(n_rows)]) / (np.max(np.abs(signal)) + 1e-8)
    L, S = rpca(M, max_iter=30)

    # Reconstrução antidiagonal
    def reconstruct(mat):
        result = np.zeros(N)
        counts = np.zeros(N)
        for i in range(n_rows):
            for j in range(n_cols):
                result[i+j] += mat[i, j]
                counts[i+j] += 1
        return result / (counts + 1e-10)

    return reconstruct(L) * np.max(np.abs(signal)), reconstruct(S) * np.max(np.abs(signal))


# ─── EMD (Empirical Mode Decomposition) ──────────────────────────────────────

def _get_envelopes(signal):
    """Calcula envelopes superior e inferior via interpolação cúbica."""
    t = np.arange(len(signal))
    max_idx = argrelmax(signal, order=3)[0]
    min_idx = argrelmin(signal, order=3)[0]

    if len(max_idx) < 3 or len(min_idx) < 3:
        return None, None

    # Adiciona pontos nas bordas
    max_idx = np.concatenate([[0], max_idx, [len(signal)-1]])
    min_idx = np.concatenate([[0], min_idx, [len(signal)-1]])
    max_val = np.concatenate([[signal[0]], signal[max_idx[1:-1]], [signal[-1]]])
    min_val = np.concatenate([[signal[0]], signal[min_idx[1:-1]], [signal[-1]]])

    try:
        upper = interp1d(max_idx, max_val, kind='cubic', fill_value='extrapolate')(t)
        lower = interp1d(min_idx, min_val, kind='cubic', fill_value='extrapolate')(t)
    except Exception:
        upper = np.full_like(signal, np.mean(signal))
        lower = upper.copy()

    return upper, lower


def emd(signal, n_imfs=5, n_sifting=10):
    """
    Empirical Mode Decomposition simplificada.
    Retorna lista de IMFs e o resíduo.
    """
    residue = signal.copy().astype(float)
    imfs = []

    for _ in range(n_imfs):
        h = residue.copy()
        prev_sd = np.inf

        for _ in range(n_sifting):
            upper, lower = _get_envelopes(h)
            if upper is None:
                break
            mean_env = (upper + lower) / 2.0
            h_new = h - mean_env

            # Critério de parada: desvio padrão da diferença
            sd = np.sum((h_new - h)**2) / (np.sum(h**2) + 1e-10)
            h = h_new
            if sd < 0.2 or abs(sd - prev_sd) < 1e-5:
                break
            prev_sd = sd

        imfs.append(h)
        residue = residue - h

        if np.std(residue) < 0.001 * np.std(signal):
            break

    return imfs, residue


# ─── Filtro de Kalman Escalar (UKF 1D) ───────────────────────────────────────

def kalman_filter_1d(signal, process_var=1e-3, obs_var=1e-1):
    """
    Filtro de Kalman escalar (equivalente ao UKF em 1D linear).
    Suaviza o sinal preservando transientes relevantes.
    """
    n = len(signal)
    x = signal[0]       # estimativa do estado
    P = 1.0             # covariância do erro
    Q = process_var     # variância do processo
    R = obs_var         # variância da observação

    filtered = np.zeros(n)
    for i, z in enumerate(signal):
        # Predição
        x_pred = x
        P_pred = P + Q

        # Atualização
        K = P_pred / (P_pred + R)
        x = x_pred + K * (z - x_pred)
        P = (1 - K) * P_pred

        filtered[i] = x

    return filtered


# ─── Pipeline HHT+UKF Completo ───────────────────────────────────────────────

def hht_ukf(signal, n_imfs=4, n_sifting=8, obs_var=0.05):
    """
    Pipeline completo HHT+UKF:
    1. EMD: decompõe o sinal em IMFs
    2. Filtra os IMFs de baixa ordem com Kalman (mantém assinatura da falha)
    3. Reconstrói o sinal limpo

    Retorna sinal limpo e ganho de SNR estimado.
    """
    imfs, residue = emd(signal, n_imfs=n_imfs, n_sifting=n_sifting)

    # Filtrar apenas IMFs relevantes (não filtrar o resíduo de alta frequência)
    clean = np.zeros_like(signal, dtype=float)
    for i, imf in enumerate(imfs):
        # IMFs de baixa ordem (falha mecânica) com suavização leve
        proc_var = 1e-3 if i < 2 else 1e-2
        filtered_imf = kalman_filter_1d(imf, process_var=proc_var, obs_var=obs_var)
        clean += filtered_imf
    clean += residue

    # Estimar ganho de SNR
    noise_orig = signal - clean
    snr_gain = 0.0
    if np.std(noise_orig) > 1e-8 and np.std(clean) > 1e-8:
        snr_gain = 10 * np.log10(np.var(clean) / (np.var(noise_orig) + 1e-10))
        snr_gain = np.clip(snr_gain, 0, 15)

    # Normalizar
    max_val = np.max(np.abs(clean))
    if max_val > 1e-8:
        clean = clean / max_val

    return clean, snr_gain


def snr_estimate(clean_signal, noisy_signal):
    """Estima melhoria de SNR entre dois sinais."""
    diff = noisy_signal - clean_signal
    if np.var(diff) < 1e-12:
        return 0.0
    snr = 10 * np.log10(np.var(clean_signal) / (np.var(diff) + 1e-10))
    return float(np.clip(snr, -20, 40))
