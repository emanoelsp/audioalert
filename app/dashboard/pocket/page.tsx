"use client"

import { useState, useEffect, useRef } from "react"
import { Mic, Check, X, Save, Trash2, ArrowRight, ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Badge } from "@/components/ui/badge"
import { Spinner } from "@/components/ui/spinner"
import { Progress } from "@/components/ui/progress"

type Step = "form" | "recording" | "analyzing" | "result"

interface AnalysisResult {
  healthScore: number
  classification: "Normal" | "Anomalia"
  confidence: number
  modelUsed: string
  latency: string
}

export default function PocketPage() {
  const [step, setStep] = useState<Step>("form")
  const [assetName, setAssetName] = useState("")
  const [description, setDescription] = useState("")
  const [recordingProgress, setRecordingProgress] = useState(0)
  const [waveformData, setWaveformData] = useState<number[]>([])
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number | null>(null)

  // Simulate waveform animation
  useEffect(() => {
    if (step === "recording") {
      const interval = setInterval(() => {
        setRecordingProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval)
            setStep("analyzing")
            return 100
          }
          return prev + (100 / 160) // 16 seconds = 160 * 100ms
        })
        setWaveformData((prev) => {
          const newData = [...prev, Math.random() * 100]
          return newData.slice(-50)
        })
      }, 100)
      return () => clearInterval(interval)
    }
  }, [step])

  // Simulate analysis
  useEffect(() => {
    if (step === "analyzing") {
      const timeout = setTimeout(() => {
        const isAnomaly = Math.random() > 0.5
        setResult({
          healthScore: isAnomaly ? Math.floor(Math.random() * 40 + 20) : Math.floor(Math.random() * 20 + 75),
          classification: isAnomaly ? "Anomalia" : "Normal",
          confidence: Math.floor(Math.random() * 10 + 90),
          modelUsed: Math.random() > 0.5 ? "XGBoost" : "Mahalanobis",
          latency: "0.05ms",
        })
        setStep("result")
      }, 3000)
      return () => clearTimeout(timeout)
    }
  }, [step])

  // Draw waveform
  useEffect(() => {
    if (canvasRef.current && step === "recording") {
      const canvas = canvasRef.current
      const ctx = canvas.getContext("2d")
      if (!ctx) return

      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.strokeStyle = "oklch(0.75 0.15 75)"
      ctx.lineWidth = 2
      ctx.beginPath()

      const sliceWidth = canvas.width / waveformData.length
      let x = 0

      waveformData.forEach((value, i) => {
        const y = (value / 100) * canvas.height * 0.8 + canvas.height * 0.1
        if (i === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
        x += sliceWidth
      })

      ctx.stroke()
    }
  }, [waveformData, step])

  const handleStartRecording = () => {
    setStep("recording")
    setRecordingProgress(0)
    setWaveformData([])
  }

  const handleReset = () => {
    setStep("form")
    setAssetName("")
    setDescription("")
    setRecordingProgress(0)
    setWaveformData([])
    setResult(null)
  }

  const handleSave = () => {
    // Simulate saving
    alert("Analise salva com sucesso!")
    handleReset()
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">AudioAlert Pocket</h1>
        <p className="text-muted-foreground">Diagnostico de audio sob demanda via dispositivo movel</p>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center justify-between">
        {["Informacoes", "Gravacao", "Analise", "Resultado"].map((label, index) => {
          const stepIndex = ["form", "recording", "analyzing", "result"].indexOf(step)
          const isActive = index <= stepIndex
          const isCurrent = index === stepIndex
          return (
            <div key={label} className="flex flex-1 items-center">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium ${
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground"
                } ${isCurrent ? "ring-2 ring-primary ring-offset-2 ring-offset-background" : ""}`}
              >
                {index + 1}
              </div>
              <span
                className={`ml-2 hidden text-sm sm:block ${
                  isActive ? "text-foreground" : "text-muted-foreground"
                }`}
              >
                {label}
              </span>
              {index < 3 && (
                <div
                  className={`mx-4 h-0.5 flex-1 ${
                    index < stepIndex ? "bg-primary" : "bg-border"
                  }`}
                />
              )}
            </div>
          )
        })}
      </div>

      {/* Step 1: Form */}
      {step === "form" && (
        <Card className="border-border bg-card">
          <CardHeader>
            <CardTitle className="text-foreground">Informacoes do Ativo</CardTitle>
            <CardDescription>Identifique o equipamento a ser analisado</CardDescription>
          </CardHeader>
          <CardContent>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="assetName">Nome do Ativo</FieldLabel>
                <Input
                  id="assetName"
                  placeholder="Ex: Compressor A-01"
                  value={assetName}
                  onChange={(e) => setAssetName(e.target.value)}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="description">Descricao (opcional)</FieldLabel>
                <Textarea
                  id="description"
                  placeholder="Descreva o contexto da analise..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                />
              </Field>
            </FieldGroup>
            <Button
              className="mt-6 w-full"
              onClick={handleStartRecording}
              disabled={!assetName.trim()}
            >
              Iniciar Gravacao
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Recording */}
      {step === "recording" && (
        <Card className="border-border bg-card">
          <CardHeader className="text-center">
            <CardTitle className="text-foreground">Gravando Audio</CardTitle>
            <CardDescription>Posicione o dispositivo proximo ao equipamento</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center space-y-6">
            {/* Circular Progress */}
            <div className="relative flex h-48 w-48 items-center justify-center">
              <svg className="h-full w-full -rotate-90 transform">
                <circle
                  cx="96"
                  cy="96"
                  r="88"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                  className="text-muted"
                />
                <circle
                  cx="96"
                  cy="96"
                  r="88"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={553}
                  strokeDashoffset={553 - (553 * recordingProgress) / 100}
                  className="text-primary transition-all duration-100"
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <Mic className="h-10 w-10 animate-pulse text-primary" />
                <span className="mt-2 text-2xl font-bold text-foreground">
                  {Math.ceil((100 - recordingProgress) * 0.16)}s
                </span>
              </div>
            </div>

            {/* Waveform */}
            <div className="w-full rounded-lg border border-border bg-muted/30 p-4">
              <canvas ref={canvasRef} width={400} height={100} className="w-full" />
            </div>

            <p className="text-sm text-muted-foreground">
              Gravando {assetName}...
            </p>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Analyzing */}
      {step === "analyzing" && (
        <Card className="border-border bg-card">
          <CardHeader className="text-center">
            <CardTitle className="text-foreground">Analisando Audio</CardTitle>
            <CardDescription>Processando dados com inteligencia artificial</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center space-y-6 py-12">
            <div className="relative flex h-24 w-24 items-center justify-center">
              <div className="absolute h-full w-full animate-spin rounded-full border-4 border-muted border-t-primary" />
              <Spinner className="h-8 w-8 text-primary" />
            </div>
            <div className="space-y-2 text-center">
              <p className="font-medium text-foreground">Executando inferencia...</p>
              <p className="text-sm text-muted-foreground">
                Extraindo caracteristicas espectrais e aplicando modelo de ML
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 4: Result */}
      {step === "result" && result && (
        <div className="space-y-4">
          <Card className="border-border bg-card">
            <CardHeader className="text-center">
              <CardTitle className="text-foreground">Resultado da Analise</CardTitle>
              <CardDescription>{assetName}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Health Score Gauge */}
              <div className="flex flex-col items-center space-y-4">
                <div className="relative flex h-40 w-40 items-center justify-center">
                  <svg className="h-full w-full -rotate-90 transform">
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="currentColor"
                      strokeWidth="12"
                      fill="none"
                      className="text-muted"
                    />
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="currentColor"
                      strokeWidth="12"
                      fill="none"
                      strokeDasharray={440}
                      strokeDashoffset={440 - (440 * result.healthScore) / 100}
                      className={
                        result.healthScore > 70
                          ? "text-success"
                          : result.healthScore > 40
                          ? "text-primary"
                          : "text-destructive"
                      }
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-3xl font-bold text-foreground">{result.healthScore}</span>
                    <span className="text-sm text-muted-foreground">Health Score</span>
                  </div>
                </div>

                <Badge
                  className={`px-4 py-2 text-lg ${
                    result.classification === "Normal"
                      ? "bg-success text-success-foreground"
                      : "bg-destructive text-destructive-foreground"
                  }`}
                >
                  {result.classification === "Normal" ? (
                    <Check className="mr-2 h-5 w-5" />
                  ) : (
                    <X className="mr-2 h-5 w-5" />
                  )}
                  {result.classification}
                </Badge>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-3 gap-4 rounded-lg border border-border bg-muted/30 p-4">
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Confianca</p>
                  <p className="text-lg font-bold text-foreground">{result.confidence}%</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Modelo</p>
                  <p className="text-lg font-bold text-foreground">{result.modelUsed}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Latencia</p>
                  <p className="text-lg font-bold text-foreground">{result.latency}</p>
                </div>
              </div>

              {/* XAI Section */}
              <div className="space-y-2">
                <h3 className="font-semibold text-foreground">Explicabilidade (XAI)</h3>
                <div className="rounded-lg border border-border bg-muted/30 p-4">
                  <p className="mb-2 text-sm text-muted-foreground">Heatmap do Espectrograma</p>
                  <div className="h-32 w-full rounded bg-gradient-to-r from-blue-900 via-yellow-500 to-red-600 opacity-80">
                    <div className="flex h-full items-center justify-center">
                      <span className="rounded bg-background/80 px-2 py-1 text-xs text-foreground">
                        Visualizacao espectro-temporal
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex gap-4">
            <Button variant="outline" className="flex-1" onClick={handleReset}>
              <Trash2 className="mr-2 h-4 w-4" />
              Descartar
            </Button>
            <Button className="flex-1" onClick={handleSave}>
              <Save className="mr-2 h-4 w-4" />
              Salvar no Banco
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
