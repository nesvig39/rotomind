"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { Search, Filter, UserCircle, ArrowUpDown, ChevronDown } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils/cn";
import { formatZScore, getZScoreClass } from "@/lib/utils/format";
import { CATEGORIES } from "@/lib/types";

// Mock player data for demonstration
const mockPlayers = [
  { id: 1, name: "Nikola Jokić", pos: "C", team: "DEN", games: 48, zTotal: 18.2, zPts: 2.1, zReb: 3.4, zAst: 4.2, zStl: 1.8, zBlk: 0.9, z3pm: 0.4, zFg: 2.8, zFt: 2.6 },
  { id: 2, name: "Luka Dončić", pos: "PG", team: "DAL", games: 45, zTotal: 15.7, zPts: 3.8, zReb: 1.9, zAst: 3.1, zStl: 0.4, zBlk: 0.2, z3pm: 1.4, zFg: 1.8, zFt: 3.1 },
  { id: 3, name: "Shai Gilgeous-Alexander", pos: "PG", team: "OKC", games: 50, zTotal: 14.3, zPts: 3.2, zReb: 0.8, zAst: 1.2, zStl: 2.1, zBlk: 0.4, z3pm: 0.9, zFg: 2.4, zFt: 3.3 },
  { id: 4, name: "Giannis Antetokounmpo", pos: "PF", team: "MIL", games: 47, zTotal: 13.9, zPts: 2.9, zReb: 2.8, zAst: 1.1, zStl: 0.3, zBlk: 2.1, z3pm: -0.8, zFg: 2.8, zFt: 2.7 },
  { id: 5, name: "Anthony Davis", pos: "C", team: "LAL", games: 44, zTotal: 13.2, zPts: 2.4, zReb: 2.9, zAst: 0.6, zStl: 0.7, zBlk: 2.4, z3pm: 0.3, zFg: 2.1, zFt: 1.8 },
  { id: 6, name: "Jayson Tatum", pos: "SF", team: "BOS", games: 49, zTotal: 12.8, zPts: 2.7, zReb: 1.4, zAst: 0.9, zStl: 0.8, zBlk: 0.6, z3pm: 2.1, zFg: 1.9, zFt: 2.4 },
  { id: 7, name: "Tyrese Haliburton", pos: "PG", team: "IND", games: 42, zTotal: 12.1, zPts: 1.1, zReb: -0.3, zAst: 3.8, zStl: 1.2, zBlk: 0.1, z3pm: 1.8, zFg: 2.2, zFt: 2.2 },
  { id: 8, name: "Anthony Edwards", pos: "SG", team: "MIN", games: 50, zTotal: 11.5, zPts: 3.1, zReb: 0.7, zAst: 0.5, zStl: 0.9, zBlk: 0.3, z3pm: 1.6, zFg: 1.8, zFt: 2.6 },
  { id: 9, name: "Devin Booker", pos: "SG", team: "PHX", games: 46, zTotal: 10.8, zPts: 2.8, zReb: 0.4, zAst: 1.4, zStl: 0.6, zBlk: 0.1, z3pm: 1.2, zFg: 2.1, zFt: 2.2 },
  { id: 10, name: "Donovan Mitchell", pos: "SG", team: "CLE", games: 48, zTotal: 10.4, zPts: 2.6, zReb: 0.3, zAst: 0.8, zStl: 1.1, zBlk: 0.2, z3pm: 1.8, zFg: 1.8, zFt: 1.8 },
];

type SortField = "zTotal" | "zPts" | "zReb" | "zAst" | "zStl" | "zBlk" | "z3pm" | "zFg" | "zFt";
type ViewMode = "zscores" | "pergame" | "totals";

