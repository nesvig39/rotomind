"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { Sparkles, ChevronRight, Play, Pause, ArrowLeftRight, UserMinus } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils/cn";
import type { AIInsight } from "@/lib/types";

interface AIInsightCardProps {
  insight: AIInsight;
  onAction?: () => void;
  className?: string;
}

const insightIcons = {
  start: Play,
  bench: Pause,
  trade: ArrowLeftRight,
  pickup: Sparkles,
  drop: UserMinus,
};

const insightColors = {
  start: "success",
  bench: "warning",
  trade: "info",
  pickup: "success",
  drop: "error",
} as const;

export function AIInsightCard({ insight, onAction, className }: AIInsightCardProps) {
  const Icon = insightIcons[insight.type];
  const color = insightColors[insight.type];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01 }}
    >
      <Card
        className={cn(
          "card-hover cursor-pointer border-l-4",
          color === "success" && "border-l-success",
          color === "warning" && "border-l-warning",
          color === "error" && "border-l-error",
          color === "info" && "border-l-info",
          className
        )}
        onClick={onAction}
      >
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <div
              className={cn(
                "p-2 rounded-lg",
                color === "success" && "bg-success/10",
                color === "warning" && "bg-warning/10",
                color === "error" && "bg-error/10",
                color === "info" && "bg-info/10"
              )}
            >
              <Icon
                className={cn(
                  "h-4 w-4",
                  color === "success" && "text-success",
                  color === "warning" && "text-warning",
                  color === "error" && "text-error",
                  color === "info" && "text-info"
                )}
              />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <p className="font-medium text-sm">{insight.title}</p>
                <Badge variant="secondary" className="text-xs">
                  {Math.round(insight.confidence * 100)}% confident
                </Badge>
              </div>
              <p className="text-sm text-foreground-secondary mt-1">{insight.description}</p>
              {insight.players && insight.players.length > 0 && (
                <div className="flex gap-1 mt-2">
                  {insight.players.map((player) => (
                    <Badge key={player.id} variant="outline" className="text-xs">
                      {player.full_name}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
            <ChevronRight className="h-4 w-4 text-foreground-tertiary flex-shrink-0" />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

interface AIInsightListProps {
  insights: AIInsight[];
  maxVisible?: number;
  className?: string;
}

export function AIInsightList({ insights, maxVisible = 5, className }: AIInsightListProps) {
  const visibleInsights = insights.slice(0, maxVisible);
  const remainingCount = insights.length - maxVisible;

  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-brand" />
        <h3 className="font-semibold">AI Insights</h3>
        <Badge variant="secondary">{insights.length}</Badge>
      </div>
      <div className="space-y-2">
        {visibleInsights.map((insight) => (
          <AIInsightCard key={insight.id} insight={insight} />
        ))}
      </div>
      {remainingCount > 0 && (
        <Button variant="ghost" className="w-full">
          View {remainingCount} more insights
          <ChevronRight className="h-4 w-4 ml-1" />
        </Button>
      )}
    </div>
  );
}
