"use client";

import * as React from "react";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { CATEGORIES, type CategoryKey } from "@/lib/types";
import { cn } from "@/lib/utils/cn";

interface ZScoreData {
  [key: string]: number;
}

interface ZScoreRadarProps {
  data: ZScoreData;
  compareData?: ZScoreData;
  dataLabel?: string;
  compareLabel?: string;
  showLegend?: boolean;
  className?: string;
}

export function ZScoreRadar({
  data,
  compareData,
  dataLabel = "Your Team",
  compareLabel = "League Avg",
  showLegend = true,
  className,
}: ZScoreRadarProps) {
  const chartData = CATEGORIES.map((cat) => ({
    category: cat.label,
    fullLabel: cat.fullLabel,
    value: data[cat.key] || 0,
    compare: compareData?.[cat.key] || 0,
  }));

  return (
    <div className={cn("w-full h-[300px]", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
          <PolarGrid
            stroke="hsl(var(--border))"
            strokeDasharray="3 3"
          />
          <PolarAngleAxis
            dataKey="category"
            tick={{ fill: "hsl(var(--foreground-secondary))", fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[-3, 3]}
            tick={{ fill: "hsl(var(--foreground-tertiary))", fontSize: 10 }}
            axisLine={false}
          />

          {/* Comparison data (if provided) */}
          {compareData && (
            <Radar
              name={compareLabel}
              dataKey="compare"
              stroke="hsl(var(--foreground-tertiary))"
              fill="hsl(var(--foreground-tertiary))"
              fillOpacity={0.2}
              strokeDasharray="5 5"
            />
          )}

          {/* Main data */}
          <Radar
            name={dataLabel}
            dataKey="value"
            stroke="hsl(var(--brand))"
            fill="hsl(var(--brand))"
            fillOpacity={0.3}
            strokeWidth={2}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--background-elevated))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
              color: "hsl(var(--foreground))",
            }}
            formatter={(value: number, name: string) => [
              value.toFixed(2),
              name,
            ]}
          />

          {showLegend && (
            <Legend
              wrapperStyle={{
                color: "hsl(var(--foreground-secondary))",
                fontSize: "12px",
              }}
            />
          )}
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
