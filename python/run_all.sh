#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# DIAMOND CRISTAL CLEAN — Runner Completo
# Roda todos os 28 experimentos e gera as 8 sínteses.
# Uso: bash run_all.sh [--from NB] [--to NB] [--nb NB]
# ═══════════════════════════════════════════════════════════════

set -e
cd "$(dirname "$0")"

PYTHON=python3

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  DIAMOND CRISTAL CLEAN — Pipeline de Experimentos"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ─── Verifica dependências ───────────────────────────────────────
echo "▸ Verificando dependências..."
$PYTHON -c "import scipy, sklearn, pandas, xgboost, nbformat" 2>/dev/null || {
    echo "  Instalando pacotes necessários..."
    $PYTHON -m pip install --quiet scipy scikit-learn pandas xgboost nbformat
}
echo "  ✅ Dependências OK"
echo ""

# ─── Cria estrutura de diretórios ────────────────────────────────
mkdir -p experiments_results/{figures,metrics,models}

# ─── Roda experimentos ───────────────────────────────────────────
echo "▸ Rodando experimentos..."
$PYTHON run_experiments.py "$@"

# ─── Gera sínteses ───────────────────────────────────────────────
echo ""
echo "▸ Gerando sínteses..."
$PYTHON generate_synthesis.py

# ─── Resumo ──────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Pipeline completo!"
echo ""
echo "  📂 Resultados em: experiments_results/"
echo "     figures/    — gráficos PNG de cada NB"
echo "     metrics/    — métricas JSON de cada NB"
echo ""
echo "  📓 Sínteses geradas:"
ls -1 SINTESE_*.ipynb 2>/dev/null | sed 's/^/     /'
echo ""
echo "  Para abrir as sínteses:"
echo "     jupyter notebook"
echo "═══════════════════════════════════════════════════════════"
