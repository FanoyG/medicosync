import { Link } from "wouter";
import { Activity, Users, Upload, Shield, ArrowRight, CheckCircle, Lock } from "lucide-react";

export default function Landing() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Nav */}
      <header className="bg-primary text-white">
        <div className="max-w-5xl mx-auto px-5 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center">
              <Activity className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold text-base">MedicoSync</span>
          </div>
          <Link href="/login">
            <button className="px-4 py-1.5 bg-white text-primary text-sm font-semibold rounded-full hover:bg-white/90 transition-colors" data-testid="button-signin">
              Sign In
            </button>
          </Link>
        </div>

        {/* Hero inside blue header */}
        <div className="max-w-5xl mx-auto px-5 pt-10 pb-16 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-white/15 rounded-full text-white/90 text-xs font-medium mb-5">
            <CheckCircle className="w-3.5 h-3.5" /> HIPAA-Compliant Medical Platform
          </div>
          <h1 className="text-3xl md:text-5xl font-bold text-white leading-tight mb-4">
            Empower Your Practice<br />with MedicoSync
          </h1>
          <p className="text-white/75 text-base md:text-lg max-w-xl mx-auto mb-8 leading-relaxed">
            Manage patient records, upload documents, and share medical data securely — in one beautiful app.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="/login">
              <button className="px-7 py-3 bg-white text-primary font-bold rounded-full hover:bg-white/90 transition-colors flex items-center gap-2 justify-center" data-testid="button-start-trial">
                Get Started Free <ArrowRight className="w-4 h-4" />
              </button>
            </Link>
            <Link href="/login">
              <button className="px-7 py-3 bg-white/15 text-white font-semibold rounded-full hover:bg-white/25 transition-colors justify-center">
                Sign In
              </button>
            </Link>
          </div>
        </div>
      </header>

      {/* Stats */}
      <div className="max-w-5xl mx-auto px-5 -mt-6 w-full">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { v: "10,000+", l: "Active doctors" },
            { v: "2M+",     l: "Records stored" },
            { v: "99.9%",   l: "Uptime SLA" },
            { v: "HIPAA",   l: "Compliant" },
          ].map(({ v, l }) => (
            <div key={l} className="bg-card rounded-2xl border border-border p-4 text-center shadow-sm">
              <p className="text-xl font-bold text-primary">{v}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{l}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Features */}
      <div className="max-w-5xl mx-auto px-5 py-12 w-full">
        <h2 className="text-xl font-bold text-foreground mb-5">Everything for a modern practice</h2>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
          {[
            { icon: Users, title: "Patient Management", desc: "Searchable database with full patient profiles and history.", color: "bg-blue-50 text-blue-600" },
            { icon: Upload, title: "Record Uploads", desc: "Drag-and-drop for lab results, X-rays, visit notes.", color: "bg-green-50 text-green-600" },
            { icon: Shield, title: "Secure Sharing", desc: "Time-limited, code-protected links for sharing records.", color: "bg-purple-50 text-purple-600" },
            { icon: Lock, title: "HIPAA Compliant", desc: "Built to the highest healthcare privacy standards.", color: "bg-orange-50 text-orange-600" },
          ].map(({ icon: Icon, title, desc, color }) => (
            <div key={title} className="bg-card rounded-2xl border border-border p-5 hover:shadow-md transition-shadow">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${color}`}>
                <Icon className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-foreground text-sm mb-1">{title}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="bg-primary mt-auto">
        <div className="max-w-5xl mx-auto px-5 py-12 text-center">
          <h2 className="text-xl font-bold text-white mb-2">Ready to get started?</h2>
          <p className="text-white/70 text-sm mb-6 max-w-sm mx-auto">
            Join thousands of doctors already using MedicoSync.
          </p>
          <Link href="/login">
            <button className="px-7 py-3 bg-white text-primary font-bold rounded-full hover:bg-white/90 transition-colors inline-flex items-center gap-2">
              Start Free Trial <ArrowRight className="w-4 h-4" />
            </button>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-5 px-5">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
              <Activity className="w-3 h-3 text-white" />
            </div>
            <span className="font-bold text-sm">MedicoSync</span>
          </div>
          <p className="text-xs text-muted-foreground">© 2024 MedicoSync. HIPAA Compliant.</p>
        </div>
      </footer>
    </div>
  );
}
