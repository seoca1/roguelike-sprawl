# 🏰 Dungeon Mode + NPC Events Guide

Complete walkthrough of the new dungeon-style exploration and NPC dialogue system.

---

## 🎯 What's New

### **Dungeon-Style Matrix**
- 2D grid layout (7×5 rooms)
- Cardinal direction movement (N/S/E/W)
- Visual corridors between rooms
- Color-coded room types

### **NPC Encounters**
- Dialogue trees with player choices
- Info gathering, item rewards, combat
- Multiple NPCs (Dixie Flatline, etc.)
- Arrow-key navigation for choices

### **Combat Results**
- Victory rewards (materials, credits)
- Inventory system
- Continue exploring after combat

---

## 🏰 Dungeon Layout

### Map Structure (7 cols × 5 rows)

```
   0    1    2    3    4    5    6
   +----+----+----+----+----+----+----+
0  |    |    |    |    |    |    |    |
   +----+----+----+----+----+----+----+
1  |    | SR |    |    |    |    |    |
   +----+----+----+----+----+----+----+
2  | E--|--C-|--N-|--C-|--D-|--C-|--I--|
   +----+----+----+----+----+----+----+
3  |    |    |    |    |    | SR | >> |
   +----+----+----+----+----+----+----+
4  |    |    |    |    |    |    |    |
   +----+----+----+----+----+----+----+

Legend:
  E = Entry         D = Data Vault
  N = NPC (Dixie)   I = ICE
  C = Corridor      SR = Side Room
  >> = Exit
```

### Path to Victory
```
Entry → Corridor → Dixie (NPC) → Corridor → Data → Corridor → ICE → Exit
   0,2     1,2        2,2         3,2      4,2     5,2      6,2   6,3
```

---

## 🎮 Movement Controls

### Cardinal Directions Only

| Key | Direction | Effect |
|-----|-----------|--------|
| **↑** | NORTH (Up) | Move to room above |
| **↓** | SOUTH (Down) | Move to room below |
| **←** | WEST (Left) | Move to room left |
| **→** | EAST (Right) | Move to room right |

**Important**: You can ONLY move to directly connected rooms.

### Visual Feedback

**Each room** has:
- **Border color** by type:
  - **Cyan**: Current room (you)
  - **Red**: ICE (danger)
  - **Gold**: Data (objective)
  - **Magenta**: NPC
  - **Green**: Exit
  - **Gray**: Corridor/router

- **Glyph** in the center:
  - `▶` Player marker
  - `$` Data
  - `!` ICE
  - `?` NPC
  - `·` Corridor

---

## 🎭 NPC Encounters

### How to Start

1. Move to NPC room (magenta border, `?` glyph)
2. Press **SPACE** to open action menu
3. NPC encounter starts automatically

### Dixie Flatline (First NPC)

When you reach Dixie's room and press SPACE:

```
┌──────────────────────────────────────┐
│ NPC ENCOUNTER — Dixie Flatline       │
├──────────────────────────────────────┤
│                                      │
│ ◇D◇ Dixie Flatline                   │
│ ==================================== │
│                                      │
│ Heh. You don't look like a regular   │
│ jacker. The Finn send you?           │
│                                      │
│ What do you say?                     │
│                                      │
│ > [1] Yeah, I'm on a job...          │
│   [2] Who wants to know?             │
│   [3] Got any advice?                │
│                                      │
└──────────────────────────────────────┘
```

### Navigation

- **↑↓**: Select choice
- **ENTER**: Confirm
- **1-9**: Quick select

### Choice Effects

| Effect | Result |
|--------|--------|
| **GAIN_INFO** | Learn something (logged in activity) |
| **GOODBYE** | End conversation, return to matrix |
| **CONTINUE** | Show NPC response, advance dialogue |
| **GIVE_ITEM** | Receive item in inventory |

### Example: Choice 3 (Ask for advice)

```
Player selects: [3] Got any advice?

Result:
  >>> Got any advice for navigating this grid?
  >>> Dixie shares tactical info.
  >>> Learned: The ICE blocks the direct path. Find another way.
```

---

## ⚔️ Combat Flow

### Entering Combat

1. Navigate to ICE room (red border, `!` glyph)
2. Press **SPACE**
3. Select **ENGAGE** or press **E**
4. Combat screen appears

### Combat Process

**Auto-combat in demo mode**:
- Auto-attacks every 2s
- Auto-skill usage for testing
- Combat ends when one side HP = 0

**Manual mode**:
- ↑↓: Select skill
- ENTER: Use skill
- 1-4: Quick use
- ESC: Flee

### Victory Results

When you win:

```
=== Combat finished: victory ===
>>> Rewards: 1x ICE Shard, 50 credits

[VICTORY SCREEN]
Outcome: VICTORY
Duration: 12.4s
Your HP: 85/100

>>> Gained: 1x ICE Shard
>>> Gained: 50 credits

(Returns to Matrix after 3s)
```

### What You Get

**On victory**:
- 1× ICE Shard (crafting material)
- 50 credits
- XP toward next grade (future)
- Continue matrix exploration

