import { useEffect } from "react";
import { useRoute, useLocation, Link } from "wouter";
import { ArrowLeft } from "lucide-react";
import { useForm } from "react-hook-form";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useGetPatient, useUpdatePatient } from "@/lib/apiClient";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";

interface PatientFormValues {
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  gender: "male" | "female" | "other";
  bloodGroup?: string;
  phoneNumber?: string;
}

export default function PatientEdit() {
  const [, params] = useRoute("/patients/:id/edit");
  const patientId = params?.id ?? "";
  const [, setLocation] = useLocation();
  const { toast } = useToast();

  const { data: patient, isLoading } = useGetPatient(patientId);
  const updatePatient = useUpdatePatient();

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<PatientFormValues>({
    defaultValues: {
      firstName: "",
      lastName: "",
      dateOfBirth: "",
      gender: "male",
      bloodGroup: "",
      phoneNumber: "",
    },
  });

  useEffect(() => {
    if (patient) {
      reset({
        firstName: patient.firstName,
        lastName: patient.lastName,
        dateOfBirth: patient.dateOfBirth,
        gender: patient.gender,
        bloodGroup: patient.bloodGroup ?? "",
        phoneNumber: patient.phoneNumber ?? "",
      });
    }
  }, [patient, reset]);

  const onSubmit = handleSubmit((data) => {
    updatePatient.mutate(
      {
        id: patientId,
        data: {
          firstName: data.firstName,
          lastName: data.lastName,
          dateOfBirth: data.dateOfBirth,
          gender: data.gender,
          bloodGroup: data.bloodGroup === "none" ? undefined : data.bloodGroup || undefined,
          phoneNumber: data.phoneNumber || undefined,
        },
      },
      {
        onSuccess: () => {
          toast({ title: "Patient updated successfully." });
          setLocation(`/patients/${patientId}`);
        },
        onError: (err) => toast({ title: "Unable to update patient", description: err.message, variant: "destructive" }),
      }
    );
  });

  return (
    <ProtectedRoute>
      <Layout title="Edit Patient">
        <div className="max-w-2xl mx-auto w-full px-4 pt-4 pb-12">
          <div className="flex items-center gap-3 mb-5">
            <Link href={`/patients/${patientId}`}>
              <button type="button" className="w-10 h-10 rounded-full bg-muted/80 flex items-center justify-center text-foreground hover:bg-muted transition">
                <ArrowLeft className="w-4 h-4" />
              </button>
            </Link>
            <div>
              <p className="text-sm text-muted-foreground">Editing patient profile</p>
              <h1 className="text-2xl font-semibold text-foreground">{patient ? `${patient.firstName} ${patient.lastName}` : "Patient"}</h1>
            </div>
          </div>

          <div className="bg-card border border-border rounded-3xl p-5 space-y-5">
            {isLoading ? (
              <div className="space-y-3">
                <Skeleton className="h-10 rounded-2xl" />
                <Skeleton className="h-10 rounded-2xl" />
                <Skeleton className="h-10 rounded-2xl" />
              </div>
            ) : (
              <form onSubmit={onSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <Label htmlFor="firstName">First Name</Label>
                    <Input id="firstName" className="rounded-xl" {...register("firstName", { required: true })} />
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="lastName">Last Name</Label>
                    <Input id="lastName" className="rounded-xl" {...register("lastName", { required: true })} />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <Label htmlFor="dateOfBirth">Date of Birth</Label>
                    <Input id="dateOfBirth" type="date" className="rounded-xl" {...register("dateOfBirth", { required: true })} />
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="gender">Gender Identity</Label>
                    <Select
                      onValueChange={(value) => setValue("gender", value as PatientFormValues["gender"])}
                      defaultValue="male"
                    >
                      <SelectTrigger id="gender" className="rounded-xl" aria-label="Gender">
                        <SelectValue placeholder="Select gender" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">Male</SelectItem>
                        <SelectItem value="female">Female</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <Label htmlFor="bloodGroup">Blood Group</Label>
                    <Select
                      onValueChange={(value) => setValue("bloodGroup", value)}
                      defaultValue={patient?.bloodGroup ?? "none"}
                    >
                      <SelectTrigger id="bloodGroup" className="rounded-xl" aria-label="Blood group">
                        <SelectValue placeholder="Select blood group" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        <SelectItem value="A+">A+</SelectItem>
                        <SelectItem value="A-">A-</SelectItem>
                        <SelectItem value="B+">B+</SelectItem>
                        <SelectItem value="B-">B-</SelectItem>
                        <SelectItem value="AB+">AB+</SelectItem>
                        <SelectItem value="AB-">AB-</SelectItem>
                        <SelectItem value="O+">O+</SelectItem>
                        <SelectItem value="O-">O-</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="phoneNumber">Phone Number</Label>
                    <Input id="phoneNumber" className="rounded-xl" {...register("phoneNumber")} />
                  </div>
                </div>

                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <Button type="button" variant="outline" onClick={() => setLocation(`/patients/${patientId}`)} className="w-full md:w-auto">
                    Cancel
                  </Button>
                  <Button type="submit" className="w-full md:w-auto">
                    {updatePatient.isPending ? "Saving..." : "Save changes"}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  );
}
