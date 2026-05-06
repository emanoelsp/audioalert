"use client"

// Valores pré-computados fora do componente para evitar hydration mismatch com Math.random()
const SPECTRUM_BARS = Array.from({ length: 60 }, (_, i) => {
  const position = i / 60
  const bellCurve = Math.sin(position * Math.PI)
  // PRNG determinístico baseado no índice (LCG simples)
  const r1 = ((i * 1664525 + 1013904223) & 0xffffffff) / 0xffffffff
  const r2 = (((i + 31) * 22695477 + 1) & 0xffffffff) / 0xffffffff
  return {
    height: 20 + bellCurve * 60,
    animationDelay: -(r1 * 2),
    animationDuration: 0.8 + r2 * 1.5,
    opacity: 0.3 + bellCurve * 0.7,
  }
})

import Link from "next/link"
import { 
  AudioWaveform, 
  Activity, 
  Shield, 
  Zap, 
  BarChart3, 
  Clock, 
  CheckCircle2,
  ArrowRight,
  ChevronRight,
  Cpu,
  Waves,
  Smartphone, 
  HardDrive  
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

/**
 * Componente de Onda de Áudio Animada
 * Simula a captação de áudio em tempo real com CSS puro
 */
const ActiveWaveform = () => (
  <div className="flex items-center justify-center gap-0.5 h-5 w-6">
    {[...Array(4)].map((_, i) => (
      <div
        key={i}
        className="w-1 bg-primary-foreground rounded-full animate-waveform"
        style={{
          height: '100%',
          animationDuration: `${0.6 + i * 0.1}s`,
          animationDelay: `${i * 0.15}s`
        }}
      />
    ))}
  </div>
)

const modules = [
  {
    icon: Smartphone,
    title: "AudioAlert Pocket",
    badge: "Versatilidade Mobile",
    description: "Transforme seu smartphone em uma ferramenta de inspeção acústica instantânea. Ideal para diagnósticos sob demanda e triagens rápidas em campo.",
    features: [
      "Captura via Web Audio API (16s)",
      "Inferência Cloud em tempo real",
      "Explicabilidade XAI no celular",
      "Histórico de análises portátil"
    ],
    color: "bg-blue-500/10 text-blue-500"
  },
  {
    icon: HardDrive,
    title: "AudioAlert Node",
    badge: "Potência Industrial",
    description: "Hardware IoT dedicado com IA embarcada (TinyML). Monitoramento contínuo 24/7 direto na borda para ativos críticos.",
    features: [
      "Processamento local (Edge AI)",
      "Latência ultrabaixa (0.05ms)",
      "Operação autônoma offline",
      "Integração via API Industrial"
    ],
    color: "bg-amber-500/10 text-amber-500"
  }
]

const stats = [
  { value: "99.7%", label: "de precisão na detecção", company: "Indústria Automotiva" },
  { value: "85%", label: "redução em downtime", company: "Siderúrgica Nacional" },
  { value: "< 50ms", label: "latência de resposta", company: "Petroquímica Global" },
  { value: "24/7", label: "monitoramento contínuo", company: "Energia Renovável" },
]

const features = [
  {
    icon: Waves,
    title: "Análise Acústica Avançada",
    description: "Algoritmos de ML processam padrões sonoros em tempo real para identificar anomalias antes que se tornem falhas críticas.",
  },
  {
    icon: Cpu,
    title: "Edge Computing",
    description: "Processamento local com latência ultrabaixa. Decisões em milissegundos sem depender de conectividade.",
  },
  {
    icon: Shield,
    title: "Manutenção Preditiva",
    description: "Preveja falhas com antecedência e planeje intervenções no momento ideal, maximizando a vida útil dos equipamentos.",
  },
  {
    icon: BarChart3,
    title: "Dashboards em Tempo Real",
    description: "Visualize o estado de saúde de toda sua planta industrial com métricas acionáveis e alertas inteligentes.",
  },
]

const useCases = [
  "Motores elétricos e redutores",
  "Compressores e bombas",
  "Esteiras transportadoras",
  "Turbinas e geradores",
  "Sistemas HVAC industriais",
  "Prensas e equipamentos hidráulicos",
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="fixed top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
              <ActiveWaveform />
            </div>
            <span className="text-lg font-semibold">AudioAlert</span>
          </div>
          
          <nav className="hidden items-center gap-8 md:flex">
            <Link href="#features" className="text-sm text-muted-foreground transition-colors hover:text-foreground">Recursos</Link>
            <Link href="#how-it-works" className="text-sm text-muted-foreground transition-colors hover:text-foreground">Como Funciona</Link>
            <Link href="#pricing" className="text-sm text-muted-foreground transition-colors hover:text-foreground">Preços</Link>
            <Link href="#contact" className="text-sm text-muted-foreground transition-colors hover:text-foreground">Contato</Link>
          </nav>

          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm">Entrar</Button>
            </Link>
            <Link href="/signup">
              <Button size="sm">
                Começar Agora
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </header>
{/* ESPECTRO DE ÁUDIO FIXO (Fundo da Tela Inteira) */}
<div className="fixed bottom-0 left-0 w-full h-[40vh] z-0 pointer-events-none overflow-hidden" aria-hidden="true">
          
          {/* Névoa de base (Glow Âmbar) */}
          <div className="absolute bottom-[-100px] left-1/2 w-[120%] h-[200px] -translate-x-1/2 bg-amber-500/20 blur-[100px]" />
          
          {/* Barras do Espectrograma */}
          <div className="absolute bottom-0 left-0 w-full flex items-end justify-between gap-[2px] px-2 h-full opacity-30">
            {/* 60 barras de frequências simuladas com valores determinísticos */}
            {SPECTRUM_BARS.map((bar, i) => (
              <div
                key={i}
                className="w-full bg-amber-600/30 rounded-t-sm animate-spectrum-bar"
                style={{
                  height: `${bar.height}%`,
                  animationDelay: `${bar.animationDelay}s`,
                  animationDuration: `${bar.animationDuration}s`,
                  opacity: bar.opacity,
                }}
              />
            ))}
          </div>
          
          {/* Gradiente superior para o espectro sumir suavemente na página */}
          <div className="absolute top-0 left-0 w-full h-1/2" />
        </div>
      {/* HERO */}
      <section className="relative min-h-screen w-full flex flex-col items-center justify-center overflow-hidden text-center isolate pt-16">       
         <div className="mx-auto max-w-4xl px-6">
          <Badge className="mb-6">Monitoramento acústico industrial com IA</Badge>
          <h1 className="text-5xl font-bold leading-tight">
            Detecte falhas pelo som antes que elas parem sua operação
          </h1>
          <p className="mt-6 text-lg text-muted-foreground">
            Identifique problemas em equipamentos em tempo real usando inteligência artificial aplicada ao áudio.
          </p>
         {/* Destaque da Solução Não Invasiva */}
         <div className="mt-8 relative overflow-hidden rounded-xl border border-amber-500/20 bg-background/40 px-6 py-4 shadow-xl backdrop-blur-md sm:px-8 max-w-3xl mx-auto">
            {/* Efeito de brilho de fundo na caixa */}
            <div className="absolute inset-0 bg-gradient-to-r from-amber-500/10 via-transparent to-amber-500/10 opacity-50" />
            
            <p className="relative flex flex-col sm:flex-row items-center justify-center gap-2 text-sm sm:text-base text-muted-foreground">
              <span className="flex items-center gap-2 font-semibold text-foreground">
                <Shield className="h-5 w-5 text-amber-500" /> 
                Solução 100% não invasiva:
              </span>
              <span>
                Capture pelo <strong className="text-amber-500 font-medium">celular</strong> ou acople <strong className="text-amber-500 font-medium">hardware</strong>, sem intervir nos equipamentos.
              </span>
            </p>
          </div>
      
{/* Barra de Confiança (Trust Badge) */}
<div className="mt-12 inline-flex flex-col sm:flex-row items-center justify-center gap-6 rounded-full border border-amber-500/20 bg-amber-500/10 px-8 py-3 text-sm font-semibold text-amber-500/90 shadow-[0_0_30px_-5px_rgba(245,158,11,0.15)] backdrop-blur-md">
            <span className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-amber-500" />
              Sem instalação complexa
            </span>
            
            {/* Divisor vertical (some no mobile) */}
            <span className="hidden sm:block h-5 w-[1px] bg-amber-500/30"></span> 
            
            <span className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-amber-500" />
              Sem parada de máquina
            </span>
          </div>        
          <div className="mt-10 flex justify-center gap-4">
            <Button className="bg-amber-500 text-white hover:bg-amber-500/90 text-xl text-gray-900" size="lg">Ver demonstração <ArrowRight className="ml-2 h-4 w-4" /></Button>
          </div>
          </div>
      </section>

      {/* MÓDULOS */}
      <section className="py-20 bg-muted/20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold">Como você utiliza o AudioAlert</h2>
          </div>
          <div className="grid gap-8 lg:grid-cols-2">
            {modules.map((module, index) => (
              <Card key={index} className="hover:border-primary/50 transition-colors">
                <CardContent className="p-8">
                  <div className="flex justify-between mb-6 bg-ye">
                    <div className={`flex h-14 w-14 items-center justify-center rounded-2xl ${module.color}`}>
                      <module.icon className="h-8 w-8" />
                    </div>
                    <Badge className="bg-primary text-primary-foreground" variant="secondary">{module.badge}</Badge>
                  </div>
                  <h3 className="text-2xl font-bold mb-4">{module.title}</h3>
                  <p className="text-muted-foreground mb-6">{module.description}</p>
                  <div className="space-y-2">
                    {module.features.map((f, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm">
                        <CheckCircle2 className="h-4 w-4 text-primary" />
                        {f}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="border-y border-border bg-muted/30 py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 lg:grid-cols-4">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl font-bold lg:text-4xl">{stat.value}</div>
                <div className="mt-1 text-sm text-muted-foreground">{stat.label}</div>
                <div className="mt-2 text-xs text-muted-foreground/70 italic">{stat.company}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold sm:text-4xl">Tecnologia construída para ambientes industriais</h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Combinamos sensores acústicos de alta fidelidade com algoritmos de machine learning para oferecer o mais avançado sistema de manutenção preditiva.
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            {features.map((feature, index) => (
              <Card key={index} className="bg-card/50">
                <CardContent className="p-6">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 mb-4">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="font-semibold text-xl">{feature.title}</h3>
                  <p className="text-muted-foreground mt-2 leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section id="how-it-works" className="bg-muted/30 py-20 lg:py-32 border-y">
        <div className="mx-auto max-w-7xl px-6">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            <div>
              <h2 className="text-3xl font-bold sm:text-4xl">Do áudio ao insight em milissegundos</h2>
              <p className="mt-4 text-lg text-muted-foreground">Nossa solução captura, processa e analisa sinais acústicos continuamente, identificando padrões que indicam desgaste ou falha iminente.</p>
              <div className="mt-8 space-y-6">
                {[
                  { step: 1, title: "Captura Acústica", text: "Sensores de alta fidelidade capturam o espectro sonoro dos equipamentos em tempo real." },
                  { step: 2, title: "Processamento Edge", text: "Algoritmos de ML processam localmente, garantindo latência mínima e operação offline." },
                  { step: 3, title: "Alerta Inteligente", text: "O sistema classifica anomalias e envia alertas priorizados para sua equipe de manutenção." }
                ].map((item) => (
                  <div key={item.step} className="flex gap-4">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">{item.step}</div>
                    <div>
                      <h3 className="font-semibold">{item.title}</h3>
                      <p className="mt-1 text-sm text-muted-foreground">{item.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border bg-card p-8">
              <h3 className="mb-6 font-semibold">Aplicações Suportadas</h3>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {useCases.map((useCase, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm text-muted-foreground">
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    <span>{useCase}</span>
                  </div>
                ))}
              </div>
              <div className="mt-8 rounded-lg border border-primary/20 bg-primary/5 p-4 flex items-center gap-3">
                <Clock className="h-5 w-5 text-primary" />
                <div>
                  <div className="font-medium">Implementação Rápida</div>
                  <div className="text-sm text-muted-foreground">Setup completo em menos de 24 horas</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA FINAL */}
      <section className="py-24 text-center">
        <div className="max-w-3xl mx-auto px-6">
          <h2 className="text-4xl font-bold">Reduza falhas antes que elas aconteçam</h2>
          <p className="mt-4 text-lg text-muted-foreground">Comece a monitorar seus equipamentos hoje mesmo e garanta a disponibilidade operacional.</p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link href="/signup">
              <Button size="lg" className="min-w-[200px]">Criar Conta Gratuita <ArrowRight className="ml-2 h-4 w-4" /></Button>
            </Link>
            <Link href="/login">
              <Button variant="outline" size="lg" className="min-w-[200px]">Já tenho conta</Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-muted/30 py-12">
        <div className="mx-auto max-w-7xl px-6 flex flex-col items-center justify-between gap-6 md:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <ActiveWaveform />
            </div>
            <span className="font-semibold">AudioAlert</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-muted-foreground">
            <Link href="#" className="hover:text-foreground">Termos de Uso</Link>
            <Link href="#" className="hover:text-foreground">Privacidade</Link>
            <Link href="#" className="hover:text-foreground">Documentação</Link>
          </div>
          <div className="text-sm text-muted-foreground">© 2026 AudioAlert. Todos os direitos reservados.</div>
        </div>
      </footer>
    </div>
  )
}

