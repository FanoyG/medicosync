import { useState, useRef } from "react";
import { ArrowLeft, Camera, FolderOpen, FileText, X, FlaskConical, Scan, StickyNote } from "lucide-react";
import { Link, useLocation } from "wouter";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useCreateRecord, useListPatients } from "@/lib/apiClient";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

// Aligned keys with your backend's RecordType Enum standards
const types = [
  { value: "lab",   label: "Lab Report",  icon: FlaskConical },
  { value: "xray",  label: "X-Ray",       icon: Scan },
  { value: "visit", label: "Visit Note",  icon: StickyNote },
  { value: "image", label: "Image",       icon: FileText },
  { value: "other", label: "Other",       icon: FileText },
];

export default function RecordUpload() {
  const [, setLocation] = useLocation();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [recordType, setRecordType] = useState("lab");
  const [patientId, setPatientId] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  
  const { data: patients } = useListPatients();
  const createRecord = useCreateRecord();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) { 
      setFile(f); 
      if (!title) setTitle(f.name.replace(/\.[^.]+$/, "")); 
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!patientId || !title || !recordType || !file) {
      toast({ title: "Fill in all required fields", variant: "destructive" });
      return;
    }
    
    createRecord.mutate(
      { data: {
        patientId,
        title,
        recordType,
        file,
      }},
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: ["/records/patient", patientId] });
          toast({ title: "Record uploaded successfully!" });
          setLocation(`/patients/${patientId}`);
        },
        onError: (err: any) => toast({ title: "Upload failed", description: err.message, variant: "destructive" }),
      }
    );
  };

  const mobileHeader = (
    <div className="px-4 pt-3 pb-4">
      <div className="flex items-center gap-3">
        <Link href="/patients">
          <button type="button" className="w-8 h-8 flex items-center justify-center rounded-full bg-white/20">
            <ArrowLeft className="w-4 h-4 text-white" />
          </button>
        </Link>
        <h1 className="text-white text-lg font-bold">Upload Patient Records</h1>
      </div>
    </div>
  );

  return (
    <ProtectedRoute>
      <Layout title="Upload Records" mobileHeader={mobileHeader}>
        <div className="max-w-lg mx-auto px-4 pt-4 pb-12">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Patient selector */}
            <div className="bg-card rounded-2xl border border-border p-4 space-y-3">
              {(() => {
                const p = patients?.find(x => String(x.id) === patientId);
                return p ? (
                  <div className="flex items-center gap-3 mb-1">
                    <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-semibold text-sm flex-shrink-0">
                      {p.firstName[0]}{p.lastName[0]}
                    </div>
                    <div>
                      <p className="font-semibold text-sm text-foreground">{p.firstName} {p.lastName}</p>
                    </div>
                  </div>
                ) : null;
              })()}
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Patient <span className="text-destructive">*</span></Label>
                <Select value={patientId} onValueChange={setPatientId}>
                  <SelectTrigger className="rounded-xl h-10 bg-background" data-testid="select-patient">
                    <SelectValue placeholder="Select patient" />
                  </SelectTrigger>
                  <SelectContent>
                    {patients?.map(p => (
                      <SelectItem key={p.id} value={String(p.id)}>
                        {p.firstName} {p.lastName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>



            {/* Selection pills + Title */}
            <div className="bg-card rounded-2xl border border-border p-4 space-y-3">
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Type</Label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {types.map(t => (
                    <button
                      key={t.value}
                      type="button"
                      onClick={() => setRecordType(t.value)}
                      className={cn(
                        "px-3 py-1.5 rounded-full text-xs font-medium transition-all border",
                        recordType === t.value
                          ? "bg-primary text-white border-primary"
                          : "bg-background text-muted-foreground border-border hover:border-primary/50"
                      )}
                      data-testid={`category-${t.value}`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Title <span className="text-destructive">*</span></Label>
                <Input
                  placeholder="e.g. Blood Test Result"
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                  className="rounded-xl h-10"
                  data-testid="input-title"
                />
              </div>
            </div>

            {/* Integrated File selection */}
            <div className="bg-card rounded-2xl border border-border p-4 space-y-3">
              <Label className="text-xs text-muted-foreground">File Selection</Label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  className="flex-1 flex items-center justify-center gap-2 h-11 rounded-xl border border-border bg-background text-sm text-muted-foreground hover:border-primary/50 transition-all active:bg-muted"
                >
                  <Camera className="w-4 h-4" />
                  Camera
                </button>
                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  className="flex-1 flex items-center justify-center gap-2 h-11 rounded-xl border border-border bg-background text-sm text-muted-foreground hover:border-primary/50 transition-all active:bg-muted"
                  data-testid="button-browse-files"
                >
                  <FolderOpen className="w-4 h-4" />
                  Files
                </button>
              </div>
              <input ref={fileRef} type="file" className="hidden" onChange={handleFileChange} accept=".pdf,.jpg,.jpeg,.png" />
              {file ? (
                <div className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
                  <FileText className="w-4 h-4 text-blue-500 flex-shrink-0" />
                  <span className="text-sm text-blue-700 dark:text-blue-300 flex-1 truncate">{file.name}</span>
                  <button type="button" onClick={() => setFile(null)} className="text-blue-500">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : null}
            </div>



            <Button
              type="submit"
              className="w-full h-12 rounded-xl text-base font-semibold"
              disabled={createRecord.isPending}
              data-testid="button-upload"
            >
              {createRecord.isPending ? "Uploading..." : "Upload Record"}
            </Button>
          </form>
        </div>
      </Layout>
    </ProtectedRoute>
  );
}
