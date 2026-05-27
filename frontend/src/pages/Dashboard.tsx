import { Link } from "wouter";
import { UserPlus, Upload, MessageSquare, ChevronRight, Bell } from "lucide-react";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/lib/auth";
import { useGetDashboardStats, useListPatients } from "@/lib/apiClient";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

const quickAccess = [
  { href: "/patients",       icon: UserPlus,      label: "Add Patient",     color: "bg-blue-100 text-blue-600 dark:bg-blue-900/40" },
  { href: "/records/upload", icon: Upload,        label: "Upload Records",  color: "bg-green-100 text-green-600 dark:bg-green-900/40" },
  { href: "/share",          icon: MessageSquare, label: "Chat",            color: "bg-purple-100 text-purple-600 dark:bg-purple-900/40" },
];

function StatPill({ label, value, active, onClick }: { label: string; value?: number; active?: boolean; onClick?: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex-1 flex flex-col items-center px-2 py-2 rounded-xl text-center transition-all",
        active ? "bg-white text-primary shadow-sm" : "bg-white/20 text-white/80"
      )}
    >
      <span className={cn("text-lg font-bold", active ? "text-primary" : "text-white")}>
        {value ?? "—"}
      </span>
      <span className="text-[10px] font-medium leading-tight mt-0.5 whitespace-nowrap">{label}</span>
    </button>
  );
}

export default function Dashboard() {
  const { doctorName } = useAuth();
  const { data: stats, isLoading: statsLoading } = useGetDashboardStats();
  const { data: patients, isLoading: patientsLoading } = useListPatients();

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good Morning" : hour < 17 ? "Good Afternoon" : "Good Evening";

  const mobileHeader = (
    <div className="px-4 pt-4 pb-5">
      {/* Top row */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-white/80 text-sm font-medium">{greeting},</p>
          <h1 className="text-white text-xl font-bold leading-tight">
            Dr. {doctorName ?? "Doctor"}!
          </h1>
        </div>
        <button className="w-9 h-9 flex items-center justify-center rounded-full bg-white/20 relative">
          <Bell className="w-4.5 h-4.5 text-white" />
          <span className="absolute top-1 right-1 w-1.5 h-1.5 bg-red-400 rounded-full" />
        </button>
      </div>
      {/* Stat pills — Fixed parameter targets */}
      <div className="flex gap-2">
        <StatPill label="Total Patients"         value={stats?.totalPatients ?? 0} active />
        <StatPill label="Active Shares"          value={stats?.activeShares ?? 0} />
        <StatPill label="Total Records"          value={stats?.totalRecords ?? 0} />
      </div>
    </div>
  );

  return (
    <ProtectedRoute>
      <Layout title="Dashboard" mobileHeader={mobileHeader}>
        <div className="max-w-2xl mx-auto w-full">
          {/* Desktop greeting */}
          <div className="hidden md:block px-6 pt-6 pb-2">
            <h2 className="text-xl font-bold text-foreground">
              {greeting}, Dr. {doctorName ?? "Doctor"}! 👋
            </h2>
            <p className="text-sm text-muted-foreground mt-0.5">Here's what's happening today.</p>
          </div>

          {/* Desktop stats — Fixed mapped labels and parameter keys */}
          <div className="hidden md:grid grid-cols-3 gap-4 px-6 py-4">
            {[
              { label: "Total Patients", value: stats?.totalPatients ?? 0 },
              { label: "Active Shares",  value: stats?.activeShares ?? 0 },
              { label: "Total Records",  value: stats?.totalRecords ?? 0 },
            ].map(({ label, value }) => (
              <div key={label} className="bg-card rounded-xl p-4 border border-border text-center">
                <p className="text-2xl font-bold text-primary">{statsLoading ? "—" : value}</p>
                <p className="text-xs text-muted-foreground mt-1">{label}</p>
              </div>
            ))}
          </div>

          {/* Search bar */}
          <div className="px-4 py-3">
            <div className="relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
              </svg>
              <input
                type="search"
                placeholder="Search"
                className="w-full h-10 pl-9 pr-4 bg-card rounded-xl border border-border text-sm outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
                data-testid="input-search"
              />
            </div>
          </div>

          {/* Quick Access */}
          <div className="px-4 pb-4">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">Quick Access</p>
            <div className="grid grid-cols-3 gap-3">
              {quickAccess.map(({ href, icon: Icon, label, color }) => (
                <Link
                  key={href}
                  href={href}
                  className="flex flex-col items-center gap-2 p-4 bg-card rounded-2xl border border-border active:scale-95 hover:shadow-sm transition-all"
                  data-testid={`quick-${label.toLowerCase().replace(/ /g, "-")}`}
                >
                  <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center", color)}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-medium text-center leading-tight text-foreground">{label}</span>
                </Link>
              ))}
            </div>
          </div>

          {/* My Patients */}
          <div className="px-4 pb-4">
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">My Patients</p>
              <Link href="/patients" className="text-xs text-primary font-medium">See all</Link>
            </div>

            <div className="space-y-2">
              {patientsLoading ? (
                [1, 2, 3].map(i => (
                  <div key={i} className="flex items-center gap-3 p-3 bg-card rounded-xl border border-border">
                    <Skeleton className="w-10 h-10 rounded-full flex-shrink-0" />
                    <div className="flex-1">
                      <Skeleton className="h-4 w-32 mb-1.5" />
                      <Skeleton className="h-3 w-20" />
                    </div>
                  </div>
                ))
              ) : patients && patients.length > 0 ? (
                patients.slice(0, 5).map(p => (
                  <Link
                    key={p.id}
                    href={`/patients/${p.id}`}
                    className="flex items-center gap-3 p-3 bg-card rounded-xl border border-border active:bg-muted hover:shadow-sm transition-all group"
                    data-testid={`patient-row-${p.id}`}
                  >
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold text-sm flex-shrink-0">
                      {p.firstName?.[0] || ""}{p.lastName?.[0] || ""}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-foreground">{p.firstName} {p.lastName}</p>
                      <p className="text-xs text-muted-foreground capitalize">{p.gender}</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors flex-shrink-0" />
                  </Link>
                ))
              ) : (
                <div className="py-8 text-center bg-card rounded-xl border border-border">
                  <p className="text-muted-foreground text-sm">No patients yet</p>
                  <Link href="/patients" className="mt-2 inline-block text-primary text-sm font-medium">Add first patient →</Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  );
}
