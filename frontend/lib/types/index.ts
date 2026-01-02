// Player types
export interface Player {
  id: number;
  nba_id: number;
  espn_id?: number;
  full_name: string;
  team_abbreviation?: string;
  position?: string;
  is_active: boolean;
  espn_ownership_pct?: number;
  espn_injury_status?: string;
}

export interface PlayerStats {
  player_id: number;
  full_name?: string;
  games: number;
  // Raw stats
  PTS: number;
  REB: number;
  AST: number;
  STL: number;
  BLK: number;
  FG3M: number;
  FG_PCT: number;
  FT_PCT: number;
  // Z-scores
  z_total: number;
  z_pts?: number;
  z_reb?: number;
  z_ast?: number;
  z_stl?: number;
  z_blk?: number;
  z_tpm?: number;
  z_fg_pct?: number;
  z_ft_pct?: number;
}

// Team types
export interface FantasyTeam {
  id: number;
  name: string;
  owner_name?: string;
  league_id?: number;
  espn_team_id?: number;
  players?: Player[];
}

// League types
export interface League {
  id: number;
  name: string;
  season: string;
  espn_league_id?: number;
  espn_configured: boolean;
  last_espn_sync?: string;
}

export interface DailyStandings {
  id: number;
  team_id: number;
  league_id: number;
  date: string;
  rank: number;
  total_roto_points: number;
  points_pts: number;
  points_reb: number;
  points_ast: number;
  points_stl: number;
  points_blk: number;
  points_tpm: number;
  points_fg_pct: number;
  points_ft_pct: number;
}

// Trade analysis types
export interface TradeRequest {
  team_a_roster?: number[];
  team_b_roster?: number[];
  team_a_id?: number;
  team_b_id?: number;
  players_to_b: number[];
  players_to_a: number[];
}

export interface TradeImpact {
  before: number;
  after: number;
  diff: number;
  category_changes: CategoryBreakdown;
}

export interface TradeResult {
  team_a: TradeImpact;
  team_b: TradeImpact;
}

export interface CategoryBreakdown {
  pts: number;
  reb: number;
  ast: number;
  stl: number;
  blk: number;
  tpm: number;
  fg_pct: number;
  ft_pct: number;
}

// Task/Agent types
export interface AgentTask {
  id: string;
  task_type: string;
  status: "pending" | "running" | "completed" | "failed";
  payload: Record<string, unknown>;
  result: Record<string, unknown>;
  error?: string;
  created_at: string;
  updated_at: string;
}

// UI types
export interface AIInsight {
  id: string;
  type: "start" | "bench" | "trade" | "pickup" | "drop";
  title: string;
  description: string;
  confidence: number;
  players?: Player[];
  action?: () => void;
}

export interface Command {
  id: string;
  name: string;
  description?: string;
  icon?: React.ReactNode;
  shortcut?: string;
  action: () => void;
  category?: string;
}

// Category metadata
export const CATEGORIES = [
  { key: "pts", label: "PTS", fullLabel: "Points", color: "#8b5cf6" },
  { key: "reb", label: "REB", fullLabel: "Rebounds", color: "#06b6d4" },
  { key: "ast", label: "AST", fullLabel: "Assists", color: "#10b981" },
  { key: "stl", label: "STL", fullLabel: "Steals", color: "#f59e0b" },
  { key: "blk", label: "BLK", fullLabel: "Blocks", color: "#ef4444" },
  { key: "tpm", label: "3PM", fullLabel: "3-Pointers", color: "#3b82f6" },
  { key: "fg_pct", label: "FG%", fullLabel: "Field Goal %", color: "#ec4899" },
  { key: "ft_pct", label: "FT%", fullLabel: "Free Throw %", color: "#a855f7" },
] as const;

export type CategoryKey = (typeof CATEGORIES)[number]["key"];
