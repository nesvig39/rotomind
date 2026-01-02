# 🏀 Rotomind Frontend

A modern, Databricks One-inspired frontend for the Fantasy NBA Assistant.

## 🎨 Design Philosophy

This frontend is inspired by [Databricks One](https://www.databricks.com/blog/introducing-databricks-one) - a unified AI platform that brings together data, analytics, and AI in one seamless experience.

### Key Design Principles

1. **Unified Experience**: All fantasy management tools in one cohesive platform
2. **Intelligence First**: AI recommendations surface proactively, not hidden in menus
3. **Context-Aware**: The UI adapts based on user activity
4. **Real-Time**: Live updates for stats, standings, and injury reports
5. **Accessible**: Full keyboard navigation and screen reader support

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS |
| Components | shadcn/ui + Radix |
| State | TanStack Query + Zustand |
| Charts | Recharts |
| Animations | Framer Motion |
| Command Palette | cmdk |

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- npm or pnpm
- Backend API running at `http://localhost:8000`

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── (dashboard)/       # Main authenticated routes
│   │   ├── page.tsx       # Command Center (home)
│   │   ├── players/       # Player Explorer
│   │   ├── trade-analyzer/# Trade Analysis
│   │   └── layout.tsx     # Dashboard layout
│   ├── globals.css        # Global styles
│   └── layout.tsx         # Root layout
├── components/
│   ├── ui/                # Base UI components
│   ├── layout/            # Sidebar, Header, Command Palette
│   ├── features/          # Feature-specific components
│   └── charts/            # Data visualization
├── lib/
│   ├── api/               # API client
│   ├── hooks/             # React hooks
│   ├── stores/            # Zustand stores
│   ├── types/             # TypeScript types
│   └── utils/             # Utility functions
└── public/                # Static assets
```

## 🎯 Key Features

### Command Center (Dashboard)
- Real-time standings overview
- AI-powered lineup recommendations
- Category breakdown visualization
- Hot waiver wire picks

### Trade Analyzer
- Interactive trade builder
- Real-time Z-score impact analysis
- Category-by-category breakdown
- AI-powered trade verdicts

### Player Explorer
- Sortable player rankings
- Z-score visualization
- Position/team filtering
- Quick stats panel

### Command Palette (⌘K)
- Quick navigation
- AI suggestions
- Recent actions
- Keyboard-first design

## 🎨 Design System

### Colors
- **Brand**: Orange (#f97316) - Basketball-inspired accent
- **Dark Theme**: Default with light mode support
- **Category Colors**: Unique color per stat category

### Typography
- **Sans**: Inter (UI text)
- **Mono**: JetBrains Mono (code, stats)

### Components
- Built on Radix primitives for accessibility
- Consistent spacing (4px grid)
- Subtle animations with Framer Motion

## 📱 Responsive Design

The UI is fully responsive:
- **Desktop**: Full sidebar, multi-column layouts
- **Tablet**: Collapsible sidebar, 2-column grids
- **Mobile**: Bottom navigation, single-column layouts

## 🧪 Testing

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Component development
npm run storybook
```

## 📦 Build

```bash
# Production build
npm run build

# Start production server
npm start
```

## 🔗 API Integration

The frontend connects to the FastAPI backend at `NEXT_PUBLIC_API_URL`.

Key endpoints used:
- `GET /players` - Player list
- `GET /stats` - Player Z-scores
- `POST /analyze/trade` - Trade analysis
- `POST /recommend/lineup` - Lineup recommendations
- `GET /leagues/{id}/standings` - League standings

## 📝 Development Notes

### Adding New Components

1. Create component in appropriate directory
2. Export from index file
3. Add Storybook story for documentation

### State Management

- **Server State**: TanStack Query (caching, refetching)
- **UI State**: Zustand (theme, sidebar, modals)
- **Form State**: React Hook Form + Zod

### Code Style

- TypeScript strict mode
- ESLint + Prettier
- Component-first architecture
- Colocation of related code

---

Built with ❤️ for fantasy basketball managers.
