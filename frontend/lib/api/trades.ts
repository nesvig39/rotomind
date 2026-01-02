import { api } from "./client";
import type { TradeRequest, TradeResult } from "../types";

/**
 * Trade analysis API endpoints
 */
export const tradesApi = {
  /**
   * Analyze a trade between two teams
   */
  async analyzeTrade(request: TradeRequest): Promise<TradeResult> {
    return api.post<TradeResult>("/analyze/trade", request);
  },

  /**
   * Get lineup recommendations for a roster
   */
  async getLineupRecommendations(rosterIds: number[]): Promise<unknown[]> {
    return api.post<unknown[]>("/recommend/lineup", rosterIds);
  },
};
