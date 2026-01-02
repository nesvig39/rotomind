"use client";

import * as React from "react";
import {
  LineChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  YAxis,
} from "recharts";
import { cn } from "@/lib/utils/cn";

interface TrendSparklineProps {
  data: number[];
  trend?: "up" | "down" | "stable";
  height?: number;
  className?: string;
}

export function TrendSparkline({
  data,
  trend,
  height = 40,
  className,
}: TrendSparklineProps) {
  const chartData = data.map((value, index) => ({ value, index }));

  const getStrokeColor = () => {
    if (trend === "up") return "hsl(var(--success))";
    if (trend === "down") return "hsl(var(--error))";
    return "hsl(var(--brand))";
  };

  return (
    <div className={cn("w-full", className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <YAxis domain={["dataMin - 1", "dataMax + 1"]} hide />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--background-elevated))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "6px",
              padding: "4px 8px",
              fontSize: "12px",
            }}
            formatter={(value: number) => [value.toFixed(1), "Value"]}
            labelFormatter={() => ""}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke={getStrokeColor()}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: getStrokeColor() }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
