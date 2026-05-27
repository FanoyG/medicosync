import { useMutation, useQuery } from "@tanstack/react-query";
import type { UseQueryOptions, UseMutationOptions } from "@tanstack/react-query";

const API_BASE = ((import.meta as any).env?.VITE_API_URL as string) ?? "";

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${path}`;

  const body = options.body;
  const headers: globalThis.Record<string, string> = {
    ...(options.headers as globalThis.Record<string, string>),
  };

  // Only set JSON content type when the request body is not FormData
  if (!(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  // Automatically inject the token from localStorage
  const token = localStorage.getItem("token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    let errMsg = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      errMsg = body?.detail ?? body?.message ?? errMsg;
    } catch {
    }
    throw new Error(errMsg);
  }
  if (res.status === 204) return null as T;

  const data = await res.json();
  return camelize(data) as T;
}

// ─── Interfaces matched against your Pydantic schemas ───

export interface Patient {
  id: string;
  doctorId: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  gender: "male" | "female" | "other";
  bloodGroup?: string;
  phoneNumber?: string;
  createdAt: string;
}

export interface MedicalRecord { 
  id: string;
  patientId: string;
  doctorId: string;
  title: string;
  recordType: "lab" | "visit" | "xray" | "image" | "other";
  downloadUrl: string;
  fileType: string;
  uploadedAt: string;
}

export interface ShareLink {
  token: string;
  expiresAt: string;
  plainOtpCode?: string;
}

export interface SharedRecordAccess {
  recordTitle: string;
  recordType: "lab" | "visit" | "xray" | "image" | "other";
  downloadUrl: string;
  doctorName: string;
  expiresAt: string;
}

export interface DashboardStats {
  totalPatients: number;
  totalRecords: number;
  activeShares: number;
}

// ─── Query Hook Operations linked to your exact backend paths ───

// Endpoint 10: GET /patients/
export function useListPatients(options?: { query?: UseQueryOptions<Patient[]> }) {
  return useQuery<Patient[]>({
    queryKey: ["/patients"],
    queryFn: () => apiFetch<Patient[]>("/patients/"),
    ...options?.query,
  });
}

// Add this re-usable query hook to handle listing specific patient records
export function useListPatientRecords(
  patientId: string,
  options?: { query?: UseQueryOptions<MedicalRecord[]> }
) {
  return useQuery<MedicalRecord[]>({
    queryKey: ["/records/patient", patientId],
    queryFn: () => apiFetch<MedicalRecord[]>(`/records/patient/${patientId}`),
    enabled: !!patientId,
    ...options?.query,
  });
}

// Endpoint 11: GET /patients/{id}
export function useGetPatient(id: string, options?: { query?: UseQueryOptions<Patient> }) {
  return useQuery<Patient>({
    queryKey: ["/patients", id],
    queryFn: () => apiFetch<Patient>(`/patients/${id}`),
    enabled: !!id,
    ...options?.query,
  });
}

// Endpoint 7: POST /patients/
export function useCreatePatient(
  options?: UseMutationOptions<Patient, Error, Omit<Patient, "id" | "doctorId" | "createdAt">>
) {
  return useMutation<Patient, Error, Omit<Patient, "id" | "doctorId" | "createdAt">>({
    mutationFn: (data) => {
      // Re-map fields into exact snake_case format your pydantic schema expects for input
      const payload = {
        first_name: data.firstName,
        last_name: data.lastName,
        date_of_birth: data.dateOfBirth,
        gender: data.gender,
        blood_group: data.bloodGroup || null,
        phone_number: data.phoneNumber || null
      };
      return apiFetch<Patient>("/patients/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    ...options,
  });
}

// Endpoint 8: PATCH /patients/{id}
export function useUpdatePatient(
  options?: UseMutationOptions<Patient, Error, { id: string; data: Partial<Omit<Patient, "id" | "doctorId" | "createdAt">> }>
) {
  return useMutation<Patient, Error, { id: string; data: Partial<Omit<Patient, "id" | "doctorId" | "createdAt">> }>({
    mutationFn: ({ id, data }) => {
      const payload: any = {};
      if (data.firstName !== undefined) payload.first_name = data.firstName;
      if (data.lastName !== undefined) payload.last_name = data.lastName;
      if (data.dateOfBirth !== undefined) payload.date_of_birth = data.dateOfBirth;
      if (data.gender !== undefined) payload.gender = data.gender;
      if (data.bloodGroup !== undefined) payload.blood_group = data.bloodGroup;
      if (data.phoneNumber !== undefined) payload.phone_number = data.phoneNumber;
      return apiFetch<Patient>(`/patients/${id}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
    },
    ...options,
  });
}

