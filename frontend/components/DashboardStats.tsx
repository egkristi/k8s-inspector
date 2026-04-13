import React from "react";

interface DashboardStatsProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: string;
}

export default function DashboardStats({ title, value, icon, trend }: DashboardStatsProps) {
  return (
    <div className="p-6 bg-card border border-border rounded-xl shadow-sm flex flex-col">
      <div className="flex justify-between items-start">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        <div className="text-muted-foreground">{icon}</div>
      </div>
      <div className="mt-4">
        <h3 className="text-3xl font-bold tracking-tight">{value}</h3>
        {trend && (
          <p className="text-xs text-muted-foreground mt-2">{trend}</p>
        )}
      </div>
    </div>
  );
}
