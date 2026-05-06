"use client"

import { useState } from "react"
import { History, Filter, Tag, Smartphone, Radio, Calendar, ChevronDown, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface Anomaly {
  id: string
  asset: string
  source: "Pocket" | "Node"
  plant?: string
  date: string
  time: string
  anomalyScore: number
  classification: string | null
  severity: "low" | "medium" | "high"
  model: string
}

const classificationOptions = [
  "Falha de Rolamento",
  "Lubrificacao Insuficiente",
  "Desalinhamento",
  "Desbalanceamento",
  "Folga Mecanica",
  "Cavitacao",
  "Falha Eletrica",
  "Outro",
]

const initialAnomalies: Anomaly[] = [
  {
    id: "1",
    asset: "Compressor A-01",
    source: "Node",
    plant: "Planta Industrial A",
    date: "2024-01-15",
    time: "14:32:15",
    anomalyScore: 0.82,
    classification: "Falha de Rolamento",
    severity: "high",
    model: "XGBoost",
  },
  {
    id: "2",
    asset: "Bomba Hidraulica B-03",
    source: "Pocket",
    date: "2024-01-15",
    time: "12:15:42",
    anomalyScore: 0.65,
    classification: "Desbalanceamento",
    severity: "medium",
    model: "Mahalanobis",
  },
  {
    id: "3",
    asset: "Motor Eletrico C-12",
    source: "Node",
    plant: "Planta Industrial A",
    date: "2024-01-14",
    time: "09:45:30",
    anomalyScore: 0.45,
    classification: null,
    severity: "low",
    model: "XGBoost",
  },
  {
    id: "4",
    asset: "Ventilador D-05",
    source: "Node",
    plant: "Planta Industrial B",
    date: "2024-01-14",
    time: "08:20:18",
    anomalyScore: 0.71,
    classification: "Desalinhamento",
    severity: "medium",
    model: "Mahalanobis",
  },
  {
    id: "5",
    asset: "Gerador E-02",
    source: "Pocket",
    date: "2024-01-13",
    time: "16:55:02",
    anomalyScore: 0.88,
    classification: "Falha Eletrica",
    severity: "high",
    model: "XGBoost",
  },
  {
    id: "6",
    asset: "Bomba Centrifuga F-01",
    source: "Node",
    plant: "Planta Industrial A",
    date: "2024-01-13",
    time: "11:30:45",
    anomalyScore: 0.52,
    classification: null,
    severity: "medium",
    model: "Mahalanobis",
  },
  {
    id: "7",
    asset: "Compressor G-03",
    source: "Pocket",
    date: "2024-01-12",
    time: "15:10:22",
    anomalyScore: 0.38,
    classification: "Lubrificacao Insuficiente",
    severity: "low",
    model: "XGBoost",
  },
  {
    id: "8",
    asset: "Redutor H-04",
    source: "Node",
    plant: "Planta Industrial B",
    date: "2024-01-12",
    time: "10:05:33",
    anomalyScore: 0.76,
    classification: null,
    severity: "high",
    model: "Mahalanobis",
  },
]

export default function HistoryPage() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>(initialAnomalies)
  const [sourceFilter, setSourceFilter] = useState<string>("all")
  const [dateFilter, setDateFilter] = useState<string>("all")
  const [classifyDialogOpen, setClassifyDialogOpen] = useState(false)
  const [selectedAnomaly, setSelectedAnomaly] = useState<Anomaly | null>(null)

  const filteredAnomalies = anomalies.filter((anomaly) => {
    if (sourceFilter !== "all" && anomaly.source !== sourceFilter) return false
    if (dateFilter !== "all") {
      const today = new Date()
      const anomalyDate = new Date(anomaly.date)
      const diffDays = Math.floor((today.getTime() - anomalyDate.getTime()) / (1000 * 60 * 60 * 24))
      if (dateFilter === "today" && diffDays > 0) return false
      if (dateFilter === "week" && diffDays > 7) return false
      if (dateFilter === "month" && diffDays > 30) return false
    }
    return true
  })

  const handleClassify = (classification: string) => {
    if (!selectedAnomaly) return
    setAnomalies((prev) =>
      prev.map((a) => (a.id === selectedAnomaly.id ? { ...a, classification } : a))
    )
    setClassifyDialogOpen(false)
    setSelectedAnomaly(null)
  }

  const openClassifyDialog = (anomaly: Anomaly) => {
    setSelectedAnomaly(anomaly)
    setClassifyDialogOpen(true)
  }

  const unclassifiedCount = anomalies.filter((a) => !a.classification).length

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Historico de Anomalias</h1>
          <p className="text-muted-foreground">
            Gerenciamento e classificacao de anomalias detectadas
          </p>
        </div>
        {unclassifiedCount > 0 && (
          <Badge variant="outline" className="w-fit border-primary text-primary">
            {unclassifiedCount} nao classificadas
          </Badge>
        )}
      </div>

      {/* Filters */}
      <Card className="border-border bg-card">
        <CardContent className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium text-foreground">Filtros:</span>
          </div>
          <div className="flex flex-1 flex-wrap gap-4">
            <Select value={sourceFilter} onValueChange={setSourceFilter}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="Fonte" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas as Fontes</SelectItem>
                <SelectItem value="Pocket">Pocket</SelectItem>
                <SelectItem value="Node">Node</SelectItem>
              </SelectContent>
            </Select>
            <Select value={dateFilter} onValueChange={setDateFilter}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="Periodo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todo Periodo</SelectItem>
                <SelectItem value="today">Hoje</SelectItem>
                <SelectItem value="week">Ultima Semana</SelectItem>
                <SelectItem value="month">Ultimo Mes</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <span className="text-sm text-muted-foreground">
            {filteredAnomalies.length} resultados
          </span>
        </CardContent>
      </Card>

      {/* Table */}
      <Card className="border-border bg-card">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="border-border hover:bg-transparent">
                <TableHead className="text-muted-foreground">Ativo</TableHead>
                <TableHead className="text-muted-foreground">Fonte</TableHead>
                <TableHead className="text-muted-foreground">Data/Hora</TableHead>
                <TableHead className="text-muted-foreground">Score</TableHead>
                <TableHead className="text-muted-foreground">Severidade</TableHead>
                <TableHead className="text-muted-foreground">Classificacao</TableHead>
                <TableHead className="text-muted-foreground">Acoes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAnomalies.map((anomaly) => (
                <TableRow key={anomaly.id} className="border-border">
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-medium text-foreground">{anomaly.asset}</span>
                      {anomaly.plant && (
                        <span className="text-xs text-muted-foreground">{anomaly.plant}</span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={`flex w-fit items-center gap-1 ${
                        anomaly.source === "Node"
                          ? "border-success/50 text-success"
                          : "border-primary/50 text-primary"
                      }`}
                    >
                      {anomaly.source === "Node" ? (
                        <Radio className="h-3 w-3" />
                      ) : (
                        <Smartphone className="h-3 w-3" />
                      )}
                      {anomaly.source}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="text-foreground">{anomaly.date}</span>
                      <span className="text-xs text-muted-foreground">{anomaly.time}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span
                      className={`font-mono font-bold ${
                        anomaly.anomalyScore > 0.7
                          ? "text-destructive"
                          : anomaly.anomalyScore > 0.5
                          ? "text-primary"
                          : "text-foreground"
                      }`}
                    >
                      {(anomaly.anomalyScore * 100).toFixed(0)}%
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        anomaly.severity === "high"
                          ? "destructive"
                          : anomaly.severity === "medium"
                          ? "default"
                          : "secondary"
                      }
                      className={
                        anomaly.severity === "high"
                          ? "bg-destructive"
                          : anomaly.severity === "medium"
                          ? "bg-primary text-primary-foreground"
                          : ""
                      }
                    >
                      {anomaly.severity === "high"
                        ? "Alta"
                        : anomaly.severity === "medium"
                        ? "Media"
                        : "Baixa"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {anomaly.classification ? (
                      <span className="flex items-center gap-1 text-sm text-foreground">
                        <Check className="h-3 w-3 text-success" />
                        {anomaly.classification}
                      </span>
                    ) : (
                      <span className="text-sm text-muted-foreground">Nao classificada</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => openClassifyDialog(anomaly)}
                    >
                      <Tag className="mr-1 h-3 w-3" />
                      Classificar
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Classification Dialog */}
      <Dialog open={classifyDialogOpen} onOpenChange={setClassifyDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Classificar Anomalia</DialogTitle>
            <DialogDescription>
              {selectedAnomaly && (
                <>
                  Selecione o tipo de falha para <strong>{selectedAnomaly.asset}</strong>
                </>
              )}
            </DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-3 pt-4">
            {classificationOptions.map((option) => (
              <Button
                key={option}
                variant="outline"
                className={`justify-start ${
                  selectedAnomaly?.classification === option
                    ? "border-primary bg-primary/10"
                    : ""
                }`}
                onClick={() => handleClassify(option)}
              >
                {option}
              </Button>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
