"""
Zoo de modelos: XGBoost, GMM, Mahalanobis, OC-SVM, Isolation Forest,
MLP (proxy CNN), Autoencoder simples (proxy LSTM-AE) e Tiny-AST proxy.
Todos retornam scores de anomalia (maior = mais anômalo).
"""
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.mixture import GaussianMixture
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.pipeline import Pipeline
import xgboost as xgb


# ─── Mixup augmentation ───────────────────────────────────────────────────────

def mixup_augment(X, y, alpha=0.4, n_aug_factor=2, seed=42):
    """
    Mixup: x̃ = λx_i + (1-λ)x_j, λ ~ Beta(α, α)
    Retorna X aumentado e labels suavizados.
    """
    rng = np.random.default_rng(seed)
    n = len(X)
    n_new = n * n_aug_factor
    X_aug, y_aug = list(X), list(y.astype(float))

    for _ in range(n_new):
        i, j = rng.integers(0, n, size=2)
        lam = rng.beta(alpha, alpha)
        x_mix = lam * X[i] + (1 - lam) * X[j]
        y_mix = lam * y[i] + (1 - lam) * y[j]
        X_aug.append(x_mix)
        y_aug.append(y_mix)

    X_aug = np.array(X_aug)
    y_aug = np.array(y_aug)
    y_hard = (y_aug >= 0.5).astype(int)
    return X_aug, y_hard


# ─── XGBoost ─────────────────────────────────────────────────────────────────

def build_xgboost(n_estimators=100, max_depth=3, reg_lambda=1.0, seed=42):
    """XGBoost com hiperparâmetros padrão DIAMOND CRISTAL CLEAN."""
    return xgb.XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        reg_lambda=reg_lambda,
        eval_metric='logloss',
        use_label_encoder=False,
        random_state=seed,
        n_jobs=-1,
        verbosity=0,
    )


def train_xgboost(X_train, y_train, X_test, use_mixup=False, alpha=0.4,
                  scaler=None, **kwargs):
    """Treina XGBoost com ou sem Mixup. Retorna (model, scaler, scores_test)."""
    if scaler is None:
        scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_train)
    X_te = scaler.transform(X_test)

    if use_mixup:
        X_tr, y_tr = mixup_augment(X_tr, y_train, alpha=alpha)
    else:
        y_tr = y_train

    model = build_xgboost(**kwargs)
    model.fit(X_tr, y_tr)
    scores = model.predict_proba(X_te)[:, 1]
    return model, scaler, scores


# ─── GMM (não supervisionado) ─────────────────────────────────────────────────

class GMMDetector:
    """GMM treinado apenas em dados normais. Score = -log-verossimilhança."""
    def __init__(self, n_components=5, covariance_type='full', seed=42):
        self.gmm = GaussianMixture(
            n_components=n_components,
            covariance_type=covariance_type,
            random_state=seed,
            max_iter=200
        )
        self.scaler = StandardScaler()

    def fit(self, X_normal):
        X = self.scaler.fit_transform(X_normal)
        self.gmm.fit(X)
        # Determina threshold pela distribuição Gamma
        scores_normal = -self.gmm.score_samples(X)
        return self

    def score(self, X):
        """Retorna score de anomalia (maior = mais anômalo)."""
        X = self.scaler.transform(X)
        return -self.gmm.score_samples(X)

    def predict_fn(self, X_single):
        """Para medição de latência."""
        return self.score(X_single)


# ─── Mahalanobis ─────────────────────────────────────────────────────────────

class MahalanobisDetector:
    """Distância de Mahalanobis como score de anomalia."""
    def __init__(self):
        self.scaler = StandardScaler()
        self.mu = None
        self.cov_inv = None

    def fit(self, X_normal):
        X = self.scaler.fit_transform(X_normal)
        self.mu = np.mean(X, axis=0)
        cov = np.cov(X.T) + 1e-5 * np.eye(X.shape[1])
        try:
            self.cov_inv = np.linalg.inv(cov)
        except np.linalg.LinAlgError:
            self.cov_inv = np.linalg.pinv(cov)
        return self

    def score(self, X):
        X = self.scaler.transform(X)
        diff = X - self.mu
        scores = np.array([
            float(np.sqrt(d @ self.cov_inv @ d))
            for d in diff
        ])
        return scores

    def predict_fn(self, X_single):
        return self.score(X_single)


