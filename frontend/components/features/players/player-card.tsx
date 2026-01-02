"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { Check, X, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils/cn";
import { formatZScore, getZScoreClass } from "@/lib/utils/format";
import type { Player, PlayerStats } from "@/lib/types";

export interface PlayerCardProps {
  player: Player;
  stats?: PlayerStats;
  showZScores?: boolean;
  recommendation?: "start" | "bench" | "drop";
  isSelected?: boolean;
  onSelect?: () => void;
  onRemove?: () => void;
  compact?: boolean;
  className?: string;
}

export function PlayerCard({
  player,
  stats,
  showZScores = true,
  recommendation,
  isSelected = false,
  onSelect,
  onRemove,
  compact = false,
  className,
}: PlayerCardProps) {
  const recommendationConfig = {
    start: {
      icon: Check,
      label: "START",
      bgColor: "bg-success/10",
      textColor: "text-success",
      borderColor: "border-success/30",
    },
    bench: {
      icon: AlertTriangle,
      label: "BENCH",
      bgColor: "bg-warning/10",
      textColor: "text-warning",
      borderColor: "border-warning/30",
    },
    drop: {
      icon: X,
      label: "DROP",
      bgColor: "bg-error/10",
      textColor: "text-error",
      borderColor: "border-error/30",
    },
  };

  const recConfig = recommendation ? recommendationConfig[recommendation] : null;

  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className={cn(
          "flex items-center gap-3 p-3 rounded-lg border bg-background-surface",
          isSelected ? "border-brand" : "border-border",
          onSelect && "cursor-pointer hover:border-border-hover",
          className
        )}
        onClick={onSelect}
      >
        <div className="w-10 h-10 rounded-full bg-background-hover flex items-center justify-center text-lg">
          🏀
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium truncate">{player.full_name}</p>
          <p className="text-xs text-foreground-secondary">
            {player.position} • {player.team_abbreviation}
          </p>
        </div>
        {onRemove && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onRemove();
            }}
            className="p-1 hover:bg-background-hover rounded"
          >
            <X className="h-4 w-4 text-foreground-tertiary" />
          </button>
        )}
        {stats && showZScores && (
          <div className={cn("text-sm font-medium", getZScoreClass(stats.z_total))}>
            {formatZScore(stats.z_total)}
          </div>
        )}
      </motion.div>
    );
  }

  return (
    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
      <Card
        className={cn(
          "card-hover overflow-hidden",
          recConfig?.borderColor,
          isSelected && "ring-2 ring-brand",
          onSelect && "cursor-pointer",
          className
        )}
        onClick={onSelect}
      >
        {/* Recommendation Badge */}
        {recConfig && (
          <div
            className={cn("px-3 py-1.5 flex items-center gap-1.5", recConfig.bgColor)}
          >
            <recConfig.icon className={cn("h-4 w-4", recConfig.textColor)} />
            <span className={cn("text-xs font-semibold", recConfig.textColor)}>
              {recConfig.label}
            </span>
          </div>
        )}

        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            {/* Player Avatar */}
            <div className="w-12 h-12 rounded-full bg-background-hover flex items-center justify-center text-2xl flex-shrink-0">
              🏀
            </div>

            <div className="flex-1 min-w-0">
              {/* Player Name */}
              <div className="flex items-center gap-2">
                <p className="font-semibold truncate">{player.full_name}</p>
                {player.espn_injury_status && (
                  <Badge variant="error" className="text-xs">
                    {player.espn_injury_status}
                  </Badge>
                )}
              </div>

              {/* Position & Team */}
              <p className="text-sm text-foreground-secondary">
                {player.position} • {player.team_abbreviation}
              </p>

              {/* Z-Score Display */}
              {stats && showZScores && (
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-xs text-foreground-tertiary">Z-Score:</span>
                  <span
                    className={cn("text-lg font-bold", getZScoreClass(stats.z_total))}
                  >
                    {formatZScore(stats.z_total)}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Category Breakdown */}
          {stats && showZScores && (
            <div className="mt-4 grid grid-cols-4 gap-2 text-xs">
              <ZScoreMini label="PTS" value={stats.z_pts || 0} />
              <ZScoreMini label="REB" value={stats.z_reb || 0} />
              <ZScoreMini label="AST" value={stats.z_ast || 0} />
              <ZScoreMini label="STL" value={stats.z_stl || 0} />
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}

function ZScoreMini({ label, value }: { label: string; value: number }) {
  return (
    <div className="text-center">
      <p className="text-foreground-tertiary">{label}</p>
      <p className={cn("font-medium", getZScoreClass(value))}>{formatZScore(value)}</p>
    </div>
  );
}
