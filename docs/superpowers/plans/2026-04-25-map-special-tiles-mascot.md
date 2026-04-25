# 扫雷增强：地图 / 特殊格 / 角色动画 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an adventure map level-selection screen, three types of special surprise tiles, and a rich mascot expression system to the single-file minesweeper game.

**Architecture:** All changes are in `D:/projects/minesweeper/index.html`. Feature A (map screen) adds a new `#map-screen` div that covers the viewport, with JS show/hide toggling `display` on both divs. Feature C (special tiles) adds a `state.specials` 2-D array and CSS pulsing glow on hidden tiles; effects fire via `triggerSpecial()` called from `floodReveal`. Feature E (mascot) adds CSS animation classes on `.mascot-wrap` and `.turtle-wrap`, toggled by a single `setMascotMood()` call from game event handlers.

**Tech Stack:** Vanilla HTML/CSS/JS, inline SVG scene illustrations, CSS `@keyframes`, `localStorage`.

---

## File Map

| Section | What changes |
|---------|-------------|
| `<style>` | +map screen, +special glow, +mascot mood, +click-phrase CSS |
| `<body>` (before `game-wrap`) | +`#map-screen` div |
| `game-wrap` div | +`id="game-wrap"` + `style="display:none"` |
| Top-bar HTML | +Map button, overlay btn `onclick` → `overlayBtnClick()` |
| `I18N` zh + en | +mapTitle, mapSub, mapBtn, specialStar/Chest/Boost toasts, catPhrases array |
| JS: new module-level vars | `currentScreen`, `mascotMood`, `catPhraseIdx`, `idleTimer` |
| JS: `state` object | +`specials`, `boostActive`, `_justUnlocked` |
| JS: `initGame()` | +initialize specials/boostActive, call `resetIdleTimer()` |
| JS: `placeMines()` | +call `placeSpecials()` + `applySpecialGlow()` at end |
| JS: `endGame()` | +unlock next level, set `_justUnlocked`, call `setMascotMood` |
| JS: `showOverlay()` | +`setStars()`, conditional overlay-btn label |
| JS: `floodReveal()` | +`setTimeout(()=>triggerSpecial(r,c),200)` for special cells |
| JS: `triggerCombo()` | +`setMascotMood` calls at combo 3 and 6 |
| JS: `handleClick()` | +`setMascotMood('scared')`, `setTurtleMood('scared')` |
| JS: boot | `applyLang(); showMapScreen();` (remove `initGame()`) |
| JS: new functions | `showMapScreen`, `showGameScreen`, `enterLevel`, `renderMapScreen`, `overlayBtnClick`, `getUnlockedLevel`, `setUnlockedLevel`, `getStars`, `setStars`, `placeSpecials`, `applySpecialGlow`, `triggerSpecial`, `activateBoost`, `setMascotMood`, `setTurtleMood`, `showCatPhrase`, `resetIdleTimer` |

---

## ── Feature A: Adventure Map Screen ──────────────────────────────────────────

### Task 1: Map Screen HTML + game-wrap id

**Files:**
- Modify: `D:/projects/minesweeper/index.html`

- [ ] **Step 1: Add id and hide game-wrap**

Find (line ~348):
```html
<div class="game-wrap">
```
Replace with:
```html
<div class="game-wrap" id="game-wrap" style="display:none">
```

- [ ] **Step 2: Insert map-screen div before game-wrap**

Insert the following block immediately before `<div class="game-wrap" id="game-wrap"`:
```html
<!-- ── Map Screen ── -->
<div id="map-screen" class="map-screen">
  <h1 class="map-title" data-i18n="mapTitle">选择关卡</h1>
  <p class="map-sub" data-i18n="mapSub">完成关卡解锁下一个地点！</p>
  <div class="map-cards" id="mapCards"></div>
</div>
```

- [ ] **Step 3: Change overlay button onclick**

Find:
```html
<button class="overlay-btn" id="overlayBtn" onclick="resetGame()"></button>
```
Replace with:
```html
<button class="overlay-btn" id="overlayBtn" onclick="overlayBtnClick()"></button>
```

- [ ] **Step 4: Add Map button to top-bar**

Find:
```html
<button class="btn-icon" id="btnLang" onclick="toggleLang()">
```
Insert immediately before it:
```html
<button class="btn-icon" id="btnMap" onclick="showMapScreen()" title="Map">🗺️</button>
```

- [ ] **Step 5: Open browser at http://localhost:3456**

Verify: page shows "选择关卡" title on the gradient background. The game grid is not visible. No JS errors in DevTools console.

- [ ] **Step 6: Commit**
```bash
cd D:/projects/minesweeper && git add index.html && git commit -m "feat(map): add map screen HTML and hide game-wrap by default"
```

---

### Task 2: Map Screen + Special Tile + Mascot CSS

**Files:**
- Modify: `D:/projects/minesweeper/index.html` (`<style>` block)

- [ ] **Step 1: Add map screen CSS**

