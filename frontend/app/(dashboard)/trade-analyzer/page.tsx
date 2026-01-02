"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { ArrowLeftRight } from "lucide-react";
import { TradeBuilder } from "@/components/features/trades/trade-builder";
import { TradeImpactCard } from "@/components/features/trades/trade-impact-card";
import { useTradeStore } from "@/lib/stores/trade-store";
import type { CategoryKey } from "@/lib/types";

// Mock category changes for demonstration
const mockCategoryChanges: Array<{
  category: CategoryKey;
  before: number;
  after: number;
}> = [
  { category: "pts", before: 7, after: 8 },
  { category: "reb", before: 8, after: 6 },
  { category: "ast", before: 9, after: 11 },
  { category: "stl", before: 4, after: 9 },
  { category: "blk", before: 8, after: 7 },
  { category: "tpm", before: 6, after: 8 },
  { category: "fg_pct", before: 7, after: 8 },
  { category: "ft_pct", before: 6, after: 5 },
];

export default function TradeAnalyzerPage() {
  const { result } = useTradeStore();

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <ArrowLeftRight className="h-6 w-6 text-brand" />
          Trade Analyzer
        </h1>
        <p className="text-foreground-secondary mt-1">
          Build and analyze trades with real-time Z-score impact analysis.
        </p>
      </motion.div>

      {/* Trade Builder */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <TradeBuilder />
      </motion.div>

      {/* Impact Analysis */}
      {result ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          <TradeImpactCard
            title="Your Team Impact"
            overallDiff={result.team_a.diff}
            categoryChanges={mockCategoryChanges}
            verdict={result.team_a.diff > 0 ? "accept" : result.team_a.diff < -1 ? "reject" : "neutral"}
            verdictReason={
              result.team_a.diff > 0
                ? "This trade improves your weakest category (STL) while maintaining your strengths."
                : "This trade negatively impacts your overall Z-score."
            }
            projectedRankChange={{ before: 3, after: result.team_a.diff > 0 ? 2 : 4 }}
          />

          <TradeImpactCard
            title="Opponent's Impact"
            overallDiff={result.team_b.diff}
            categoryChanges={mockCategoryChanges.map((c) => ({
              ...c,
              before: c.after,
              after: c.before,
            }))}
          />
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="flex items-center justify-center py-16 border-2 border-dashed border-border rounded-xl"
        >
          <div className="text-center">
            <ArrowLeftRight className="h-12 w-12 text-foreground-tertiary mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground-secondary">
              No Trade Analysis Yet
            </h3>
            <p className="text-foreground-tertiary mt-1 max-w-sm">
              Select players to trade from both teams and click &quot;Analyze Trade&quot; to see the
              impact.
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
}
