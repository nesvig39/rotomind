"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils/cn";

export interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  variant?: "default" | "success" | "warning" | "error";
  className?: string;
}

export function StatCard({
  title,
  value,
  change,
  changeLabel,
  icon,
  variant = "default",
  className,
}: StatCardProps) {
  const getTrend = () => {
    if (!change) return null;
    if (change > 0) return { icon: TrendingUp, color: "text-success", prefix: "+" };
    if (change < 0) return { icon: TrendingDown, color: "text-error", prefix: "" };
    return { icon: Minus, color: "text-foreground-tertiary", prefix: "" };
  };

  const trend = getTrend();

  const variantStyles = {
    default: "border-border",
    success: "border-success/30 bg-success/5",
    warning: "border-warning/30 bg-warning/5",
    error: "border-error/30 bg-error/5",
  };

  return (
    <Card className={cn("card-hover", variantStyles[variant], className)}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-foreground-secondary">{title}</p>
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-3xl font-bold tracking-tight"
            >
              {value}
            </motion.p>
            {trend && (
              <div className="flex items-center gap-1 text-sm">
                <trend.icon className={cn("h-4 w-4", trend.color)} />
                <span className={trend.color}>
                  {trend.prefix}
                  {Math.abs(change!)}
                </span>
                {changeLabel && (
                  <span className="text-foreground-tertiary">{changeLabel}</span>
                )}
              </div>
            )}
          </div>
          {icon && (
            <div className="p-2 bg-background-hover rounded-lg">
              {icon}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
