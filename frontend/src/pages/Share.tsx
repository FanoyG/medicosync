import { useLocation } from "wouter";
import { useEffect } from "react";

export default function Share() {
  const [, setLocation] = useLocation();
  useEffect(() => { setLocation("/patients"); }, [setLocation]);
  return null;
}
