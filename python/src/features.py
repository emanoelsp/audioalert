"""
Extração de características: Log-Mel, MFCC, Delta-MFCC, NMF, CWT, STFT,
Kurtosis, Crest Factor e energias por banda.
"""
import numpy as np
from scipy.signal import stft as scipy_stft
from scipy.fft import dct
from sklearn.decomposition import NMF

SR = 16000
N_FFT = 512
HOP = 256
N_MEL = 64
N_MFCC = 13
FMIN = 20.0
FMAX = 8000.0


# ─── Mel Filterbank ──────────────────────────────────────────────────────────

def _hz_to_mel(hz):
    return 2595.0 * np.log10(1.0 + hz / 700.0)


def _mel_to_hz(mel):
    return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)


def mel_filterbank(sr=SR, n_fft=N_FFT, n_mel=N_MEL, fmin=FMIN, fmax=FMAX):
    """Cria banco de filtros triangulares na escala Mel."""
    mel_min = _hz_to_mel(fmin)
    mel_max = _hz_to_mel(fmax)
    mel_points = np.linspace(mel_min, mel_max, n_mel + 2)
    hz_points = _mel_to_hz(mel_points)
    bins = np.floor((n_fft + 1) * hz_points / sr).astype(int)
    bins = np.clip(bins, 0, n_fft // 2)

    filters = np.zeros((n_mel, n_fft // 2 + 1))
    for m in range(1, n_mel + 1):
        f_m_minus = bins[m - 1]
        f_m = bins[m]
        f_m_plus = bins[m + 1]
        for k in range(f_m_minus, f_m + 1):
            if f_m > f_m_minus:
                filters[m-1, k] = (k - f_m_minus) / (f_m - f_m_minus + 1e-10)
        for k in range(f_m, f_m_plus + 1):
            if f_m_plus > f_m:
                filters[m-1, k] = (f_m_plus - k) / (f_m_plus - f_m + 1e-10)

    return filters


_MEL_FB = mel_filterbank()


def log_mel_spectrogram(signal, sr=SR, n_fft=N_FFT, hop=HOP, n_mel=N_MEL):
    """Calcula Log-Mel Spectrogram (frames × n_mel)."""
    frames = []
    window = np.hanning(n_fft)
    for start in range(0, len(signal) - n_fft + 1, hop):
        frame = signal[start:start + n_fft] * window
        spectrum = np.abs(np.fft.rfft(frame)) ** 2
        mel = _MEL_FB @ spectrum
        log_mel = np.log(mel + 1e-8)
        frames.append(log_mel)
    return np.array(frames)   # (T, n_mel)


def mfcc(log_mel, n_mfcc=N_MFCC):
    """Calcula MFCCs a partir do Log-Mel via DCT-II."""
    coeffs = dct(log_mel, type=2, axis=-1, norm='ortho')
    return coeffs[:, :n_mfcc]   # (T, n_mfcc)


def delta(feat, width=3):
    """Primeira derivada (delta) de uma matriz de features."""
    T, D = feat.shape
    out = np.zeros_like(feat)
    pad = np.pad(feat, ((width, width), (0, 0)), mode='edge')
    denominador = 2 * sum(i**2 for i in range(1, width+1))
    for t in range(T):
        out[t] = sum(i * (pad[t+width+i] - pad[t+width-i])
                     for i in range(1, width+1)) / denominador
    return out


def stft_features(signal, n_fft=N_FFT, hop=HOP):
    """Retorna magnitude do STFT (freq × time)."""
    f, t, Zxx = scipy_stft(signal, fs=SR, nperseg=n_fft, noverlap=n_fft-hop)
    return np.abs(Zxx).T  # (time, freq)


def cwt_approx(signal, n_scales=32, fmin=50, fmax=4000, sr=SR):
    """CWT aproximada via banco de filtros Gabor (evita pywt)."""
    t = np.arange(len(signal)) / sr
    freqs = np.logspace(np.log10(fmin), np.log10(fmax), n_scales)
    result = np.zeros((len(signal), n_scales))
    for i, f in enumerate(freqs):
        sigma = 7.0 / (2 * np.pi * f)
        kernel_len = min(int(6 * sigma * sr), len(signal) // 4)
        if kernel_len < 3:
            continue
        kt = np.linspace(-kernel_len/sr, kernel_len/sr, 2*kernel_len+1)
        kernel = np.exp(-kt**2 / (2*sigma**2)) * np.cos(2*np.pi*f*kt)
        kernel /= np.linalg.norm(kernel) + 1e-10
        conv = np.convolve(signal, kernel, mode='same')
        result[:, i] = np.abs(conv)
    return result


# ─── NMF Error ───────────────────────────────────────────────────────────────

class NMFDetector:
    """Usa erro de reconstrução NMF como score de anomalia."""
    def __init__(self, n_components=8):
        self.n_components = n_components
        self.model = NMF(n_components=n_components, max_iter=200, random_state=42)

    def fit(self, X):
        """X: (n_samples, n_features) — features não negativas."""
        X_pos = np.abs(X)
        self.model.fit(X_pos)
        return self

    def reconstruction_error(self, X):
        """Retorna erro de reconstrução L2 por amostra."""
        X_pos = np.abs(X)
        W = self.model.transform(X_pos)
        X_rec = W @ self.model.components_
        errors = np.sqrt(np.mean((X_pos - X_rec)**2, axis=1))
        return errors


# ─── Estatísticas do sinal ───────────────────────────────────────────────────

def kurtosis(signal):
    mu = np.mean(signal)
    sigma = np.std(signal) + 1e-10
    return np.mean(((signal - mu) / sigma)**4)


def crest_factor(signal):
    rms = np.sqrt(np.mean(signal**2)) + 1e-10
    return np.max(np.abs(signal)) / rms


def band_energies(signal, sr=SR):
    """Energias nas faixas baixa (0-800Hz), média (800-2500Hz), alta (2500-5000Hz)."""
    spectrum = np.abs(np.fft.rfft(signal))**2
    freqs = np.fft.rfftfreq(len(signal), 1/sr)
    e_low  = np.mean(spectrum[(freqs >= 0)    & (freqs < 800)])
    e_mid  = np.mean(spectrum[(freqs >= 800)  & (freqs < 2500)])
    e_high = np.mean(spectrum[(freqs >= 2500) & (freqs < 5000)])
    total = e_low + e_mid + e_high + 1e-10
    return e_low/total, e_mid/total, e_high/total


# ─── Super-Vetor ─────────────────────────────────────────────────────────────

def extract_super_vector(signal, nmf_error=None, include_cwt=False,
                         include_stft_stats=False):
    """
    Extrai Super-Vetor ~100D de um sinal 1D.
    Retorna vetor de features.
    """
    mel = log_mel_spectrogram(signal)
    if len(mel) == 0:
        return np.zeros(100)

    # Mel stats (128D: mean + std por banda)
    mel_mean = np.mean(mel, axis=0)  # (n_mel,)
    mel_std  = np.std(mel, axis=0)   # (n_mel,)

    # MFCC (13D mean + 13D std + 13D delta mean)
    mfcc_feat = mfcc(mel)
    mfcc_mean = np.mean(mfcc_feat, axis=0)
    mfcc_std  = np.std(mfcc_feat, axis=0)
    delta_feat = delta(mfcc_feat)
    delta_mean = np.mean(delta_feat, axis=0)

    # Estatísticas escalares
    kurt = kurtosis(signal)
    cf   = crest_factor(signal)
    e_low, e_mid, e_high = band_energies(signal)

    parts = [mel_mean, mel_std, mfcc_mean, mfcc_std, delta_mean,
             [kurt, cf, e_low, e_mid, e_high]]

    if nmf_error is not None:
        parts.append([nmf_error])

    if include_cwt:
        cwt_feat = cwt_approx(signal, n_scales=16)
        parts.append(np.mean(cwt_feat, axis=0))
        parts.append(np.std(cwt_feat, axis=0))

    if include_stft_stats:
        stft_feat = stft_features(signal)
        parts.append(np.mean(stft_feat, axis=0)[:32])

    vec = np.concatenate([np.atleast_1d(p) for p in parts])
    return vec


def batch_extract(signals, nmf_detector=None, include_cwt=False,
                  include_stft=False, verbose=False):
    """Extrai features de um array de sinais."""
    features = []
    for i, sig in enumerate(signals):
        nmf_err = None
        if nmf_detector is not None:
            mel = log_mel_spectrogram(sig)
            if len(mel) > 0:
                err = nmf_detector.reconstruction_error(np.abs(mel))
                nmf_err = float(np.mean(err))
        vec = extract_super_vector(sig, nmf_error=nmf_err,
                                   include_cwt=include_cwt,
                                   include_stft_stats=include_stft)
        features.append(vec)
        if verbose and (i+1) % 50 == 0:
            print(f"  Features: {i+1}/{len(signals)}")
    return np.array(features)