Insert this block inside `<style>`, right before the closing `</style>` tag:
```css
/* ── Map Screen ── */
.map-screen{position:fixed;inset:0;z-index:50;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px;}
.map-title{font-family:'Fredoka One',cursive;font-size:38px;color:white;text-shadow:0 3px 14px rgba(0,0,0,0.32);margin-bottom:6px;letter-spacing:1px;}
.map-sub{font-size:14px;font-weight:800;color:rgba(255,255,255,0.82);margin-bottom:26px;}
.map-cards{display:flex;gap:14px;flex-wrap:wrap;justify-content:center;max-width:900px;}
.level-card{background:rgba(255,255,255,0.18);border:3px solid rgba(255,255,255,0.65);border-radius:28px;padding:18px 14px 16px;width:155px;text-align:center;backdrop-filter:blur(8px);box-shadow:0 8px 32px rgba(40,20,100,0.28);transition:transform .2s,box-shadow .2s;position:relative;overflow:hidden;cursor:pointer;}
.level-card:not(.locked):hover{transform:translateY(-7px) scale(1.05);box-shadow:0 18px 44px rgba(40,20,100,0.45);}
.level-card.locked{filter:saturate(0.25) brightness(0.85);cursor:not-allowed;}
.level-card-scene{width:96px;height:96px;border-radius:50%;margin:0 auto 12px;overflow:hidden;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 16px rgba(0,0,0,0.18);}
.level-card-scene svg{width:96px;height:96px;}
.level-card-name{font-family:'Fredoka One',cursive;font-size:16px;color:white;text-shadow:0 2px 8px rgba(0,0,0,0.3);margin-bottom:3px;}
.level-card-diff{font-size:11px;font-weight:800;color:rgba(255,255,255,0.7);margin-bottom:7px;}
.level-card-stars{font-size:14px;letter-spacing:1px;min-height:18px;color:white;}
.level-card-lock{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.42);border-radius:25px;font-size:38px;}
@keyframes cardUnlock{0%{filter:saturate(0.25) brightness(0.85)}100%{filter:saturate(1) brightness(1)}}
.level-card.just-unlocked{animation:cardUnlock .7s .1s ease forwards;}
.level-card.just-unlocked .level-card-lock{animation:unlockPop .6s ease forwards;opacity:0;}
@keyframes unlockPop{0%{transform:scale(1.2);opacity:1}100%{transform:scale(0.4);opacity:0}}

/* ── Special Tiles ── */
@keyframes glowGold{0%,100%{box-shadow:0 5px 0 #7060B8,inset 0 1px 0 rgba(255,255,255,.45),0 2px 10px rgba(80,50,180,.25),0 0 4px 0 rgba(255,215,0,.25)}50%{box-shadow:0 5px 0 #7060B8,inset 0 1px 0 rgba(255,255,255,.45),0 2px 10px rgba(80,50,180,.25),0 0 14px 5px rgba(255,215,0,.6)}}
@keyframes glowBlue{0%,100%{box-shadow:0 5px 0 #7060B8,inset 0 1px 0 rgba(255,255,255,.45),0 2px 10px rgba(80,50,180,.25),0 0 4px 0 rgba(56,189,248,.25)}50%{box-shadow:0 5px 0 #7060B8,inset 0 1px 0 rgba(255,255,255,.45),0 2px 10px rgba(80,50,180,.25),0 0 14px 5px rgba(56,189,248,.6)}}
@keyframes glowPurple{0%,100%{box-shadow:0 5px 0 #7060B8,inset 0 1px 0 rgba(255,255,255,.45),0 2px 10px rgba(80,50,180,.25),0 0 4px 0 rgba(167,139,250,.25)}50%{box-shadow:0 5px 0 #7060B8,inset 0 1px 0 rgba(255,255,255,.45),0 2px 10px rgba(80,50,180,.25),0 0 14px 5px rgba(167,139,250,.6)}}
.tile.hidden.sp-star{animation:glowGold 2s ease-in-out infinite;}
.tile.hidden.sp-chest{animation:glowBlue 2.2s ease-in-out infinite;}
.tile.hidden.sp-boost{animation:glowPurple 1.8s ease-in-out infinite;}
@keyframes specialReveal{0%{transform:scale(1)}40%{transform:scale(1.28)}70%{transform:scale(0.92)}100%{transform:scale(1)}}
.tile.special-pop{animation:specialReveal .38s cubic-bezier(.34,1.56,.64,1);}
.special-icon-overlay{position:absolute;pointer-events:none;z-index:30;font-size:32px;animation:specialIconFloat 1s ease-out forwards;}
@keyframes specialIconFloat{0%{transform:translateY(0) scale(1.2);opacity:1}100%{transform:translateY(-52px) scale(0.6);opacity:0}}
.timer-boost{position:relative;}.timer-boost::after{content:'⚡';font-size:13px;position:absolute;top:-2px;right:-18px;animation:boostBlink .5s ease-in-out infinite alternate;}
@keyframes boostBlink{from{opacity:1}to{opacity:.25}}

/* ── Mascot Moods ── */
.mascot-wrap.mascot--happy{animation:catHappy .5s ease-in-out infinite alternate;}
@keyframes catHappy{0%{transform:translateY(-4px) scale(1.05) rotate(-3deg)}100%{transform:translateY(-14px) scale(1.1) rotate(3deg)}}
.mascot-wrap.mascot--scared{animation:catScared .4s ease-in-out 3;}
@keyframes catScared{0%,100%{transform:translateY(0) rotate(0)}25%{transform:translateY(-8px) rotate(7deg)}75%{transform:translateY(-6px) rotate(-7deg)}}
.mascot-wrap.mascot--cheer{animation:catCheer .32s ease-in-out infinite alternate;}
@keyframes catCheer{0%{transform:translateY(0) rotate(-6deg)}100%{transform:translateY(-20px) scale(1.12) rotate(6deg)}}
.mascot-wrap.mascot--cry{animation:catCry 1.6s ease-in-out infinite;}
@keyframes catCry{0%,100%{transform:translateY(0) rotate(-1deg)}50%{transform:translateY(-4px) rotate(1deg)}}
.mascot-expr{position:absolute;bottom:-4px;left:50%;transform:translateX(-50%);font-size:24px;pointer-events:none;z-index:5;animation:exprPop .3s cubic-bezier(.34,1.56,.64,1) both;}
@keyframes exprPop{from{transform:translateX(-50%) scale(0)}to{transform:translateX(-50%) scale(1)}}
.cat-star-particle{position:absolute;pointer-events:none;z-index:6;font-size:16px;animation:starParticle .85s ease-out forwards;}
@keyframes starParticle{0%{transform:translate(0,0) scale(1);opacity:1}100%{transform:translate(var(--tx),var(--ty)) scale(0.3);opacity:0}}
.turtle-wrap.turtle--scared{animation:turtleHide .45s ease-in-out forwards;}
@keyframes turtleHide{0%{transform:rotate(-4deg) translateY(0)}100%{transform:rotate(0) translateY(22px)}}
.turtle-wrap.turtle--happy{animation:turtleHappy .4s ease-in-out infinite alternate;}
@keyframes turtleHappy{0%{transform:rotate(-7deg) translateY(0)}100%{transform:rotate(7deg) translateY(-12px)}}
.click-phrase{position:absolute;top:-16px;left:50%;transform:translateX(-50%);white-space:nowrap;background:white;border-radius:14px;padding:6px 12px;font-size:12px;font-weight:900;color:#7C3AED;border:2px solid #E8DEFF;box-shadow:0 4px 14px rgba(100,60,200,0.2);pointer-events:none;z-index:10;animation:phraseFloat 2.5s ease-out forwards;}
.click-phrase::after{content:'';position:absolute;bottom:-10px;left:50%;transform:translateX(-50%);border:6px solid transparent;border-top-color:white;}
@keyframes phraseFloat{0%{opacity:0;transform:translateX(-50%) translateY(0)}15%{opacity:1;transform:translateX(-50%) translateY(-8px)}80%{opacity:1;transform:translateX(-50%) translateY(-12px)}100%{opacity:0;transform:translateX(-50%) translateY(-22px)}}
```

