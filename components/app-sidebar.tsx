"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import {
  LayoutDashboard,
  Smartphone,
  Radio,
  History,
  Settings,
  AudioWaveform,
  LogOut,
  User,
  FlaskConical,
} from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { useAuth } from "@/contexts/auth-context"
import { toast } from "sonner"
import Swal from "sweetalert2"

const navItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "AudioAlert Pocket",
    href: "/dashboard/pocket",
    icon: Smartphone,
  },
  {
    title: "AudioAlert Node",
    href: "/dashboard/node",
    icon: Radio,
  },
  {
    title: "Historico de Anomalias",
    href: "/dashboard/history",
    icon: History,
  },
  {
    title: "Configuracoes",
    href: "/dashboard/settings",
    icon: Settings,
  },
  {
    title: "Como Funciona",
    href: "/dashboard/experimentos",
    icon: FlaskConical,
  },
]

export function AppSidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    const result = await Swal.fire({
      title: "Sair do Sistema",
      text: "Tem certeza que deseja encerrar sua sessao?",
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Sim, sair",
      cancelButtonText: "Cancelar",
      background: "#0f172a",
      color: "#f8fafc",
      confirmButtonColor: "#f59e0b",
      cancelButtonColor: "#475569",
    })

    if (result.isConfirmed) {
      try {
        await logout()
        toast.success("Sessao encerrada com sucesso!")
        router.push("/")
      } catch {
        toast.error("Erro ao encerrar sessao.")
      }
    }
  }

  const getInitials = (name: string | null) => {
    if (!name) return "U"
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <Sidebar>
      <SidebarHeader className="border-b border-sidebar-border px-6 py-4">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
            <AudioWaveform className="h-6 w-6 text-primary-foreground" />
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-bold text-sidebar-foreground">AudioAlert</span>
            <span className="text-xs text-muted-foreground">Industrial IoT</span>
          </div>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="text-muted-foreground">Navegacao</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => {
                const isActive = pathname === item.href || 
                  (item.href !== "/dashboard" && pathname.startsWith(item.href))
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton asChild isActive={isActive}>
                      <Link href={item.href}>
                        <item.icon className="h-5 w-5" />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="border-t border-sidebar-border p-4">
        <Link 
          href="/dashboard/profile"
          className="mb-3 flex items-center gap-3 rounded-lg bg-sidebar-accent/50 p-3 transition-colors hover:bg-sidebar-accent"
        >
          <Avatar className="h-9 w-9">
            <AvatarFallback className="bg-primary text-primary-foreground text-sm">
              {user ? getInitials(user.displayName) : <User className="h-4 w-4" />}
            </AvatarFallback>
          </Avatar>
          <div className="flex flex-col overflow-hidden">
            <span className="truncate text-sm font-medium text-sidebar-foreground">
              {user?.displayName || "Usuario"}
            </span>
            <span className="truncate text-xs text-muted-foreground">
              {user?.email || "email@exemplo.com"}
            </span>
          </div>
        </Link>
        <Button 
          variant="ghost" 
          className="w-full justify-start gap-2 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
          onClick={handleLogout}
        >
          <LogOut className="h-4 w-4" />
          <span>Sair</span>
        </Button>
      </SidebarFooter>
    </Sidebar>
  )
}