# ─── OC-SVM ──────────────────────────────────────────────────────────────────

def train_ocsvm(X_normal, X_test, nu=0.1, kernel='rbf'):
    """OC-SVM treinado em dados normais. Score: decision_function negada."""
    scaler = StandardScaler()
    X_n = scaler.fit_transform(X_normal)
    X_t = scaler.transform(X_test)
    model = OneClassSVM(nu=nu, kernel=kernel, gamma='scale')
    model.fit(X_n)
    scores = -model.decision_function(X_t)
    return model, scaler, scores


# ─── Isolation Forest ─────────────────────────────────────────────────────────

def train_isolation_forest(X_train, X_test, contamination=0.1, seed=42):
    """Isolation Forest. Score: anomaly_score negado."""
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_train)
    X_te = scaler.transform(X_test)
    model = IsolationForest(contamination=contamination, random_state=seed, n_jobs=-1)
    model.fit(X_tr)
    scores = -model.decision_function(X_te)
    return model, scaler, scores


# ─── MLP (proxy CNN) ──────────────────────────────────────────────────────────

def train_mlp_cnn_proxy(X_train, y_train, X_test, hidden=(256, 128, 64), seed=42):
    """
    MLP profundo como proxy da CNN.
    Simula comportamento: boa acurácia, latência e memória maiores.
    """
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_train)
    X_te = scaler.transform(X_test)
    model = MLPClassifier(
        hidden_layer_sizes=hidden,
        max_iter=200,
        random_state=seed,
        early_stopping=True,
        n_iter_no_change=10,
        verbose=False
    )
    model.fit(X_tr, y_train)
    scores = model.predict_proba(X_te)[:, 1]
    return model, scaler, scores


# ─── Autoencoder simples (proxy LSTM-AE) ─────────────────────────────────────

class SimpleAutoencoder:
    """
    Autoencoder MLP. Score = erro de reconstrução.
    Proxy do LSTM-AE: mesma ideia, implementação mais leve.
    """
    def __init__(self, n_features, n_latent=32, seed=42):
        self.encoder = MLPRegressor(
            hidden_layer_sizes=(128, n_latent),
            max_iter=200, random_state=seed, verbose=False
        )
        self.decoder = MLPRegressor(
            hidden_layer_sizes=(128, n_features),
            max_iter=200, random_state=seed+1, verbose=False
        )
        self.scaler = StandardScaler()
        self.n_latent = n_latent

    def fit(self, X_normal):
        X = self.scaler.fit_transform(X_normal)
        # Treina encoder para comprimir
        X_reduced = X @ np.random.randn(X.shape[1], self.n_latent) / np.sqrt(self.n_latent)
        self.encoder.fit(X, X_reduced)
        # Treina decoder para reconstruir
        X_enc = self.encoder.predict(X)
        self.decoder.fit(X_enc, X)
        return self

    def score(self, X):
        X_sc = self.scaler.transform(X)
        X_enc = self.encoder.predict(X_sc)
        X_rec = self.decoder.predict(X_enc)
        errors = np.sqrt(np.mean((X_sc - X_rec)**2, axis=1))
        return errors

    def predict_fn(self, X_single):
        return self.score(X_single)


# ─── Tiny-AST proxy (modelo de referência para XAI) ──────────────────────────

def build_tiny_ast_proxy(X_train, y_train, X_test, seed=42):
    """
    Proxy do Tiny-AST: MLP grande com alto custo computacional.
    Alta acurácia, alta latência e memória — inviável para Edge.
    """
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_train)
    X_te = scaler.transform(X_test)
    # Arquitetura maior para simular custo do Transformer
    model = MLPClassifier(
        hidden_layer_sizes=(512, 256, 128, 64),
        max_iter=300,
        random_state=seed,
        early_stopping=True,
        verbose=False
    )
    model.fit(X_tr, y_train)
    scores = model.predict_proba(X_te)[:, 1]
    return model, scaler, scores