- [ ] **Step 2: Verify CSS loads without errors**

Open http://localhost:3456 in browser. DevTools console → no errors. Map screen title still visible.

- [ ] **Step 3: Commit**
```bash
git add index.html && git commit -m "feat: add map/special/mascot CSS animations"
```

---

### Task 3: Map Screen JavaScript

**Files:**
- Modify: `D:/projects/minesweeper/index.html` (JS section)

- [ ] **Step 1: Add i18n keys to I18N.zh**

In `I18N.zh`, after `achUnlock:'成就解锁',`, add:
```js
mapTitle:'选择关卡',mapSub:'完成关卡解锁下一个地点！',mapBtn:'返回地图',
specialStar:'⭐ 幸运星！+50分奖励！',specialChest:'💎 宝箱！获得一个提示！',specialBoost:'⚡ 加速！计时暂停5秒！',
catPhrases:['加油！你一定行的！','仔细想想，答案就在眼前！','好棒！继续保持！','没关系，再试一次！','你是最厉害的小探险家！','相信自己！','慢慢来，不着急～','耶！离胜利不远了！'],
```

- [ ] **Step 2: Add i18n keys to I18N.en**

In `I18N.en`, after `achUnlock:'Achievement Unlocked',`, add:
```js
mapTitle:'Choose Level',mapSub:'Complete a level to unlock the next!',mapBtn:'Back to Map',
specialStar:'⭐ Lucky Star! +50 bonus!',specialChest:'💎 Treasure! Got a hint!',specialBoost:'⚡ Boost! Timer paused 5s!',
catPhrases:['You can do it!','Think carefully, the answer is close!','Great job, keep it up!','No worries, try again!','You are the greatest explorer!','Believe in yourself!','Take your time~','Woohoo! Victory is near!'],
```

- [ ] **Step 3: Add module-level variables after the `pick` function**

