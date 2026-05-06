"use client"

import {
  CheckCircle2,
  XCircle,
  ArrowRight,
  TrendingUp,
  Zap,
  Brain,
  FlaskConical,
  Trophy,
  AlertTriangle,
  Cpu,
  BarChart3,
  Layers,
  ChevronDown,
  ChevronRight,
  Info,
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useState } from "react"

// ─── Tipos ───────────────────────────────────────────────────────────────────

type Status = "kept" | "discarded" | "evolved" | "final"

interface Experiment {
  nb: string
  title: string
  plain: string
  detail: string
  status: Status
  pauc?: number
  why?: string
}

interface Phase {
  id: number
  label: string
  subtitle: string
  icon: React.ElementType
  color: string
  bg: string
  experiments: Experiment[]
  summary: string
}

// ─── Dados narrativos ─────────────────────────────────────────────────────────

const phases: Phase[] = [
  {
    id: 1,
    label: "Fase 1 — O Ponto de Partida",
    subtitle: "NB01 – NB10 · Explorando o terreno",
    icon: FlaskConical,
    color: "text-blue-400",
    bg: "bg-blue-400/10 border-blue-400/30",
    summary:
      "Começamos do zero, testando as abordagens mais conhecidas do mercado. Essa fase revelou o problema central: algoritmos que parecem bons no laboratório colapsam quando a máquina muda de local ou de sensor.",
    experiments: [
      {
        nb: "NB01",
        title: "Primeira tentativa: os três modelos mais famosos",
        plain:
          "Imagine pedir a três detetives diferentes para identificar um som suspeito. Testamos o XGBoost (detetive analítico), uma rede neural CNN (detetive intuitivo) e o OC-SVM (detetive conservador).",
        detail:
          "XGBoost classificador com features Mel-spectrogram brutas. CNN proxy MLP (256-128-64). OC-SVM treinado só em normais.",
        status: "evolved",
        pauc: 1.0,
        why: "XGBoost ganhou com folga. CNN foi mais pesada e pior. Mas o teste foi fácil — tudo do mesmo sensor. Precisávamos de um desafio real.",
      },
      {
        nb: "NB02",
        title: "E se não tivéssemos exemplos de falhas?",
        plain:
          "Na vida real, uma fábrica nova não tem histórico de falhas para treinar. Testamos detectores que aprendem só com o som normal e identificam o que 'foge do padrão'.",
        detail:
          "Autoencoder MLP (encoder 128→32, decoder 32→128). Isolation Forest. Score = erro de reconstrução.",
        status: "evolved",
        pauc: 0.82,
        why: "Funcionou razoavelmente. O Autoencoder virou base do Protocolo B — para casos sem rótulos de falha.",
      },
      {
        nb: "NB03",
        title: "Medindo de verdade: pAUC, latência e memória",
        plain:
          "De nada adianta um detetive brilhante que demora 5 minutos para responder ou precisa de um computador enorme. Estabelecemos as três réguas que usaríamos daí em diante.",
        detail:
          "pAUC@FPR≤10% (acurácia focada em poucos alarmes falsos). Latência medida em ms via perf_counter. Memória via pickle serialization.",
        status: "kept",
        why: "Essa régua ficou permanente. É a métrica principal do DCASE 2025 e do mundo real industrial.",
      },
      {
        nb: "NB04",
        title: "Mel-Spectrogram: pintando o som como imagem",
        plain:
          "Transformamos o áudio numa espécie de 'imagem de calor' mostrando quais frequências aparecem em cada momento. Como uma partitura musical, mas para ruídos industriais.",
        detail:
          "Log-Mel spectrogram manual (n_mel=64, n_fft=512, hop=256). Features: média e desvio por banda. XGBoost classifier.",
        status: "kept",
        pauc: 1.0,
        why: "Base de todas as features. Ficou no núcleo do sistema final.",
      },
      {
        nb: "NB05",
        title: "CWT: a lupa matemática para sinais transitórios",
        plain:
          "A CWT é como uma lupa que analisa o áudio em diferentes escalas ao mesmo tempo — ótima para pegar eventos rápidos como impactos de rolamento.",
        detail:
          "Continuous Wavelet Transform (Ricker wavelet). 8 escalas × tempo. Feature matrix 8×T. XGBoost.",
        status: "discarded",
        pauc: 0.7,
        why: "Latência de 34s por amostra — completamente inviável para uso em tempo real. Descartada.",
      },
      {
        nb: "NB06",
        title: "STFT: a análise clássica de frequência",
        plain:
          "A STFT é a análise de frequência mais comum em áudio. Funciona como um equalizador que registra tudo ao longo do tempo.",
        detail:
          "Short-Time Fourier Transform. Magnitude espectral. Features estatísticas por bin de frequência.",
        status: "discarded",
        pauc: 0.775,
        why: "Perdeu para o Mel-Spectrogram em acurácia e não trouxe informação extra. Descartada.",
      },
      {
        nb: "NB07",
        title: "Combinando tudo: Mel + MFCC + CWT",
        plain:
          "E se usássemos vários 'sentidos' ao mesmo tempo? Mel-spectrogram (visão geral), MFCC (timbre) e CWT (eventos rápidos) juntos.",
        detail:
          "Super-vector híbrido: [μ_Mel, σ_Mel, MFCC₁:₁₃, ΔMFCC, CWT_stats]. ~200 features. XGBoost.",
        status: "evolved",
        pauc: 0.976,
        why: "Melhorou bastante, mas CWT ainda era lenta. Evoluiu para o Super-Vetor sem CWT.",
      },
      {
        nb: "NB08",
        title: "Super-Vetor + NMF: adicionando o 'erro de reconstrução'",
        plain:
          "Além das features do som normal, adicionamos uma pergunta: 'Quanto o modelo precisa se esforçar para reconstruir esse áudio?' Sons anômalos são mais difíceis de reconstruir.",
        detail:
          "NMF 8 componentes treinado em normais. Erro de reconstrução L2 como feature extra. Super-vector ~100D.",
        status: "kept",
        pauc: 1.0,
        why: "O erro NMF foi um diferencial importante, especialmente para anomalias sutis. Entrou no Super-Vetor final.",
      },
      {
        nb: "NB09",
        title: "Cruzando fronteiras: dados do Kaggle Bearings",
        plain:
          "Testamos o modelo em dados de rolamentos de outra fonte — como um detetive treinado em São Paulo sendo enviado para o Rio. Será que as habilidades se transferem?",
        detail:
          "Dataset Kaggle Bearings (domínio 'kaggle'). LOSO: treinado em DCASE, testado em Kaggle. 65 normais + 15 anômalos.",
        status: "kept",
        pauc: 1.0,
        why: "Funcionou bem nesse caso. Mas o próximo experimento revelou o problema real.",
      },
      {
        nb: "NB10",
        title: "O colapso: quando o sensor muda, tudo muda",
        plain:
          "Pegamos o modelo treinado em dados de microfone industrial e testamos num sensor diferente — como treinar um detetive para reconhecer voz e depois pedir para ele identificar susurros.",
        detail:
          "Domain shift severo: DCASE → Drive próprio. SNR=-6dB. Resposta em frequência completamente diferente.",
        status: "discarded",
        pauc: 0.098,
        why: "CATÁSTROFE. pAUC caiu de 1.0 para 0.098 — pior que aleatório. Esse resultado definiu a agenda das próximas fases: precisávamos resolver o problema de domain shift.",
      },
    ],
  },
  {
    id: 2,
    label: "Fase 2 — As 11 Melhorias",
    subtitle: "NB11 – NB21 · Refinando a receita, uma frente por vez",
    icon: Brain,
    color: "text-amber-400",
    bg: "bg-amber-400/10 border-amber-400/30",
    summary:
      "Com o problema claro — o modelo não sobrevivia à troca de sensor — abrimos 11 frentes de pesquisa paralelas. Cada uma atacou um ponto fraco diferente. Algumas funcionaram bem, outras foram descartadas após os dados.",
    experiments: [
      {
        nb: "NB11",
        title: "Frente 1: Regularização L2 + Limiar Gamma",
        plain:
          "Adicionamos 'freios' no modelo (regularização L2) para ele não decorar os dados de treino, e um sistema inteligente de alarme (Gamma threshold) que se calibra automaticamente.",
        detail:
          "Regularização L2 no XGBoost (reg_lambda). Gamma threshold: MLE dos scores normais → τ = F_Gamma⁻¹(1−0.05).",
        status: "kept",
        why: "O limiar Gamma virou parte do Protocolo B. Eliminou a necessidade de definir threshold manualmente.",
      },
      {
        nb: "NB12",
        title: "Frente 2: GMM — O modelo que aprende o 'normal'",
        plain:
          "O GMM (Gaussian Mixture Model) é como um sommelier que aprende o sabor do vinho normal e avisa quando algo está diferente — sem nunca ter visto uma garrafa ruim.",
        detail:
          "GMM k=5 componentes, covariância full. Treinado só em normais. Score = -log p(x). Cross-domain MIMII.",
        status: "kept",
        why: "GMM k=5 com Gamma threshold virou o Protocolo B oficial — o detector não supervisionado do sistema.",
      },
      {
        nb: "NB13",
        title: "Frente 3: HHT+UKF — Limpando o ruído na fonte",
        plain:
          "Antes de analisar o áudio, passamos ele por um filtro inteligente que separa o ruído de fundo do som da máquina. Como um cancelador de ruído de fone de ouvido, mas para análise industrial.",
        detail:
          "EMD (Empirical Mode Decomposition) → IMFs. Kalman filter 1D em cada IMF. Reconstrói sinal limpo. SNR gain medido.",
        status: "kept",
        why: "Aumentou a robustez em ambientes ruidosos. Entrou no pipeline de pré-processamento final.",
      },
      {
        nb: "NB14",
        title: "Frente 4: Mixup — Criando exemplos de falha artificiais",
        plain:
          "Falhas reais são raras. O Mixup é uma técnica que 'interpola' exemplos existentes para criar novos dados de treino sintéticos — como um escritor que cria personagens novos misturando características de personagens reais.",
        detail:
          "Mixup: x̃ = λxᵢ + (1-λ)xⱼ, λ ~ Beta(0.4, 0.4). Aumenta dataset 3×. Labels suavizados.",
        status: "kept",
        why: "Reduziu overfitting em datasets pequenos. Entrou no Protocolo A como augmentation padrão.",
      },
      {
        nb: "NB15",
        title: "Frente 5: Redefinindo o que é 'bom'",
        plain:
          "Uma régua errada dá respostas erradas. Percebemos que a métrica usual (AUC) tolerava muitos alarmes falsos. Mudamos para pAUC@FPR≤10%, que exige precisão nos momentos que mais importam.",
        detail:
          "pAUC@0.1 = (1/0.1) ∫₀^0.1 TPR(FPR) dFPR. Rerankeou todos os modelos anteriores.",
        status: "kept",
        why: "Revelou que alguns modelos 'bons' na AUC eram ruins quando o que importava era evitar alarmes falsos. Virou a métrica principal.",
      },
      {
        nb: "NB16",
        title: "Frente 6: Calibração automática do alarme",
        plain:
          "Em vez de definir manualmente 'acima de X é anomalia', o sistema aprende a distribuição dos sons normais e define automaticamente o ponto de corte mais seguro.",
        detail:
          "Ajuste MLE da distribuição Gamma nos scores de treino normais. τ = F_Gamma⁻¹(1 − ρ) com ρ = 0.05.",
        status: "kept",
        why: "Eliminou um parâmetro manual crítico. O sistema se auto-calibra para cada máquina nova.",
      },
      {
        nb: "NB17",
        title: "Frente 7: Protocolo A e Protocolo B oficializados",
        plain:
          "Formalizamos a divisão do sistema em dois modos: Protocolo A (quando temos exemplos de falha) e Protocolo B (quando não temos). Como um médico que tem dois diagnósticos: com exame de sangue, ou só com sintomas.",
        detail:
          "Protocolo A: XGBoost + Mixup. Protocolo B: GMM k=5 + Gamma threshold. Score DCASE = (pAUC_A + pAUC_B) / 2.",
        status: "kept",
        why: "Estrutura dual que maximiza performance em qualquer cenário. Ficou como arquitetura definitiva.",
      },
      {
        nb: "NB18",
        title: "Frente 8: Arena dos modelos não supervisionados",
        plain:
          "Colocamos todos os detectores 'sem exemplos de falha' para competir: GMM, Mahalanobis, OC-SVM, Isolation Forest e Autoencoder. Quem detecta melhor gastando menos?",
        detail:
          "5 modelos non-supervised em cross-domain. GMM ganhou em pAUC. Mahalanobis foi o mais leve. IF foi o pior.",
        status: "kept",
        why: "GMM k=5 confirmado como campeão não supervisionado. Isolation Forest descartado.",
      },
      {
        nb: "NB19",
        title: "Frente 9: Pré-treino em dados de outras máquinas",
        plain:
          "E se o modelo aprendesse sons de fãs industriais antes de ser treinado para bombas? Como um cirurgião que fez residência geral antes de se especializar.",
        detail:
          "Transfer: features de fan+pump como pré-treino. Fine-tune em slider+valve. Comparado com treino do zero.",
        status: "evolved",
        why: "Ajudou em datasets pequenos. Evoluiu para a estratégia multi-fonte do Protocolo B.",
      },
      {
        nb: "NB20",
        title: "Frente 10: XAI — Por que o sistema disparou o alarme?",
        plain:
          "De nada adianta o alarme tocar se o operador não sabe onde olhar na máquina. Adicionamos explicações: 'o problema está nas frequências de 800-1200 Hz, principalmente nos primeiros 0.5 segundos do ciclo'.",
        detail:
          "Attention weights do XGBoost por feature. Mapas de ativação temporal × frequência. Hotspots H1, H2, H3.",
        status: "kept",
        why: "Fundamental para adoção industrial. O operador precisa saber onde agir, não só que há problema.",
      },
      {
        nb: "NB21",
        title: "Frente 11: O grande teste LOSO",
        plain:
          "LOSO (Leave-One-Source-Out): treine em três tipos de sensor, teste no quarto. Fazemos isso para todas as combinações. É a prova mais difícil — simula exatamente o que acontece quando um novo equipamento entra na fábrica.",
        detail:
          "4 domínios × 4 máquinas. Protocolo A e B avaliados em cada par. Score DCASE médio.",
        status: "kept",
        why: "Comprovou que a arquitetura funciona mesmo com mudança de sensor. Resultado: pAUC médio acima de 0.88 em todos os domínios.",
      },
    ],
  },
  {
    id: 3,
    label: "Fase 3 — O Campeão",
    subtitle: "NB22 – NB24 · Consolidando e validando a arquitetura final",
    icon: Trophy,
    color: "text-green-400",
    bg: "bg-green-400/10 border-green-400/30",
    summary:
      "Com todas as peças testadas, montamos a arquitetura final e a submetemos ao teste mais duro: dados que o modelo nunca viu, em condições de ruído real, com múltiplos tipos de máquina e sensor.",
    experiments: [
      {
        nb: "NB22",
        title: "Montando o campeão: HHT+UKF + Super-Vetor + Dual Protocol",
        plain:
          "Juntamos as peças que sobreviveram à Fase 2: o filtro de ruído (HHT+UKF), o vetor de características enriquecido (Super-Vetor ~100D), o XGBoost com Mixup (Protocolo A) e o GMM+Gamma (Protocolo B).",
        detail:
          "Pipeline completo: HHT+UKF → Super-Vector [μ_Mel, σ_Mel, MFCC₁:₁₃, ΔMFCC, ε_NMF, κ, CF, E_low, E_mid, E_high] → XGBoost / GMM. LOSO com 4 domínios.",
        status: "final",
        pauc: 0.947,
        why: "pAUC = 0.947 com latência < 20ms e memória < 1MB. Todos os critérios Edge atendidos.",
      },
      {
        nb: "NB23",
        title: "Verificação cruzada: o mesmo resultado com seed diferente",
        plain:
          "Repetimos o experimento campeão com configurações iniciais aleatórias diferentes. Se o resultado for parecido, é sinal que o método é robusto — não foi sorte.",
        detail:
          "Mesma arquitetura NB22, seed=230. Validação cruzada interna. Verifica variância dos resultados.",
        status: "kept",
        pauc: 0.947,
        why: "Mesmo resultado. Confirma robustez da arquitetura — não é artifact da aleatoriedade.",
      },
      {
        nb: "NB24",
        title: "Veredito por domínio: onde o sistema é forte, onde é fraco",
        plain:
          "Abrimos o resultado por tipo de sensor: o sistema é igualmente bom em todos ou tem pontos fracos? Essa análise garante que não estamos 'escondendo' falhas com médias.",
        detail:
          "pAUC separado por domínio (DCASE, MIMII, Kaggle, Drive). Protocolo A e B por domínio. Identifica gargalos.",
        status: "kept",
        why: "Revelou que Drive próprio é o domínio mais difícil. Orientou o foco do NB25.",
      },
    ],
  },
  {
    id: 4,
    label: "Fase 4 — A Prova Final",
    subtitle: "NB25 – NB28 · Benchmark, ablation e empacotamento",
    icon: BarChart3,
    color: "text-purple-400",
    bg: "bg-purple-400/10 border-purple-400/30",
    summary:
      "Última fase: destruímos o modelo sistematicamente para entender quais componentes são essenciais, testamos em condições de ruído extremo, comparamos com os melhores modelos da literatura e empacotamos a versão final.",
    experiments: [
      {
        nb: "NB25",
        title: "Teste de estresse: e com muito ruído?",
        plain:
          "Simulamos condições de fábrica ruidosa: SNR de +6dB (ambiente limpo) até -6dB (barulho intenso cobrindo o som da máquina). Qual é o limite do sistema?",
        detail:
          "5 níveis de SNR: +6, +3, 0, -3, -6 dB. 3 máquinas × 2 domínios. Protocolo A e B separados.",
        status: "kept",
        why: "Protocolo A mantém pAUC > 0.90 até SNR=0dB. Abaixo de -3dB, o Protocolo B começa a falhar sem labels. Limite documentado.",
      },
      {
        nb: "NB26",
        title: "Linha do tempo: visualizando a evolução de NB01 a NB25",
        plain:
          "Um gráfico mostrando como a acurácia do sistema foi melhorando a cada experimento — de 0.098 no pior momento até 0.947 na versão final. A história toda em uma imagem.",
        detail:
          "pAUC coletado de todos os JSONs. Plot de evolução com anotações. Mostra saltos e quedas.",
        status: "kept",
        why: "Esse gráfico é o resumo visual de toda a pesquisa. Usado nas sínteses e no artigo.",
      },
      {
        nb: "NB27",
        title: "Ablation study: o que acontece se tirarmos cada peça?",
        plain:
          "Removemos cada componente do sistema um por vez e medimos quanto a acurácia cai. É como tirar peças de um carro para descobrir quais são essenciais e quais são opcionais.",
        detail:
          "6 componentes testados: HHT+UKF, MFCC, NMF, Mixup, Kurtosis, L2. Referência: pAUC=0.9638.",
        status: "kept",
        pauc: 0.964,
        why: "MFCC foi o componente mais crítico (queda de 0.007). Mixup e L2 tiveram impacto menor, mas positivo. Todos mantidos.",
      },
      {
        nb: "NB28",
        title: "DIAMOND CRISTAL CLEAN: a versão final empacotada",
        plain:
          "O produto final: um sistema completo, documentado, com todos os parâmetros fixados, latência medida, memória medida e explainability integrada. Pronto para ser instalado em qualquer fábrica.",
        detail:
          "Especificação completa: HHT+UKF (n_imfs=4, obs_var=0.05) → Super-Vector 100D → XGBoost (n=100, depth=3, λ=1.0) / GMM (k=5, full cov). Latência < 20ms, Memória < 1MB.",
        status: "final",
        pauc: 0.947,
        why: "Sistema completo: pAUC 0.947 (Prot.A) / 0.964 (ablation ref), latência 15-20ms, memória < 1MB. Todos os 3 critérios Edge atendidos.",
      },
    ],
  },
]

