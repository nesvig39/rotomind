"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeftRight, Plus, RefreshCw, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PlayerCard } from "@/components/features/players/player-card";
import { cn } from "@/lib/utils/cn";
import { useTradeStore } from "@/lib/stores/trade-store";
import { useTradeAnalysis } from "@/lib/hooks/use-trade-analysis";
import type { Player } from "@/lib/types";

interface TradeBuilderProps {
  className?: string;
}

export function TradeBuilder({ className }: TradeBuilderProps) {
  const {
    teamAPlayers,
    teamBPlayers,
    playersToSend,
    playersToReceive,
    removePlayerToSend,
    removePlayerToReceive,
    isAnalyzing,
    swapTeams,
    clearTrade,
  } = useTradeStore();

  const { mutate: analyzeTrade } = useTradeAnalysis();

  const handleAnalyze = () => {
    if (playersToSend.length === 0 || playersToReceive.length === 0) return;

    analyzeTrade({
      team_a_roster: teamAPlayers.map((p) => p.id),
      team_b_roster: teamBPlayers.map((p) => p.id),
      players_to_b: playersToSend.map((p) => p.id),
      players_to_a: playersToReceive.map((p) => p.id),
    });
  };

  const totalSendingZ = playersToSend.reduce((sum, _p) => sum - 2.5, 0); // Mock
  const totalReceivingZ = playersToReceive.reduce((sum, _p) => sum + 2.8, 0); // Mock

  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <ArrowLeftRight className="h-5 w-5 text-brand" />
            Trade Builder
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={swapTeams}>
              <RefreshCw className="h-4 w-4 mr-1" />
              Swap
            </Button>
            <Button variant="ghost" size="sm" onClick={clearTrade}>
              Clear
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <div className="grid grid-cols-2 divide-x divide-border">
          {/* Sending Side */}
          <TradeSide
            title="📤 You Send"
            subtitle="Select players to trade away"
            players={playersToSend}
            availablePlayers={teamAPlayers.filter(
              (p) => !playersToSend.find((s) => s.id === p.id)
            )}
            onRemove={removePlayerToSend}
            totalZ={totalSendingZ}
            isNegative
          />

          {/* Receiving Side */}
          <TradeSide
            title="📥 You Receive"
            subtitle="Select players to acquire"
            players={playersToReceive}
            availablePlayers={teamBPlayers.filter(
              (p) => !playersToReceive.find((r) => r.id === p.id)
            )}
            onRemove={removePlayerToReceive}
            totalZ={totalReceivingZ}
          />
        </div>

        {/* Analyze Button */}
        <div className="p-4 bg-background-hover border-t border-border">
          <Button
            onClick={handleAnalyze}
            disabled={
              playersToSend.length === 0 || playersToReceive.length === 0 || isAnalyzing
            }
            className="w-full"
            size="lg"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <ArrowLeftRight className="h-4 w-4 mr-2" />
                Analyze Trade
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

interface TradeSideProps {
  title: string;
  subtitle: string;
  players: Player[];
  availablePlayers: Player[];
  onRemove: (playerId: number) => void;
  totalZ: number;
  isNegative?: boolean;
}

function TradeSide({
  title,
  subtitle,
  players,
  availablePlayers,
  onRemove,
  totalZ,
  isNegative,
}: TradeSideProps) {
  const [showPicker, setShowPicker] = React.useState(false);

  return (
    <div className="p-4">
      <div className="mb-4">
        <h4 className="font-semibold">{title}</h4>
        <p className="text-sm text-foreground-secondary">{subtitle}</p>
      </div>

      {/* Selected Players */}
      <div className="space-y-2 mb-4 min-h-[120px]">
        <AnimatePresence mode="popLayout">
          {players.map((player) => (
            <PlayerCard
              key={player.id}
              player={player}
              compact
              onRemove={() => onRemove(player.id)}
            />
          ))}
        </AnimatePresence>

        {players.length === 0 && (
          <div className="flex items-center justify-center h-24 border-2 border-dashed border-border rounded-lg text-foreground-tertiary text-sm">
            No players selected
          </div>
        )}
      </div>

      {/* Add Player Button */}
      <Button
        variant="outline"
        className="w-full"
        onClick={() => setShowPicker(!showPicker)}
      >
        <Plus className="h-4 w-4 mr-1" />
        Add Player
      </Button>

      {/* Player Picker */}
      <AnimatePresence>
        {showPicker && availablePlayers.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-2 space-y-1 max-h-40 overflow-y-auto"
          >
            {availablePlayers.slice(0, 5).map((player) => (
              <PlayerCard
                key={player.id}
                player={player}
                compact
                onSelect={() => {
                  // Add player logic handled by parent
                  setShowPicker(false);
                }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Total Z-Score */}
      <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
        <span className="text-sm text-foreground-secondary">Total Z-Score:</span>
        <span
          className={cn(
            "font-bold",
            isNegative ? "text-error" : "text-success"
          )}
        >
          {isNegative && totalZ < 0 ? "" : "+"}
          {totalZ.toFixed(1)}
        </span>
      </div>
    </div>
  );
}
