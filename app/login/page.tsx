"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { AudioWaveform, Mail, Lock, Eye, EyeOff } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Spinner } from "@/components/ui/spinner"
import { useAuth } from "@/contexts/auth-context"
import { toast } from "sonner"
import Swal from "sweetalert2"

export default function LoginPage() {
  const router = useRouter()
  const { signIn, resetPassword } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      await signIn(email, password)
      toast.success("Login realizado com sucesso!")
      router.push("/dashboard")
    } catch (error: unknown) {
      const firebaseError = error as { code?: string }
      let message = "Erro ao realizar login. Tente novamente."
      
      if (firebaseError.code === "auth/user-not-found") {
        message = "Usuario nao encontrado."
      } else if (firebaseError.code === "auth/wrong-password") {
        message = "Senha incorreta."
      } else if (firebaseError.code === "auth/invalid-email") {
        message = "Email invalido."
      } else if (firebaseError.code === "auth/too-many-requests") {
        message = "Muitas tentativas. Tente novamente mais tarde."
      }
      
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleForgotPassword = async () => {
    const result = await Swal.fire({
      title: "Recuperar Senha",
      text: "Digite seu email para receber o link de recuperacao:",
      input: "email",
      inputPlaceholder: "seu@email.com",
      showCancelButton: true,
      confirmButtonText: "Enviar",
      cancelButtonText: "Cancelar",
      background: "#0f172a",
      color: "#f8fafc",
      confirmButtonColor: "#f59e0b",
      inputValidator: (value) => {
        if (!value) {
          return "Por favor, digite seu email"
        }
        return null
      },
    })

    if (result.isConfirmed && result.value) {
      try {
        await resetPassword(result.value)
        await Swal.fire({
          title: "Email Enviado!",
          text: "Verifique sua caixa de entrada para redefinir sua senha.",
          icon: "success",
          background: "#0f172a",
          color: "#f8fafc",
          confirmButtonColor: "#f59e0b",
        })
      } catch {
        toast.error("Erro ao enviar email de recuperacao.")
      }
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
          <CardTitle className="text-2xl font-bold text-foreground">Entrar no AudioAlert</CardTitle>
          <CardDescription className="text-muted-foreground">
            Sistema Industrial de Monitoramento por Audio
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-6">
            <FieldGroup>
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
                    placeholder="Digite sua senha"
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
            </FieldGroup>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Spinner className="mr-2 h-4 w-4" />
                  Entrando...
                </>
              ) : (
                "Entrar"
              )}
            </Button>

            <div className="space-y-2 text-center text-sm">
              <button
                type="button"
                onClick={handleForgotPassword}
                className="text-primary hover:underline"
              >
                Esqueceu sua senha?
              </button>
              <p className="text-muted-foreground">
                Nao tem conta?{" "}
                <Link href="/signup" className="text-primary hover:underline">
                  Cadastre-se
                </Link>
              </p>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
