"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Trophy,
  Users,
  UserCircle,
  ArrowLeftRight,
  Settings,
  Sparkles,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useUIStore } from "@/lib/stores/ui-store";

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const mainNavItems: NavItem[] = [
  { title: "Command Center", href: "/", icon: LayoutDashboard },
  { title: "Leagues", href: "/leagues", icon: Trophy },
  { title: "My Teams", href: "/teams", icon: Users },
  { title: "Players", href: "/players", icon: UserCircle },
  { title: "Trade Analyzer", href: "/trade-analyzer", icon: ArrowLeftRight },
];

const bottomNavItems: NavItem[] = [{ title: "Settings", href: "/settings", icon: Settings }];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();

  return (
    <TooltipProvider delayDuration={0}>
      <motion.aside
        initial={false}
        animate={{ width: sidebarCollapsed ? 64 : 240 }}
        transition={{ duration: 0.2, ease: "easeInOut" }}
        className={cn(
          "flex flex-col h-screen bg-background-surface border-r border-border",
          className
        )}
      >
        {/* Logo */}
        <div className="flex items-center h-14 px-4 border-b border-border">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand flex items-center justify-center">
              <span className="text-white font-bold text-lg">🏀</span>
            </div>
            <AnimatePresence>
              {!sidebarCollapsed && (
                <motion.span
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: "auto" }}
                  exit={{ opacity: 0, width: 0 }}
                  className="font-semibold text-lg overflow-hidden whitespace-nowrap"
                >
                  Rotomind
                </motion.span>
              )}
            </AnimatePresence>
          </Link>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
          {mainNavItems.map((item) => (
            <NavLink
              key={item.href}
              item={item}
              isActive={pathname === item.href}
              isCollapsed={sidebarCollapsed}
            />
          ))}

          <Separator className="my-4" />

          {/* AI Insights Section */}
          <div className="space-y-1">
            {!sidebarCollapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="px-3 py-2 text-xs font-medium text-foreground-tertiary uppercase tracking-wider"
              >
                AI Insights
              </motion.div>
            )}
            <InsightCard collapsed={sidebarCollapsed} />
          </div>
        </nav>

        {/* Bottom Navigation */}
        <div className="p-2 border-t border-border space-y-1">
          {bottomNavItems.map((item) => (
            <NavLink
              key={item.href}
              item={item}
              isActive={pathname === item.href}
              isCollapsed={sidebarCollapsed}
            />
          ))}

          {/* Collapse Toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebar}
            className="w-full justify-center"
          >
            {sidebarCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <>
                <ChevronLeft className="h-4 w-4 mr-2" />
                <span>Collapse</span>
              </>
            )}
          </Button>
        </div>
      </motion.aside>
    </TooltipProvider>
  );
}

interface NavLinkProps {
  item: NavItem;
  isActive: boolean;
  isCollapsed: boolean;
}

function NavLink({ item, isActive, isCollapsed }: NavLinkProps) {
  const Icon = item.icon;

  const linkContent = (
    <Link
      href={item.href}
      className={cn(
        "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
        isActive
          ? "bg-brand/10 text-brand border border-brand/20"
          : "text-foreground-secondary hover:bg-background-hover hover:text-foreground"
      )}
    >
      <Icon className={cn("h-5 w-5 flex-shrink-0", isActive && "text-brand")} />
      <AnimatePresence>
        {!isCollapsed && (
          <motion.span
            initial={{ opacity: 0, width: 0 }}
            animate={{ opacity: 1, width: "auto" }}
            exit={{ opacity: 0, width: 0 }}
            className="overflow-hidden whitespace-nowrap"
          >
            {item.title}
          </motion.span>
        )}
      </AnimatePresence>
      {item.badge && !isCollapsed && (
        <span className="ml-auto bg-brand text-white text-xs px-2 py-0.5 rounded-full">
          {item.badge}
        </span>
      )}
    </Link>
  );

  if (isCollapsed) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>{linkContent}</TooltipTrigger>
        <TooltipContent side="right">{item.title}</TooltipContent>
      </Tooltip>
    );
  }

  return linkContent;
}

interface InsightCardProps {
  collapsed: boolean;
}

function InsightCard({ collapsed }: InsightCardProps) {
  if (collapsed) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex items-center justify-center p-3 rounded-md bg-brand/5 border border-brand/20 cursor-pointer hover:bg-brand/10">
            <Sparkles className="h-5 w-5 text-brand" />
          </div>
        </TooltipTrigger>
        <TooltipContent side="right" className="max-w-xs">
          <p className="font-medium">AI Suggestion</p>
          <p className="text-sm text-foreground-secondary">
            Start Tyrese Maxey over Jrue Holiday tonight
          </p>
        </TooltipContent>
      </Tooltip>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="p-3 rounded-md bg-brand/5 border border-brand/20"
    >
      <div className="flex items-start gap-2">
        <Sparkles className="h-4 w-4 text-brand mt-0.5 flex-shrink-0" />
        <div className="min-w-0">
          <p className="text-sm font-medium text-foreground">Start Maxey Tonight</p>
          <p className="text-xs text-foreground-secondary mt-1">
            Tyrese Maxey has a higher ceiling vs ORL than Jrue Holiday.
          </p>
        </div>
      </div>
    </motion.div>
  );
}
