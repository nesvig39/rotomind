# 🎨 Rotomind Figma Design Specifications

> Complete design specifications for building Rotomind in Figma

---

## 📐 Frame Sizes

| Screen | Width | Height | Type |
|--------|-------|--------|------|
| Desktop Dashboard | 1440px | 900px | Laptop |
| Desktop Wide | 1920px | 1080px | Monitor |
| Tablet | 768px | 1024px | iPad |
| Mobile | 375px | 812px | iPhone X |

---

## 🎨 Color Tokens

### Background Colors
```
bg-base:      #0A0A0B    (Main background)
bg-surface:   #121214    (Cards, sidebar)
bg-elevated:  #1A1A1D    (Modals, dropdowns)
bg-hover:     #252529    (Hover states)
```

### Brand Colors
```
brand:           #F97316  (Primary orange)
brand-secondary: #EA580C  (Hover orange)
brand-muted:     #431407  (Subtle backgrounds)
```

### Semantic Colors
```
success:  #22C55E  (Green - positive)
warning:  #F59E0B  (Amber - caution)
error:    #EF4444  (Red - negative)
info:     #3B82F6  (Blue - informational)
```

### Text Colors
```
text-primary:    #FAFAFA  (Main text)
text-secondary:  #A1A1AA  (Muted text)
text-tertiary:   #71717A  (Placeholder)
```

### Border Colors
```
border:        #27272A  (Default)
border-hover:  #3F3F46  (Hover)
border-focus:  #F97316  (Focus state)
```

### 8-Category Colors
```
PTS:  #8B5CF6  (Violet)
REB:  #06B6D4  (Cyan)
AST:  #10B981  (Emerald)
STL:  #F59E0B  (Amber)
BLK:  #EF4444  (Red)
3PM:  #3B82F6  (Blue)
FG%:  #EC4899  (Pink)
FT%:  #A855F7  (Purple)
```

---

## 📝 Typography

### Font Family
```
Primary: Inter (Google Fonts)
Fallback: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
```

### Type Scale
| Name | Size | Weight | Line Height | Usage |
|------|------|--------|-------------|-------|
| Display | 36px | 700 | 1.2 | Hero metrics |
| H1 | 24px | 700 | 1.3 | Page titles |
| H2 | 20px | 600 | 1.4 | Section headers |
| H3 | 16px | 600 | 1.5 | Card titles |
| Body | 14px | 400 | 1.5 | Body text |
| Small | 13px | 400 | 1.5 | Secondary text |
| Caption | 12px | 500 | 1.4 | Labels, badges |
| Micro | 11px | 600 | 1.3 | Uppercase labels |

---

## 📏 Spacing System

### Base: 4px

| Token | Value | Usage |
|-------|-------|-------|
| space-1 | 4px | Tight spacing |
| space-2 | 8px | Icon gaps |
| space-3 | 12px | Component padding |
| space-4 | 16px | Card padding |
| space-5 | 20px | Section gaps |
| space-6 | 24px | Large gaps |
| space-8 | 32px | Section padding |

---

## 🔲 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| radius-sm | 4px | Badges, small buttons |
| radius-md | 8px | Buttons, inputs, cards |
| radius-lg | 12px | Modals, large cards |
| radius-xl | 16px | Feature cards |
| radius-full | 9999px | Pills, avatars |

---

## 🌓 Shadows

### Dark Theme
```css
shadow-sm:   0 1px 2px rgba(0, 0, 0, 0.3)
shadow-md:   0 4px 6px rgba(0, 0, 0, 0.4)
shadow-lg:   0 10px 15px rgba(0, 0, 0, 0.5)
shadow-glow: 0 0 20px rgba(249, 115, 22, 0.3)
```

---

## 📦 Component Specifications

### Sidebar
```
Width: 240px (expanded), 64px (collapsed)
Background: bg-surface (#121214)
Border-right: 1px solid border (#27272A)

Logo Area:
  Height: 56px
  Padding: 0 16px
  Logo icon: 32×32px, radius-md, bg-brand

Nav Item:
  Height: 40px
  Padding: 10px 12px
  Border-radius: radius-md (8px)
  Icon: 20px
  Gap: 12px
  
  States:
    Default: text-secondary
    Hover: bg-hover, text-primary
    Active: bg-brand/10, text-brand, border 1px brand/20
```

