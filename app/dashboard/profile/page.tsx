"use client"

import { useState } from "react"
import { useAuth } from "@/contexts/auth-context"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Spinner } from "@/components/ui/spinner"
import { toast } from "sonner"
import Swal from "sweetalert2"
import { User, Mail, Phone, Building2, Shield, Key, Save, Eye, EyeOff } from "lucide-react"

export default function ProfilePage() {
  const { user, userData, updateUserProfile, changePassword, loading } = useAuth()
  const router = useRouter()
  
  const [profileForm, setProfileForm] = useState({
    displayName: userData?.displayName || user?.displayName || "",
    phone: userData?.phone || "",
    company: userData?.company || "",
  })
  
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  })
  
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [isSavingPassword, setIsSavingPassword] = useState(false)

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    )
  }

  if (!user) {
    router.push("/login")
    return null
  }

  const getInitials = (name: string | null | undefined) => {
    if (!name) return "U"
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2)
  }

  const getRoleBadge = (role: string | undefined) => {
    switch (role) {
      case "admin":
        return <Badge variant="destructive">Administrador</Badge>
      case "operator":
        return <Badge variant="default">Operador</Badge>
      default:
        return <Badge variant="secondary">Visualizador</Badge>
    }
  }

  const handleSaveProfile = async () => {
    setIsSavingProfile(true)
    try {
      await updateUserProfile({
        displayName: profileForm.displayName,
        phone: profileForm.phone,
        company: profileForm.company,
      })
      toast.success("Perfil atualizado com sucesso!")
    } catch (error) {
      console.error("[v0] Error updating profile:", error)
      toast.error("Erro ao atualizar perfil")
    } finally {
      setIsSavingProfile(false)
    }
  }

  const handleChangePassword = async () => {
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      toast.error("As senhas nao coincidem")
      return
    }

    if (passwordForm.newPassword.length < 6) {
      toast.error("A nova senha deve ter pelo menos 6 caracteres")
      return
    }

    const result = await Swal.fire({
      title: "Alterar senha?",
      text: "Voce sera desconectado apos alterar a senha.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#f59e0b",
      cancelButtonColor: "#64748b",
      confirmButtonText: "Sim, alterar",
      cancelButtonText: "Cancelar",
      background: "#1e293b",
      color: "#f1f5f9",
    })

    if (!result.isConfirmed) return

    setIsSavingPassword(true)
    try {
      await changePassword(passwordForm.currentPassword, passwordForm.newPassword)
      
      await Swal.fire({
        title: "Senha alterada!",
        text: "Sua senha foi alterada com sucesso. Faca login novamente.",
        icon: "success",
        confirmButtonColor: "#f59e0b",
        background: "#1e293b",
        color: "#f1f5f9",
      })
      
      router.push("/login")
    } catch (error: unknown) {
      console.error("[v0] Error changing password:", error)
      const errorMessage = error instanceof Error && error.message.includes("wrong-password")
        ? "Senha atual incorreta"
        : "Erro ao alterar senha"
      toast.error(errorMessage)
    } finally {
      setIsSavingPassword(false)
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Meu Perfil</h1>
        <p className="text-muted-foreground">Gerencie suas informacoes pessoais e seguranca</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Profile Card */}
        <Card className="lg:col-span-1">
          <CardContent className="flex flex-col items-center p-6">
            <Avatar className="h-24 w-24">
              <AvatarImage src={user.photoURL || undefined} />
              <AvatarFallback className="bg-primary text-2xl text-primary-foreground">
                {getInitials(user.displayName || userData?.displayName)}
              </AvatarFallback>
            </Avatar>
            
            <h2 className="mt-4 text-xl font-semibold text-foreground">
              {user.displayName || userData?.displayName || "Usuario"}
            </h2>
            <p className="text-sm text-muted-foreground">{user.email}</p>
            
            <div className="mt-3">
              {getRoleBadge(userData?.role)}
            </div>

            <Separator className="my-6 w-full" />

            <div className="w-full space-y-4 text-sm">
              <div className="flex items-center gap-3 text-muted-foreground">
                <Mail className="h-4 w-4" />
                <span>{user.email}</span>
              </div>
              {userData?.phone && (
                <div className="flex items-center gap-3 text-muted-foreground">
                  <Phone className="h-4 w-4" />
                  <span>{userData.phone}</span>
                </div>
              )}
              {userData?.company && (
                <div className="flex items-center gap-3 text-muted-foreground">
                  <Building2 className="h-4 w-4" />
                  <span>{userData.company}</span>
                </div>
              )}
              <div className="flex items-center gap-3 text-muted-foreground">
                <Shield className="h-4 w-4" />
                <span>{userData?.plantAccess?.length || 0} plantas com acesso</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Edit Forms */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Configuracoes da Conta</CardTitle>
            <CardDescription>Atualize suas informacoes pessoais e senha</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="profile" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="profile" className="gap-2">
                  <User className="h-4 w-4" />
                  Perfil
                </TabsTrigger>
                <TabsTrigger value="security" className="gap-2">
                  <Key className="h-4 w-4" />
                  Seguranca
                </TabsTrigger>
              </TabsList>

              <TabsContent value="profile" className="mt-6">
                <FieldGroup>
                  <Field>
                    <FieldLabel htmlFor="displayName">Nome Completo</FieldLabel>
                    <Input
                      id="displayName"
                      value={profileForm.displayName}
                      onChange={(e) => setProfileForm({ ...profileForm, displayName: e.target.value })}
                      placeholder="Seu nome completo"
                    />
                  </Field>

                  <Field>
                    <FieldLabel htmlFor="email">Email</FieldLabel>
                    <Input
                      id="email"
                      value={user.email || ""}
                      disabled
                      className="bg-muted"
                    />
                    <p className="text-xs text-muted-foreground">O email nao pode ser alterado</p>
                  </Field>

                  <Field>
                    <FieldLabel htmlFor="phone">Telefone</FieldLabel>
                    <Input
                      id="phone"
                      value={profileForm.phone}
                      onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                      placeholder="(11) 99999-9999"
                    />
                  </Field>

                  <Field>
                    <FieldLabel htmlFor="company">Empresa</FieldLabel>
                    <Input
                      id="company"
                      value={profileForm.company}
                      onChange={(e) => setProfileForm({ ...profileForm, company: e.target.value })}
                      placeholder="Nome da sua empresa"
                    />
                  </Field>
                </FieldGroup>

                <Button 
                  onClick={handleSaveProfile} 
                  disabled={isSavingProfile}
                  className="mt-6"
                >
                  {isSavingProfile ? (
                    <Spinner className="mr-2 h-4 w-4" />
                  ) : (
                    <Save className="mr-2 h-4 w-4" />
                  )}
                  Salvar Alteracoes
                </Button>
              </TabsContent>

              <TabsContent value="security" className="mt-6">
                <FieldGroup>
                  <Field>
                    <FieldLabel htmlFor="currentPassword">Senha Atual</FieldLabel>
                    <div className="relative">
                      <Input
                        id="currentPassword"
                        type={showCurrentPassword ? "text" : "password"}
                        value={passwordForm.currentPassword}
                        onChange={(e) => setPasswordForm({ ...passwordForm, currentPassword: e.target.value })}
                        placeholder="Digite sua senha atual"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                        onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      >
                        {showCurrentPassword ? (
                          <EyeOff className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <Eye className="h-4 w-4 text-muted-foreground" />
                        )}
                      </Button>
                    </div>
                  </Field>

                  <Field>
                    <FieldLabel htmlFor="newPassword">Nova Senha</FieldLabel>
                    <div className="relative">
                      <Input
                        id="newPassword"
                        type={showNewPassword ? "text" : "password"}
                        value={passwordForm.newPassword}
                        onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                        placeholder="Digite a nova senha"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                        onClick={() => setShowNewPassword(!showNewPassword)}
                      >
                        {showNewPassword ? (
                          <EyeOff className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <Eye className="h-4 w-4 text-muted-foreground" />
                        )}
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Minimo de 6 caracteres</p>
                  </Field>

                  <Field>
                    <FieldLabel htmlFor="confirmPassword">Confirmar Nova Senha</FieldLabel>
                    <Input
                      id="confirmPassword"
                      type="password"
                      value={passwordForm.confirmPassword}
                      onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                      placeholder="Confirme a nova senha"
                    />
                  </Field>
                </FieldGroup>

                <Button 
                  onClick={handleChangePassword} 
                  disabled={isSavingPassword || !passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword}
                  className="mt-6"
                >
                  {isSavingPassword ? (
                    <Spinner className="mr-2 h-4 w-4" />
                  ) : (
                    <Key className="mr-2 h-4 w-4" />
                  )}
                  Alterar Senha
                </Button>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
