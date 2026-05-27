import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Eye, EyeOff, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

const signupSchema = z.object({
  name: z.string().min(2, "At least 2 characters"),
  email: z.string().email("Enter a valid email"),
  password: z.string().min(6, "Min. 6 characters"),
});

type LoginData = z.infer<typeof loginSchema>;
type SignupData = z.infer<typeof signupSchema>;

export default function Login() {
  const [tab, setTab] = useState<"login" | "signup">("login");
  const [showPw, setShowPw] = useState(false);
  const { login, signup, error: apiError, clearError } = useAuth();

  const loginForm = useForm<LoginData>({ resolver: zodResolver(loginSchema) });
  const signupForm = useForm<SignupData>({ resolver: zodResolver(signupSchema) });

  const onLogin = async (data: LoginData) => {
    try {
      await login(data.email, data.password);
    } catch (err) {
      console.error(err);
    }
  };

  const onSignup = async (data: SignupData) => {
    try {
      await signup(data.name, data.email, data.password);
    } catch (err) {
      console.error(err);
    }
  };

  const handleTabChange = (newTab: "login" | "signup") => {
    setTab(newTab);
    setShowPw(false);
    clearError();
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center px-4 py-10">
      <div className="flex flex-col items-center mb-8">
        <div className="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center shadow-lg mb-3">
          <Activity className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-foreground tracking-tight">MedicoSync</h1>
        <p className="text-sm text-muted-foreground mt-1">Medical Records Platform</p>
      </div>

      <div className="w-full max-w-sm bg-card rounded-2xl shadow-sm border border-border overflow-hidden">
        <div className="flex border-b border-border">
          {(["login", "signup"] as const).map(t => (
            <button
              key={t}
              type="button"
              onClick={() => handleTabChange(t)}
              className={cn(
                "flex-1 py-3.5 text-sm font-semibold transition-all",
                tab === t ? "text-primary border-b-2 border-primary bg-primary/5" : "text-muted-foreground hover:text-foreground"
              )}
            >
              {t === "login" ? "Login" : "Sign Up"}
            </button>
          ))}
        </div>

        <div className="p-6">
          {apiError && (
            <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-xl text-xs font-medium text-center">
              {apiError}
            </div>
          )}

          {tab === "login" ? (
            <form onSubmit={loginForm.handleSubmit(onLogin)} className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Email</label>
                <Input type="email" placeholder="dr.chen@hospital.com" {...loginForm.register("email")} />
                {loginForm.formState.errors.email && <p className="text-xs text-destructive">{loginForm.formState.errors.email.message}</p>}
              </div>
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Password</label>
                  <button type="button" className="text-xs text-primary hover:underline">Forgot Password?</button>
                </div>
                <div className="relative">
                  <Input type={showPw ? "text" : "password"} placeholder="••••••••" className="bg-background pr-10" {...loginForm.register("password")} />
                  <button type="button" onClick={() => setShowPw(v => !v)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                    {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {loginForm.formState.errors.password && <p className="text-xs text-destructive">{loginForm.formState.errors.password.message}</p>}
              </div>
              <Button type="submit" className="w-full rounded-xl h-11 font-semibold text-base mt-2" disabled={loginForm.formState.isSubmitting}>
                {loginForm.formState.isSubmitting ? "Logging in..." : "Login"}
              </Button>
            </form>
          ) : (
            <form onSubmit={signupForm.handleSubmit(onSignup)} className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Name</label>
                <Input type="text" placeholder="Dr. Jane Smith" {...signupForm.register("name")} />
                {signupForm.formState.errors.name && <p className="text-xs text-destructive">{signupForm.formState.errors.name.message}</p>}
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Email</label>
                <Input type="email" placeholder="dr.smith@hospital.com" {...signupForm.register("email")} />
                {signupForm.formState.errors.email && <p className="text-xs text-destructive">{signupForm.formState.errors.email.message}</p>}
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Password</label>
                <div className="relative">
                  <Input type={showPw ? "text" : "password"} placeholder="Min. 6 characters" className="bg-background pr-10" {...signupForm.register("password")} />
                  <button type="button" onClick={() => setShowPw(v => !v)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                    {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {signupForm.formState.errors.password && <p className="text-xs text-destructive">{signupForm.formState.errors.password.message}</p>}
              </div>
              <Button type="submit" className="w-full rounded-xl h-11 font-semibold text-base mt-2" disabled={signupForm.formState.isSubmitting}>
                {signupForm.formState.isSubmitting ? "Creating..." : "Create Account"}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