### Header
```
Height: 56px
Background: bg-surface (#121214)
Border-bottom: 1px solid border (#27272A)
Padding: 0 24px

Search Bar:
  Width: 280px
  Height: 36px
  Background: bg-hover (#252529)
  Border: 1px solid border (#27272A)
  Border-radius: radius-md (8px)
  Padding: 0 12px
  
  Kbd Badge:
    Background: bg-surface
    Border: 1px solid border
    Border-radius: 4px
    Padding: 2px 6px
    Font-size: 11px

Icon Button:
  Size: 36×36px
  Border-radius: radius-md (8px)
  Icon-size: 20px
  
  Notification Badge:
    Size: 8×8px
    Background: brand
    Position: top-6, right-6
```

### Stat Card
```
Background: bg-surface (#121214)
Border: 1px solid border (#27272A)
Border-radius: radius-lg (12px)
Padding: 20px

Variants:
  Success: border-color rgba(34, 197, 94, 0.3), bg rgba(34, 197, 94, 0.05)
  Brand: border-color rgba(249, 115, 22, 0.2), bg rgba(249, 115, 22, 0.05)

Elements:
  Label: 13px, 500 weight, text-secondary
  Value: 28px, 700 weight, text-primary
  Change: 13px, flex with icon
    Positive: success color
    Negative: error color
    
  Icon Wrapper:
    Size: 40×40px
    Background: bg-hover
    Border-radius: radius-md
```

### Player Card
```
Background: bg-surface (#121214)
Border: 1px solid border (#27272A)
Border-radius: radius-lg (12px)
Overflow: hidden

Recommendation Banner:
  Padding: 8px 12px
  Font-size: 12px, 600 weight
  
  START: bg rgba(34, 197, 94, 0.1), text success
  BENCH: bg rgba(245, 158, 11, 0.1), text warning
  
Content:
  Padding: 16px
  
  Avatar: 48×48px, radius-full, bg-hover
  Name: 15px, 600 weight
  Meta: 13px, text-secondary
  
  Z-Score Display:
    Label: 12px, text-tertiary
    Value: 18px, 700 weight, success color
    
  Z-Stats Grid:
    4 columns, gap 8px
    Border-top: 1px solid border
    Margin-top: 12px, Padding-top: 12px
    
    Stat Label: 10px, text-tertiary
    Stat Value: 12px, 600 weight
```

### Category Bar
```
Row Height: 28px
Gap: 12px

Label: 
  Width: 36px
  Font: 12px, 600 weight
  Color: category color

Bar Background:
  Height: 12px
  Background: bg-hover (#252529)
  Border-radius: 6px
  
Bar Fill:
  Border-radius: 6px
  Background: category color
  Animation: width 0.5s ease

Rank:
  Width: 40px
  Font: 13px
  Color: text-secondary
  Text-align: right
  
Trend:
  Width: 16px
  Font: 10px
  ▲ = success, ▼ = error, → = text-tertiary
```

### Trade Builder
```
Grid: 2 columns, divided

Trade Side:
  Padding: 20px
  Border-right: 1px solid border (left side only)
  
  Header:
    Title: 15px, 600 weight
    Subtitle: 13px, text-secondary
    Margin-bottom: 16px
    
  Player Chip:
    Background: bg-surface
    Border: 1px solid border
    Border-radius: radius-md
    Padding: 12px
    Margin-bottom: 8px
    
    Avatar: 36×36px
    Name: 14px, 500 weight
    Meta: 12px, text-secondary
    Remove: text-tertiary, hover error
    
  Total Section:
    Border-top: 1px solid border
    Margin-top: 16px
    Padding-top: 16px
    
    Value:
      Negative: error color
      Positive: success color
      Font: 14px, 700 weight

Action Bar:
  Background: bg-hover
  Padding: 16px 20px
  
  Button:
    Full width
    Height: 44px
    Font: 15px
```

### Trade Impact Card
```
Same as stat card base

Overall Impact:
  Background: bg-hover
  Border-radius: radius-md
  Padding: 16px
  Display: flex, justify-between
  
  Value:
    Font: 20px, 700 weight
    Color: success (if positive)
    
Verdict Box:
  Background: rgba(34, 197, 94, 0.1)
  Border: 2px solid success
  Border-radius: radius-lg
  Padding: 20px
  
  Header:
    Font: 16px, 700 weight
    Color: success
    Icon gap: 8px
    
  Text:
    Font: 14px
    Color: text-secondary
    Line-height: 1.6
```

