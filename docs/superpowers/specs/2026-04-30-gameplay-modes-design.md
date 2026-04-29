# Gameplay Modes Expansion — Design Spec

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add four gameplay features to increase depth and replayability: visible in-level star challenges, a time-attack mode, a survival mode, and a custom difficulty mode — all accessible from a new "More Modes" modal on the map screen.

**Architecture:** Add `state.mode = 'classic' | 'survival' | 'time-attack' | 'custom'` to the existing state object. Existing functions (`initGame`, `endGame`, `getStarCount`) branch on `state.mode`. A new `modesModal` overlay is added to the map screen. All logic stays in `index.html` — no new files needed.

**Tech Stack:** Vanilla JS, Web Audio API, CSS (already in use). No new dependencies.

---

## Feature 1 — Visible Star Conditions

### What it does
Each level has three explicit star goals shown in a strip below the top bar throughout the game. Goals update in real-time (achieved = bright, not yet = dim).

### Star rules (all 10 levels)

| Level | ⭐ | ⭐⭐ | ⭐⭐⭐ |
|-------|-----|------|--------|
| 1 入门  | 通关 | 零踩雷 | 45秒内 |
| 2 初级  | 通关 | 零踩雷 | 90秒内 |
| 3 中级  | 通关 | 零踩雷 | 120秒内 |
| 4 高级  | 通关 | 零踩雷 | 150秒内 |
| 5 专家  | 通关 | 零踩雷 | 180秒内 |
| 6 挑战  | 通关 | 零踩雷 | 210秒内 |
| 7 极难  | 通关 | 零踩雷 | 240秒内 |
| 8 史诗  | 通关 | 零踩雷 | 300秒内 |
| 9 传奇  | 通关 | 零踩雷 | 360秒内 |
| 10 神话 | 通关 | 零踩雷 | 420秒内 |

### `getStarCount()` rewrite
```js
function getStarCount() {
  if (!state.won) {
    if (state.revealedSafe / state.totalSafe >= 0.7) return 1;
    return 0;
  }
  const timeLimits = [45,90,120,150,180,210,240,300,360,420];
  const limit = timeLimits[(state.level || 1) - 1];
  if (state.mineHits === 0 && state.elapsed <= limit) return 3;
  if (state.mineHits === 0) return 2;
  return 1;
}
```

### Star strip HTML (inserted after `.best-bar`, before `.main-area`)
```html
<div class="star-strip" id="starStrip">
  <div class="star-cond" id="sc1"><span class="sc-icon">⭐</span><span class="sc-text" data-i18n="sc1">通关</span></div>
  <div class="star-cond" id="sc2"><span class="sc-icon">⭐</span><span class="sc-text" id="sc2text"></span></div>
  <div class="star-cond" id="sc3"><span class="sc-icon">⭐</span><span class="sc-text" id="sc3text"></span></div>
</div>
```

### `updateStarStrip()` — called from `updateUI()` and `updateStars()`
- sc1 achieved when `state.revealedSafe === state.totalSafe` (won)
- sc2 achieved when `state.mineHits === 0`
- sc3 achieved when `state.elapsed <= timeLimits[level-1]` AND won

---

## Feature 2 — More Modes Modal

### Map screen changes
Add a 4th button to `.map-action-btns`:
```html
<button class="map-action-btn map-modes-btn" onclick="openModes()" id="mapModesBtn">
  🎮 <span data-i18n="modesBtn">更多模式</span>
</button>
```

### Modes modal HTML
```html
<div class="modal-overlay" id="modesModal" onclick="if(event.target===this)closeModes()">
  <div class="modal-card">
    <h2 class="modal-title" data-i18n="modesTitle">更多模式</h2>
    <div class="mode-card mode-time" onclick="startTimeAttack()">...</div>
    <div class="mode-card mode-surv" onclick="startSurvival()">...</div>
    <div class="mode-card mode-custom" onclick="openCustom()">...</div>
    <button class="modal-close-btn modal-close-btn--ghost" onclick="closeModes()">关闭</button>
  </div>
</div>
```

