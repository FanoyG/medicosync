import { useState } from "react";
import { useRoute } from "wouter";
import { Activity, Shield, FileText, Download, FlaskConical, Scan, StickyNote, AlertCircle, CheckCircle, RotateCcw } from "lucide-react";
import { useVerifyShareToken, useResendShareOtp, SharedRecordAccess } from "@/lib/apiClient";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

const catIcon: Record<string, React.ElementType> = {
  lab: FlaskConical, xray: Scan, visit: StickyNote, image: FileText, other: FileText,
};
const catLabel: Record<string, string> = {
  lab: "Lab Result", xray: "X-Ray", visit: "Visit Note", image: "Image", other: "Other",
};

export default function ShareAccess() {
  const [, params] = useRoute("/share/access/:token");
  const token = params?.token ?? "";
  const [code, setCode] = useState("");
  const [verifiedData, setVerifiedData] = useState<SharedRecordAccess | null>(null);
  const [error, setError] = useState("");

  const verify = useVerifyShareToken();
  const resend = useResendShareOtp();
  const [resendCooldown, setResendCooldown] = useState(0);

  const handleVerify = () => {
    setError("");
    verify.mutate(
      { data: { token, verificationCode: code } },
      {
        onSuccess: (data) => { 
          setVerifiedData(data);
        },
        onError: (err: any) => setError(err.message || "Invalid verification code. Please check and try again."),
      }
    );
  };

  const handleResendOtp = () => {
    setError("");
    setResendCooldown(120);
    const timer = setInterval(() => {
      setResendCooldown(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    resend.mutate(
      { data: { token } },
      {
        onSuccess: () => {
          setCode("");
        },
        onError: (err: any) => setError(err.message || "Failed to resend code. Please try again."),
      }
    );
  };

  const activeDisplayData = verifiedData;
  const IconComponent = activeDisplayData ? (catIcon[activeDisplayData.recordType] || FileText) : FileText;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header bar */}
      <header className="bg-primary text-white">
        <div className="max-w-lg mx-auto w-full px-4 pt-4 pb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center">
                <Activity className="w-3.5 h-3.5 text-white" />
              </div>
              <span className="font-bold text-base">MedicoSync</span>
            </div>
            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-white/15 rounded-full text-xs font-medium">
              <Shield className="w-3 h-3" /> Secure Gate
            </div>
          </div>
          <h1 className="text-lg font-bold">Secure Access Verification</h1>
          <h2 className="text-sm font-medium text-white/80 mt-0.5">
            {activeDisplayData ? `Verified Request: File from ${activeDisplayData.doctorName}` : "Verify Identity Verification Matrix"}
          </h2>
        </div>
      </header>

      <div className="flex-1 max-w-lg mx-auto w-full px-4 -mt-3 pb-12">
        {!verifiedData ? (
          <div className="bg-card rounded-2xl border border-border p-5 shadow-sm space-y-4">
            <div>
              <p className="text-sm font-semibold text-foreground">Verification Code Required</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                Please enter the 6-digit secure access passcode provided to authorize this medical record download.
              </p>
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                inputMode="numeric"
                maxLength={6}
                placeholder="000000"
                value={code}
                onChange={e => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                className="flex-1 h-11 px-4 bg-background rounded-xl border border-border text-center text-lg font-mono tracking-widest outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                data-testid="input-verification-code"
              />
              <Button
                onClick={handleVerify}
                disabled={code.length !== 6 || verify.isPending}
                className="h-11 px-5 rounded-xl font-medium text-sm"
                data-testid="button-verify"
              >
                {verify.isPending ? "Validating..." : "Verify Code"}
              </Button>
            </div>
            
            {error && (
              <p className="text-xs text-destructive flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5" /> {error}
              </p>
            )}
            
            <button
              type="button"
              onClick={handleResendOtp}
              disabled={resendCooldown > 0 || resend.isPending}
              className="w-full text-xs text-primary hover:underline font-medium disabled:text-muted-foreground transition-colors"
              data-testid="button-resend-otp"
            >
              {resendCooldown > 0 ? (
                <span className="flex items-center justify-center gap-1">
                  <RotateCcw className="w-3 h-3" /> Resend Code ({resendCooldown}s)
                </span>
              ) : (
                <span className="flex items-center justify-center gap-1">
                  <RotateCcw className="w-3 h-3" /> {resend.isPending ? "Sending..." : "Resend Code"}
                </span>
              )}
            </button>
          </div>
        ) : (
          <div className="space-y-4 pt-2">
            {/* Pacient status badge row */}
            <div className="bg-card rounded-2xl border border-border p-4 shadow-sm">
              <h3 className="text-sm font-bold text-foreground">Verified Document Record</h3>
              <p className="text-xs text-muted-foreground mt-0.5">Origin practitioner: <span className="font-semibold text-primary">{verifiedData.doctorName}</span></p>
            </div>

            {/* Document list render module */}
            <div className="bg-card rounded-2xl border border-border overflow-hidden shadow-sm">
              <div className="px-4 py-3 border-b border-border bg-muted/20">
                <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wide">Available Records List</h4>
              </div>
              
              <div className="p-4 flex items-center justify-between gap-4 bg-background border-b border-border" data-testid="card-shared-record-main">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-xl bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center flex-shrink-0">
                    <IconComponent className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <p className="text-sm font-semibold text-foreground truncate">{verifiedData.recordTitle}</p>
                      <span className="text-[10px] font-medium text-green-600 bg-green-50 dark:bg-green-900/20 px-1.5 py-0.5 rounded-full">
                        Verified
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground capitalize">{catLabel[verifiedData.recordType] || "Medical File"}</p>
                  </div>
                </div>

                <div className="flex gap-1.5 flex-shrink-0">
                  <a href={verifiedData.downloadUrl} target="_blank" rel="noreferrer" className="text-xs text-primary hover:underline font-medium" data-testid="button-download-link">
                    Download
                  </a>
                  <span className="text-muted-foreground text-xs">/</span>
                  <a href={verifiedData.downloadUrl} target="_blank" rel="noreferrer" className="text-xs text-primary hover:underline font-medium">
                    View
                  </a>
                </div>
              </div>

              <div className="px-4 py-3 bg-muted/30">
                <p className="text-xs text-muted-foreground text-center">
                  Sharing session is encrypted and secure.
                </p>
              </div>
            </div>

            {/* Access pill indicator check confirmation panel */}
            <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
              <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
              <p className="text-xs text-green-700 dark:text-green-400">
                Access verified securely. Revokes automatically on: {new Date(verifiedData.expiresAt).toLocaleDateString()}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
