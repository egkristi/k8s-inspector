"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Server, 
  ShieldCheck, 
  LineChart, 
  DollarSign, 
  Wrench, 
  Settings 
} from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  const routes = [
    { name: "Overview", path: "/", icon: LayoutDashboard },
    { name: "Clusters", path: "/clusters", icon: Server },
    { name: "Security", path: "/security", icon: ShieldCheck },
    { name: "Performance", path: "/insights", icon: LineChart },
    { name: "Cost Analysis", path: "/cost", icon: DollarSign },
    { name: "Playbooks", path: "/playbooks", icon: Wrench },
  ];

  return (
    <div className="w-64 border-r border-border bg-card flex flex-col">
      <div className="h-16 flex items-center px-6 border-b border-border">
        <span className="text-xl font-bold flex items-center gap-2">
          🐦‍⬛ k8s-inspector
        </span>
      </div>
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 px-2">
          Dashboard
        </div>
        {routes.map((route) => {
          const active = pathname === route.path;
          const Icon = route.icon;
          return (
            <Link
              key={route.path}
              href={route.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                active 
                  ? "bg-primary text-primary-foreground font-medium" 
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
            >
              <Icon className="w-4 h-4" />
              {route.name}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-border">
        <Link
          href="/settings"
          className="flex items-center gap-3 px-3 py-2 rounded-md text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
        >
          <Settings className="w-4 h-4" />
          Settings
        </Link>
      </div>
    </div>
  );
}