Find:
```js
const pick=a=>a[Math.floor(Math.random()*a.length)];
```
Insert immediately after it:
```js
// ─── Map screen state ──────────────────────────────────────────────────────────
let currentScreen='map';
let mascotMood='default';
let catPhraseIdx=0;
let idleTimer=null;
```

- [ ] **Step 4: Add localStorage helpers after the new module variables**

Insert after the four `let` declarations:
```js
const getUnlockedLevel=()=>parseInt(localStorage.getItem('sweeper-unlock')||'1');
const setUnlockedLevel=n=>{if(n>getUnlockedLevel())localStorage.setItem('sweeper-unlock',String(n));};
const getStars=lv=>parseInt(localStorage.getItem(`sweeper-stars-${lv}`)||'0');
const setStars=(lv,s)=>{if(s>getStars(lv))localStorage.setItem(`sweeper-stars-${lv}`,String(s));};
```

- [ ] **Step 5: Add MAP_SCENES constant and renderMapScreen()**

Insert after the `setStars` declaration:
```js
const MAP_SCENES=[
  `<svg viewBox="0 0 96 96" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="48" cy="48" r="48" fill="#4ADE80"/><circle cx="48" cy="48" r="40" fill="#22C55E"/><rect x="44" y="62" width="8" height="20" rx="3" fill="#92400E"/><polygon points="48,10 20,52 76,52" fill="#15803D"/><polygon points="48,22 24,58 72,58" fill="#166534"/><polygon points="48,30 28,62 68,62" fill="#14532D"/><circle cx="76" cy="22" r="10" fill="#FDE68A"/></svg>`,
  `<svg viewBox="0 0 96 96" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="48" cy="48" r="48" fill="#FBBF24"/><circle cx="48" cy="48" r="40" fill="#F59E0B"/><path d="M8 80 Q28 56 48 70 Q68 84 88 66 L88 88 L8 88Z" fill="#D97706"/><rect x="45" y="28" width="6" height="42" rx="3" fill="#15803D"/><rect x="29" y="42" width="16" height="6" rx="3" fill="#15803D"/><rect x="51" y="34" width="16" height="6" rx="3" fill="#15803D"/><circle cx="72" cy="24" r="12" fill="#FDE68A" opacity=".9"/></svg>`,
  `<svg viewBox="0 0 96 96" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="48" cy="48" r="48" fill="#38BDF8"/><circle cx="48" cy="48" r="40" fill="#0284C7"/><path d="M8 60 Q20 48 32 60 Q44 72 56 60 Q68 48 80 60 L88 88 L8 88Z" fill="#0369A1"/><ellipse cx="36" cy="46" rx="13" ry="7" fill="#FDE68A"/><polygon points="49,46 58,40 58,52" fill="#FDE68A"/><circle cx="31" cy="44" r="2" fill="#1F2937"/><circle cx="68" cy="24" r="10" fill="#FDE68A"/></svg>`,
  `<svg viewBox="0 0 96 96" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="48" cy="48" r="48" fill="#BAE6FD"/><circle cx="48" cy="48" r="40" fill="#E0F2FE"/><polygon points="48,12 12,76 84,76" fill="white"/><polygon points="48,12 30,52 66,52" fill="#BAE6FD"/><circle cx="18" cy="28" r="3" fill="white" opacity=".8"/><circle cx="76" cy="20" r="2.5" fill="white" opacity=".8"/><text x="48" y="90" font-size="18" text-anchor="middle" fill="#0284C7">❄️</text></svg>`,
  `<svg viewBox="0 0 96 96" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="48" cy="48" r="48" fill="#1E1B4B"/><circle cx="48" cy="48" r="40" fill="#312E81"/><circle cx="20" cy="20" r="2" fill="white"/><circle cx="72" cy="14" r="1.5" fill="white"/><circle cx="82" cy="38" r="2" fill="#FDE68A"/><circle cx="12" cy="62" r="1.5" fill="white"/><circle cx="84" cy="72" r="2" fill="white"/><circle cx="30" cy="78" r="1.5" fill="#FDE68A"/><rect x="42" y="34" width="12" height="30" rx="6" fill="#F87171"/><polygon points="48,22 42,36 54,36" fill="#FECDD3"/><rect x="35" y="50" width="7" height="14" rx="3" fill="#FCA5A5"/><rect x="54" y="50" width="7" height="14" rx="3" fill="#FCA5A5"/><circle cx="48" cy="50" r="5" fill="#BFDBFE"/><path d="M44 64 Q48 78 52 64" fill="#FB923C" opacity=".9"/></svg>`,
];

function renderMapScreen(){
  const unlocked=getUnlockedLevel();
  const names={zh:['🌲 森林','🏜️ 沙漠','🌊 海洋','⛰️ 雪山','🚀 太空'],en:['🌲 Forest','🏜️ Desert','🌊 Ocean','⛰️ Snow','🚀 Space']};
  const diffs={zh:['入门·6×6','初级·8×8','中级·9×9','高级·10×10','专家·10×10'],en:['Starter·6×6','Easy·8×8','Medium·9×9','Hard·10×10','Expert·10×10']};
  const container=document.getElementById('mapCards');if(!container)return;
  container.innerHTML=[1,2,3,4,5].map(lv=>{
    const locked=lv>unlocked;
    const s=getStars(lv);
    const starStr=s>0?'⭐'.repeat(s)+'☆'.repeat(3-s):'☆☆☆';
    return `<div class="level-card${locked?' locked':''}" id="lvcard-${lv}"${locked?'':` onclick="enterLevel(${lv})"`}>`+
      `<div class="level-card-scene">${MAP_SCENES[lv-1]}</div>`+
      `<div class="level-card-name">${names[lang][lv-1]}</div>`+
      `<div class="level-card-diff">${diffs[lang][lv-1]}</div>`+
      `<div class="level-card-stars">${starStr}</div>`+
      (locked?'<div class="level-card-lock">🔒</div>':'')+
      `</div>`;
  }).join('');
}

function showMapScreen(){
  currentScreen='map';
  renderMapScreen();
  document.getElementById('map-screen').style.display='flex';
  document.getElementById('game-wrap').style.display='none';
  if(state._justUnlocked){
    const lv=state._justUnlocked;state._justUnlocked=null;
    setTimeout(()=>{const card=document.getElementById(`lvcard-${lv}`);if(card)card.classList.add('just-unlocked');},300);
  }
}

function showGameScreen(){
  currentScreen='game';
  document.getElementById('map-screen').style.display='none';
  document.getElementById('game-wrap').style.display='';
}

function enterLevel(n){
  state.level=n;state.hints=3;state.peeks=3;state.safeDigs=3;
  showGameScreen();initGame();
  document.getElementById('levelSelect').value=n;
}

function overlayBtnClick(){
  document.getElementById('overlay').classList.remove('show');
  if(state.won){showMapScreen();}else{resetGame();}
}
```

