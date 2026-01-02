"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { Trophy, TrendingUp, Sparkles, Users, Calendar, ChevronRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/features/insights/stat-card";
import { AIInsightList } from "@/components/features/insights/ai-insight-card";
import { PlayerCard } from "@/components/features/players/player-card";
import { CategoryBreakdown } from "@/components/charts/category-bar";
import { TrendSparkline } from "@/components/charts/trend-sparkline";
import type { AIInsight, Player, CategoryKey } from "@/lib/types";
import { format } from "date-fns";

// Mock data for demonstration
const mockInsights: AIInsight[] = [
  {
    id: "1",
    type: "start",
    title: "Start Tyrese Maxey",
    description: "Maxey has a higher ceiling vs ORL than Jrue Holiday tonight.",
    confidence: 0.87,
  },
  {
    id: "2",
    type: "trade",
    title: "Trade Window Alert",
    description: "Your league's trade deadline is in 2 days. Consider your options.",
    confidence: 1.0,
  },
  {
    id: "3",
    type: "pickup",
    title: "Waiver Wire: Cason Wallace",
    description: "Rising +2.1 Z-Score over last 7 days. Consider dropping Kyle Kuzma.",
    confidence: 0.82,
  },
];

const mockPlayers: Player[] = [
  {
    id: 1,
    nba_id: 201939,
    full_name: "Stephen Curry",
    team_abbreviation: "GSW",
    position: "PG",
    is_active: true,
  },
  {
    id: 2,
    nba_id: 2544,
    full_name: "LeBron James",
    team_abbreviation: "LAL",
    position: "SF",
    is_active: true,
  },
  {
    id: 3,
    nba_id: 202681,
    full_name: "Kyrie Irving",
    team_abbreviation: "DAL",
    position: "PG",
    is_active: true,
  },
];

const mockCategoryStandings: Array<{
  category: CategoryKey;
  rank: number;
  total: number;
  trend?: "up" | "down" | "stable";
}> = [
  { category: "pts", rank: 7, total: 12, trend: "up" },
  { category: "reb", rank: 4, total: 12, trend: "up" },
  { category: "ast", rank: 2, total: 12, trend: "stable" },
  { category: "stl", rank: 9, total: 12, trend: "down" },
  { category: "blk", rank: 6, total: 12, trend: "up" },
  { category: "tpm", rank: 5, total: 12, trend: "stable" },
  { category: "fg_pct", rank: 3, total: 12, trend: "up" },
  { category: "ft_pct", rank: 5, total: 12, trend: "stable" },
];

const mockTrendData = [12.5, 13.2, 14.1, 13.8, 15.2, 16.1, 15.8];

const waiversHot = [
  { name: "Cason Wallace", change: "+2.1" },
  { name: "Jalen Williams", change: "+1.8" },
  { name: "Keegan Murray", change: "+1.5" },
];

export default function CommandCenter() {
  const today = new Date();

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-brand/10 to-brand/5 border border-brand/20 rounded-xl p-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              📊 Command Center
            </h1>
            <p className="text-foreground-secondary mt-1">
              Good morning! You have 3 players with games today.
            </p>
          </div>
          <div className="flex items-center gap-2 text-foreground-secondary">
            <Calendar className="h-4 w-4" />
            <span>{format(today, "EEEE, MMM d, yyyy")}</span>
          </div>
        </div>
      </motion.div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <StatCard
            title="Standings Rank"
            value="3rd of 12"
            change={2}
            changeLabel="from last week"
            icon={<Trophy className="h-5 w-5 text-brand" />}
            variant="success"
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
        >
          <Card className="card-hover">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-foreground-secondary">Z-Score Trend</p>
                  <p className="text-3xl font-bold">+15.8</p>
                  <div className="flex items-center gap-1 text-sm text-success">
                    <TrendingUp className="h-4 w-4" />
                    <span>+2.3 this week</span>
                  </div>
                </div>
                <div className="w-24">
                  <TrendSparkline data={mockTrendData} trend="up" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="card-hover border-brand/20 bg-brand/5">
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-brand/10 rounded-lg">
                  <Sparkles className="h-5 w-5 text-brand" />
                </div>
                <div>
                  <p className="font-medium">AI Insight</p>
                  <p className="text-sm text-foreground-secondary mt-1">
                    &quot;Consider starting Tyrese Maxey over Jrue Holiday today. Maxey has higher ceiling vs ORL.&quot;
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Today's Lineup Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
      >
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-brand" />
                Today&apos;s Lineup Recommendations
              </CardTitle>
              <Button variant="ghost" size="sm">
                View All
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {mockPlayers.map((player, index) => (
                <PlayerCard
                  key={player.id}
                  player={player}
                  stats={{
                    player_id: player.id,
                    games: 45,
                    PTS: 28.5,
                    REB: 5.2,
                    AST: 6.1,
                    STL: 1.2,
                    BLK: 0.3,
                    FG3M: 5.1,
                    FG_PCT: 0.481,
                    FT_PCT: 0.912,
                    z_total: 3.2 - index * 0.7,
                    z_pts: 2.8 - index * 0.5,
                    z_reb: 0.1,
                    z_ast: 1.2,
                    z_stl: 0.5,
                  }}
                  recommendation={index < 2 ? "start" : "bench"}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="lg:col-span-2"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-5 w-5 text-brand" />
                Category Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CategoryBreakdown standings={mockCategoryStandings} />
            </CardContent>
          </Card>
        </motion.div>

        {/* Hot on Waivers */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-brand" />
                Hot on Waiver Wire
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {waiversHot.map((player, index) => (
                <div
                  key={player.name}
                  className="flex items-center justify-between p-3 bg-background-hover rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-foreground-tertiary font-medium">
                      {index + 1}.
                    </span>
                    <span className="font-medium">{player.name}</span>
                  </div>
                  <span className="text-success font-medium">{player.change} Z</span>
                </div>
              ))}
              <Button variant="outline" className="w-full">
                Analyze Pickups
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* AI Insights Panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <CardContent className="p-6">
            <AIInsightList insights={mockInsights} />
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
