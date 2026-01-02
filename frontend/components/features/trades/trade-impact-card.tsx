"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { Check, X, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils/cn";
import { CATEGORIES, type CategoryKey } from "@/lib/types";

interface CategoryChange {
  category: CategoryKey;
  before: number;
  after: number;
}

interface TradeImpactCardProps {
  title: string;
  overallDiff: number;
  categoryChanges: CategoryChange[];
  verdict?: "accept" | "reject" | "neutral";
  verdictReason?: string;
  projectedRankChange?: { before: number; after: number };
  className?: string;
}

export function TradeImpactCard({
  title,
  overallDiff,
  categoryChanges,
  verdict,
  verdictReason,
  projectedRankChange,
  className,
}: TradeImpactCardProps) {
  const verdictConfig = {
    accept: {
      icon: Check,
      label: "ACCEPT",
      bgColor: "bg-success/10",
      textColor: "text-success",
      borderColor: "border-success",
    },
    reject: {
      icon: X,
      label: "REJECT",
      bgColor: "bg-error/10",
      textColor: "text-error",
      borderColor: "border-error",
    },
    neutral: {
      icon: Minus,
      label: "NEUTRAL",
      bgColor: "bg-warning/10",
      textColor: "text-warning",
      borderColor: "border-warning",
    },
  };

  const vConfig = verdict ? verdictConfig[verdict] : null;

  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Overall Impact */}
        <div className="flex items-center justify-between p-3 bg-background-hover rounded-lg">
          <span className="text-foreground-secondary">Overall Impact:</span>
          <div className="flex items-center gap-2">
            {overallDiff > 0 ? (
              <TrendingUp className="h-5 w-5 text-success" />
            ) : overallDiff < 0 ? (
              <TrendingDown className="h-5 w-5 text-error" />
            ) : (
              <Minus className="h-5 w-5 text-foreground-tertiary" />
            )}
            <span
              className={cn(
                "text-xl font-bold",
                overallDiff > 0 && "text-success",
                overallDiff < 0 && "text-error",
                overallDiff === 0 && "text-foreground-tertiary"
              )}
            >
              {overallDiff > 0 ? "+" : ""}
              {overallDiff.toFixed(2)} Z
            </span>
          </div>
        </div>

        {/* Category Changes */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-foreground-secondary">
            Category Changes
          </h4>
          {categoryChanges.map((change, i) => {
            const diff = change.after - change.before;
            const catMeta = CATEGORIES.find((c) => c.key === change.category);

            return (
              <motion.div
                key={change.category}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="flex items-center gap-3"
              >
                <span
                  className="w-10 text-xs font-medium"
                  style={{ color: catMeta?.color }}
                >
                  {catMeta?.label || change.category}
                </span>
                <div className="flex-1">
                  <CategoryBar before={change.before} after={change.after} />
                </div>
                <div className="flex items-center gap-1 w-16 justify-end">
                  {diff > 0 ? (
                    <TrendingUp className="h-3 w-3 text-success" />
                  ) : diff < 0 ? (
                    <TrendingDown className="h-3 w-3 text-error" />
                  ) : null}
                  <span
                    className={cn(
                      "text-xs font-medium",
                      diff > 0 && "text-success",
                      diff < 0 && "text-error",
                      diff === 0 && "text-foreground-tertiary"
                    )}
                  >
                    {diff > 0 ? "+" : ""}
                    {diff.toFixed(1)}
                  </span>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Verdict */}
        {vConfig && (
          <div
            className={cn(
              "p-4 rounded-lg border-2",
              vConfig.bgColor,
              vConfig.borderColor
            )}
          >
            <div className="flex items-center gap-2 mb-2">
              <vConfig.icon className={cn("h-5 w-5", vConfig.textColor)} />
              <span className={cn("font-bold", vConfig.textColor)}>
                {vConfig.label}
              </span>
            </div>
            {verdictReason && (
              <p className="text-sm text-foreground-secondary">{verdictReason}</p>
            )}
            {projectedRankChange && (
              <p className="text-sm mt-2">
                <span className="text-foreground-tertiary">Projected Rank: </span>
                <span className="font-medium">
                  {projectedRankChange.before} → {projectedRankChange.after}
                </span>
                {projectedRankChange.after < projectedRankChange.before && (
                  <span className="text-success ml-1">
                    (↑{projectedRankChange.before - projectedRankChange.after})
                  </span>
                )}
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function CategoryBar({ before, after }: { before: number; after: number }) {
  const maxValue = 12; // Max rank in a 12-team league
  const beforeWidth = (before / maxValue) * 100;
  const afterWidth = (after / maxValue) * 100;
  const isImproved = after > before;

  return (
    <div className="relative h-4 bg-background-hover rounded-full overflow-hidden">
      {/* Before bar */}
      <div
        className="absolute inset-y-0 left-0 bg-foreground-tertiary/30 rounded-full"
        style={{ width: `${beforeWidth}%` }}
      />
      {/* After bar */}
      <motion.div
        initial={{ width: `${beforeWidth}%` }}
        animate={{ width: `${afterWidth}%` }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className={cn(
          "absolute inset-y-0 left-0 rounded-full",
          isImproved ? "bg-success" : after < before ? "bg-error" : "bg-foreground-tertiary"
        )}
      />
    </div>
  );
}
