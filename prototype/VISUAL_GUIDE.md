# 🎨 Visual Guide - Understanding the Matrix Screen

This guide explains how to identify where you are in the Matrix and what you can do.

---

## 🎯 Finding Your Current Node

### Multiple Visual Indicators

Your current node (where you are) is **highlighted in 5 different ways**:

#### 1. **Bright Cyan Border** (`#═══║`)
```
Normal node:          Current node (YOU):
+----------+          #===========#
| Data     |          ║ ICE      ║
| +ZDR:6   |          ║ !ZDR:8   ║
+----------+          #===========#
```

- Normal nodes: Gray `+` `-` `|`
- **Current node: Bright cyan** `#` `=` `║`

#### 2. **Yellow Text Inside**
```
Normal node:          Current node (YOU):
+----------+          #===========#
| ICE      |          ║ ICE      ║  ← Yellow text!
| !ZDR:8   |          ║ !ZDR:8   ║
+----------+          #===========#
```

- Normal nodes: Gray text
- **Current node: Bright yellow text**

#### 3. **Dark Cyan Background**
```
#===========#
║░ICE░░░░░░║  ← Cyan-tinted background
║░!ZDR:8░░░║
#===========#
```

The entire interior has a **dark cyan tint** - no other node has this.

#### 4. **Arrow Markers Around It**
```
      [ YOU ]        ← Label above
         v           ← Top arrow
    #===========#
 >  ║ ICE      ║  <  ← Left/right arrows
    ║ !ZDR:8   ║
    #===========#
         ^           ← Bottom arrow
```

**Four arrows** point to your current node from all sides.

#### 5. **"[ YOU ]" Label Above**
```
      [ YOU ]        ← This label only appears above current node
    #===========#
    ║ ICE      ║
    ║ !ZDR:8   ║
    #===========#
```

---

## 📺 Screen Layout

### Title Bar (Top)
```
════════════════════════════════════════════════════════════════════════════════
MATRIX — ICE-Guardian [ICE]                    ← Current node name + type!
────────────────────────────────────────────────────────────────────────────────
PPL: 6  |  Zone: Security Grid  |  ZDR: 8  |  Status: SAFE (0.75x)
════════════════════════════════════════════════════════════════════════════════
```

**The title bar shows your current node's name!**
- "MATRIX — ICE-Guardian [ICE]"
- Changes when you move to a different node

### Side Panel (Right)
```
════════════════════════════════════════════════════════════════════════════════
[STATUS]
════════════════════════════════════════════════════════════════════════════════
=== CURRENT NODE ===
Name: ICE-Guardian     ← Your current node
Type: ICE              ← Node type
ZDR: 8 | Status: SAFE

=== WHAT TO DO ===
→ SPACE: Engage ICE    ← What you can do here
→ Arrow keys: Move
→ ESC: Leave matrix

Visited: 3 nodes
════════════════════════════════════════════════════════════════════════════════
```

**Always look here** to confirm where you are and what you can do.

### Footer (Bottom)
```
════════════════════════════════════════════════════════════════════════════════
Step 5  T+12.3s  |  >>> Moved ↑ UP to ICE-Guardian (ICE)
════════════════════════════════════════════════════════════════════════════════
```

Shows your **most recent action** - confirms where you moved.

---

## 🆕 Phase 1-5 — Visual Layer 추가

Phase 1-5 (ADR-0060, ADR-0061) 가 추가한 시각 레이어 (전부 ASCII):

| Phase | 시각 효과 | 트리거 |
|---|---|---|
| 1 | **2-D BSP 그리드** (방 + 복도 + 룸 타입 색상) | `D` 토글 |
| 1.5 | **Jack-in glitch** (글리치 burst + 슬로모) | JAC-IN |
| 1.5 | **Room flash** (단색 짧은 플래시) | ICE 처치 |
| 1.5 | **Data acquired** (파티클 + 시네마틱 텍스트) | DATA 픽업 |
| 1.5 | **Jack-out whiteout** (백색 폭발 + 시네마틱) | JAC-OUT |
| 2 | **BSP 미로** (시드별 다른 레이아웃) | 매 런 |
| 5 | **Novel Hook dispatch** (자동 트리거 시 텍스트 표시) | 상태 천이 |

### VFX 4종 (Phase 1.5)

```
[jackin_glitch]   ─ 글리치 글리프 burst + 슬로모션 16ms
                    트리거: 미션 시작 / JAC-IN
[room_flash]      ─ 단색 짧은 플래시 (~80ms)
                    트리거: ICE 처치 / 방 클리어
[data_acquired]   ─ 파티클 + '>> DATA FRAGMENT RECOVERED' 시네마틱
                    트리거: DATA 노드 픽업
[jackout_whiteout] ─ 백색 폭발 + '>> JACKING OUT...' 시네마틱
                    트리거: EXIT 도달 / JAC-OUT
```

검증:
```bash
PYTHONPATH=src .venv/bin/python scripts/play_vfx_overlay.py
```

---

## 🎨 Node Appearance Comparison

### Side-by-Side

