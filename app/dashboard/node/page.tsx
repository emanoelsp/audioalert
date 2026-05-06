"use client"

import { useState, useEffect } from "react"
import { Factory, Radio, Plus, ChevronRight, X, Cpu, Clock, Database, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface Node {
  id: string
  name: string
  status: "online" | "offline"
  anomalyScore: number
  anomalyHistory: number[]
  model: "XGBoost" | "Mahalanobis"
  latency: string
  memoryFootprint: string
  lastUpdate: string
}

interface Plant {
  id: string
  name: string
  location: string
  nodes: Node[]
}

const initialPlants: Plant[] = [
  {
    id: "1",
    name: "Planta Industrial A",
    location: "Sao Paulo, SP",
    nodes: [
      {
        id: "n1",
        name: "Compressor Principal",
        status: "online",
        anomalyScore: 0.12,
        anomalyHistory: [0.1, 0.12, 0.15, 0.11, 0.13, 0.12, 0.14, 0.12],
        model: "XGBoost",
        latency: "0.05ms",
        memoryFootprint: "2.3MB",
        lastUpdate: "2s atras",
      },
      {
        id: "n2",
        name: "Bomba Hidraulica 01",
        status: "online",
        anomalyScore: 0.78,
        anomalyHistory: [0.3, 0.45, 0.52, 0.61, 0.68, 0.72, 0.75, 0.78],
        model: "Mahalanobis",
        latency: "0.03ms",
        memoryFootprint: "1.8MB",
        lastUpdate: "5s atras",
      },
      {
        id: "n3",
        name: "Motor Eletrico A1",
        status: "online",
        anomalyScore: 0.08,
        anomalyHistory: [0.08, 0.09, 0.07, 0.08, 0.09, 0.08, 0.07, 0.08],
        model: "XGBoost",
        latency: "0.04ms",
        memoryFootprint: "2.1MB",
        lastUpdate: "1s atras",
      },
    ],
  },
  {
    id: "2",
    name: "Planta Industrial B",
    location: "Campinas, SP",
    nodes: [
      {
        id: "n4",
        name: "Ventilador Industrial",
        status: "online",
        anomalyScore: 0.15,
        anomalyHistory: [0.12, 0.14, 0.13, 0.15, 0.14, 0.16, 0.14, 0.15],
        model: "XGBoost",
        latency: "0.05ms",
        memoryFootprint: "2.2MB",
        lastUpdate: "3s atras",
      },
      {
        id: "n5",
        name: "Gerador Backup",
        status: "offline",
        anomalyScore: 0,
        anomalyHistory: [0, 0, 0, 0, 0, 0, 0, 0],
        model: "Mahalanobis",
        latency: "-",
        memoryFootprint: "1.9MB",
        lastUpdate: "2h atras",
      },
    ],
  },
]

function Sparkline({ data, highlight }: { data: number[]; highlight?: boolean }) {
  const max = Math.max(...data, 1)
  const width = 100
  const height = 30
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width
    const y = height - (value / max) * height
    return `${x},${y}`
  })

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        points={points.join(" ")}
        fill="none"
        stroke={highlight ? "oklch(0.55 0.2 25)" : "oklch(0.75 0.15 75)"}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {data.length > 0 && (
        <circle
          cx={(data.length - 1) / (data.length - 1) * width}
          cy={height - (data[data.length - 1] / max) * height}
          r="3"
          fill={highlight ? "oklch(0.55 0.2 25)" : "oklch(0.75 0.15 75)"}
        />
      )}
    </svg>
  )
}

