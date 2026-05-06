"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { AudioWaveform, Mail, Lock, Eye, EyeOff, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Checkbox } from "@/components/ui/checkbox"
import { Spinner } from "@/components/ui/spinner"
import { useAuth } from "@/contexts/auth-context"
import { toast } from "sonner"
import Swal from "sweetalert2"

export default function SignupPage() {
  const router = useRouter()
  const { signUp } = useAuth()
  const [displayName, setDisplayName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [acceptTerms, setAcceptTerms] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (password !== confirmPassword) {
      toast.error("As senhas nao coincidem.")
      return
    }

    if (password.length < 6) {
      toast.error("A senha deve ter pelo menos 6 caracteres.")
      return
    }

    if (!acceptTerms) {
      toast.error("Voce deve aceitar os termos de uso.")
      return
    }

    const result = await Swal.fire({
      title: "Confirmar Cadastro",
      html: `
        <p>Voce esta criando uma conta com:</p>
        <p><strong>Nome:</strong> ${displayName}</p>
        <p><strong>Email:</strong> ${email}</p>
      `,
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Confirmar",
      cancelButtonText: "Cancelar",
      background: "#0f172a",
      color: "#f8fafc",
      confirmButtonColor: "#f59e0b",
    })

    if (!result.isConfirmed) return

    setIsLoading(true)
    
    try {
      await signUp(email, password, displayName)
      
      await Swal.fire({
        title: "Conta Criada!",
        text: "Bem-vindo ao AudioAlert. Sua conta foi criada com sucesso.",
        icon: "success",
        background: "#0f172a",
        color: "#f8fafc",
        confirmButtonColor: "#f59e0b",
      })
      
      router.push("/dashboard")
    } catch (error: unknown) {
      const firebaseError = error as { code?: string }
      let message = "Erro ao criar conta. Tente novamente."
      
      if (firebaseError.code === "auth/email-already-in-use") {
        message = "Este email ja esta em uso."
      } else if (firebaseError.code === "auth/invalid-email") {
        message = "Email invalido."
      } else if (firebaseError.code === "auth/weak-password") {
        message = "Senha muito fraca. Use pelo menos 6 caracteres."
      }
      
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute left-1/4 top-1/4 h-96 w-96 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-primary/5 blur-3xl" />
      </div>
           {/* Mega Wave Background Container - FORÇADO PARA FRENTE E SÓLIDO */}
           <div className="absolute inset-0 z-0 pointer-events-none" aria-hidden="true">
          
          {/* ONDA GIGANTE - ÂMBAR OPACA */}
          <div className="absolute bottom-0 left-0 w-full h-[400px]">
            {/* Onda de Fundo (Ligeiramente mais escura para dar contraste 3D) */}
            <svg 
              className="absolute bottom-0 left-[-50%] w-[200%] h-full animate-mega-wave text-amber-700"
              style={{ animationDuration: '25s', animationDelay: '-5s' }}
              viewBox="0 0 1440 320" 
              preserveAspectRatio="none"
            >
              <path 
                fill="currentColor" 
                d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,224C672,245,768,267,864,250.7C960,235,1056,181,1152,149.3C1248,117,1344,107,1392,101.3L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
              />
            </svg>

            {/* Onda Principal (Âmbar 500 Brilhante e Opaca) */}
            <svg 
              className="absolute bottom-0 left-0 w-[200%] h-[80%] animate-mega-wave text-amber-500"
              viewBox="0 0 1440 320" 
              preserveAspectRatio="none"
            >
              <path 
                fill="currentColor" 
                d="M0,160L48,176C96,192,192,224,288,213.3C384,203,480,149,576,149.3C672,149,768,203,864,218.7C960,235,1056,213,1152,186.7C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
              />
            </svg>
          </div>
        </div>
      <Card className="relative w-full max-w-md border-border bg-card/80 backdrop-blur-sm">
        <CardHeader className="text-center">
          <Link href="/" className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary transition-transform hover:scale-105">
            <AudioWaveform className="h-8 w-8 text-primary-foreground" />
          </Link>
          <CardTitle className="text-2xl font-bold text-foreground">Criar Conta</CardTitle>
          <CardDescription className="text-muted-foreground">
            Comece a monitorar seus equipamentos hoje
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSignup} className="space-y-6">
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="displayName">Nome Completo</FieldLabel>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="displayName"
                    type="text"
                    placeholder="Seu nome"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </Field>
              <Field>
                <FieldLabel htmlFor="email">Email</FieldLabel>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="seu@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </Field>
              <Field>
                <FieldLabel htmlFor="password">Senha</FieldLabel>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Minimo 6 caracteres"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10 pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </Field>
              <Field>
                <FieldLabel htmlFor="confirmPassword">Confirmar Senha</FieldLabel>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="confirmPassword"
                    type={showPassword ? "text" : "password"}
                    placeholder="Repita a senha"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </Field>
            </FieldGroup>

            <div className="flex items-start gap-2">
              <Checkbox
                id="terms"
                checked={acceptTerms}
                onCheckedChange={(checked) => setAcceptTerms(checked === true)}
              />
              <label htmlFor="terms" className="text-sm text-muted-foreground">
                Li e aceito os{" "}
                <Link href="#" className="text-primary hover:underline">
                  Termos de Uso
                </Link>{" "}
                e a{" "}
                <Link href="#" className="text-primary hover:underline">
                  Politica de Privacidade
                </Link>
              </label>
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Spinner className="mr-2 h-4 w-4" />
                  Criando conta...
                </>
              ) : (
                "Criar Conta"
              )}
            </Button>

            <p className="text-center text-sm text-muted-foreground">
              Ja tem conta?{" "}
              <Link href="/login" className="text-primary hover:underline">
                Entrar
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
