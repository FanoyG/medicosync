import { useState } from "react";
import { Link } from "wouter";
import { Search, ChevronRight, UserPlus } from "lucide-react";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useListPatients, useCreatePatient } from "@/lib/apiClient"; // Cleaned unused query keys
import { useQueryClient } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"; // Cleaned broken DialogFooter
import { useForm } from "react-hook-form";
import { useToast } from "@/hooks/use-toast";
import { differenceInYears } from "date-fns";
import { cn } from "@/lib/utils";

function getAge(dob: string) {
  try { return differenceInYears(new Date(), new Date(dob)); } catch { return "—"; }
}

const avatarColors = [
  "bg-blue-100 text-blue-600",
  "bg-green-100 text-green-600",
  "bg-purple-100 text-purple-600",
  "bg-orange-100 text-orange-600",
  "bg-pink-100 text-pink-600",
];

export default function Patients() {
  const [search, setSearch] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const { data: patients, isLoading, refetch } = useListPatients(); // Fixed: Re-routed query structure to fetch complete list
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const createPatient = useCreatePatient();

  const { register, handleSubmit, setValue, reset, formState: { errors } } = useForm<{
    firstName: string; lastName: string; dateOfBirth: string; gender: string; bloodGroup?: string; phoneNumber?: string;
  }>({
    defaultValues: {
      gender: "male",
      bloodGroup: "",
      phoneNumber: "",
    },
  });

  const onAdd = handleSubmit(data => {
    const formattedData = {
      ...data,
      gender: data.gender as "male" | "female" | "other",
      dateOfBirth: typeof data.dateOfBirth === "string"
        ? data.dateOfBirth
        : (data.dateOfBirth as Date).toISOString().split("T")[0],
    };

    createPatient.mutate(
      formattedData,
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: ["/patients"] }); // Aligned key syntax layout
          refetch();
          setShowAdd(false);
          reset();
          toast({ title: "Patient added successfully!" });
        },
        onError: () => toast({ title: "Error saving patient profile", variant: "destructive" }),
      }
    );
  });

  // Client-side dynamic search index mapping matching the state arrays
  const filteredPatients = patients?.filter(p => 
    `${p.firstName} ${p.lastName}`.toLowerCase().includes(search.toLowerCase())
  ) ?? [];

  const mobileHeader = (
    <div className="px-4 pt-4 pb-4">
      <div className="flex items-center justify-between">
        <h1 className="text-white text-xl font-bold">Patients</h1>
        <button
          type="button"
          onClick={() => setShowAdd(true)}
          className="w-9 h-9 flex items-center justify-center rounded-full bg-white/20 active:bg-white/30"
          data-testid="button-add-patient-header"
        >
          <UserPlus className="w-4.5 h-4.5 text-white" />
        </button>
      </div>
      <p className="text-white/70 text-sm mt-0.5">
        {filteredPatients ? `${filteredPatients.length} patient${filteredPatients.length !== 1 ? "s" : ""}` : "Loading..."}
      </p>
    </div>
  );

  return (
    <ProtectedRoute>
      <Layout title="Patients" mobileHeader={mobileHeader}>
        <div className="max-w-2xl mx-auto w-full px-4 pt-3 pb-4">
          {/* Desktop add button */}
          <div className="hidden md:flex items-center justify-between mb-4 pt-2">
            <div>
              <p className="text-sm text-muted-foreground">
                {filteredPatients ? `${filteredPatients.length} total` : "Loading..."}
              </p>
            </div>
            <Button onClick={() => setShowAdd(true)} className="gap-2 rounded-xl" data-testid="button-add-patient">
              <UserPlus className="w-4 h-4" /> Add Patient
            </Button>
          </div>

          {/* Search Input Bar */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="search"
              placeholder="Search patients..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full h-10 pl-9 pr-4 bg-card rounded-xl border border-border text-sm outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              data-testid="input-search-patients"
            />
          </div>

          {/* Patient list interface grid */}
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center gap-3 p-3.5 bg-card rounded-xl border border-border">
                  <Skeleton className="w-11 h-11 rounded-full flex-shrink-0" />
                  <div className="flex-1">
                    <Skeleton className="h-4 w-32 mb-1.5" />
                    <Skeleton className="h-3 w-20" />
                  </div>
                </div>
              ))}
            </div>
          ) : filteredPatients.length > 0 ? (
            <div className="space-y-2">
              {filteredPatients.map((p, idx) => (
                <Link
                  key={p.id}
                  href={`/patients/${p.id}`}
                  className="flex items-center gap-3 p-3.5 bg-card rounded-xl border border-border active:bg-muted hover:shadow-sm transition-all group"
                  data-testid={`card-patient-${p.id}`}
                >
                  <div className={cn(
                    "w-11 h-11 rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0",
                    avatarColors[idx % avatarColors.length]
                  )}>
                    {(p.firstName?.[0] || "") + (p.lastName?.[0] || "")}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-foreground" data-testid={`text-patient-name-${p.id}`}>
                      {p.firstName} {p.lastName}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5 capitalize">
                      {p.gender}, Age {getAge(p.dateOfBirth)}
                    </p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors flex-shrink-0" />
                </Link>
              ))}
            </div>
          ) : (
            <div className="py-16 text-center">
              <div className="w-14 h-14 rounded-full bg-muted flex items-center justify-center mx-auto mb-3">
                <UserPlus className="w-6 h-6 text-muted-foreground" />
              </div>
              <p className="text-base font-semibold text-foreground mb-1">
                {search ? "No matches found" : "No patients yet"}
              </p>
              {!search && (
                <Button className="mt-4 rounded-xl gap-2" onClick={() => setShowAdd(true)}>
                  <UserPlus className="w-4 h-4" /> Add First Patient
                </Button>
              )}
            </div>
          )}
        </div>
                {/* Mobile FAB Trigger Action Button */}
        <button
          type="button"
          onClick={() => setShowAdd(true)}
          className="md:hidden fixed bottom-20 right-4 w-14 h-14 bg-primary text-white rounded-full shadow-lg active:scale-95 transition-all flex items-center justify-center z-30"
          data-testid="button-fab-add-patient"
        >
          <UserPlus className="w-5 h-5" />
        </button>

        {/* Add Patient Modal Overlays */}
        <Dialog open={showAdd} onOpenChange={setShowAdd}>
          <DialogContent className="rounded-2xl max-w-sm p-6 bg-card border border-border">
            <DialogHeader>
              <DialogTitle className="text-lg font-bold">Add New Patient</DialogTitle>
            </DialogHeader>
            <form onSubmit={onAdd} className="space-y-3 pt-1">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">First Name</Label>
                  <Input placeholder="Sarah" data-testid="input-first-name" className="rounded-xl h-9" {...register("firstName", { required: true })} />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Last Name</Label>
                  <Input placeholder="Johnson" data-testid="input-last-name" className="rounded-xl h-9" {...register("lastName", { required: true })} />
                </div>
              </div>
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Date of Birth</Label>
                <Input type="date" data-testid="input-dob" className="rounded-xl h-9" {...register("dateOfBirth", { required: true })} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Gender Identity</Label>
                <Select onValueChange={v => setValue("gender", v)} defaultValue="male">
                  <SelectTrigger className="rounded-xl h-9 bg-background" data-testid="select-gender">
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Blood Group (optional)</Label>
                <Select onValueChange={v => setValue("bloodGroup", v === "none" ? "" : v)} defaultValue="none">
                  <SelectTrigger className="rounded-xl h-9 bg-background" data-testid="select-blood-group">
                    <SelectValue placeholder="Select blood group" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
                    { ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].map(group => (
                      <SelectItem key={group} value={group}>{group}</SelectItem>
                    )) }
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Phone (optional)</Label>
                <Input placeholder="+1 555-0000" className="rounded-xl h-9" {...register("phoneNumber")} />
              </div>
              
              {/* Form Action Controls Button Row Grid */}
              <div className="flex gap-2 pt-3">
                <Button type="button" variant="outline" className="rounded-xl flex-1 h-10 text-sm font-medium" onClick={() => setShowAdd(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={createPatient.isPending} className="rounded-xl flex-1 h-10 text-sm font-semibold" data-testid="button-save-patient">
                  {createPatient.isPending ? "Adding..." : "Add Patient"}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </Layout>
    </ProtectedRoute>
  );
}
