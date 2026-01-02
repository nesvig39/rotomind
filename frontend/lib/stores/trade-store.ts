import { create } from "zustand";
import type { Player, TradeResult } from "../types";

interface TradeBuilderState {
  // Team A (user's team)
  teamAId: number | null;
  teamAPlayers: Player[];
  playersToSend: Player[];

  // Team B (opponent)
  teamBId: number | null;
  teamBPlayers: Player[];
  playersToReceive: Player[];

  // Analysis result
  result: TradeResult | null;
  isAnalyzing: boolean;

  // Actions
  setTeamA: (teamId: number, players: Player[]) => void;
  setTeamB: (teamId: number, players: Player[]) => void;
  addPlayerToSend: (player: Player) => void;
  removePlayerToSend: (playerId: number) => void;
  addPlayerToReceive: (player: Player) => void;
  removePlayerToReceive: (playerId: number) => void;
  setResult: (result: TradeResult | null) => void;
  setIsAnalyzing: (analyzing: boolean) => void;
  clearTrade: () => void;
  swapTeams: () => void;
}

export const useTradeStore = create<TradeBuilderState>((set) => ({
  // Initial state
  teamAId: null,
  teamAPlayers: [],
  playersToSend: [],
  teamBId: null,
  teamBPlayers: [],
  playersToReceive: [],
  result: null,
  isAnalyzing: false,

  // Actions
  setTeamA: (teamId, players) => set({ teamAId: teamId, teamAPlayers: players }),
  setTeamB: (teamId, players) => set({ teamBId: teamId, teamBPlayers: players }),

  addPlayerToSend: (player) =>
    set((state) => {
      if (state.playersToSend.find((p) => p.id === player.id)) return state;
      return { playersToSend: [...state.playersToSend, player] };
    }),

  removePlayerToSend: (playerId) =>
    set((state) => ({
      playersToSend: state.playersToSend.filter((p) => p.id !== playerId),
    })),

  addPlayerToReceive: (player) =>
    set((state) => {
      if (state.playersToReceive.find((p) => p.id === player.id)) return state;
      return { playersToReceive: [...state.playersToReceive, player] };
    }),

  removePlayerToReceive: (playerId) =>
    set((state) => ({
      playersToReceive: state.playersToReceive.filter((p) => p.id !== playerId),
    })),

  setResult: (result) => set({ result }),
  setIsAnalyzing: (isAnalyzing) => set({ isAnalyzing }),

  clearTrade: () =>
    set({
      playersToSend: [],
      playersToReceive: [],
      result: null,
      isAnalyzing: false,
    }),

  swapTeams: () =>
    set((state) => ({
      teamAId: state.teamBId,
      teamAPlayers: state.teamBPlayers,
      playersToSend: state.playersToReceive,
      teamBId: state.teamAId,
      teamBPlayers: state.teamAPlayers,
      playersToReceive: state.playersToSend,
      result: null,
    })),
}));
