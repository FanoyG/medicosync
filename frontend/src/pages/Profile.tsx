import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/lib/auth";
import { useTheme } from "@/lib/theme";
import { LogOut, Moon, Sun, Bell, Lock, HelpCircle, ChevronRight, User } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Profile() {
  const { doctorName, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const sections = [
    {
      title: "Account",
      items: [
        { icon: User, label: "Edit Profile", onClick: () => {} },
        { icon: Bell, label: "Notifications", onClick: () => {} },
        { icon: Lock, label: "Privacy & Security", onClick: () => {} },
      ],
    },
    {
      title: "Preferences",
      items: [
        {
          icon: theme === "dark" ? Sun : Moon,
          label: theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode",
          onClick: toggleTheme,
        },
      ],
    },
    {
      title: "Support",
      items: [
        { icon: HelpCircle, label: "Help & Support", onClick: () => {} },
      ],
    },
  ];

  const mobileHeader = (
    <div className="px-4 pt-4 pb-6 flex flex-col items-center">
      <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center text-white text-2xl font-bold mb-3">
        {doctorName ? doctorName[0].toUpperCase() : "D"}
      </div>
      <h1 className="text-white text-lg font-bold">Dr. {doctorName ?? "Doctor"}</h1>
      <p className="text-white/70 text-sm">Physician · MedicoSync</p>
    </div>
  );

  return (
    <ProtectedRoute>
      <Layout title="Profile" mobileHeader={mobileHeader}>
        <div className="max-w-lg mx-auto px-4 pt-4 pb-6 space-y-4">
          {/* Desktop profile card */}
          <div className="hidden md:flex items-center gap-4 bg-card rounded-2xl border border-border p-5">
            <div className="w-14 h-14 rounded-full bg-primary flex items-center justify-center text-white text-xl font-bold flex-shrink-0">
              {doctorName ? doctorName[0].toUpperCase() : "D"}
            </div>
            <div>
              <h2 className="text-lg font-bold text-foreground">Dr. {doctorName ?? "Doctor"}</h2>
              <p className="text-sm text-muted-foreground">Physician · MedicoSync</p>
            </div>
          </div>

          {sections.map(({ title, items }) => (
            <div key={title} className="bg-card rounded-2xl border border-border overflow-hidden">
              <p className="px-4 pt-3 pb-1 text-xs font-semibold text-muted-foreground uppercase tracking-wide">{title}</p>
              <div className="divide-y divide-border">
                {items.map(({ icon: Icon, label, onClick }) => (
                  <button
                    key={label}
                    onClick={onClick}
                    className="w-full flex items-center gap-3 px-4 py-3.5 hover:bg-muted/50 active:bg-muted transition-colors"
                  >
                    <div className="w-8 h-8 rounded-xl bg-muted flex items-center justify-center flex-shrink-0">
                      <Icon className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <span className="text-sm font-medium text-foreground flex-1 text-left">{label}</span>
                    <ChevronRight className="w-4 h-4 text-muted-foreground" />
                  </button>
                ))}
              </div>
            </div>
          ))}

          {/* Sign out */}
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-4 py-4 bg-card rounded-2xl border border-destructive/20 hover:bg-destructive/5 active:bg-destructive/10 transition-colors"
            data-testid="button-logout"
          >
            <div className="w-8 h-8 rounded-xl bg-destructive/10 flex items-center justify-center flex-shrink-0">
              <LogOut className="w-4 h-4 text-destructive" />
            </div>
            <span className="text-sm font-semibold text-destructive flex-1 text-left">Sign Out</span>
          </button>
        </div>
      </Layout>
    </ProtectedRoute>
  );
}
