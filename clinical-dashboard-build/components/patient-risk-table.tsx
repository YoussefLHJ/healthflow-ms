"use client"

import type { ModelRisqueResponse } from "@/lib/types"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ChevronRight, ArrowUpRight, ArrowDownRight } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface PatientRiskTableProps {
  patients: ModelRisqueResponse[]
}

export function PatientRiskTable({ patients }: PatientRiskTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Patient ID</TableHead>
          <TableHead>Risk Category</TableHead>
          <TableHead>Risk Score</TableHead>
          <TableHead>Primary Drivers (SHAP)</TableHead>
          <TableHead>Prediction Date</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {patients.map((patient) => (
          <TableRow key={patient.patient_resource_id}>
            <TableCell className="font-medium">{patient.patient_resource_id}</TableCell>
            <TableCell>
              <Badge
                variant="outline"
                className={
                  patient.risk_category === "High"
                    ? "border-destructive text-destructive bg-destructive/5"
                    : patient.risk_category === "Medium"
                      ? "border-chart-2 text-chart-2 bg-chart-2/5"
                      : "border-chart-1 text-chart-1 bg-chart-1/5"
                }
              >
                {patient.risk_category}
              </Badge>
            </TableCell>
            <TableCell>
              <div className="flex items-center gap-2">
                <div className="w-16 h-2 rounded-full bg-muted overflow-hidden">
                  <div
                    className="h-full transition-all"
                    style={{
                      width: `${patient.readmission_risk_score * 100}%`,
                      backgroundColor:
                        patient.risk_category === "High"
                          ? "var(--chart-3)"
                          : patient.risk_category === "Medium"
                            ? "var(--chart-2)"
                            : "var(--chart-1)",
                    }}
                  />
                </div>
                <span className="text-xs font-mono">{(patient.readmission_risk_score * 100).toFixed(0)}%</span>
              </div>
            </TableCell>
            <TableCell>
              <div className="flex gap-1">
                {patient.shap_explanations.slice(0, 2).map((exp, i) => (
                  <TooltipProvider key={i}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Badge variant="secondary" className="text-[10px] py-0 px-1 cursor-default">
                          {exp.impact === "positive" ? (
                            <ArrowUpRight className="w-2 h-2 mr-1 text-destructive" />
                          ) : (
                            <ArrowDownRight className="w-2 h-2 mr-1 text-chart-1" />
                          )}
                          {exp.feature_name}
                        </Badge>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="text-xs">
                          {exp.feature_name}: {exp.feature_value.toString()}
                        </p>
                        <p className="text-[10px] text-muted-foreground">SHAP Value: {exp.shap_value.toFixed(3)}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                ))}
                {patient.shap_explanations.length > 2 && (
                  <Badge variant="outline" className="text-[10px] py-0 px-1">
                    +{patient.shap_explanations.length - 2} more
                  </Badge>
                )}
              </div>
            </TableCell>
            <TableCell className="text-xs text-muted-foreground">
              {new Date(patient.prediction_timestamp).toLocaleDateString()}
            </TableCell>
            <TableCell className="text-right">
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <ChevronRight className="h-4 w-4" />
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