Each mode card shows the player's personal best (stored in localStorage):
- Time attack: `ta-best` key → highest score
- Survival: `surv-best` key → highest level reached

### Custom difficulty sub-panel (inside modesModal, toggled)
Three presets: Easy (8×8, 10 mines), Medium (9×9, 15 mines), Hard (10×10, 25 mines).  
A range slider adjusts mine count within ±50% of the preset default.  
Mine density shown as percentage. Warning shown if density > 40%.

---

## Feature 3 — Time Attack Mode

### State changes
```js
state.mode = 'time-attack';
state.taTimeLeft = 180; // 3 minutes countdown
state.taScore = 0;
state.taRoundsCleared = 0;
```

### Game loop changes
- `initGame()`: when `state.mode === 'time-attack'`, use fixed 9×9, 15-mine board. Skip level unlock logic.
- A **countdown timer** runs separately from `state.elapsed`. Displayed prominently in the top bar replacing the level chip.
- On win: `state.taRoundsCleared++`, add bonus points, auto-restart board. Time continues counting down.
- On lose (hit mine with no lives): lose 1 life (starts with 3), board resets, time continues.
- When `taTimeLeft` reaches 0: call `endTimeAttack()` → show overlay with final score + rounds cleared + personal best comparison.
- `endTimeAttack()` saves score to `localStorage.setItem('ta-best', score)` if new record.

### Scoring
- +10 per safe tile revealed
- +100 bonus per board cleared
- Combo multiplier applies normally

### i18n keys to add
```js
modesBtn: '更多模式', modesTitle: '更多模式',
timeAttackName: '时间挑战', timeAttackDesc: '3分钟内翻更多格子，刷新最高分',
survivalName: '生存模式', survivalDesc: '1条命连闯，看能到第几关',
customName: '自定义难度', customDesc: '选预设，微调地雷数，随心挑战',
taTimeLeft: '剩余时间', taRounds: '已通关',
survLevel: '当前关卡', survBest: '最远记录',
taOver: '时间到！', taScore: '最终得分',
survOver: '生存结束', survReached: '到达第 {n} 关',
customStart: '开始游戏', customMines: '地雷数量', customDensity: '密度',
sc1: '通关', sc2: '零踩雷', sc3Label: '{n}秒内',
modeBest: '最高分', modeRecord: '最远记录',
```
(English equivalents also added to `I18N.en`)

---

## Feature 4 — Survival Mode

### State changes
```js
state.mode = 'survival';
state.survLevel = 1;   // current survival level (1–10)
state.survScore = 0;
// lives fixed at 1 — lose = endSurvival()
```

### Game loop changes
- `initGame()`: when `state.mode === 'survival'`, use `LEVELS[state.survLevel]` config. Set `state.lives = 1`.
- On win: `state.survLevel++`, accumulate score, auto-advance to next level after 1s delay. If `survLevel > 10`, call `endSurvival(true)` — all levels cleared.
- On lose (mine with 0 lives): call `endSurvival(false)`.
- `endSurvival()`: overlay shows level reached + score. Saves `surv-best` to localStorage if new record.

### Progress bar
A row of level indicators (1–10) shown below the top bar in survival mode. Completed = green, current = pulsing amber, future = dim.

---

## File Structure

Only `index.html` is modified. Changes are additive:

| Section | Change |
|---------|--------|
| CSS | `.star-strip`, `.star-cond`, `.mode-card`, `.surv-progress`, `.custom-panel` styles |
| HTML | `#starStrip`, `#modesModal`, updated `#mapModesBtn` |
| JS i18n | ~20 new keys in both `zh` and `en` |
| JS logic | `getStarCount()` rewrite, `updateStarStrip()`, `openModes/closeModes`, `startTimeAttack`, `startSurvival`, `openCustom`, `endTimeAttack`, `endSurvival`, `initGame` mode branching, `endGame` mode branching |

---

## Out of Scope
- Online leaderboard (no backend)
- Friend challenge / share result (separate future feature)
- Seasonal themes
