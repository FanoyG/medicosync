import { ReactNode } from "react";
import { Link, useLocation } from "wouter";
import {
  LayoutDashboard, Users, Upload, User,
  LogOut, Bell, Moon, Sun, Activity,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { useTheme } from "@/lib/theme";
import { cn } from "@/lib/utils";

const bottomNav = [
  { href: "/dashboard", label: "Home",     icon: LayoutDashboard },
  { href: "/patients",  label: "Patients", icon: Users },
  { href: "/records/upload", label: "Upload",   icon: Upload },
  { href: "/profile",   label: "Profile",  icon: User },
];

const sideNav = [
  { href: "/dashboard",      label: "Dashboard",     icon: LayoutDashboard },
  { href: "/patients",       label: "Patients",      icon: Users },
  { href: "/records/upload", label: "Upload Records",icon: Upload },
];

interface LayoutProps {
  children: ReactNode;
  /** blue gradient top bar content for mobile — optional */
  mobileHeader?: ReactNode;
  title?: string;
}

export default function Layout({ children, mobileHeader, title }: LayoutProps) {
  const [location] = useLocation();
  const { doctorName, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const activeNav = (href: string) =>
    href === "/dashboard"
      ? location === "/dashboard" || location === "/"
      : location.startsWith(href);

  return (
    <div className="flex min-h-screen bg-background">
      {/* ── Desktop sidebar ─────────────────────────────────────── */}
      <aside className="hidden md:flex w-60 flex-shrink-0 flex-col bg-sidebar border-r border-sidebar-border fixed inset-y-0 left-0 z-30">
        {/* Logo */}
        <div className="h-16 flex items-center gap-2.5 px-5 border-b border-sidebar-border">
          <div className="w-8 h-8 rounded-xl bg-primary flex items-center justify-center shadow-sm">
            <Activity className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-[17px] tracking-tight text-foreground">MedicoSync</span>
        </div>

        {/* Nav items */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {sideNav.map(({ href, label, icon: Icon }) => {
            const active = activeNav(href);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-[14px] font-medium transition-all",
                  active
                    ? "bg-primary text-white shadow-sm"
                    : "text-sidebar-foreground hover:bg-accent"
                )}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-sidebar-border">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
              {doctorName ? doctorName[0].toUpperCase() : "D"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-foreground truncate">Dr. {doctorName ?? "Doctor"}</p>
              <p className="text-xs text-muted-foreground">Physician</p>
            </div>
          </div>
          <div className="flex gap-1">
            <button
              onClick={toggleTheme}
              className="flex-1 flex items-center justify-center gap-1.5 px-2 py-1.5 rounded-lg text-xs text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
            >
              {theme === "dark" ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
              {theme === "dark" ? "Light" : "Dark"}
            </button>
            <button
              onClick={logout}
              className="flex items-center justify-center p-1.5 rounded-lg text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main content ────────────────────────────────────────── */}
      <main className="flex-1 md:ml-60 flex flex-col min-h-screen">
        {/* Mobile header — blue top bar */}
        <header className="md:hidden bg-primary text-white">
          {mobileHeader ?? (
            <div className="flex items-center justify-between px-4 pt-3 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center">
                  <Activity className="w-3.5 h-3.5 text-white" />
                </div>
                <span className="font-bold text-base">{title ?? "MedicoSync"}</span>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={toggleTheme} className="w-8 h-8 flex items-center justify-center rounded-full bg-white/15 active:bg-white/30 transition-colors">
                  {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                </button>
                <button className="w-8 h-8 flex items-center justify-center rounded-full bg-white/15 active:bg-white/30 transition-colors relative">
                  <Bell className="w-4 h-4" />
                  <span className="absolute top-1 right-1 w-1.5 h-1.5 bg-red-400 rounded-full" />
                </button>
              </div>
            </div>
          )}
        </header>

        {/* Desktop top bar */}
        <div className="hidden md:flex items-center justify-between px-6 h-14 border-b border-border bg-card/80 backdrop-blur sticky top-0 z-20">
          <h1 className="text-base font-semibold text-foreground">{title ?? "Dashboard"}</h1>
          <div className="flex items-center gap-2">
            <button onClick={toggleTheme} className="p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors">
              {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            <button className="p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors relative">
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-red-400 rounded-full" />
            </button>
            <button
              onClick={logout}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign out
            </button>
          </div>
        </div>

        {/* Page content */}
        <div className="flex-1 pb-20 md:pb-0 page-enter">
          {children}
        </div>

        {/* ── Mobile bottom nav ────────────────────────────────── */}
        <nav className="md:hidden fixed bottom-0 inset-x-0 bg-white dark:bg-card border-t border-border z-40 safe-bottom">
          <div className="flex items-stretch h-16 pb-safe">
            {bottomNav.map(({ href, label, icon: Icon }) => {
              const active = activeNav(href);
              const isUpload = href === "/records/upload";
              if (isUpload) {
                return (
                  <Link
                    key={href}
                    href={href}
                    className="flex-1 flex flex-col items-center justify-center gap-0.5 relative"
                  >
                    <span className={cn(
                      "w-12 h-12 rounded-full flex items-center justify-center shadow-md -mt-4 transition-all",
                      active ? "bg-primary scale-110" : "bg-primary"
                    )}>
                      <Icon className="w-5 h-5 text-white" />
                    </span>
                    <span className={cn(
                      "text-[10px] font-medium mt-0.5",
                      active ? "text-primary" : "text-muted-foreground"
                    )}>{label}</span>
                  </Link>
                );
              }
              return (
                <Link
                  key={href}
                  href={href}
                  className="flex-1 flex flex-col items-center justify-center gap-0.5 transition-colors"
                >
                  <Icon className={cn(
                    "w-5 h-5 transition-colors",
                    active ? "text-primary" : "text-muted-foreground"
                  )} />
                  <span className={cn(
                    "text-[10px] font-medium",
                    active ? "text-primary" : "text-muted-foreground"
                  )}>{label}</span>
                </Link>
              );
            })}
          </div>
        </nav>
      </main>
    </div>
  );
}
