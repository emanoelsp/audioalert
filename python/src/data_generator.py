"""
Gerador de dados sintéticos que simula áudio industrial realista.
4 tipos de máquina × 4 domínios × (normal + anomalias)
"""
import numpy as np
from scipy.signal import butter, filtfilt

SR = 16000       # taxa de amostragem
DURATION = 2.0   # segundos por segmento
N_SAMPLES = int(SR * DURATION)


def _pink_noise(n):
    """Ruído rosa (1/f) via filtragem de ruído branco."""
    white = np.random.randn(n)
    b = np.array([0.049922035, -0.095993537, 0.050612699, -0.004408786])
    a = np.array([1, -2.494956002, 2.017265875, -0.522189400])
    return filtfilt(b, a, white)


def _apply_domain_response(signal, domain):
    """Simula resposta de frequência de cada domínio de gravação."""
    t = np.fft.rfftfreq(len(signal), 1/SR)
    S = np.fft.rfft(signal)
    if domain == 'dcase':
        # Sensor plano
        H = np.ones_like(t)
    elif domain == 'mimii':
        # Microfone industrial: leve boost 2-5kHz
        H = 1.0 + 0.3 * np.exp(-((t - 3500)/1500)**2)
    elif domain == 'kaggle':
        # Acelerômetro: ênfase em alta frequência
        H = 1.0 + 0.6 * (t / SR * 2)
        H = np.clip(H, 0.5, 2.5)
    elif domain == 'drive':
        # Smartphone: rolloff em alta, mais ruído de fundo
        H = 1.0 / (1.0 + (t / 4000)**2)
    else:
        H = np.ones_like(t)
    return np.fft.irfft(S * H, n=len(signal))