### Data Table
```
Border: 1px solid border
Border-radius: radius-lg
Overflow: hidden

Header Row:
  Background: bg-hover
  
  Cell:
    Padding: 12px 16px
    Font: 12px, 600 weight, uppercase
    Color: text-secondary
    Letter-spacing: 0.5px
    
Body Row:
  Border-bottom: 1px solid border
  
  Hover:
    Background: bg-hover
    
  Selected:
    Background: rgba(249, 115, 22, 0.05)
    
  Cell:
    Padding: 12px 16px
    Font: 14px
    
Player Cell:
  Display: flex, gap 12px
  Avatar: 32×32px
  Name: 14px, 500 weight
  Team: 12px, text-tertiary
  
Badge (Position):
  Background: bg-hover
  Border-radius: radius-full
  Padding: 4px 8px
  Font: 11px, 600 weight
  
Pagination:
  Border-top: 1px solid border
  Padding: 16px 20px
  
  Button:
    Padding: 6px 12px
    Border: 1px solid border
    Border-radius: radius-sm
    Font: 13px
    
    Active:
      Background: rgba(249, 115, 22, 0.1)
      Border-color: brand
      Color: brand
```

### Command Palette
```
Overlay:
  Background: rgba(0, 0, 0, 0.6)
  Backdrop-filter: blur(4px)
  
Dialog:
  Width: 560px
  Background: bg-elevated (#1A1A1D)
  Border: 1px solid border
  Border-radius: radius-xl (16px)
  Box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5)
  
Search Input:
  Height: 56px
  Padding: 0 16px
  Border-bottom: 1px solid border
  
  Icon: 18px
  Input: 16px, bg transparent
  
List:
  Max-height: 400px
  Padding: 8px
  
Group Title:
  Font: 11px, 600 weight, uppercase
  Color: text-tertiary
  Padding: 8px 12px
  
Item:
  Padding: 10px 12px
  Border-radius: radius-md
  Font: 14px
  Gap: 12px
  
  Default: text-secondary
  Hover: bg-hover, text-primary
  Selected: bg brand/10, text brand
  
  Shortcut:
    Background: bg-surface
    Border: 1px solid border
    Border-radius: 4px
    Padding: 2px 6px
    Font: 11px

Footer:
  Border-top: 1px solid border
  Padding: 12px 16px
  Font: 12px, text-tertiary
  Display: flex, justify-between
```

### Mobile Bottom Nav
```
Background: bg-surface
Border-top: 1px solid border

Item:
  Flex: 1
  Padding: 12px 8px
  Text-align: center
  
  Icon: 20px
  Label: 10px
  
  Default: text-tertiary
  Active: brand color
```

---

## 🖼️ Figma Frame Setup

### Auto Layout Settings

**Sidebar:**
- Direction: Vertical
- Padding: 0
- Gap: 0
- Fill: Hug

**Card:**
- Direction: Vertical
- Padding: 0
- Gap: 0
- Fill: Fill

**Stats Grid:**
- Direction: Horizontal
- Gap: 16
- Fill: Fill

**Player Cards Grid:**
- Direction: Horizontal
- Gap: 16
- Fill: Fill
- Wrap: Yes (for responsive)

**Category List:**
- Direction: Vertical
- Gap: 12
- Fill: Fill

---

## 📱 Responsive Breakpoints

| Breakpoint | Width | Sidebar | Columns |
|------------|-------|---------|---------|
| Desktop XL | 1920+ | 240px | 3 |
| Desktop | 1440-1919 | 240px | 3 |
| Laptop | 1024-1439 | 64px (collapsed) | 2 |
| Tablet | 768-1023 | Hidden | 2 |
| Mobile | <768 | Hidden + Bottom Nav | 1 |

---

## 🎬 Animation Specs

| Animation | Duration | Easing |
|-----------|----------|--------|
| Hover transition | 150ms | ease-in-out |
| Sidebar collapse | 200ms | ease-in-out |
| Card hover lift | 150ms | ease-out |
| Bar fill | 500ms | ease-out |
| Modal appear | 150ms | ease-out |
| Modal backdrop | 150ms | linear |

---

## 📁 Figma Page Structure

```
Rotomind Design System
├── 🎨 Foundations
│   ├── Colors
│   ├── Typography
│   ├── Spacing
│   └── Icons
├── 🧩 Components
│   ├── Buttons
│   ├── Inputs
│   ├── Cards
│   ├── Tables
│   ├── Navigation
│   └── Overlays
├── 📱 Screens
│   ├── Command Center
│   ├── Trade Analyzer
│   ├── Player Explorer
│   ├── League Standings
│   └── Mobile Views
└── 🔄 Prototypes
    └── User Flows
```

---

## ✅ Checklist for Figma

- [ ] Create color styles with all tokens
- [ ] Create text styles for type scale
- [ ] Create effect styles for shadows
- [ ] Build base components with variants
- [ ] Create responsive frames
- [ ] Add interactive prototypes
- [ ] Export assets (icons, illustrations)
- [ ] Document component usage

---

*Use these specifications alongside the HTML prototype (figma-prototype.html) for pixel-perfect Figma implementation.*