export default function PlayerExplorerPage() {
  const [search, setSearch] = React.useState("");
  const [sortField, setSortField] = React.useState<SortField>("zTotal");
  const [sortDir, setSortDir] = React.useState<"asc" | "desc">("desc");
  const [viewMode, setViewMode] = React.useState<ViewMode>("zscores");
  const [selectedPlayer, setSelectedPlayer] = React.useState<typeof mockPlayers[0] | null>(null);

  const filteredPlayers = React.useMemo(() => {
    return mockPlayers
      .filter((p) => p.name.toLowerCase().includes(search.toLowerCase()))
      .sort((a, b) => {
        const aVal = a[sortField];
        const bVal = b[sortField];
        return sortDir === "desc" ? bVal - aVal : aVal - bVal;
      });
  }, [search, sortField, sortDir]);

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortDir(sortDir === "desc" ? "asc" : "desc");
    } else {
      setSortField(field);
      setSortDir("desc");
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <UserCircle className="h-6 w-6 text-brand" />
          Player Explorer
        </h1>
        <p className="text-foreground-secondary mt-1">
          View and sort players by their season-long Z-scores across all 8 categories.
        </p>
      </motion.div>

      {/* Search and Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-4"
      >
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground-tertiary" />
          <Input
            placeholder="Search players..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            Position
            <ChevronDown className="h-4 w-4 ml-1" />
          </Button>
          <Button variant="outline">
            Team
            <ChevronDown className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </motion.div>

      {/* View Mode Toggle */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="flex gap-2"
      >
        <span className="text-sm text-foreground-secondary py-2">Toggle Columns:</span>
        {[
          { key: "zscores", label: "Z-Scores" },
          { key: "pergame", label: "Per-Game" },
          { key: "totals", label: "Totals" },
        ].map((mode) => (
          <Button
            key={mode.key}
            variant={viewMode === mode.key ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode(mode.key as ViewMode)}
          >
            {mode.label}
          </Button>
        ))}
      </motion.div>

      {/* Player Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-background-hover">
                    <th className="text-left p-4 font-medium text-foreground-secondary">Rank</th>
                    <th className="text-left p-4 font-medium text-foreground-secondary">Player</th>
                    <th className="text-center p-4 font-medium text-foreground-secondary">Pos</th>
                    <th className="text-center p-4 font-medium text-foreground-secondary">GP</th>
                    <SortableHeader field="zTotal" current={sortField} dir={sortDir} onSort={handleSort}>Total</SortableHeader>
                    <SortableHeader field="zPts" current={sortField} dir={sortDir} onSort={handleSort}>PTS</SortableHeader>
                    <SortableHeader field="zReb" current={sortField} dir={sortDir} onSort={handleSort}>REB</SortableHeader>
                    <SortableHeader field="zAst" current={sortField} dir={sortDir} onSort={handleSort}>AST</SortableHeader>
                    <SortableHeader field="zStl" current={sortField} dir={sortDir} onSort={handleSort}>STL</SortableHeader>
                    <SortableHeader field="zBlk" current={sortField} dir={sortDir} onSort={handleSort}>BLK</SortableHeader>
                    <SortableHeader field="z3pm" current={sortField} dir={sortDir} onSort={handleSort}>3PM</SortableHeader>
                    <SortableHeader field="zFg" current={sortField} dir={sortDir} onSort={handleSort}>FG%</SortableHeader>
                    <SortableHeader field="zFt" current={sortField} dir={sortDir} onSort={handleSort}>FT%</SortableHeader>
                  </tr>
                </thead>
                <tbody>
                  {filteredPlayers.map((player, index) => (
                    <motion.tr
                      key={player.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.02 }}
                      className={cn(
                        "border-b border-border cursor-pointer transition-colors",
                        selectedPlayer?.id === player.id
                          ? "bg-brand/10"
                          : "hover:bg-background-hover"
                      )}
                      onClick={() => setSelectedPlayer(player)}
                    >
                      <td className="p-4 font-medium text-foreground-tertiary">{index + 1}</td>
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-background-hover flex items-center justify-center text-sm">
                            🏀
                          </div>
                          <div>
                            <p className="font-medium">{player.name}</p>
                            <p className="text-xs text-foreground-tertiary">{player.team}</p>
                          </div>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <Badge variant="secondary">{player.pos}</Badge>
                      </td>
                      <td className="p-4 text-center text-foreground-secondary">{player.games}</td>
                      <td className={cn("p-4 text-center font-bold", getZScoreClass(player.zTotal))}>
                        {formatZScore(player.zTotal)}
                      </td>
                      <ZScoreCell value={player.zPts} />
                      <ZScoreCell value={player.zReb} />
                      <ZScoreCell value={player.zAst} />
                      <ZScoreCell value={player.zStl} />
                      <ZScoreCell value={player.zBlk} />
                      <ZScoreCell value={player.z3pm} />
                      <ZScoreCell value={player.zFg} />
                      <ZScoreCell value={player.zFt} />
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="p-4 border-t border-border flex items-center justify-between text-sm text-foreground-secondary">
              <span>Showing 1-{filteredPlayers.length} of {mockPlayers.length} players</span>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" disabled>
                  ← Prev
                </Button>
                <Button variant="outline" size="sm" className="bg-brand/10 border-brand text-brand">
                  1
                </Button>
                <Button variant="outline" size="sm">
                  2
                </Button>
                <Button variant="outline" size="sm">
                  3
                </Button>
                <Button variant="outline" size="sm">
                  Next →
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Quick Stats Panel */}
      {selectedPlayer && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">
                📊 Quick Stats: {selectedPlayer.name}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-4 md:grid-cols-8 gap-4">
                {CATEGORIES.map((cat) => {
                  const value = selectedPlayer[`z${cat.key.charAt(0).toUpperCase()}${cat.key.slice(1)}` as keyof typeof selectedPlayer] as number || 0;
                  return (
                    <div key={cat.key} className="text-center p-3 bg-background-hover rounded-lg">
                      <p className="text-xs text-foreground-tertiary">{cat.label}</p>
                      <p className={cn("text-lg font-bold", getZScoreClass(value))}>
                        {formatZScore(value)}
                      </p>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}

interface SortableHeaderProps {
  field: SortField;
  current: SortField;
  dir: "asc" | "desc";
  onSort: (field: SortField) => void;
  children: React.ReactNode;
}

function SortableHeader({ field, current, dir, onSort, children }: SortableHeaderProps) {
  const isActive = field === current;

  return (
    <th
      className="p-4 text-center font-medium text-foreground-secondary cursor-pointer hover:text-foreground transition-colors"
      onClick={() => onSort(field)}
    >
      <div className="flex items-center justify-center gap-1">
        {children}
        <ArrowUpDown
          className={cn(
            "h-3 w-3",
            isActive ? "text-brand" : "text-foreground-tertiary"
          )}
        />
      </div>
    </th>
  );
}

function ZScoreCell({ value }: { value: number }) {
  return (
    <td className={cn("p-4 text-center", getZScoreClass(value))}>
      {formatZScore(value)}
    </td>
  );
}
