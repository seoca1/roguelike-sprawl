# 📊 Status Panel Guide

The persistent right-side panel that shows everything you need to know at a glance.

---

## 🎯 What Is It?

A **permanent panel on the right side** of the screen that displays:

1. **Player Stats** - Grade, PPL, HP, AP
2. **Current Location** - Screen, current node, position
3. **Mission Info** - Active mission, client, reward, objective
4. **Inventory** - Materials and items you have
5. **Recent Activity** - Last 3 actions

**Always visible** across all screens (Matrix, Combat, Hub, Cinematic).

---

## 📺 Layout

### Screen Structure

```
┌─────────────────────────────────────────┬─────────────────────────┐
│ TITLE BAR (full width)                  │ (cut off, divider here) │
├─────────────────────────────────────────┤                         │
│                                         │ ┌─────────────────────┐ │
│                                         │ │ PLAYER              │ │
│                                         │ │ Grade: 1            │ │
│                                         │ │ PPL: 6              │ │
│         MAIN CONTENT                    │ │                     │ │
│       (Matrix / Combat / etc.)          │ │ WHERE               │ │
│                                         │ │ Screen: MATRIX      │ │
│                                         │ │ At: DATA-7F         │ │
│                                         │ │ Type: Data          │ │
│                                         │ │ Visited: 3/7        │ │
│                                         │ │                     │ │
│                                         │ │ MISSION             │ │
│                                         │ │ First Jack          │ │
│                                         │ │ Client: Finn        │ │
│                                         │ │ Reward: 500 cr      │ │
│                                         │ │ Obj: Get the data   │ │
│                                         │ │                     │ │
│                                         │ │ INVENTORY           │ │
│                                         │ │ (empty)             │ │
│                                         │ │                     │ │
│                                         │ │ ACTIVITY            │ │
│                                         │ │ Moved ↑ UP to       │ │
│                                         │ │ DATA-7F             │ │
│                                         │ └─────────────────────┘ │
├─────────────────────────────────────────┴─────────────────────────┤
│ CONTROLS (full width)                                             │
├────────────────────────────────────────────────────────────────────┤
│ FOOTER                                                             │
└────────────────────────────────────────────────────────────────────┘
```

**Width**: 28 columns (right side)  
**Height**: 35 rows (vertical, matches main content)

---

## 📋 Sections Explained

### 1. PLAYER Section
```
=============================
 PLAYER
=============================
Grade: 1
PPL:   6
HP:    100/100
AP:    3/6
[==========      ]  ← HP bar (color-coded)
```

**What it shows**:
- **Grade** (1, 2, 3...): Player progression level
- **PPL** (Player Power Level): Combat strength
- **HP/AP** (in combat only): Current health and action points
- **HP bar**: Visual health with color coding

**Color coding**:
- **HP >= 70%**: Green `(0, 255, 0)`
- **HP 30-70%**: Yellow `(255, 255, 0)`
- **HP < 30%**: Red `(255, 50, 50)`

### 2. WHERE Section
```
-----------------------------
 WHERE
-----------------------------
Screen: MATRIX
At: DATA-7F          ← Current node name
Type: Data           ← Node type
Visited: 3/7         ← Progress
```

**Screen-specific info**:
- **Matrix**: Current node, type, visited count
- **Combat**: Enemy name, enemy HP
- **Hub**: "At: The Sprawl Hub"
- **Cinematic**: Current scene title

### 3. MISSION Section
```
-----------------------------
 MISSION
-----------------------------
First Jack           ← Mission title
Client: Finn         ← Who gave it
Reward: 500 cr       ← What you get
Obj:                 ← Objective
Get the demo file
```

**Shows**:
- Active mission title
- Client (NPC who gave it)
- Reward (credits)
- Objective description

**If no mission**:
```
MISSION
(none active)
```

### 4. INVENTORY Section
```
-----------------------------
 INVENTORY
-----------------------------
ICE Shard x3
Data Fragment x2
Combat Module x1
```

**Shows top 3 items** in your inventory.

**If empty**:
```
INVENTORY
(empty)
```

### 5. ACTIVITY Section
```
-----------------------------
 ACTIVITY
-----------------------------
Moved ↑ UP to DATA-7F
SCAN: DATA-7F (data)
Action menu opened
```

**Shows last 3 actions** - your recent activity log.

**If no activity**:
```
ACTIVITY
(no activity)
```

---

## 🎮 Why This Helps

### No More Guessing

**Before** (had to look in multiple places):
- Title bar for screen
- Side panel for current node
- Title for stats
- Memory for inventory
- Footer for last action

**After** (all in one place):
- Glance right side → everything you need

### Better Decision Making