- [ ] **Step 6: Update applyLang() to refresh map when on map screen**

In `applyLang()`, find the last statement `renderBestBar();` and add after it:
```js
if(currentScreen==='map')renderMapScreen();
```

- [ ] **Step 7: Update boot sequence**

Find at the very end of the `<script>`:
```js
applyLang();
initGame();
```
Replace with:
```js
applyLang();
showMapScreen();
```

- [ ] **Step 8: Verify map screen in browser**

Open http://localhost:3456. Should see 5 level cards. Level 1 has no lock, levels 2-5 are locked (desaturated + 🔒). Clicking level 1 → game screen appears. Language toggle → card names update. Back to map button (🗺️) → returns to map.

- [ ] **Step 9: Commit**
```bash
git add index.html && git commit -m "feat(map): map screen JS - render, unlock, screen switching"
```

---

### Task 4: Win Flow → Unlock + Return to Map

**Files:**
- Modify: `D:/projects/minesweeper/index.html`

- [ ] **Step 1: Add `_justUnlocked` and `specials`/`boostActive` to state declaration**

Find the `let state={` block. Replace the closing of the block:
```js
  combo:0,comboTimer:null,bestCombo:0,
};
```
With:
```js
  combo:0,comboTimer:null,bestCombo:0,
  specials:[],boostActive:false,_justUnlocked:null,
};
```

- [ ] **Step 2: Store stars in showOverlay()**

In `showOverlay(won)`, find:
```js
const isNew=won&&setBest(state.level,state.score);
```
Replace with:
```js
const isNew=won&&setBest(state.level,state.score);
if(won)setStars(state.level,stars);
```

- [ ] **Step 3: Unlock next level and set overlay btn label in showOverlay()**

In `showOverlay(won)`, find:
```js
document.getElementById('overlayBtn').textContent=t('playAgain');
```
Replace with:
```js
document.getElementById('overlayBtn').textContent=won?t('mapBtn'):t('playAgain');
```

- [ ] **Step 4: Unlock next level in endGame() on win**

In `endGame(won)`, find:
```js
    const stars=getStarCount();
    setTimeout(()=>{checkAchievements(true,stars);showOverlay(true);},800);
```
Replace with:
```js
    const stars=getStarCount();
    if(state.level<5){setUnlockedLevel(state.level+1);state._justUnlocked=state.level+1;}
    setTimeout(()=>{checkAchievements(true,stars);showOverlay(true);},800);
```

- [ ] **Step 5: Verify full win flow**

Play level 1 to completion. Overlay shows "返回地图". Click → map appears with level 2 now unlocked and the card has a brief unlock animation. Level 1 card shows the earned stars.

- [ ] **Step 6: Verify loss flow**

Lose level 1 (let lives reach 0). Overlay shows "再玩一次！". Click → resets same level in game screen (no map shown).

- [ ] **Step 7: Commit**
```bash
git add index.html && git commit -m "feat(map): win unlocks next level and returns to map"
```

---

## ── Feature C: Special Tiles ─────────────────────────────────────────────────

### Task 5: Special Tiles Data Layer + Glow

**Files:**
- Modify: `D:/projects/minesweeper/index.html`

