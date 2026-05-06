"use client"

import { useState } from "react"
import { Settings, User, Bell, Cpu, Shield, Save } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Field, FieldGroup, FieldLabel, FieldDescription } from "@/components/ui/field"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"

export default function SettingsPage() {
  const [userName, setUserName] = useState("Operador Industrial")
  const [email, setEmail] = useState("operador@empresa.com")
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [pushNotifications, setPushNotifications] = useState(true)
  const [anomalyThreshold, setAnomalyThreshold] = useState("0.5")
  const [defaultModel, setDefaultModel] = useState("auto")
  const [twoFactorAuth, setTwoFactorAuth] = useState(false)
  const [sessionTimeout, setSessionTimeout] = useState("30")

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Configuracoes</h1>
        <p className="text-muted-foreground">Gerencie suas preferencias e configuracoes do sistema</p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="bg-muted">
          <TabsTrigger value="profile" className="data-[state=active]:bg-card">
            <User className="mr-2 h-4 w-4" />
            Perfil
          </TabsTrigger>
          <TabsTrigger value="notifications" className="data-[state=active]:bg-card">
            <Bell className="mr-2 h-4 w-4" />
            Notificacoes
          </TabsTrigger>
          <TabsTrigger value="models" className="data-[state=active]:bg-card">
            <Cpu className="mr-2 h-4 w-4" />
            Modelos
          </TabsTrigger>
          <TabsTrigger value="security" className="data-[state=active]:bg-card">
            <Shield className="mr-2 h-4 w-4" />
            Seguranca
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <Card className="border-border bg-card">
            <CardHeader>
              <CardTitle className="text-foreground">Informacoes do Perfil</CardTitle>
              <CardDescription>Atualize suas informacoes pessoais</CardDescription>
            </CardHeader>
            <CardContent>
              <FieldGroup>
                <Field>
                  <FieldLabel htmlFor="userName">Nome</FieldLabel>
                  <Input
                    id="userName"
                    value={userName}
                    onChange={(e) => setUserName(e.target.value)}
                  />
                </Field>
                <Field>
                  <FieldLabel htmlFor="email">Email</FieldLabel>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </Field>
              </FieldGroup>
              <Button className="mt-6">
                <Save className="mr-2 h-4 w-4" />
                Salvar Alteracoes
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <Card className="border-border bg-card">
            <CardHeader>
              <CardTitle className="text-foreground">Preferencias de Notificacao</CardTitle>
              <CardDescription>Configure como deseja receber alertas</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between rounded-lg border border-border bg-muted/30 p-4">
                <div className="space-y-0.5">
                  <Label className="text-foreground">Notificacoes por Email</Label>
                  <p className="text-sm text-muted-foreground">
                    Receba alertas de anomalias por email
                  </p>
                </div>
                <Switch
                  checked={emailNotifications}
                  onCheckedChange={setEmailNotifications}
                />
              </div>
              <div className="flex items-center justify-between rounded-lg border border-border bg-muted/30 p-4">
                <div className="space-y-0.5">
                  <Label className="text-foreground">Notificacoes Push</Label>
                  <p className="text-sm text-muted-foreground">
                    Receba alertas em tempo real no navegador
                  </p>
                </div>
                <Switch
                  checked={pushNotifications}
                  onCheckedChange={setPushNotifications}
                />
              </div>
              <Separator />
              <Field>
                <FieldLabel htmlFor="threshold">Limiar de Alerta</FieldLabel>
                <FieldDescription>
                  Anomaly score minimo para disparar uma notificacao
                </FieldDescription>
                <Select value={anomalyThreshold} onValueChange={setAnomalyThreshold}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0.3">Baixo (30%)</SelectItem>
                    <SelectItem value="0.5">Medio (50%)</SelectItem>
                    <SelectItem value="0.7">Alto (70%)</SelectItem>
                    <SelectItem value="0.9">Critico (90%)</SelectItem>
                  </SelectContent>
                </Select>
              </Field>
              <Button className="mt-6">
                <Save className="mr-2 h-4 w-4" />
                Salvar Preferencias
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Models Tab */}
        <TabsContent value="models">
          <Card className="border-border bg-card">
            <CardHeader>
              <CardTitle className="text-foreground">Configuracao de Modelos ML</CardTitle>
              <CardDescription>
                Configure os parametros dos modelos de aprendizado de maquina
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Field>
                <FieldLabel htmlFor="defaultModel">Modelo Padrao</FieldLabel>
                <FieldDescription>
                  Selecione o modelo a ser usado quando nenhum for especificado
                </FieldDescription>
                <Select value={defaultModel} onValueChange={setDefaultModel}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="auto">Automatico (Recomendado)</SelectItem>
                    <SelectItem value="xgboost">XGBoost (Supervisionado)</SelectItem>
                    <SelectItem value="mahalanobis">Mahalanobis (Nao-Supervisionado)</SelectItem>
                  </SelectContent>
                </Select>
              </Field>

              <Separator />

              <div className="space-y-4">
                <h3 className="font-medium text-foreground">Informacoes dos Modelos</h3>
                
                <div className="rounded-lg border border-border bg-muted/30 p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-foreground">XGBoost</h4>
                      <p className="text-sm text-muted-foreground">
                        Modelo supervisionado para classificacao de falhas conhecidas
                      </p>
                    </div>
                    <span className="rounded bg-success/20 px-2 py-1 text-xs text-success">
                      Ativo
                    </span>
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Latencia</p>
                      <p className="font-mono font-bold text-foreground">0.05ms</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Acuracia</p>
                      <p className="font-mono font-bold text-foreground">94.2%</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Memoria</p>
                      <p className="font-mono font-bold text-foreground">2.3MB</p>
                    </div>
                  </div>
                </div>

                <div className="rounded-lg border border-border bg-muted/30 p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-foreground">Mahalanobis Distance</h4>
                      <p className="text-sm text-muted-foreground">
                        Modelo nao-supervisionado para deteccao de novidades
                      </p>
                    </div>
                    <span className="rounded bg-success/20 px-2 py-1 text-xs text-success">
                      Ativo
                    </span>
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Latencia</p>
                      <p className="font-mono font-bold text-foreground">0.03ms</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Sensibilidade</p>
                      <p className="font-mono font-bold text-foreground">97.8%</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Memoria</p>
                      <p className="font-mono font-bold text-foreground">1.8MB</p>
                    </div>
                  </div>
                </div>
              </div>

              <Button className="mt-6">
                <Save className="mr-2 h-4 w-4" />
                Salvar Configuracoes
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <Card className="border-border bg-card">
            <CardHeader>
              <CardTitle className="text-foreground">Seguranca da Conta</CardTitle>
              <CardDescription>Gerencie suas configuracoes de seguranca</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between rounded-lg border border-border bg-muted/30 p-4">
                <div className="space-y-0.5">
                  <Label className="text-foreground">Autenticacao em Dois Fatores</Label>
                  <p className="text-sm text-muted-foreground">
                    Adicione uma camada extra de seguranca a sua conta
                  </p>
                </div>
                <Switch checked={twoFactorAuth} onCheckedChange={setTwoFactorAuth} />
              </div>

              <Field>
                <FieldLabel htmlFor="sessionTimeout">Tempo de Sessao</FieldLabel>
                <FieldDescription>
                  Tempo de inatividade antes do logout automatico
                </FieldDescription>
                <Select value={sessionTimeout} onValueChange={setSessionTimeout}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="15">15 minutos</SelectItem>
                    <SelectItem value="30">30 minutos</SelectItem>
                    <SelectItem value="60">1 hora</SelectItem>
                    <SelectItem value="120">2 horas</SelectItem>
                  </SelectContent>
                </Select>
              </Field>

              <Separator />

              <div className="space-y-4">
                <h3 className="font-medium text-foreground">Acoes de Seguranca</h3>
                <div className="flex flex-wrap gap-4">
                  <Button variant="outline">Alterar Senha</Button>
                  <Button variant="outline">Ver Sessoes Ativas</Button>
                  <Button variant="destructive">Encerrar Todas as Sessoes</Button>
                </div>
              </div>

              <Button className="mt-6">
                <Save className="mr-2 h-4 w-4" />
                Salvar Configuracoes
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