In combat, you can see:
- Your HP (is it low?)
- Your AP (can I use a skill?)
- Your enemy (what am I fighting?)
- Your mission (what's the goal?)

All without leaving the main screen!

### Context Awareness

The panel **adapts** to current screen:
- **Matrix**: Shows current node info
- **Combat**: Shows enemy HP
- **Hub**: Shows hub status
- **Cinematic**: Shows scene name

---

## 🔍 Screen-by-Screen

### Matrix Screen
```
PLAYER
Grade: 1  PPL: 6

WHERE
Screen: MATRIX
At: ICE-Guardian    ← Current node
Type: ICE           ← Node type
Visited: 4/7        ← Progress

MISSION
First Jack
Reward: 500 cr

ACTIVITY
Moved ↑ UP to ICE-Guardian
```

**Useful for**: Knowing where you are, progress, objective

### Combat Screen
```
PLAYER
Grade: 1  PPL: 6
HP: 80/100          ← Damage taken
AP: 3/6             ← Resources
[========  ]       ← Visual HP

WHERE
Screen: COMBAT
Enemy: ICE-Sentinel ← Fighting who
EHp: 120/150       ← Enemy HP

MISSION
First Jack
Obj: Get the data

ACTIVITY
Used skill: ATTACK
Selected: ICE BREAKER
```

**Useful for**: Tracking both your and enemy HP, mission goal

### Hub Screen
```
PLAYER
Grade: 1  PPL: 6

WHERE
Screen: HUB
At: The Sprawl Hub

MISSION
First Jack
Reward: 500 cr

INVENTORY
ICE Shard x2
```

**Useful for**: Seeing inventory before crafting/buying

### Cinematic Screen
```
PLAYER
Grade: 1  PPL: 6

WHERE
Screen: CINEMATIC
Scene: PROLOGUE

ACTIVITY
Story advancing...
```

**Useful for**: Knowing which story scene is playing

---

## 🆕 Phase 1-5 — Status Panel 확장

Phase 1-5 (ADR-0060, ADR-0061) 가 추가한 status panel 항목:

| Phase | 항목 | 표시 위치 |
|---|---|---|
| 1 | `dungeon_mode: True/False` | 상태 헤더 (Matrix/Dungeon 토글) |
| 1.5 | VFX 활성 카운터 (`fx.has_active_effects()`) | Matrix / Combat footer |
| 2 | `mission_grade` + `character_ref` | 미션 시작 시 status |
| 3 | `(rooms, edges)` — 매핑된 미션 형태 | 미션 카드 hover |
| 4 | ECS `cleared_rooms` / `visited_rooms` 카운트 | Matrix HUD |
| 5 | `current_novel_stem` — dispatch 중인 단편 | Cinematic overlay |

### Dungeon Mode 표시

`D` 키로 토글 시 status panel 에 다음이 표시:

```
WHERE
Screen: MATRIX (DUNGEON MODE)
Layout: BSP seed=42 grade=1 ref=veteran
```

검증 (BSP 미로 + ECS 통합):
```bash
PYTHONPATH=src .venv/bin/python scripts/play_dungeon_mode.py
PYTHONPATH=src .venv/bin/python scripts/play_ecs_dungeon.py
```

---

## 💡 Reading Tips

### HP/AP in Combat
- **HP at 80%**: Green, you have lots of health
- **HP at 50%**: Yellow, be careful
- **HP at 20%**: Red, consider defending

### Activity Log
The **most recent message** is at the bottom (most recent).

```
ACTIVITY
> Moved ↑ UP         ← Older
> SCAN: DATA-7F      ← Middle
> EXTRACT: Data OK   ← Newest
```

### Color Meanings
- **Cyan title bars**: Section headers
- **Yellow text**: Important info (current item, objectives)
- **Red text**: Warning/danger
- **Green text**: Good/healthy
- **Gray text**: Normal info

---

## 🔧 Technical Details

### Width Allocation
- **Screen width**: 80 columns
- **Main content**: 52 columns
- **Status panel**: 28 columns

### Always Visible
The panel is **rendered on top of** the screen content but doesn't block interaction. You can still:
- See your current location
- Move with arrow keys
- Use skills

### Updates
The panel **updates every frame** in real-time:
- HP/AP change instantly
- Inventory updates after pickups
- Activity log appends after every action

---

## 🐛 Troubleshooting

### "Panel covers part of the screen"
The panel takes 28 columns on the right. Main content is now 52 columns wide.
- **This is normal** - the layout was redesigned
- Most content fits in 52 columns

### "Some info shows (none) or (empty)"
This means you don't have that data yet:
- `(none active)` = No mission selected
- `(empty)` = No items in inventory
- `(no activity)` = First frame, no actions yet

### "Can't read text"
Try:
- Increasing terminal font size
- Use fullscreen mode
- Read text version: `make text-demo`

---

## 📊 Quick Reference

| Section | What | When Useful |
|---------|------|-------------|
| **PLAYER** | Your stats | Always |
| **WHERE** | Current location | Navigation |
| **MISSION** | Active job | Goal tracking |
| **INVENTORY** | Your items | Crafting/trading |
| **ACTIVITY** | Recent actions | Confirming actions |

**Key insight**: Glance right → know everything!

---

## 🎮 Try It

```bash
make demo
```

Watch the right panel:
1. **Prologue**: Scene name appears
2. **Briefing**: Mission info appears
3. **Matrix**: Current node updates as you move
4. **Combat**: HP/AP/Enemy HP all visible

**The panel is your persistent dashboard** - always shows what's important! 📊
