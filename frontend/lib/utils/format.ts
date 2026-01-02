import { format, formatDistanceToNow } from "date-fns";

/**
 * Format a number with sign prefix for Z-scores
 */
export function formatZScore(value: number, decimals = 1): string {
  const formatted = Math.abs(value).toFixed(decimals);
  if (value > 0) return `+${formatted}`;
  if (value < 0) return `-${formatted}`;
  return formatted;
}

/**
 * Get CSS class for Z-score coloring
 */
export function getZScoreClass(value: number): string {
  if (value > 0.5) return "z-positive";
  if (value < -0.5) return "z-negative";
  return "z-neutral";
}

/**
 * Format a percentage
 */
export function formatPercent(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format a date for display
 */
export function formatDate(date: string | Date, pattern = "MMM d, yyyy"): string {
  return format(new Date(date), pattern);
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
}

/**
 * Format a large number with abbreviation
 */
export function formatNumber(value: number): string {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`;
  }
  return value.toString();
}

/**
 * Format ordinal (1st, 2nd, 3rd, etc.)
 */
export function formatOrdinal(n: number): string {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}