- [ ] **Step 1: Initialize specials in initGame()**

In `initGame()`, find the `Object.assign(state,{` block. Add inside it (after `combo:0,bestCombo:0,`):
```js
    specials:Array.from({length:cfg.size},()=>Array(cfg.size).fill(null)),
    boostActive:false,
```

- [ ] **Step 2: Add placeSpecials() after neighborMines()**

Insert after the `neighborMines` function:
```js
function placeSpecials(){
  const types=['star','chest','boost'];
  const count=state.level<=2?2:3;
  // Prefer number cells (adjacentMines > 0) so they require deliberate clicks
  const candidates=[];
  for(let r=0;r<state.size;r++)for(let c=0;c<state.size;c++)
    if(state.board[r][c]>0)candidates.push([r,c]);
  // Shuffle candidates
  for(let i=candidates.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[candidates[i],candidates[j]]=[candidates[j],candidates[i]];}
  candidates.slice(0,count).forEach(([r,c],i)=>{state.specials[r][c]=types[i%types.length];});
}

function applySpecialGlow(){
  for(let r=0;r<state.size;r++)for(let c=0;c<state.size;c++){
    const sp=state.specials[r]&&state.specials[r][c];if(!sp)continue;
    const tile=getTileEl(r,c);if(tile)tile.classList.add(`sp-${sp}`);
  }
}
```

- [ ] **Step 3: Call placeSpecials + applySpecialGlow from placeMines()**

In `placeMines()`, find the last line:
```js
  for(let r=0;r<state.size;r++)for(let c=0;c<state.size;c++)if(state.board[r][c]!==-1)state.board[r][c]=neighborMines(r,c);
```
Add after it:
```js
  placeSpecials();applySpecialGlow();
```

- [ ] **Step 4: Verify special tile glow in browser**

Open http://localhost:3456, enter level 1. After the first tile click, look for 2 tiles with a subtle colored glow (gold/blue/purple pulsing). Inspect DevTools to confirm `.sp-star`, `.sp-chest`, or `.sp-boost` classes on tile elements.

- [ ] **Step 5: Commit**
```bash
git add index.html && git commit -m "feat(specials): data layer, placement, and CSS glow"
```

---

### Task 6: Special Tile Reveal Effects

**Files:**
- Modify: `D:/projects/minesweeper/index.html`

- [ ] **Step 1: Add triggerSpecial() and activateBoost() after applySpecialGlow()**

```js
function triggerSpecial(r,c){
  const sp=state.specials[r]&&state.specials[r][c];if(!sp)return;
  state.specials[r][c]=null;
  const tile=getTileEl(r,c);
  if(tile){tile.classList.remove(`sp-${sp}`);tile.classList.add('special-pop');setTimeout(()=>tile.classList.remove('special-pop'),420);}
  // Floating icon
  const grid=document.getElementById('gameGrid');
  if(tile&&grid){
    const gr=grid.getBoundingClientRect(),tr=tile.getBoundingClientRect();
    const icon=document.createElement('div');icon.className='special-icon-overlay';
    icon.textContent=sp==='star'?'⭐':sp==='chest'?'💎':'⚡';
    icon.style.cssText=`left:${tr.left-gr.left+tr.width/2-20}px;top:${tr.top-gr.top-10}px`;
    grid.appendChild(icon);setTimeout(()=>icon.remove(),1050);
  }
  // Apply effect
  if(sp==='star'){state.score+=50;updateUI();showToast(t('specialStar'));}
  else if(sp==='chest'){state.hints=Math.min(state.hints+1,9);updatePowerupUI();showToast(t('specialChest'));}
  else if(sp==='boost'){activateBoost();}
}

function activateBoost(){
  if(state.boostActive)return;
  state.boostActive=true;
  clearInterval(state.timerInterval);state.timerInterval=null;
  const timerEl=document.getElementById('timerDisplay');
  if(timerEl)timerEl.closest('.stat-panel').classList.add('timer-boost');
  showToast(t('specialBoost'));
  setTimeout(()=>{
    state.boostActive=false;
    const el=document.getElementById('timerDisplay');
    if(el)el.closest('.stat-panel').classList.remove('timer-boost');
    if(!state.gameOver&&!state.paused&&state.gameStarted)startTimer();
  },5000);
}
```

- [ ] **Step 2: Call triggerSpecial from floodReveal()**

In `floodReveal()`, find:
```js
    if(state.board[cr][cc]!==-1){state.revealedSafe++;state.score+=10;count++;}
```
Replace with:
```js
    if(state.board[cr][cc]!==-1){state.revealedSafe++;state.score+=10;count++;
      if(state.specials[cr]&&state.specials[cr][cc])setTimeout(()=>triggerSpecial(cr,cc),220);}
```

- [ ] **Step 3: Verify all three special effects**

Play a game and find the glowing tiles. Reveal them:
- **Gold glow (⭐)**: score increases by 50, toast "⭐ 幸运星！+50分奖励！"
- **Blue glow (💎)**: hint count on button increases by 1, toast "💎 宝箱！获得一个提示！"
- **Purple glow (⚡)**: timer stops for 5s (confirm by counting seconds), then resumes, toast "⚡ 加速！"