def _machine_base(machine_type, duration=DURATION, sr=SR):
    """Gera som base de máquina saudável."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    if machine_type == 'fan':
        f0 = 50.0
        signal = (np.sin(2*np.pi*f0*t) + 0.5*np.sin(2*np.pi*2*f0*t) +
                  0.25*np.sin(2*np.pi*3*f0*t) + 0.4*_pink_noise(len(t)))
    elif machine_type == 'pump':
        f0 = 60.0
        signal = (np.sin(2*np.pi*f0*t) + 0.6*np.sin(2*np.pi*2*f0*t) +
                  0.3*np.abs(np.sin(2*np.pi*0.5*f0*t)) +
                  0.35*_pink_noise(len(t)))
    elif machine_type == 'slider':
        f0 = 80.0
        mod = 1.0 + 0.3*np.sin(2*np.pi*2*t)
        signal = mod * np.sin(2*np.pi*f0*t) + 0.5*_pink_noise(len(t))
    elif machine_type == 'valve':
        f0 = 120.0
        signal = (0.7*np.sin(2*np.pi*f0*t) + 0.3*np.random.randn(len(t)) +
                  0.4*_pink_noise(len(t)))
    else:
        signal = 0.5*_pink_noise(len(t))
    return signal / (np.max(np.abs(signal)) + 1e-8)


def _add_anomaly(signal, machine_type, severity=1.0):
    """Adiciona assinatura de falha ao sinal normal."""
    t = np.linspace(0, DURATION, len(signal), endpoint=False)
    sr = len(signal) / DURATION
    rng = np.random.default_rng(42)
    anomaly = np.zeros_like(signal)

    if machine_type == 'fan':
        # Lâmina danificada: impactos periódicos
        bpfo = 47.0
        for k in range(int(DURATION * bpfo)):
            idx = int(k / bpfo * sr)
            if idx < len(anomaly):
                width = int(0.005 * sr)
                impulse = severity * 0.8 * np.exp(-np.linspace(0, 5, width))
                anomaly[idx:idx+width] += impulse[:len(anomaly[idx:idx+width])]
    elif machine_type == 'pump':
        # Cavitação: bursts de alta frequência
        n_bursts = rng.integers(3, 8)
        for _ in range(n_bursts):
            start = rng.integers(0, len(signal)//2)
            width = int(0.05 * sr)
            hf = severity * 0.9 * np.sin(2*np.pi*5000*t[start:start+width])
            hf *= np.hanning(min(width, len(hf)))
            anomaly[start:start+len(hf)] += hf
    elif machine_type == 'slider':
        # Falha de rolamento: impactos periódicos irregulares
        fi = 45.0
        jitter = 0.1
        for k in range(int(DURATION * fi)):
            dt = rng.normal(1/fi, jitter/fi)
            idx = int(k * dt * sr)
            if idx < len(anomaly):
                width = int(0.003 * sr)
                anomaly[idx:idx+width] += severity * 0.7 * np.random.randn(min(width, len(anomaly[idx:])))
    elif machine_type == 'valve':
        # Válvula emperrada: variação de amplitude sustentada
        mod_freq = 3.0
        anomaly = severity * 0.5 * np.abs(np.sin(2*np.pi*mod_freq*t)) * signal

    result = signal + anomaly
    return result / (np.max(np.abs(result)) + 1e-8)


def generate_dataset(n_normal=60, n_anomaly=20, machines=None, domains=None,
                     snr_db=6.0, domain_shift=False, seed=42):
    """
    Gera dataset sintético completo.
    Retorna: X (n_samples, N_SAMPLES), y (labels), meta (dict com info por sample)
    """
    np.random.seed(seed)
    if machines is None:
        machines = ['fan', 'pump', 'slider', 'valve']
    if domains is None:
        domains = ['dcase']

    X, y, meta = [], [], []
    signal_power = 1.0  # normalizado
    noise_power = signal_power / (10 ** (snr_db / 10))

    for domain in domains:
        for machine in machines:
            # Normal samples
            for i in range(n_normal):
                sig = _machine_base(machine)
                sig = _apply_domain_response(sig, domain)
                noise = np.sqrt(noise_power) * np.random.randn(len(sig))
                if domain_shift and domain == 'drive':
                    noise *= 2.5  # mais ruído no smartphone
                sig = sig + noise
                sig = sig / (np.max(np.abs(sig)) + 1e-8)
                X.append(sig)
                y.append(0)
                meta.append({'machine': machine, 'domain': domain, 'label': 'normal', 'idx': i})

            # Anomalous samples
            for i in range(n_anomaly):
                severity = np.random.uniform(0.6, 1.2)
                sig = _machine_base(machine)
                sig = _add_anomaly(sig, machine, severity)
                sig = _apply_domain_response(sig, domain)
                noise = np.sqrt(noise_power) * np.random.randn(len(sig))
                if domain_shift and domain == 'drive':
                    noise *= 2.5
                sig = sig + noise
                sig = sig / (np.max(np.abs(sig)) + 1e-8)
                X.append(sig)
                y.append(1)
                meta.append({'machine': machine, 'domain': domain, 'label': 'anomaly', 'idx': i})

    X = np.array(X)
    y = np.array(y)
    return X, y, meta


def train_test_split_loso(X, y, meta, test_domain):
    """Leave-One-Source-Out split: separa por domínio de gravação."""
    train_idx = [i for i, m in enumerate(meta) if m['domain'] != test_domain]
    test_idx  = [i for i, m in enumerate(meta) if m['domain'] == test_domain]
    return (X[train_idx], y[train_idx],
            X[test_idx],  y[test_idx])


def generate_mimii_snr(machine='fan', snr_levels=(-6, 0, 6), n_per_snr=30, seed=42):
    """Gera dados MIMII simulados em múltiplos SNRs."""
    datasets = {}
    for snr in snr_levels:
        X, y, meta = generate_dataset(
            n_normal=n_per_snr, n_anomaly=n_per_snr//3,
            machines=[machine], domains=['mimii'],
            snr_db=snr, seed=seed
        )
        datasets[snr] = (X, y)
    return datasets