// Endpoint 14: POST /records/ (Uses standard json mapping for metadata registry triggers)
export function useCreateRecord(
  options?: UseMutationOptions<MedicalRecord, Error, { data: { patientId: string; title: string; recordType: string; file: File; notes?: string; recordDate?: string } }>
) {
  return useMutation<MedicalRecord, Error, { data: { patientId: string; title: string; recordType: string; file: File; notes?: string; recordDate?: string } }>({
    mutationFn: ({ data }) => {
      const formData = new FormData();
      formData.append("patient_id", data.patientId);
      formData.append("title", data.title);
      formData.append("record_type", data.recordType);
      formData.append("file", data.file);
      if (data.notes) {
        formData.append("notes", data.notes);
      }
      if (data.recordDate) {
        formData.append("record_date", data.recordDate);
      }
      return apiFetch<MedicalRecord>("/records/", {
        method: "POST",
        body: formData,
      });
    },
    ...options,
  });
}

// Endpoint 15: POST /shares
export function useSharePatientRecords(
  options?: UseMutationOptions<ShareLink, Error, { data: { recordId: string; expiresInHours: number } }>
) {
  return useMutation<ShareLink, Error, { data: { recordId: string; expiresInHours: number } }>({
    mutationFn: ({ data }) => {
      const payload = {
        record_id: data.recordId,
        expires_in_hours: data.expiresInHours
      };
      return apiFetch<ShareLink>("/shares", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    ...options,
  });
}

// Endpoint 17: POST /shares/resend?token=
export function useResendShareOtp(
  options?: UseMutationOptions<void, Error, { data: { token: string } }>
) {
  return useMutation<void, Error, { data: { token: string } }>({
    mutationFn: ({ data }) =>
      apiFetch<void>(`/shares/resend?token=${encodeURIComponent(data.token)}`, {
        method: "POST",
      }),
    ...options,
  });
}

// Endpoint 16: POST /shares/verify
export function useVerifyShareToken(
  options?: UseMutationOptions<SharedRecordAccess, Error, { data: { token: string; verificationCode: string } }>
) {
  return useMutation<SharedRecordAccess, Error, { data: { token: string; verificationCode: string } }>({
    mutationFn: ({ data }) => {
      const payload = {
        token: data.token,
        verification_code: data.verificationCode
      };
      return apiFetch<SharedRecordAccess>("/shares/verify", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    ...options,
  });
}

// Endpoint 12: GET /records/{record_id}
export function useGetRecord(id: string, options?: { query?: UseQueryOptions<MedicalRecord> }) {
  return useQuery<MedicalRecord>({
    queryKey: ["/records", id],
    queryFn: () => apiFetch<MedicalRecord>(`/records/${id}`),
    enabled: !!id,
    ...options?.query,
  });
}

// Endpoint 13: DELETE /records/{record_id}
export function useDeleteRecord(options?: UseMutationOptions<void, Error, string>) {
  return useMutation<void, Error, string>({
    mutationFn: (recordId) => apiFetch<void>(`/records/${recordId}`, { method: "DELETE" }),
    ...options,
  });
}

// Endpoint 5: DELETE /patients/{id}
export function useDeletePatient(options?: UseMutationOptions<void, Error, string>) {
  return useMutation<void, Error, string>({
    mutationFn: (patientId) => apiFetch<void>(`/patients/${patientId}`, { method: "DELETE" }),
    ...options,
  });
}

// Endpoint 18: GET /dashboard
export function useGetDashboardStats(options?: { query?: UseQueryOptions<DashboardStats> }) {
  return useQuery<DashboardStats>({
    queryKey: ["/dashboard"],
    queryFn: () => apiFetch<DashboardStats>("/dashboard"),
    ...options?.query,
  });
}

// Global nested normalization case mapping transformer
function camelize(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(v => camelize(v));
  } else if (obj !== null && obj.constructor === Object) {
    return Object.keys(obj).reduce((result, key) => {
      const camelKey = key.replace(/_([a-z])/g, (_, g) => g.toUpperCase());
      result[camelKey] = camelize(obj[key]);
      return result;
    }, {} as any);
  }
  return obj;
}
