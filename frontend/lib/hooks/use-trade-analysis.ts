import { useMutation } from "@tanstack/react-query";
import { tradesApi } from "../api/trades";
import type { TradeRequest } from "../types";
import { useTradeStore } from "../stores/trade-store";

/**
 * Hook to analyze a trade
 */
export function useTradeAnalysis() {
  const { setResult, setIsAnalyzing } = useTradeStore();

  return useMutation({
    mutationFn: (request: TradeRequest) => tradesApi.analyzeTrade(request),
    onMutate: () => {
      setIsAnalyzing(true);
    },
    onSuccess: (result) => {
      setResult(result);
      setIsAnalyzing(false);
    },
    onError: () => {
      setIsAnalyzing(false);
    },
  });
}

/**
 * Hook to get lineup recommendations
 */
export function useLineupRecommendations() {
  return useMutation({
    mutationFn: (rosterIds: number[]) => tradesApi.getLineupRecommendations(rosterIds),
  });
}