function NodeDetailDialog({ node, open, onOpenChange }: { node: Node; open: boolean; onOpenChange: (open: boolean) => void }) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Radio className="h-5 w-5 text-primary" />
            {node.name}
          </DialogTitle>
          <DialogDescription>Detalhes tecnicos do node de monitoramento</DialogDescription>
        </DialogHeader>
        <div className="space-y-6">
          {/* Status */}
          <div className="flex items-center justify-between rounded-lg border border-border bg-muted/30 p-4">
            <span className="text-muted-foreground">Status</span>
            <Badge
              variant={node.status === "online" ? "default" : "secondary"}
              className={node.status === "online" ? "bg-success text-success-foreground" : ""}
            >
              {node.status === "online" ? "Online" : "Offline"}
            </Badge>
          </div>

          {/* Anomaly Score */}
          <div className="rounded-lg border border-border bg-muted/30 p-4">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-muted-foreground">Anomaly Score</span>
              <span className={`text-2xl font-bold ${node.anomalyScore > 0.5 ? "text-destructive" : "text-foreground"}`}>
                {(node.anomalyScore * 100).toFixed(1)}%
              </span>
            </div>
            <Sparkline data={node.anomalyHistory} highlight={node.anomalyScore > 0.5} />
          </div>

          {/* Spectrogram Placeholder */}
          <div className="space-y-2">
            <span className="text-sm font-medium text-foreground">Ultimo Espectrograma</span>
            <div className="h-32 w-full rounded-lg border border-border bg-gradient-to-r from-blue-900 via-green-700 to-yellow-500 opacity-80">
              <div className="flex h-full items-center justify-center">
                <span className="rounded bg-background/80 px-2 py-1 text-xs text-foreground">
                  Visualizacao espectro-temporal
                </span>
              </div>
            </div>
          </div>

          {/* Technical Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-3 rounded-lg border border-border bg-muted/30 p-3">
              <Clock className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Latencia</p>
                <p className="font-bold text-foreground">{node.latency}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-lg border border-border bg-muted/30 p-3">
              <Cpu className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Modelo</p>
                <p className="font-bold text-foreground">{node.model}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-lg border border-border bg-muted/30 p-3">
              <Database className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Memoria</p>
                <p className="font-bold text-foreground">{node.memoryFootprint}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-lg border border-border bg-muted/30 p-3">
              <Zap className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Ultima Atualizacao</p>
                <p className="font-bold text-foreground">{node.lastUpdate}</p>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default function NodePage() {
  const [plants, setPlants] = useState<Plant[]>(initialPlants)
  const [selectedPlant, setSelectedPlant] = useState<Plant | null>(null)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [nodeDialogOpen, setNodeDialogOpen] = useState(false)
  const [newPlantDialogOpen, setNewPlantDialogOpen] = useState(false)
  const [newPlantName, setNewPlantName] = useState("")
  const [newPlantLocation, setNewPlantLocation] = useState("")

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setPlants((prevPlants) =>
        prevPlants.map((plant) => ({
          ...plant,
          nodes: plant.nodes.map((node) => {
            if (node.status === "offline") return node
            const newScore = Math.max(0, Math.min(1, node.anomalyScore + (Math.random() - 0.5) * 0.05))
            return {
              ...node,
              anomalyScore: newScore,
              anomalyHistory: [...node.anomalyHistory.slice(1), newScore],
              lastUpdate: "agora",
            }
          }),
        }))
      )
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  const handleAddPlant = () => {
    if (!newPlantName.trim()) return
    const newPlant: Plant = {
      id: `plant-${Date.now()}`,
      name: newPlantName,
      location: newPlantLocation,
      nodes: [],
    }
    setPlants([...plants, newPlant])
    setNewPlantName("")
    setNewPlantLocation("")
    setNewPlantDialogOpen(false)
  }

  const handleNodeClick = (node: Node) => {
    setSelectedNode(node)
    setNodeDialogOpen(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">AudioAlert Node</h1>
          <p className="text-muted-foreground">Monitoramento continuo de ativos industriais</p>
        </div>
        <Dialog open={newPlantDialogOpen} onOpenChange={setNewPlantDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Nova Planta
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Adicionar Nova Planta</DialogTitle>
              <DialogDescription>Configure uma nova planta industrial para monitoramento</DialogDescription>
            </DialogHeader>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="plantName">Nome da Planta</FieldLabel>
                <Input
                  id="plantName"
                  placeholder="Ex: Planta Industrial C"
                  value={newPlantName}
                  onChange={(e) => setNewPlantName(e.target.value)}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="plantLocation">Localizacao</FieldLabel>
                <Input
                  id="plantLocation"
                  placeholder="Ex: Rio de Janeiro, RJ"
                  value={newPlantLocation}
                  onChange={(e) => setNewPlantLocation(e.target.value)}
                />
              </Field>
            </FieldGroup>
            <Button className="mt-4 w-full" onClick={handleAddPlant} disabled={!newPlantName.trim()}>
              Adicionar Planta
            </Button>
          </DialogContent>
        </Dialog>
      </div>

      {/* Plants Grid */}
      {!selectedPlant ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {plants.map((plant) => {
            const onlineNodes = plant.nodes.filter((n) => n.status === "online").length
            const hasAlerts = plant.nodes.some((n) => n.anomalyScore > 0.5)
            return (
              <Card
                key={plant.id}
                className="cursor-pointer border-border bg-card transition-colors hover:border-primary/50"
                onClick={() => setSelectedPlant(plant)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <Factory className="h-6 w-6 text-primary" />
                    </div>
                    {hasAlerts && (
                      <Badge variant="destructive" className="bg-primary text-primary-foreground">
                        Alerta
                      </Badge>
                    )}
                  </div>
                  <CardTitle className="mt-4 text-foreground">{plant.name}</CardTitle>
                  <CardDescription>{plant.location}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Radio className="h-4 w-4 text-success" />
                      <span className="text-sm text-muted-foreground">
                        {onlineNodes}/{plant.nodes.length} nodes online
                      </span>
                    </div>
                    <ChevronRight className="h-5 w-5 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      ) : (
        <>
          {/* Back Button */}
          <Button variant="ghost" onClick={() => setSelectedPlant(null)} className="mb-4">
            <ChevronRight className="mr-2 h-4 w-4 rotate-180" />
            Voltar para Plantas
          </Button>

          {/* Plant Header */}
          <Card className="border-border bg-card">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-primary/10">
                  <Factory className="h-7 w-7 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-foreground">{selectedPlant.name}</CardTitle>
                  <CardDescription>{selectedPlant.location}</CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Nodes Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {selectedPlant.nodes.map((node) => (
              <Card
                key={node.id}
                className="cursor-pointer border-border bg-card transition-colors hover:border-primary/50"
                onClick={() => handleNodeClick(node)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-base text-foreground">{node.name}</CardTitle>
                    <div className="flex items-center gap-1">
                      <span
                        className={`h-2 w-2 rounded-full ${
                          node.status === "online" ? "bg-success" : "bg-muted-foreground"
                        }`}
                      />
                      <span className="text-xs text-muted-foreground">
                        {node.status === "online" ? "Online" : "Offline"}
                      </span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Anomaly Score</span>
                      <span
                        className={`font-bold ${
                          node.anomalyScore > 0.5 ? "text-destructive" : "text-foreground"
                        }`}
                      >
                        {(node.anomalyScore * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Sparkline data={node.anomalyHistory} highlight={node.anomalyScore > 0.5} />
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{node.model}</span>
                      <span>{node.lastUpdate}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            {/* Add Node Card */}
            <Card className="flex cursor-pointer items-center justify-center border-dashed border-border bg-transparent transition-colors hover:border-primary/50 hover:bg-muted/20">
              <CardContent className="flex flex-col items-center py-8 text-muted-foreground">
                <Plus className="mb-2 h-8 w-8" />
                <span>Adicionar Node</span>
              </CardContent>
            </Card>
          </div>
        </>
      )}

      {/* Node Detail Dialog */}
      {selectedNode && (
        <NodeDetailDialog
          node={selectedNode}
          open={nodeDialogOpen}
          onOpenChange={setNodeDialogOpen}
        />
      )}
    </div>
  )
}
