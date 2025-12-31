"use client"

import { useState } from "react"
import { Search, Filter, ChevronRight } from "lucide-react"
import type { ModelRisqueResponse } from "@/lib/types"
import Link from "next/link"

interface PatientDirectoryProps {
  patients: ModelRisqueResponse[]
}

export function PatientDirectory({ patients }: PatientDirectoryProps) {
  const [searchTerm, setSearchTerm] = useState("")

  const filteredPatients = patients.filter((p) =>
    p.patient_resource_id.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            placeholder="Search by Patient ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <button className="flex items-center gap-2 px-4 py-2 border rounded-md text-sm font-medium hover:bg-accent">
          <Filter className="h-4 w-4" />
          Filter
        </button>
      </div>

      <div className="border rounded-lg overflow-hidden bg-card">
        <table className="w-full text-sm text-left">
          <thead className="bg-muted/50 text-muted-foreground font-medium border-bottom">
            <tr>
              <th className="px-6 py-4">Patient ID</th>
              <th className="px-6 py-4">Risk Score</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Last Updated</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filteredPatients.map((patient) => (
              // <CHANGE> wrapped tr in Link to make row clickable
              <tr
                key={patient.patient_resource_id}
                className="hover:bg-muted/50 transition-colors cursor-pointer group"
              >
                <td className="px-6 py-4 font-medium">{patient.patient_resource_id}</td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-12 h-1.5 bg-accent rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary"
                        style={{ width: `${patient.readmission_risk_score * 100}%` }}
                      />
                    </div>
                    <span>{Math.round(patient.readmission_risk_score * 100)}%</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span
                    className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      patient.risk_category === "High"
                        ? "bg-red-100 text-red-700"
                        : patient.risk_category === "Medium"
                          ? "bg-amber-100 text-amber-700"
                          : "bg-green-100 text-green-700"
                    }`}
                  >
                    {patient.risk_category} Risk
                  </span>
                </td>
                <td className="px-6 py-4 text-muted-foreground">
                  {new Date(patient.prediction_timestamp).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 text-right">
                  {/* <CHANGE> added link to patient detail page */}
                  <Link
                    href={`/patients/${patient.patient_resource_id}`}
                    className="p-1 rounded-full hover:bg-accent group-hover:translate-x-1 transition-transform inline-block"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
