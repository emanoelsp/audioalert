"use client"

import { Activity, AlertTriangle, Radio, Smartphone, TrendingUp, Clock } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

const stats = [
  {
    title: "Total de Analises",
    value: "1,284",
    change: "+12%",
    icon: Activity,
    trend: "up",
  },
  {
    title: "Anomalias Detectadas",
    value: "47",
    change: "+3",
    icon: AlertTriangle,
    trend: "warning",
  },
  {
    title: "Nodes Ativos",
    value: "12",
    change: "100%",
    icon: Radio,
    trend: "up",
  },
  {
    title: "Analises Pocket",
    value: "328",
    change: "+8%",
    icon: Smartphone,
    trend: "up",
  },
]

const recentAnomalies = [
  {
    id: 1,
    asset: "Compressor A-01",
    type: "Rolamento",
    source: "Node",
    time: "2 min atras",
    severity: "high",
  },
  {
    id: 2,
    asset: "Bomba Hidraulica B-03",
    type: "Desbalanceamento",
    source: "Pocket",
    time: "15 min atras",
    severity: "medium",
  },
  {
    id: 3,
    asset: "Motor Eletrico C-12",
    type: "Lubrificacao",
    source: "Node",
    time: "1h atras",
    severity: "low",
  },
  {
    id: 4,
    asset: "Ventilador D-05",
    type: "Desalinhamento",
    source: "Node",
    time: "2h atras",
    severity: "medium",
  },
]

const activeNodes = [
  { id: 1, name: "Planta A - Setor 1", nodes: 4, online: 4, anomalies: 2 },
  { id: 2, name: "Planta A - Setor 2", nodes: 3, online: 3, anomalies: 0 },
  { id: 3, name: "Planta B - Producao", nodes: 5, online: 5, anomalies: 1 },
]

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">Visao geral do sistema AudioAlert</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title} className="border-border bg-card">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <stat.icon
                className={`h-5 w-5 ${
                  stat.trend === "warning" ? "text-primary" : "text-muted-foreground"
                }`}
              />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stat.value}</div>
              <p
                className={`text-xs ${
                  stat.trend === "warning"
                    ? "text-primary"
                    : stat.trend === "up"
                    ? "text-success"
                    : "text-muted-foreground"
                }`}
              >
                {stat.change} desde o ultimo mes
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Anomalies */}
        <Card className="border-border bg-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-foreground">
              <AlertTriangle className="h-5 w-5 text-primary" />
              Anomalias Recentes
            </CardTitle>
            <CardDescription>Ultimas deteccoes do sistema</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentAnomalies.map((anomaly) => (
                <div
                  key={anomaly.id}
                  className="flex items-center justify-between rounded-lg border border-border bg-muted/30 p-3"
                >
                  <div className="flex flex-col gap-1">
                    <span className="font-medium text-foreground">{anomaly.asset}</span>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span>{anomaly.type}</span>
                      <span>-</span>
                      <Badge
                        variant={anomaly.source === "Node" ? "secondary" : "outline"}
                        className="text-xs"
                      >
                        {anomaly.source}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
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
                    <span className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      {anomaly.time}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <Link
              href="/dashboard/history"
              className="mt-4 block text-center text-sm text-primary hover:underline"
            >
              Ver todas as anomalias
            </Link>
          </CardContent>
        </Card>

        {/* Active Nodes Summary */}
        <Card className="border-border bg-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-foreground">
              <Radio className="h-5 w-5 text-success" />
              Plantas Industriais
            </CardTitle>
            <CardDescription>Status dos nodes por planta</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activeNodes.map((plant) => (
                <div
                  key={plant.id}
                  className="flex items-center justify-between rounded-lg border border-border bg-muted/30 p-3"
                >
                  <div className="flex flex-col gap-1">
                    <span className="font-medium text-foreground">{plant.name}</span>
                    <span className="text-sm text-muted-foreground">
                      {plant.online}/{plant.nodes} nodes online
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    {plant.anomalies > 0 && (
                      <Badge variant="destructive" className="bg-primary text-primary-foreground">
                        {plant.anomalies} alertas
                      </Badge>
                    )}
                    <div className="flex h-3 w-3 items-center justify-center">
                      <span className="absolute h-3 w-3 animate-ping rounded-full bg-success opacity-75" />
                      <span className="relative h-2 w-2 rounded-full bg-success" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <Link
              href="/dashboard/node"
              className="mt-4 block text-center text-sm text-primary hover:underline"
            >
              Gerenciar plantas
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Link href="/dashboard/pocket">
          <Card className="cursor-pointer border-border bg-card transition-colors hover:border-primary/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-foreground">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Smartphone className="h-5 w-5 text-primary" />
                </div>
                AudioAlert Pocket
              </CardTitle>
              <CardDescription>
                Inicie uma nova analise de audio sob demanda usando o microfone do dispositivo
              </CardDescription>
            </CardHeader>
          </Card>
        </Link>
        <Link href="/dashboard/node">
          <Card className="cursor-pointer border-border bg-card transition-colors hover:border-primary/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-foreground">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-success/10">
                  <TrendingUp className="h-5 w-5 text-success" />
                </div>
                Monitoramento em Tempo Real
              </CardTitle>
              <CardDescription>
                Acesse os dados de monitoramento continuo dos nodes industriais instalados
              </CardDescription>
            </CardHeader>
          </Card>
        </Link>
      </div>
    </div>
  )
}