- [ ] **Step 4: Commit**
```bash
git add index.html && git commit -m "feat(specials): reveal effects, bonus score, hint +1, timer boost"
```

---

## ── Feature E: Mascot Expressions ────────────────────────────────────────────

### Task 7: Cat Mascot Expression System

**Files:**
- Modify: `D:/projects/minesweeper/index.html`

- [ ] **Step 1: Add setMascotMood() after the updateSpeech() function**

Find:
```js
function updateSpeech(){const pct=state.revealedSafe/state.totalSafe;setSpeech(pick(pct>.7?t('warn'):t('good')));}
```
Insert after it:
```js
// ─── Mascot moods ─────────────────────────────────────────────────────────────
function setMascotMood(mood,duration){
  const wrap=document.querySelector('.mascot-wrap');if(!wrap)return;
  wrap.classList.remove('mascot--happy','mascot--scared','mascot--cheer','mascot--cry');
  if(mood!=='default')wrap.classList.add(`mascot--${mood}`);
  mascotMood=mood;
  // Expression overlay emoji
  const old=wrap.querySelector('.mascot-expr');if(old)old.remove();
  const exprMap={happy:'😊',scared:'😱',cheer:'💪',cry:'😢'};
  if(exprMap[mood]){
    const expr=document.createElement('div');expr.className='mascot-expr';expr.textContent=exprMap[mood];
    wrap.appendChild(expr);setTimeout(()=>expr.remove(),1300);
  }
  // Star particles on happy / cheer
  if(mood==='happy'||mood==='cheer'){
    for(let i=0;i<4;i++){
      const p=document.createElement('div');p.className='cat-star-particle';p.textContent='⭐';
      const angle=Math.random()*Math.PI*2,dist=38+Math.random()*28;
      p.style.cssText=`left:50%;top:35%;--tx:${Math.cos(angle)*dist}px;--ty:${Math.sin(angle)*dist-18}px;animation-delay:${i*0.1}s`;
      wrap.appendChild(p);setTimeout(()=>p.remove(),950);
    }
  }
  if(duration)setTimeout(()=>{if(mascotMood===mood)setMascotMood('default');},duration);
}
```

- [ ] **Step 2: Wire scared mood to mine hit in handleClick()**

In `handleClick()`, find (inside the `if(state.board[r][c]===-1)` branch):
```js
    state.lives--;updateLivesUI();
```
Add after `updateLivesUI();`:
```js
    setMascotMood('scared',1300);
```

- [ ] **Step 3: Wire happy mood to win in endGame()**

In `endGame(won)`, find:
```js
    playWin();spawnConfetti();setSpeech(t('winTitle'));updateStars();
```
Add after `updateStars();`:
```js
    setMascotMood('happy');
```

- [ ] **Step 4: Wire cry mood to loss in endGame()**

In `endGame(won)`, find:
```js
  }else{
    revealAllMines();setSpeech('😅');
```
Add after `setSpeech('😅');`:
```js
    setMascotMood('cry');
```

- [ ] **Step 5: Verify mascot moods**

- Hit a mine → cat jumps and shows 😱, returns to normal bob after ~1.3s
- Win a level → cat bounces happily with ⭐ particles and 😊 overlay
- Lose all lives → cat droops with 😢 overlay

- [ ] **Step 6: Commit**
```bash
git add index.html && git commit -m "feat(mascot): cat expression system with particle effects"
```

---

### Task 8: Turtle Expressions + Combo Linkage

**Files:**
- Modify: `D:/projects/minesweeper/index.html`

- [ ] **Step 1: Add setTurtleMood() after setMascotMood()**

```js
function setTurtleMood(mood,duration){
  const wrap=document.querySelector('.turtle-wrap');if(!wrap)return;
  wrap.classList.remove('turtle--scared','turtle--happy');
  if(mood!=='default')wrap.classList.add(`turtle--${mood}`);
  if(duration)setTimeout(()=>{const w=document.querySelector('.turtle-wrap');if(w){w.classList.remove(`turtle--${mood}`);}},duration);
}
```

- [ ] **Step 2: Wire turtle to mine hit**

In `handleClick()`, right after `setMascotMood('scared',1300);`, add:
```js
    setTurtleMood('scared',1500);
```

- [ ] **Step 3: Wire turtle to win/loss**

In `endGame(won)`, after `setMascotMood('happy');`, add:
```js
    setTurtleMood('happy');
```
In `endGame(won)`, after `setMascotMood('cry');`, add:
```js
    setTurtleMood('scared',3000);
```

- [ ] **Step 4: Wire combo to mascot excitement in triggerCombo()**

In `triggerCombo()`, find:
```js
  if(state.combo>=3){
    playCombo();
```
Insert before `playCombo()`:
```js
    if(state.combo===3)setMascotMood('happy',2200);
    if(state.combo===6)setMascotMood('cheer');
```

