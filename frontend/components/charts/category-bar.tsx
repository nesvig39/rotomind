"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils/cn";
import { CATEGORIES, type CategoryKey } from "@/lib/types";
import { formatOrdinal } from "@/lib/utils/format";

interface CategoryBarProps {
  category: CategoryKey;
  rank: number;
  total: number;
  trend?: "up" | "down" | "stable";
  showLabel?: boolean;
  className?: string;
}

export function CategoryBar({
  category,
  rank,
  total,
  trend,
  showLabel = true,
  className,
}: CategoryBarProps) {
  const catMeta = CATEGORIES.find((c) => c.key === category);
  const percentage = ((total - rank + 1) / total) * 100; // Higher rank = more bar

  return (
    <div className={cn("flex items-center gap-3", className)}>
      {showLabel && (
        <span
          className="w-10 text-sm font-medium"
          style={{ color: catMeta?.color }}
        >
          {catMeta?.label || category.toUpperCase()}
        </span>
      )}
      <div className="flex-1 h-3 bg-background-hover rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: "easeOut", delay: 0.1 }}
          className="h-full rounded-full"
          style={{ backgroundColor: catMeta?.color }}
        />
      </div>
      <div className="flex items-center gap-1 w-12 justify-end">
        <span className="text-sm font-medium text-foreground-secondary">
          {formatOrdinal(rank)}
        </span>
        {trend === "up" && <span className="text-success text-xs">▲</span>}
        {trend === "down" && <span className="text-error text-xs">▼</span>}
      </div>
    </div>
  );
}

interface CategoryBreakdownProps {
  standings: Array<{
    category: CategoryKey;
    rank: number;
    total: number;
    trend?: "up" | "down" | "stable";
  }>;
  className?: string;
}

export function CategoryBreakdown({ standings, className }: CategoryBreakdownProps) {
  return (
    <div className={cn("space-y-2", className)}>
      {standings.map((standing, index) => (
        <motion.div
          key={standing.category}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          <CategoryBar {...standing} />
        </motion.div>
      ))}
    </div>
  );
}