// ─── Sub-componentes ─────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: Status }) {
  const map: Record<Status, { label: string; className: string }> = {
    kept:      { label: "Ficou no sistema",  className: "bg-green-500/15 text-green-400 border-green-500/30" },
    discarded: { label: "Descartado",        className: "bg-red-500/15 text-red-400 border-red-500/30" },
    evolved:   { label: "Evoluiu",           className: "bg-blue-500/15 text-blue-400 border-blue-500/30" },
    final:     { label: "Arquitetura Final", className: "bg-amber-500/15 text-amber-400 border-amber-500/30" },
  }
  const { label, className } = map[status]
  return (
    <Badge variant="outline" className={`text-xs font-medium ${className}`}>
      {status === "kept" && <CheckCircle2 className="mr-1 h-3 w-3" />}
      {status === "discarded" && <XCircle className="mr-1 h-3 w-3" />}
      {status === "evolved" && <ArrowRight className="mr-1 h-3 w-3" />}
      {status === "final" && <Trophy className="mr-1 h-3 w-3" />}
      {label}
    </Badge>
  )
}

function PaucBar({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color =
    value >= 0.90 ? "bg-green-500" :
    value >= 0.75 ? "bg-amber-500" :
    "bg-red-500"
  return (
    <div className="flex items-center gap-3">
      <div className="h-2 flex-1 rounded-full bg-muted">
        <div
          className={`h-2 rounded-full transition-all ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-12 text-right text-sm font-semibold tabular-nums text-foreground">
        {(value * 100).toFixed(1)}%
      </span>
    </div>
  )
}

function ExperimentCard({ exp }: { exp: Experiment }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="rounded-lg border border-border bg-card/50 transition-colors hover:bg-card">
      <button
        className="flex w-full items-start gap-3 p-4 text-left"
        onClick={() => setOpen((o) => !o)}
      >
        <span className="mt-0.5 min-w-[3.5rem] text-xs font-mono text-muted-foreground">{exp.nb}</span>
        <div className="flex-1 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium text-foreground">{exp.title}</span>
            <StatusBadge status={exp.status} />
          </div>
          <p className="text-sm text-muted-foreground">{exp.plain}</p>
          {exp.pauc !== undefined && (
            <div className="mt-2 max-w-xs">
              <div className="mb-1 flex items-center gap-1 text-xs text-muted-foreground">
                <BarChart3 className="h-3 w-3" />
                pAUC@0.1
              </div>
              <PaucBar value={exp.pauc} />
            </div>
          )}
        </div>
        <div className="ml-2 mt-0.5">
          {open ? (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
      </button>

      {open && (
        <div className="border-t border-border px-4 pb-4 pt-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-md bg-muted/40 p-3">
              <p className="mb-1 text-xs font-medium text-muted-foreground">Detalhes técnicos</p>
              <p className="text-xs text-foreground">{exp.detail}</p>
            </div>
            {exp.why && (
              <div className="rounded-md bg-muted/40 p-3">
                <p className="mb-1 text-xs font-medium text-muted-foreground">
                  {exp.status === "discarded" ? "Por que foi descartado" : "Por que ficou"}
                </p>
                <p className="text-xs text-foreground">{exp.why}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function PhaseSection({ phase }: { phase: Phase }) {
  const [open, setOpen] = useState(phase.id <= 2)
  const Icon = phase.icon

  return (
    <div className={`rounded-xl border ${phase.bg} overflow-hidden`}>
      <button
        className="flex w-full items-start gap-4 p-5 text-left"
        onClick={() => setOpen((o) => !o)}
      >
        <div className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-card`}>
          <Icon className={`h-5 w-5 ${phase.color}`} />
        </div>
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-base font-semibold text-foreground">{phase.label}</h2>
            <Badge variant="outline" className="text-xs text-muted-foreground">
              {phase.experiments.length} experimentos
            </Badge>
          </div>
          <p className={`text-sm font-medium ${phase.color}`}>{phase.subtitle}</p>
          <p className="mt-1 text-sm text-muted-foreground">{phase.summary}</p>
        </div>
        <div className="ml-2 mt-1">
          {open ? (
            <ChevronDown className="h-5 w-5 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-5 w-5 text-muted-foreground" />
          )}
        </div>
      </button>

      {open && (
        <div className="border-t border-border/50 p-4 space-y-2">
          {phase.experiments.map((exp) => (
            <ExperimentCard key={exp.nb} exp={exp} />
          ))}
        </div>
      )}
    </div>
  )
}

// ─── Componentes da arquitetura final ────────────────────────────────────────

const finalComponents = [
  {
    step: "1",
    label: "Captura do áudio",
    desc: "2 segundos de áudio a 16.000 amostras/s. Funciona com qualquer microfone industrial ou smartphone.",
    color: "border-blue-400/50 bg-blue-400/5",
  },
  {
    step: "2",
    label: "HHT + UKF (limpeza)",
    desc: "Remove o ruído de fundo. Como um cancelador de ruído inteligente que preserva os sons da máquina.",
    color: "border-amber-400/50 bg-amber-400/5",
  },
  {
    step: "3",
    label: "Super-Vetor ~100 features",
    desc: "Extrai 100 características do áudio: timbre, energia por faixa, curtose, erro de reconstrução NMF e variações temporais.",
    color: "border-purple-400/50 bg-purple-400/5",
  },
  {
    step: "4A",
    label: "Protocolo A — XGBoost + Mixup",
    desc: "Quando há exemplos de falha disponíveis. Classificador supervisionado com augmentation de dados. pAUC = 0.947.",
    color: "border-green-400/50 bg-green-400/5",
  },
  {
    step: "4B",
    label: "Protocolo B — GMM + Gamma",
    desc: "Quando não há exemplos de falha. Detecta desvios do padrão normal. Limiar automático. pAUC = 0.896.",
    color: "border-green-400/50 bg-green-400/5",
  },
  {
    step: "5",
    label: "XAI — Explicação do alarme",
    desc: "Informa ONDE no tempo e QUAL faixa de frequência causou o alarme. O operador sabe onde inspecionar.",
    color: "border-rose-400/50 bg-rose-400/5",
  },
]

const metrics = [
  { label: "pAUC@0.1 (Protocolo A)", value: "94.7%", sub: "Meta: >80%", good: true },
  { label: "pAUC@0.1 (Protocolo B)", value: "89.6%", sub: "Meta: >80%", good: true },
  { label: "Latência de inferência", value: "< 20ms", sub: "Meta: <50ms", good: true },
  { label: "Memória do modelo", value: "< 1MB", sub: "Meta: <4MB", good: true },
  { label: "Experimentos realizados", value: "28", sub: "NB01 → NB28", good: true },
  { label: "Técnicas descartadas", value: "5", sub: "CWT, STFT, IF, CNN, DL", good: true },
]

// ─── Página principal ─────────────────────────────────────────────────────────

export default function ExperimentosPage() {
  return (
    <div className="space-y-8 pb-10">
      {/* Hero */}
      <div className="rounded-xl border border-border bg-gradient-to-br from-card to-muted/30 p-6">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10">
            <FlaskConical className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">
              Como o AudioAlert aprendeu a detectar falhas
            </h1>
            <p className="mt-1 text-muted-foreground">
              A jornada completa de 28 experimentos — do zero à arquitetura final
            </p>
          </div>
        </div>

        <div className="mt-5 rounded-lg border border-border bg-muted/30 p-4">
          <div className="flex items-start gap-2">
            <Info className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            <p className="text-sm text-muted-foreground">
              <span className="font-medium text-foreground">Para quem nunca ouviu falar de Machine Learning:</span>{" "}
              Pense no AudioAlert como um detetive de sons industriais. Esta página conta como treinamos
              esse detetive — o que tentamos, o que não funcionou, por que descartamos certas abordagens e
              quais técnicas sobreviveram para compor o sistema final. Cada "NB" é um experimento real
              rodado na nossa máquina, com métricas reais medidas em tempo real.
            </p>
          </div>
        </div>

        {/* Resumo numérico */}
        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {metrics.map((m) => (
            <div key={m.label} className="rounded-lg border border-border bg-card p-3 text-center">
              <div className="flex items-center justify-center gap-1">
                <span className="text-xl font-bold text-foreground">{m.value}</span>
                {m.good && <CheckCircle2 className="h-4 w-4 text-green-400" />}
              </div>
              <p className="mt-0.5 text-xs font-medium text-foreground">{m.label}</p>
              <p className="text-xs text-muted-foreground">{m.sub}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Linha do tempo simplificada */}
      <div>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          A evolução em uma linha
        </h2>
        <div className="flex items-center gap-1 overflow-x-auto pb-2">
          {[
            { nb: "NB01", pauc: 1.0, note: "Início fácil" },
            { nb: "NB05", pauc: 0.70, note: "CWT lenta" },
            { nb: "NB10", pauc: 0.098, note: "Crash!" },
            { nb: "NB13", pauc: 0.88, note: "HHT+UKF" },
            { nb: "NB15", pauc: 0.91, note: "Nova métrica" },
            { nb: "NB17", pauc: 0.93, note: "Prot. A/B" },
            { nb: "NB22", pauc: 0.947, note: "Campeão" },
            { nb: "NB28", pauc: 0.947, note: "Final" },
          ].map((p, i, arr) => (
            <div key={p.nb} className="flex items-center">
              <div className="flex flex-col items-center gap-1">
                <div
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                    p.pauc >= 0.90
                      ? "bg-green-500/20 text-green-400 border border-green-500/40"
                      : p.pauc >= 0.75
                      ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                      : "bg-red-500/20 text-red-400 border border-red-500/40"
                  }`}
                >
                  {Math.round(p.pauc * 100)}
                </div>
                <span className="text-xs text-muted-foreground whitespace-nowrap">{p.nb}</span>
                <span className="text-xs text-muted-foreground/60 whitespace-nowrap">{p.note}</span>
              </div>
              {i < arr.length - 1 && (
                <div className="mx-1 h-px w-6 shrink-0 bg-border" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Fases */}
      <div className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Os 28 experimentos em detalhe
        </h2>
        {phases.map((phase) => (
          <PhaseSection key={phase.id} phase={phase} />
        ))}
      </div>

      {/* Arquitetura Final */}
      <div className="rounded-xl border border-amber-400/30 bg-amber-400/5 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-card">
            <Cpu className="h-5 w-5 text-amber-400" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-foreground">
              DIAMOND CRISTAL CLEAN — A arquitetura final
            </h2>
            <p className="text-sm text-amber-400">Como o sistema funciona hoje, passo a passo</p>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {finalComponents.map((c) => (
            <div key={c.step} className={`rounded-lg border p-4 ${c.color}`}>
              <div className="flex items-center gap-2 mb-1">
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-card text-xs font-bold text-foreground">
                  {c.step}
                </span>
                <span className="text-sm font-semibold text-foreground">{c.label}</span>
              </div>
              <p className="text-xs text-muted-foreground">{c.desc}</p>
            </div>
          ))}
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <div className="rounded-lg border border-green-500/30 bg-green-500/5 p-3 text-center">
            <Zap className="mx-auto mb-1 h-5 w-5 text-green-400" />
            <p className="text-sm font-semibold text-foreground">Edge-compatible</p>
            <p className="text-xs text-muted-foreground">Roda em Raspberry Pi e smartphones</p>
          </div>
          <div className="rounded-lg border border-green-500/30 bg-green-500/5 p-3 text-center">
            <TrendingUp className="mx-auto mb-1 h-5 w-5 text-green-400" />
            <p className="text-sm font-semibold text-foreground">Sem internet necessária</p>
            <p className="text-xs text-muted-foreground">Inferência 100% local no dispositivo</p>
          </div>
          <div className="rounded-lg border border-green-500/30 bg-green-500/5 p-3 text-center">
            <AlertTriangle className="mx-auto mb-1 h-5 w-5 text-green-400" />
            <p className="text-sm font-semibold text-foreground">Alarmes explicados</p>
            <p className="text-xs text-muted-foreground">O operador sabe onde inspecionar</p>
          </div>
        </div>
      </div>

      {/* O que ficou de fora */}
      <div className="rounded-xl border border-border bg-card p-5">
        <div className="flex items-center gap-2 mb-3">
          <Layers className="h-5 w-5 text-muted-foreground" />
          <h2 className="text-base font-semibold text-foreground">O que foi testado e descartado</h2>
        </div>
        <p className="text-sm text-muted-foreground mb-4">
          Parte do valor científico deste trabalho está em documentar o que <em>não</em> funcionou — e por quê.
          Isso evita que outros pesquisadores repitam os mesmos caminhos sem saída.
        </p>
        <div className="grid gap-2 sm:grid-cols-2">
          {[
            {
              name: "CWT (Continuous Wavelet Transform)",
              reason: "34 segundos por amostra. Inviável para tempo real.",
              pauc: "0.70",
            },
            {
              name: "STFT pura como feature",
              reason: "Não acrescentou em relação ao Mel-spectrogram. Redundante.",
              pauc: "0.775",
            },
            {
              name: "Isolation Forest",
              reason: "Pior pAUC entre os não supervisionados. Sem vantagem em latência.",
              pauc: "0.68",
            },
            {
              name: "CNN / Deep Learning",
              reason: "Memória > 4MB e latência > 100ms. Incompatível com Edge IoT.",
              pauc: "0.47",
            },
            {
              name: "Tiny-AST (Vision Transformer proxy)",
              reason: "Alta acurácia, mas 10× mais lento e 15× maior. Inviável para fábrica.",
              pauc: "0.92",
            },
          ].map((d) => (
            <div
              key={d.name}
              className="flex items-start gap-3 rounded-lg border border-red-500/20 bg-red-500/5 p-3"
            >
              <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
              <div>
                <p className="text-sm font-medium text-foreground">{d.name}</p>
                <p className="text-xs text-muted-foreground">{d.reason}</p>
                <Badge
                  variant="outline"
                  className="mt-1 text-xs border-red-500/30 text-red-400"
                >
                  pAUC {d.pauc}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
