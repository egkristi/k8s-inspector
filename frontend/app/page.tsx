"use client";

import React, { useEffect, useState } from "react";
import DashboardStats from "@/components/DashboardStats";
import { Activity, ShieldAlert, Zap, DollarSign } from "lucide-react";

export default function Home() {
  const [wsStatus, setWsStatus] = useState("Connecting...");

  useEffect(() => {
    // Mock WebSocket Connection for MVP demonstration
    const timer = setTimeout(() => setWsStatus("Connected (Real-time)"), 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Global Cluster Overview</h1>
          <p className="text-muted-foreground mt-1">Multi-cluster telemetry and AI insights.</p>
        </div>
        <div className="flex items-center gap-2 text-sm px-3 py-1 bg-secondary rounded-full">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          {wsStatus}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <DashboardStats title="Total Clusters" value="4" icon={<Activity className="w-4 h-4" />} trend="+1 this week" />
        <DashboardStats title="Avg Security Score" value="87/100" icon={<ShieldAlert className="w-4 h-4 text-orange-400" />} trend="-2 points (drift)" />
        <DashboardStats title="Cost Optimization" value="$4,293" icon={<DollarSign className="w-4 h-4 text-green-400" />} trend="Monthly potential savings" />
        <DashboardStats title="Active Anomalies" value="2" icon={<Zap className="w-4 h-4 text-yellow-400" />} trend="1 requires attention" />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="border border-border bg-card p-6 rounded-lg">
          <h2 className="text-lg font-semibold mb-4">Top AI Recommendations</h2>
          <ul className="space-y-4">
            <li className="flex justify-between items-start pb-4 border-b border-border">
              <div>
                <p className="font-medium text-red-400">Memory Exhaustion Predicted</p>
                <p className="text-sm text-muted-foreground">prod-eu: payment-service memory scaling required in ~14h</p>
              </div>
              <button className="bg-primary text-primary-foreground px-3 py-1 text-xs rounded-md">Auto-Fix</button>
            </li>
            <li className="flex justify-between items-start pb-4 border-b border-border">
              <div>
                <p className="font-medium text-orange-400">Pod Security Standard Violation</p>
                <p className="text-sm text-muted-foreground">staging: 12 pods running as root user</p>
              </div>
              <button className="bg-primary text-primary-foreground px-3 py-1 text-xs rounded-md">Apply PSP</button>
            </li>
            <li className="flex justify-between items-start">
              <div>
                <p className="font-medium text-green-400">Over-provisioned Resources</p>
                <p className="text-sm text-muted-foreground">dev-cluster: 8 orphaned PVCs detected</p>
              </div>
              <button className="bg-primary text-primary-foreground px-3 py-1 text-xs rounded-md">Clean Up</button>
            </li>
          </ul>
        </div>
        
        <div className="border border-border bg-card p-6 rounded-lg flex flex-col items-center justify-center text-center">
          <div className="w-full h-full flex flex-col items-center justify-center text-muted-foreground">
             <Activity className="w-12 h-12 mb-4 opacity-20" />
             <p>Real-time topology map initializing...</p>
          </div>
        </div>
      </div>
    </div>
  );
}