```
  NORMAL NODE              YOUR CURRENT NODE (5 INDICATORS!)

  +----------+              [ YOU ]           ← 1. Label
  | Data     |                 v              ← 2. Arrow
  | +ZDR:6   |           #===========#        ← 3. Cyan border
  +----------+        >  ║░ICE░░░░░░║  <      ← 4. Arrows L/R
                         ║░!ZDR:8░░░║         ← 5. Yellow + Cyan BG
                         #===========#
                              ^
```

### Colors
- **Normal node border**: Gray `(200, 200, 200)`
- **Current node border**: Bright cyan `(0, 255, 255)`
- **Normal node text**: Gray `(200, 200, 200)`
- **Current node text**: Bright yellow `(255, 255, 0)`
- **Current node background**: Dark cyan `(0, 64, 64)`

---

## 🧭 Navigation Feedback

### Before Moving
```
Title:  MATRIX — Entry [Entry]
        
      [ YOU ]
    #===========#
    ║ Entry    ║  ← You are here
    ║ =ZDR:0   ║
    #===========#

Side:   Name: Entry
        Type: Entry
```

### Press → (Right Arrow)
```
Footer: >>> Moved → RIGHT to DATA-7F (Data)
```

### After Moving
```
Title:  MATRIX — DATA-7F [Data]  ← Changed!
        
      [ YOU ]
    #===========#
    ║ Data     ║  ← You moved here
    ║ +ZDR:6   ║
    #===========#

Side:   Name: DATA-7F          ← Changed!
        Type: Data             ← Changed!
```

**Three places update simultaneously:**
1. **Title bar** - Shows new node name
2. **Visual highlight** - Moves to new node
3. **Side panel** - Shows new node info

---

## 🎯 Quick Reference Card

### "Where am I?"

Look for **ANY** of these:

| Indicator | What to Look For |
|-----------|------------------|
| **Border** | `#═══║` instead of `+---\|` |
| **Color** | Bright cyan border, not gray |
| **Text** | Yellow text inside box |
| **Background** | Dark cyan tint inside |
| **Arrows** | `> < v ^` pointing at the box |
| **Label** | `[ YOU ]` above the box |
| **Title** | Node name in title bar |
| **Side Panel** | "=== CURRENT NODE ===" |

**If you see ANY of these, that's your current node!**

### "Where can I move?"

Look for **gray boxes connected by lines** to your cyan box:

```
    #===========#
    ║ ICE      ║  ← YOU
    #===========#
         |
         |
    +----------+
    | Data     |  ← You can move here (gray, connected)
    +----------+
```

Use **← → ↑ ↓** to move toward connected nodes.

---

## 💡 Pro Tips

### Tip 1: Use the Title Bar
**The title bar always shows where you are!**
- No need to search the screen
- Just read: "MATRIX — [Node Name] [Type]"

### Tip 2: Check Side Panel First
Before moving, check:
```
=== WHAT TO DO ===
→ SPACE: Extract data    ← What you can do at THIS node
```

### Tip 3: Watch the Footer
After every move:
```
>>> Moved ↑ UP to ICE-Guardian (ICE)
```
Confirms where you went.

### Tip 4: Count the Indicators
If you're unsure, count the visual differences:
1. Cyan border? ✓
2. Yellow text? ✓
3. Cyan background? ✓
4. Arrows? ✓
5. "YOU" label? ✓

**5 indicators = That's definitely you!**

---

## 🐛 Troubleshooting

### "I still can't tell where I am"

**Check these in order:**

1. **Title bar** (very top):
   - Says "MATRIX — [Some Name] [Type]"?
   - That's where you are!

2. **Side panel** (right side):
   - Says "=== CURRENT NODE ==="?
   - The name shown is where you are!

3. **Look for cyan** (#═══║):
   - Find the ONLY node with cyan borders
   - That's you!

4. **Look for "[ YOU ]"**:
   - Find the ONLY label that says "[ YOU ]"
   - Right below it is your node!

### "Multiple nodes look similar"

Only **ONE** node has:
- Cyan border (all others are gray)
- Yellow text (all others are gray)
- Cyan background (all others are black)
- "[ YOU ]" label (only one has this)

**If you see cyan, that's you. Period.**

### "Colors don't show"

Run font test:
```bash
make test-tcod
```

If colors don't work, rely on:
- `#═══║` vs `+---\|` (different characters)
- "[ YOU ]" label (text only)
- Title bar showing node name

---

## 🎮 Practice Exercise

Try this to get familiar:

1. **Start demo**: `make demo`
2. **Skip to Matrix**: Press ESC twice
3. **Identify current node**:
   - Find the cyan border
   - Read "[ YOU ]" label
   - Check title bar
   - Confirm in side panel
4. **Move once**: Press → (right arrow)
5. **Watch what changes**:
   - Title bar updates
   - Highlight moves
   - Side panel updates
   - Footer confirms
6. **Repeat**: Move ← ↑ ↓ and observe changes

After 3-4 moves, you'll **instantly recognize** your current node!

---

**Summary: Your current node has a bright cyan border, yellow text, cyan background, arrows pointing at it, and "[ YOU ]" label above it. It's impossible to miss!** 🎯
