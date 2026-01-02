"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Trophy,
  Users,
  UserCircle,
  ArrowLeftRight,
  Settings,
  RefreshCw,
  Sparkles,
  Search,
  Zap,
} from "lucide-react";
import { useUIStore } from "@/lib/stores/ui-store";
import { cn } from "@/lib/utils/cn";

interface CommandItem {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  shortcut?: string;
  action: () => void;
  category: string;
}

export function CommandPalette() {
  const router = useRouter();
  const { commandPaletteOpen, setCommandPaletteOpen } = useUIStore();
  const [search, setSearch] = React.useState("");

  // Keyboard shortcut to open
  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setCommandPaletteOpen(!commandPaletteOpen);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, [commandPaletteOpen, setCommandPaletteOpen]);

  const commands: CommandItem[] = React.useMemo(
    () => [
      // Quick Actions
      {
        id: "trade",
        name: "Analyze Trade",
        icon: ArrowLeftRight,
        shortcut: "⌘T",
        action: () => router.push("/trade-analyzer"),
        category: "Quick Actions",
      },
      {
        id: "standings",
        name: "View Standings",
        icon: Trophy,
        shortcut: "⌘S",
        action: () => router.push("/leagues"),
        category: "Quick Actions",
      },
      {
        id: "sync",
        name: "Sync ESPN Rosters",
        icon: RefreshCw,
        shortcut: "⌘R",
        action: () => console.log("Sync"),
        category: "Quick Actions",
      },
      {
        id: "players",
        name: "Search Players",
        icon: UserCircle,
        shortcut: "⌘P",
        action: () => router.push("/players"),
        category: "Quick Actions",
      },

      // Navigation
      {
        id: "nav-home",
        name: "Go to Command Center",
        icon: LayoutDashboard,
        action: () => router.push("/"),
        category: "Navigation",
      },
      {
        id: "nav-leagues",
        name: "Go to Leagues",
        icon: Trophy,
        action: () => router.push("/leagues"),
        category: "Navigation",
      },
      {
        id: "nav-teams",
        name: "Go to My Teams",
        icon: Users,
        action: () => router.push("/teams"),
        category: "Navigation",
      },
      {
        id: "nav-settings",
        name: "Go to Settings",
        icon: Settings,
        action: () => router.push("/settings"),
        category: "Navigation",
      },
    ],
    [router]
  );

  const aiSuggestions = [
    { id: "ai-1", text: "Drop Kyle Kuzma for Cason Wallace" },
    { id: "ai-2", text: "Start Maxey tonight vs ORL" },
    { id: "ai-3", text: "Trade window closes in 2 days" },
  ];

  const handleSelect = (action: () => void) => {
    action();
    setCommandPaletteOpen(false);
    setSearch("");
  };

  return (
    <AnimatePresence>
      {commandPaletteOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={() => setCommandPaletteOpen(false)}
          />

          {/* Command Dialog */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ duration: 0.15 }}
            className="fixed top-[20%] left-1/2 -translate-x-1/2 w-full max-w-xl z-50"
          >
            <Command
              className="bg-background-elevated border border-border rounded-xl shadow-2xl overflow-hidden"
              loop
            >
              {/* Search Input */}
              <div className="flex items-center border-b border-border px-4">
                <Search className="h-5 w-5 text-foreground-tertiary mr-2" />
                <Command.Input
                  value={search}
                  onValueChange={setSearch}
                  placeholder="Type a command or search..."
                  className="flex-1 h-12 bg-transparent text-foreground placeholder:text-foreground-tertiary focus:outline-none"
                />
              </div>

              <Command.List className="max-h-[400px] overflow-y-auto p-2">
                <Command.Empty className="py-6 text-center text-sm text-foreground-secondary">
                  No results found.
                </Command.Empty>

                {/* Quick Actions */}
                <Command.Group heading="Quick Actions" className="px-2 py-1.5">
                  <span className="text-xs font-medium text-foreground-tertiary uppercase tracking-wider">
                    Quick Actions
                  </span>
                  {commands
                    .filter((c) => c.category === "Quick Actions")
                    .map((command) => (
                      <CommandItem
                        key={command.id}
                        command={command}
                        onSelect={() => handleSelect(command.action)}
                      />
                    ))}
                </Command.Group>

                {/* AI Suggestions */}
                <Command.Group heading="AI Suggestions" className="px-2 py-1.5 mt-2">
                  <span className="text-xs font-medium text-foreground-tertiary uppercase tracking-wider flex items-center gap-1">
                    <Sparkles className="h-3 w-3" />
                    AI Suggestions
                  </span>
                  {aiSuggestions.map((suggestion) => (
                    <Command.Item
                      key={suggestion.id}
                      value={suggestion.text}
                      onSelect={() => handleSelect(() => console.log(suggestion.text))}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2 rounded-md cursor-pointer text-sm",
                        "text-foreground-secondary hover:bg-background-hover hover:text-foreground",
                        "aria-selected:bg-brand/10 aria-selected:text-brand"
                      )}
                    >
                      <Zap className="h-4 w-4 text-brand" />
                      <span>{suggestion.text}</span>
                    </Command.Item>
                  ))}
                </Command.Group>

                {/* Navigation */}
                <Command.Group heading="Navigation" className="px-2 py-1.5 mt-2">
                  <span className="text-xs font-medium text-foreground-tertiary uppercase tracking-wider">
                    Navigation
                  </span>
                  {commands
                    .filter((c) => c.category === "Navigation")
                    .map((command) => (
                      <CommandItem
                        key={command.id}
                        command={command}
                        onSelect={() => handleSelect(command.action)}
                      />
                    ))}
                </Command.Group>
              </Command.List>

              {/* Footer */}
              <div className="border-t border-border px-4 py-2 flex items-center justify-between text-xs text-foreground-tertiary">
                <div className="flex items-center gap-4">
                  <span>
                    <kbd className="px-1.5 py-0.5 bg-background-surface rounded border border-border">
                      ↑↓
                    </kbd>{" "}
                    Navigate
                  </span>
                  <span>
                    <kbd className="px-1.5 py-0.5 bg-background-surface rounded border border-border">
                      ↵
                    </kbd>{" "}
                    Select
                  </span>
                </div>
                <span>
                  <kbd className="px-1.5 py-0.5 bg-background-surface rounded border border-border">
                    esc
                  </kbd>{" "}
                  Close
                </span>
              </div>
            </Command>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

interface CommandItemProps {
  command: CommandItem;
  onSelect: () => void;
}

function CommandItem({ command, onSelect }: CommandItemProps) {
  const Icon = command.icon;

  return (
    <Command.Item
      value={command.name}
      onSelect={onSelect}
      className={cn(
        "flex items-center gap-3 px-3 py-2 rounded-md cursor-pointer text-sm",
        "text-foreground-secondary hover:bg-background-hover hover:text-foreground",
        "aria-selected:bg-brand/10 aria-selected:text-brand"
      )}
    >
      <Icon className="h-4 w-4" />
      <span className="flex-1">{command.name}</span>
      {command.shortcut && (
        <kbd className="text-xs bg-background-surface px-1.5 py-0.5 rounded border border-border">
          {command.shortcut}
        </kbd>
      )}
    </Command.Item>
  );
}