**On defeat**:
- Return to Hub
- Lose some progress (future)
- Can retry

---

## 📊 Status Panel Updates

Your persistent right panel now shows:

```
PLAYER
Grade: 1
PPL:   6

WHERE
Screen: MATRIX
At: Dixie Flatline    ← Current room
Type: construct       ← NPC type

INVENTORY              ← NEW!
ICE Shard x1          ← Reward from combat

ACTIVITY
VICTORY! Gained: 1x ICE Shard
Moved → to ICE Barrier
```

---

## 🎯 Complete Demo Walkthrough

### Full Flow: Prologue → NPC → Combat → Result

**1. Prologue** (auto)
```
>>> "The sky above the port was the color of television..."
>>> Glitch effects
```

**2. Briefing** (auto)
```
♠F♠ FINN: Got something for you.
♠F♠ FINN: 500 credits. Easy run.
```

**3. Matrix - Enter Dungeon**
```
[ ENTRY ]  → → → [ DIXIE ]
    ↓               ↓
  SIDE         CORRIDOR
```

**4. Navigate to NPC**
- Press → (move east)
- Press → (arrive at Dixie)
- Status: "Moved → to Dixie Flatline"

**5. NPC Encounter**
- Press SPACE
- Choose dialogue option
- Learn about ICE tactics

**6. Continue to Data**
- Press → (corridor)
- Press → (data vault)
- Status: "Moved → to Data Vault"

**7. Continue to ICE**
- Press → (corridor)
- Press → (ICE barrier)
- Status: "Moved → to ICE Barrier"

**8. Combat!**
- Press SPACE → E (engage)
- Auto-combat runs
- Victory screen

**9. Results**
```
>>> VICTORY!
>>> Gained: 1x ICE Shard
>>> INVENTORY: ICE Shard x1
```

**10. Continue or Exit**
- Can return to Exit
- Or re-explore dungeon
- Demo ends

---

## 💡 Pro Tips

### Navigation
- **Cardinal only**: Use ↑↓←→, not diagonal
- **Check connections**: Each room shows valid exits
- **Path planning**: Plan route through dungeon

### NPC Strategy
- **Ask questions**: Learn useful info (logged in status)
- **Multiple visits**: Can return to NPCs (Phase 6+)
- **Effects matter**: Some choices give items, some just info

### Combat Strategy
- **Save AP for big skills**: Don't waste on basic attacks
- **Watch cooldowns**: Heavy skills have cooldowns
- **Position matters**: ICE blocks exit - defeat it first

### Inventory Tips
- **ICE Shards**: Used for crafting combat programs
- **Data Fragments**: From data nodes
- **Trade in Hub**: Visit market (Phase 6+)

---

## 🐛 Troubleshooting

### "Can't move in direction"
That direction has no connected room. Try another direction.

### "NPC won't talk"
Make sure you're ON the NPC room (current position), then press SPACE.

### "Combat is too fast/slow"
In demo mode, combat is auto. Manual mode is for player control.

### "Inventory not showing"
Check status panel right side → "INVENTORY" section. Updates after combat victory.

---

## 🔄 What's Different from Old System

### Old System
- Abstract graph view
- Free direction movement
- No NPCs
- No rewards after combat
- Linear storytelling

### New System (Dungeon Mode)
- 2D grid visualization
- **Cardinal direction** only
- **NPC encounters** with choices
- **Combat rewards** (items, credits)
- **Inventory system**

**More like classic roguelikes!**

---

## 🎮 Try It

```bash
make demo
```

**Watch the flow**:
1. Prologue (auto-advance)
2. Briefing (auto-advance)
3. **Dungeon loads** ← New!
4. **Auto-navigate** to NPC
5. **NPC dialogue** ← New!
6. **Continue to ICE**
7. **Combat** (auto)
8. **Victory + rewards** ← New!

**Total time**: ~20 seconds for full flow

---

## 📊 Summary

| Feature | Status |
|---------|--------|
| **Dungeon Grid** | ✅ 7×5 rooms |
| **Cardinal Movement** | ✅ N/S/E/W only |
| **Visual Corridors** | ✅ ASCII lines |
| **Room Types** | ✅ Entry, Data, ICE, NPC, Exit |
| **Color Coding** | ✅ By room type |
| **NPC System** | ✅ Dialogue trees |
| **Dixie Flatline** | ✅ Full event |
| **Choice Effects** | ✅ Info, items, etc. |
| **Combat Rewards** | ✅ Materials, credits |
| **Inventory** | ✅ item_id → count |
| **Status Panel** | ✅ Shows inventory |

**All 124 tests passing** ✅

---

## 🏆 Achievement Unlocked

You can now experience the **complete cyberpunk loop**:
1. **Story** (Prologue, Briefing)
2. **Exploration** (Dungeon, NPCs)
3. **Combat** (ICE encounter)
4. **Rewards** (Inventory, progress)
5. **Continue** (More story, more runs)

**Just like Neuromancer!** 🌃⚡
