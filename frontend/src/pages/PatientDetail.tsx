import { useState } from "react";
import { useRoute, useLocation, Link } from "wouter";
import {
  ArrowLeft, FileText, FlaskConical, Scan, StickyNote,
  Share2, X, Download
} from "lucide-react";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";
import {
  useGetPatient,
  useListPatientRecords,
  useSharePatientRecords,
  useDeletePatient,
  MedicalRecord,
} from "@/lib/apiClient"; // Imported MedicalRecord type explicitly
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { differenceInYears } from "date-fns";
import { cn } from "@/lib/utils";

const catIcon: Record<string, React.ElementType> = {
  lab: FlaskConical, xray: Scan, visit: StickyNote, image: FileText, other: FileText,
};
const catLabel: Record<string, string> = {
  lab: "Lab Result", xray: "X-Ray", visit: "Visit Note", image: "Image", other: "Other",
};
const catColor: Record<string, string> = {
  lab: "bg-blue-50 text-blue-600 dark:bg-blue-900/30",
  xray: "bg-purple-50 text-purple-600 dark:bg-purple-900/30",
  visit: "bg-green-50 text-green-600 dark:bg-green-900/30",
  image: "bg-yellow-50 text-yellow-600 dark:bg-yellow-900/30",
  other: "bg-gray-50 text-gray-500 dark:bg-gray-800",
};

type PageTab = "profile" | "records";