- [ ] **Step 5: Reset mascot when combo expires**

In `triggerCombo()`, find:
```js
  state.comboTimer=setTimeout(()=>{state.combo=0;},2500);
```
Replace with:
```js
  state.comboTimer=setTimeout(()=>{state.combo=0;if(mascotMood==='happy'||mascotMood==='cheer')setMascotMood('default');},2500);
```

- [ ] **Step 6: Verify turtle and combo linkage**

- Hit mine → turtle shrinks down (body slides downward)
- Win → turtle bobs happily
- Reveal 3 tiles quickly (combo 3) → cat bounces happy; combo 6 → cat enters fast cheer animation
- After combo expires → cat returns to default bob

- [ ] **Step 7: Commit**
```bash
git add index.html && git commit -m "feat(mascot): turtle expressions and combo-mascot excitement"
```

---

### Task 9: Cat Click-to-Encourage + 30s Idle

**Files:**
- Modify: `D:/projects/minesweeper/index.html`

- [ ] **Step 1: Add showCatPhrase() and resetIdleTimer() after setTurtleMood()**

```js
function showCatPhrase(){
  const phrases=t('catPhrases');
  const text=phrases[catPhraseIdx%phrases.length];catPhraseIdx++;
  const wrap=document.querySelector('.mascot-wrap');if(!wrap)return;
  const old=wrap.querySelector('.click-phrase');if(old)old.remove();
  const el=document.createElement('div');el.className='click-phrase';el.textContent=text;
  wrap.appendChild(el);setTimeout(()=>el.remove(),2600);
}

function resetIdleTimer(){
  clearTimeout(idleTimer);
  idleTimer=setTimeout(()=>{
    if(state.gameStarted&&!state.gameOver&&!state.paused){
      showCatPhrase();
      if(mascotMood==='default')setMascotMood('cheer',900);
    }
    resetIdleTimer();
  },30000);
}
```

- [ ] **Step 2: Add onclick to cat SVG**

Find the cat SVG opening tag:
```html
<svg width="128" height="158" viewBox="0 0 130 160" xmlns="http://www.w3.org/2000/svg">
```
Replace with:
```html
<svg width="128" height="158" viewBox="0 0 130 160" xmlns="http://www.w3.org/2000/svg" style="cursor:pointer" onclick="showCatPhrase()">
```

- [ ] **Step 3: Start idle timer in initGame()**

In `initGame()`, find:
```js
  clearInterval(state.timerInterval);clearTimeout(state.comboTimer);
  state.timerInterval=null;state.comboTimer=null;
```
Add after `state.comboTimer=null;`:
```js
  resetIdleTimer();
```

- [ ] **Step 4: Clear idle timer in endGame()**

In `endGame(won)`, find:
```js
  clearInterval(state.timerInterval);clearTimeout(state.comboTimer);state.timerInterval=null;stopBGM();
```
Add after `stopBGM();`:
```js
  clearTimeout(idleTimer);
```

- [ ] **Step 5: Verify click-to-encourage**

In-game: click the cat → a phrase bubble floats up above the cat and fades away after 2.5s. Click repeatedly → phrases cycle through all 8. Wait 30s idle → cat auto-shows a phrase and briefly cheers.

- [ ] **Step 6: Commit**
```bash
git add index.html && git commit -m "feat(mascot): cat click phrases and 30s idle encouragement"
```

---

## Self-Review

**Spec coverage:**
- A (Map screen): Tasks 1-4 — screen HTML, CSS, JS routing, win-unlock flow ✓
- C (Special tiles): Tasks 5-6 — data layer, glow, reveal effects, boost timer ✓
- E (Mascot): Tasks 7-9 — cat expressions, turtle, combo linkage, click phrases ✓

**Placeholder scan:** No TBD or TODO. All steps contain complete code.

**Type consistency:**
- `state.specials[r][c]` = `'star'|'chest'|'boost'|null` — consistent across `placeSpecials`, `applySpecialGlow`, `floodReveal`, `triggerSpecial` ✓
- `setMascotMood('happy'|'scared'|'cheer'|'cry'|'default')` — consistent across all 6 call sites ✓
- localStorage keys: `sweeper-unlock`, `sweeper-stars-{lv}` — no collision with existing `best-{lv}`, `achievements`, `sweeper-lang` ✓
- `getStars(lv)` called in `renderMapScreen`; `setStars(lv,s)` called in `showOverlay` — used correctly ✓

**Edge cases verified:**
- `applySpecialGlow` called after `placeSpecials`, which runs after first click — tiles exist in DOM at that point ✓
- `renderTile` resets `tile.className='tile'` removing sp-* glow on reveal — no stale glow on revealed tiles ✓
- `triggerSpecial` fires via `setTimeout(220)` — after tile is fully rendered ✓
- `activateBoost` guards against double-activation with `state.boostActive` check ✓
- `setMascotMood` guard: `if(!wrap)return` — safe when called from map screen ✓
- `state._justUnlocked` cleared after use in `showMapScreen` ✓