export default function PatientDetail() {
  const [, params] = useRoute("/patients/:id");
  const patientId = params?.id ?? ""; 
  const [pageTab, setPageTab] = useState<PageTab>("records");
  const [showShare, setShowShare] = useState(false);
  const [selectedRecId, setSelectedRecId] = useState<string | null>(null);
  const [shareHours, setShareHours] = useState("24");
  const [generatedLink, setGeneratedLink] = useState<{ token: string; otp: string } | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { data: patient, isLoading: pl } = useGetPatient(patientId);
  const { data: records, isLoading: rl } = useListPatientRecords(patientId); // Fixed to use the corrected re-added hook

  const shareM = useSharePatientRecords();
  const deletePatient = useDeletePatient();
  const { toast } = useToast();
  const [, setLocation] = useLocation();

  const doShare = () => {
    if (!selectedRecId) return;
    shareM.mutate(
      { data: { recordId: selectedRecId, expiresInHours: parseInt(shareHours, 10) } },
      {
        onSuccess: (res) => {
          setGeneratedLink({ token: res.token, otp: res.plainOtpCode || "XXXXXX" });
          toast({ title: "Secure Link Generated Successfully!" });
        },
        onError: (err) => toast({ title: "Error sharing record", description: err.message, variant: "destructive" }),
      }
    );
  };

  const handleEdit = () => {
    if (patientId) {
      setLocation(`/patients/${patientId}/edit`);
    }
  };

  const handleDelete = () => {
    if (!patientId) return;
    setShowDeleteConfirm(true);
  };

  const confirmDelete = () => {
    if (!patientId) return;
    setShowDeleteConfirm(false);

    deletePatient.mutate(patientId, {
      onSuccess: () => {
        toast({ title: "Patient deleted successfully." });
        setLocation("/patients");
      },
      onError: (err) =>
        toast({
          title: "Unable to delete patient",
          description: err.message,
          variant: "destructive",
        }),
    });
  };

  const age = patient ? differenceInYears(new Date(), new Date(patient.dateOfBirth)) : null;

  const desktopTabControls = (
    <div className="hidden md:flex items-center justify-between gap-3 mb-4">
      <div className="inline-flex rounded-full border border-border bg-background p-1">
        {(["profile", "records"] as const).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setPageTab(t)}
            className={cn(
              "px-4 py-2 rounded-full text-sm font-semibold capitalize transition-all whitespace-nowrap",
              pageTab === t
                ? "bg-primary text-white"
                : "text-foreground/80 hover:text-foreground",
            )}
          >
            {t}
          </button>
        ))}
      </div>
      <Button
        variant="outline"
        onClick={handleEdit}
        className="h-10 rounded-full"
      >
        Edit
      </Button>
    </div>
  );

  const mobileHeader = (
    <div className="px-4 pt-3 pb-0">
      <div className="flex items-center gap-3 mb-4">
        <Link href="/patients">
          <button type="button" className="w-8 h-8 flex items-center justify-center rounded-full bg-white/20">
            <ArrowLeft className="w-4 h-4 text-white" />
          </button>
        </Link>
        <span className="text-white text-base font-semibold">
          {patient ? `${patient.firstName} ${patient.lastName}` : "Patient"}
        </span>
      </div>

      <div className="flex flex-col items-center pb-5">
        <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center text-white text-xl font-bold mb-2">
          {patient ? `${patient.firstName[0]}${patient.lastName[0]}` : "??"}
        </div>
        <h2 className="text-white font-bold text-lg">
          {patient ? `${patient.firstName} ${patient.lastName}` : <Skeleton className="h-5 w-32 bg-white/20" />}
        </h2>
        <p className="text-white/70 text-sm capitalize">
          {patient ? `${patient.gender}, Age ${age}` : ""}
        </p>

        <div className="flex gap-1 mt-4 bg-white/15 rounded-full p-1">
          {(["profile", "records"] as const).map(t => (
            <button
              key={t}
              type="button"
              onClick={() => setPageTab(t)}
              className={cn(
                "px-4 py-1 rounded-full text-xs font-semibold capitalize transition-all",
                pageTab === t ? "bg-white text-primary" : "text-white/80 hover:text-white"
              )}
            >
              {t}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <ProtectedRoute>
      <Layout title="Patient" mobileHeader={mobileHeader}>
        <div className="max-w-2xl mx-auto w-full px-4 pt-4 pb-12">
          {desktopTabControls}

          {pageTab === "profile" && (
            <div className="space-y-3">
              {pl ? (
                <Skeleton className="h-32 rounded-2xl" />
              ) : (
                patient && (
                  <div className="bg-card rounded-2xl border border-border p-4">
                    <div className="grid grid-cols-2 gap-x-6 gap-y-4">
                      <div>
                        <span className="text-xs text-muted-foreground block font-medium uppercase">
                          Full Name
                        </span>
                        <span className="text-sm font-semibold text-foreground">
                          {patient.firstName} {patient.lastName}
                        </span>
                      </div>
                      <div>
                        <span className="text-xs text-muted-foreground block font-medium uppercase">
                          Gender Identity
                        </span>
                        <span className="text-sm font-medium text-foreground capitalize">
                          {patient.gender}
                        </span>
                      </div>
                      <div>
                        <span className="text-xs text-muted-foreground block font-medium uppercase">
                          Date of Birth
                        </span>
                        <span className="text-sm font-medium text-foreground">
                          {patient.dateOfBirth}
                        </span>
                      </div>
                      {patient.bloodGroup && (
                        <div>
                          <span className="text-xs text-muted-foreground block font-medium uppercase">
                            Blood Group
                          </span>
                          <span className="text-sm font-medium text-foreground capitalize">
                            {patient.bloodGroup}
                          </span>
                        </div>
                      )}
                      {patient.phoneNumber && (
                        <div>
                          <span className="text-xs text-muted-foreground block font-medium uppercase">
                            Contact Number
                          </span>
                          <span className="text-sm font-medium text-foreground">
                            {patient.phoneNumber}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )
              )}
            </div>
          )}

          {pageTab === "records" && (
            <div className="space-y-2">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                Medical Records Directory
              </h3>
              {rl ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full rounded-xl" />
                ))
              ) : records && records.length > 0 ? (
                <div className="flex flex-col gap-3">
                  {records.map((r: MedicalRecord) => {
                    const Icon = catIcon[r.recordType] || FileText;
                    return (
                      <div
                        key={r.id}
                        className="flex items-center justify-between p-3 bg-card border border-border rounded-xl"
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={cn(
                              "w-9 h-9 rounded-lg flex items-center justify-center",
                              catColor[r.recordType],
                            )}
                          >
                            <Icon className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-foreground">
                              {r.title}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {catLabel[r.recordType] || "Record"}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setSelectedRecId(r.id);
                              setShowShare(true);
                              setGeneratedLink(null);
                            }}
                            className="h-8 text-xs gap-1 rounded-lg"
                          >
                            <Share2 className="w-3 h-3" /> Share
                          </Button>
                          <a
                            href={r.downloadUrl}
                            target="_blank"
                            rel="noreferrer"
                          >
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-8 w-8 p-0 rounded-lg"
                            >
                              <Download className="w-3.5 h-3.5" />
                            </Button>
                          </a>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="py-12 text-center text-sm text-muted-foreground bg-card rounded-xl border border-border">
                  No medical record objects found for this client profile.
                </div>
              )}
            </div>
          )}

          <div className="space-y-3 mt-4">
            <div className="grid grid-cols-2 gap-2 md:hidden">
              <Button onClick={handleEdit} className="h-10 rounded-xl">
                Edit
              </Button>
              <Button
                variant="outline"
                onClick={handleDelete}
                className="h-10 rounded-xl"
              >
                Delete
              </Button>
            </div>
            <div className="hidden md:block">
              <Button
                variant="destructive"
                onClick={handleDelete}
                className="w-full h-11 rounded-xl"
              >
                Delete Patient
              </Button>
            </div>
          </div>

          <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
            <DialogContent className="max-w-sm">
              <DialogHeader>
                <DialogTitle>Confirm delete</DialogTitle>
                <DialogDescription>
                  Are you sure you want to delete this patient record? This
                  action cannot be undone.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter className="mt-4 gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowDeleteConfirm(false)}
                >
                  Cancel
                </Button>
                <Button variant="destructive" onClick={confirmDelete}>
                  Delete
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {showShare && (
            <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
              <div className="bg-card w-full max-w-sm rounded-2xl p-5 border border-border shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-base text-foreground">
                    Secure External Transfer
                  </h4>
                  <button
                    type="button"
                    onClick={() => setShowShare(false)}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {!generatedLink ? (
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs font-medium text-muted-foreground">
                        Link Expiration Threshold (Hours)
                      </label>
                      <Input
                        type="number"
                        min="1"
                        max="72"
                        value={shareHours}
                        onChange={(e) => setShareHours(e.target.value)}
                        className="h-9 text-sm bg-background mt-1"
                      />
                    </div>
                    <Button
                      onClick={doShare}
                      className="w-full h-10 rounded-xl"
                      disabled={shareM.isPending}
                    >
                      {shareM.isPending
                        ? "Generating..."
                        : "Generate One-Time Access Link"}
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-3 text-center">
                    <p className="text-xs text-muted-foreground">
                      Provide this secure tracking payload token and code to the
                      verified practitioner:
                    </p>
                    <div className="p-3 bg-muted rounded-xl text-left space-y-1.5 break-all">
                      <p className="text-xs text-foreground font-mono font-bold">
                        <span className="text-primary">Token:</span>{" "}
                        {generatedLink.token}
                      </p>
                      <p className="text-sm text-foreground font-mono font-bold">
                        <span className="text-emerald-500">Security OTP:</span>{" "}
                        {generatedLink.otp}
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      className="w-full h-10 rounded-xl mt-2"
                      onClick={() => setShowShare(false)}
                    >
                      Close Window
                    </Button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </Layout>
    </ProtectedRoute>
  );
}
