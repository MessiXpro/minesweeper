# Gameplay Modes Expansion — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add visible star conditions, a "More Modes" modal, time-attack mode, survival mode, and custom difficulty — all inside the existing single-file `index.html`.

**Architecture:** Extend `state.mode` ('classic'|'time-attack'|'survival'|'custom'). Branch existing `initGame()`, `endGame()`, `getStarCount()` on mode. Add new HTML modals, CSS, i18n keys, and JS functions in-place.

**Tech Stack:** Vanilla JS, CSS, single-file HTML. No build step. Test by opening `index.html` via `python -m http.server 3456` and verifying in browser.

---

### Task 1: Star Strip — rewrite star logic + visible in-game strip

**Files:**
- Modify: `index.html` (CSS, HTML, JS)

- [ ] **Step 1: Replace `getStarCount()` with level-aware version**

Find and replace the entire function (currently ~line 1428):

```js
// FIND:
function getStarCount(){
  const pct=state.revealedSafe/state.totalSafe;
  if(pct>=1){if(state.elapsed<60&&state.mineHits===0)return 3;if(state.elapsed<180&&state.mineHits<=1)return 2;return 1;}
  if(pct>=.7)return 1;return 0;
}

// REPLACE WITH:
const STAR_TIME_LIMITS=[45,90,120,150,180,210,240,300,360,420];
function getStarCount(){
  if(!state.won){return state.revealedSafe/state.totalSafe>=0.7?1:0;}
  const lv=typeof state.level==='number'?state.level:3;
  const limit=STAR_TIME_LIMITS[lv-1]||120;
  if(state.mineHits===0&&state.elapsed<=limit)return 3;
  if(state.mineHits===0)return 2;
  return 1;
}
```

- [ ] **Step 2: Add CSS for the star strip** (inside the `<style>` block, after `.map-help-btn{...}` line)

```css
/* ── Star Condition Strip ── */
.star-strip{display:flex;align-items:stretch;background:rgba(0,0,0,0.18);border-bottom:1px solid rgba(255,255,255,0.07);padding:0;}
.star-cond{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:5px 4px;gap:1px;border-right:1px solid rgba(255,255,255,0.07);transition:background .25s;}
.star-cond:last-child{border-right:none;}
.star-cond.achieved{background:rgba(253,211,77,0.12);}
.sc-icon{font-size:13px;line-height:1;}
.sc-text{font-size:10px;font-weight:700;color:rgba(255,255,255,0.38);line-height:1.2;text-align:center;}
.star-cond.achieved .sc-icon{filter:none;}
.star-cond.achieved .sc-text{color:#fcd34d;}
.star-cond:not(.achieved) .sc-icon{filter:grayscale(1) opacity(0.35);}
```

- [ ] **Step 3: Add HTML for the star strip** — insert between `<div class="best-bar" id="bestBar"></div>` and `<div class="main-area">`:

```html
  <!-- Star condition strip (shown during classic/custom game) -->
  <div class="star-strip" id="starStrip" style="display:none">
    <div class="star-cond" id="sc1">
      <span class="sc-icon">⭐</span>
      <span class="sc-text" id="sc1text">通关</span>
    </div>
    <div class="star-cond" id="sc2">
      <span class="sc-icon">⭐</span>
      <span class="sc-text" id="sc2text">零踩雷</span>
    </div>
    <div class="star-cond" id="sc3">
      <span class="sc-icon">⭐</span>
      <span class="sc-text" id="sc3text">??秒内</span>
    </div>
  </div>
```

- [ ] **Step 4: Add `updateStarStrip()` function** — insert after `function updateStars(){...}`:

```js
function updateStarStrip(){
  const strip=document.getElementById('starStrip');
  if(!strip)return;
  const showStrip=(state.mode==='classic'||state.mode==='custom')&&!state.gameOver;
  strip.style.display=showStrip?'flex':'none';
  if(!showStrip)return;
  const lv=typeof state.level==='number'?state.level:3;
  const limit=STAR_TIME_LIMITS[lv-1]||120;
  const won=state.revealedSafe===state.totalSafe&&state.totalSafe>0;
  const noHits=state.mineHits===0;
  const fast=state.elapsed<=limit;
  document.getElementById('sc1').classList.toggle('achieved',won);
  document.getElementById('sc2').classList.toggle('achieved',noHits);
  document.getElementById('sc3').classList.toggle('achieved',won&&noHits&&fast);
  document.getElementById('sc1text').textContent=lang==='zh'?'通关':'Clear';
  document.getElementById('sc2text').textContent=lang==='zh'?'零踩雷':'No hits';
  document.getElementById('sc3text').textContent=(lang==='zh'?`${limit}秒内`:`<${limit}s`);
}
```

- [ ] **Step 5: Hook `updateStarStrip()` into UI update cycle**

In `updateStars()` (currently `function updateStars(){const s=getStarCount();...}`), add a call at the end:

```js
// FIND:
function updateStars(){const s=getStarCount();['star1','star2','star3'].forEach((id,i)=>document.getElementById(id).classList.toggle('dim',i>=s));}

// REPLACE WITH:
function updateStars(){const s=getStarCount();['star1','star2','star3'].forEach((id,i)=>document.getElementById(id).classList.toggle('dim',i>=s));updateStarStrip();}
```

Also add `updateStarStrip()` call inside `initGame()`, right after `setSpeech(pick(t('idle')));updateStars();` on the last line of initGame setup.

- [ ] **Step 6: Verify in browser**

Run: `python -m http.server 3456` in `D:/projects/minesweeper`, open `http://localhost:3456`.
- Start a classic game → star strip appears below best bar
- ⭐ "通关" dims until board cleared
- ⭐ "零踩雷" dims the moment you hit a mine
- ⭐ "120秒内" (level 3) dims after 120s
- Return to map → strip hidden

- [ ] **Step 7: Commit**

```bash
git add index.html
git commit -m "feat: add visible star condition strip with per-level time targets"
```

---

### Task 2: i18n keys + "More Modes" modal UI

**Files:**
- Modify: `index.html` (i18n, CSS, HTML, JS)

- [ ] **Step 1: Add i18n keys to `zh` object** — insert before the closing `}` of the `zh` block (after `howPlaySteps:[...]`):

```js
modesBtn:'更多模式',modesTitle:'更多模式',
timeAttackName:'时间挑战',timeAttackDesc:'3分钟内翻更多格子，刷新最高分',
survivalName:'生存模式',survivalDesc:'1条命连闯，看能到第几关',
customName:'自定义难度',customDesc:'选预设，微调地雷数，随心挑战',
taTimeLeft:'剩余',taRounds:'已通关',taOver:'时间到！',taFinalScore:'最终得分',
survOver:'生存结束',survReached:'到达第 {n} 关！',survBestLbl:'最远记录',
customPresetEasy:'简单',customPresetMed:'中等',customPresetHard:'困难',
customMines:'地雷数量',customDensity:'密度',customStart:'🚀 开始游戏',
modesBestScore:'最高分',modesBestLevel:'最远关卡',modesClose:'关闭',
```

- [ ] **Step 2: Add same keys to `en` object** — insert before the closing `}` of the `en` block:

```js
modesBtn:'More Modes',modesTitle:'More Modes',
timeAttackName:'Time Attack',timeAttackDesc:'3 minutes — flip as many tiles as possible!',
survivalName:'Survival',survivalDesc:'1 life — how far can you go?',
customName:'Custom',customDesc:'Pick a preset and fine-tune the mines.',
taTimeLeft:'Left',taRounds:'Cleared',taOver:'Time\'s Up!',taFinalScore:'Final Score',
survOver:'Game Over',survReached:'Reached Level {n}!',survBestLbl:'Best Level',
customPresetEasy:'Easy',customPresetMed:'Medium',customPresetHard:'Hard',
customMines:'Mines',customDensity:'Density',customStart:'🚀 Start',
modesBestScore:'Best Score',modesBestLevel:'Best Level',modesClose:'Close',
```

- [ ] **Step 3: Add CSS for mode cards and custom panel** — insert after `.map-help-btn{...}` in the style block:

```css
/* ── Modes Modal ── */
.mode-card{display:flex;align-items:center;gap:14px;padding:13px 16px;border-radius:18px;margin-bottom:10px;cursor:pointer;border:2px solid transparent;transition:transform .15s,box-shadow .15s;text-align:left;}
.mode-card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(100,60,200,0.2);}
.mode-card:active{transform:scale(0.97);}
.mode-card-time{background:linear-gradient(135deg,#fef3c7,#fde68a);border-color:#f59e0b;}
.mode-card-surv{background:linear-gradient(135deg,#fce7f3,#fbcfe8);border-color:#ec4899;}
.mode-card-custom{background:linear-gradient(135deg,#d1fae5,#a7f3d0);border-color:#10b981;}
.mode-card-icon{font-size:30px;flex-shrink:0;}
.mode-card-name{font-family:'Fredoka One',cursive;font-size:16px;color:#1f1f3a;}
.mode-card-desc{font-size:12px;color:#6b7280;margin-top:2px;line-height:1.4;}
.mode-card-best{font-size:11px;font-weight:700;margin-top:4px;color:#7c3aed;}
/* Custom difficulty panel */
.custom-panel{display:none;text-align:left;margin-top:4px;}
.custom-panel.open{display:block;}
.preset-row{display:flex;gap:8px;margin-bottom:16px;}
.preset-btn{flex:1;padding:10px 4px;border-radius:14px;border:2px solid transparent;text-align:center;cursor:pointer;font-family:'Fredoka One',cursive;font-size:14px;transition:transform .12s,box-shadow .12s;background:#f3f4f6;color:#374151;}
.preset-btn.p-easy{background:#d1fae5;border-color:#10b981;color:#065f46;}
.preset-btn.p-med{background:#fef3c7;border-color:#f59e0b;color:#92400e;}
.preset-btn.p-hard{background:#fce7f3;border-color:#ec4899;color:#9d174d;}
.preset-btn.selected{transform:scale(1.07);box-shadow:0 4px 14px rgba(0,0,0,0.18);}
.custom-slider-label{font-size:13px;font-weight:700;color:#3D2F7A;display:flex;justify-content:space-between;margin-bottom:6px;}
.custom-slider-label span{color:#7c3aed;font-size:15px;}
input.mine-slider{width:100%;accent-color:#7c3aed;margin-bottom:4px;}
.custom-density{font-size:11px;color:#9080c0;margin-bottom:14px;}
.custom-start-btn{width:100%;padding:13px;border-radius:16px;border:none;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:white;font-family:'Fredoka One',cursive;font-size:17px;cursor:pointer;box-shadow:0 6px 20px rgba(124,58,237,0.4);transition:transform .12s;}
.custom-start-btn:hover{transform:scale(1.03);}
```

- [ ] **Step 4: Add Modes Modal HTML** — insert before `<!-- ── Tutorial / Help Modal ── -->`:

```html
<!-- ── More Modes Modal ── -->
<div class="modal-overlay" id="modesModal" onclick="if(event.target===this)closeModes()">
  <div class="modal-card" style="max-height:90vh;overflow-y:auto;">
    <h2 class="modal-title" id="modesTitleEl">更多模式</h2>

    <!-- Time Attack -->
    <div class="mode-card mode-card-time" onclick="startTimeAttack()">
      <div class="mode-card-icon">⏱️</div>
      <div>
        <div class="mode-card-name" id="taName">时间挑战</div>
        <div class="mode-card-desc" id="taDesc">3分钟内翻更多格子，刷新最高分</div>
        <div class="mode-card-best" id="taBest"></div>
      </div>
    </div>

    <!-- Survival -->
    <div class="mode-card mode-card-surv" onclick="startSurvival()">
      <div class="mode-card-icon">💀</div>
      <div>
        <div class="mode-card-name" id="survName">生存模式</div>
        <div class="mode-card-desc" id="survDesc">1条命连闯，看能到第几关</div>
        <div class="mode-card-best" id="survBest"></div>
      </div>
    </div>

    <!-- Custom -->
    <div class="mode-card mode-card-custom" onclick="toggleCustomPanel()">
      <div class="mode-card-icon">🎛️</div>
      <div>
        <div class="mode-card-name" id="customName">自定义难度</div>
        <div class="mode-card-desc" id="customDesc">选预设，微调地雷数，随心挑战</div>
      </div>
    </div>

    <!-- Custom sub-panel -->
    <div class="custom-panel" id="customPanel">
      <div class="preset-row">
        <button class="preset-btn p-easy selected" id="presetEasy" onclick="selectPreset('easy')">简单<br><small>8×8·10雷</small></button>
        <button class="preset-btn p-med" id="presetMed" onclick="selectPreset('med')">中等<br><small>9×9·15雷</small></button>
        <button class="preset-btn p-hard" id="presetHard" onclick="selectPreset('hard')">困难<br><small>10×10·25雷</small></button>
      </div>
      <div class="custom-slider-label"><span id="customMinesLbl">地雷数量</span><span id="customMinesVal">10</span></div>
      <input type="range" class="mine-slider" id="mineSlider" min="4" max="40" value="10" oninput="onSliderChange()">
      <div class="custom-density" id="customDensityEl">密度 15.6%</div>
      <button class="custom-start-btn" id="customStartBtn" onclick="startCustomGame()">🚀 开始游戏</button>
    </div>

    <button class="modal-close-btn modal-close-btn--ghost" onclick="closeModes()" id="modesCloseBtn" style="margin-top:12px">关闭</button>
  </div>
</div>
```

- [ ] **Step 5: Add "更多模式" button to map screen** — add after the `map-help-btn` line:

```html
<!-- FIND: -->
    <button class="map-action-btn map-help-btn" onclick="openHelp()" id="mapHelpBtn">❓ <span data-i18n="helpBtn">教程</span></button>

<!-- REPLACE WITH: -->
    <button class="map-action-btn map-help-btn" onclick="openHelp()" id="mapHelpBtn">❓ <span data-i18n="helpBtn">教程</span></button>
    <button class="map-action-btn map-modes-btn" onclick="openModes()" id="mapModesBtn">🎮 <span data-i18n="modesBtn">更多模式</span></button>
```

Add CSS for the new button color (after `.map-help-btn{...}`):
```css
.map-modes-btn{border-color:rgba(200,160,255,0.7);background:rgba(160,80,255,0.2);}
```

- [ ] **Step 6: Add JS functions for modes modal** — insert after `function closeHelp(){...}`:

```js
// ─── Modes Modal ──────────────────────────────────────────────────────────────
let _customPreset={size:8,mines:10,preset:'easy'};
function openModes(){
  // Update text
  document.getElementById('modesTitleEl').textContent=t('modesTitle');
  document.getElementById('taName').textContent=t('timeAttackName');
  document.getElementById('taDesc').textContent=t('timeAttackDesc');
  document.getElementById('survName').textContent=t('survivalName');
  document.getElementById('survDesc').textContent=t('survivalDesc');
  document.getElementById('customName').textContent=t('customName');
  document.getElementById('customDesc').textContent=t('customDesc');
  document.getElementById('modesCloseBtn').textContent=t('modesClose');
  document.getElementById('customStartBtn').textContent=t('customStart');
  document.getElementById('customMinesLbl').textContent=t('customMines');
  // Show personal bests
  const taB=localStorage.getItem('ta-best');
  document.getElementById('taBest').textContent=taB?`${t('modesBestScore')}: ${parseInt(taB).toLocaleString()}`:'';
  const sB=localStorage.getItem('surv-best');
  document.getElementById('survBest').textContent=sB?`${t('modesBestLevel')}: ${sB}`:'';
  // Preset labels
  document.getElementById('presetEasy').innerHTML=`${t('customPresetEasy')}<br><small>8×8·10雷</small>`;
  document.getElementById('presetMed').innerHTML=`${t('customPresetMed')}<br><small>9×9·15雷</small>`;
  document.getElementById('presetHard').innerHTML=`${t('customPresetHard')}<br><small>10×10·25雷</small>`;
  document.getElementById('modesModal').classList.add('show');
}
function closeModes(){
  document.getElementById('modesModal').classList.remove('show');
  document.getElementById('customPanel').classList.remove('open');
}
function toggleCustomPanel(){
  document.getElementById('customPanel').classList.toggle('open');
}
function selectPreset(p){
  const presets={easy:{size:8,mines:10},med:{size:9,mines:15},hard:{size:10,mines:25}};
  _customPreset={...presets[p],preset:p};
  ['easy','med','hard'].forEach(k=>document.getElementById(`preset${k.charAt(0).toUpperCase()+k.slice(1)}`).classList.toggle('selected',k===p));
  const sl=document.getElementById('mineSlider');
  sl.min=Math.max(4,Math.floor(presets[p].size*presets[p].size*0.08));
  sl.max=Math.floor(presets[p].size*presets[p].size*0.45);
  sl.value=presets[p].mines;
  onSliderChange();
}
function onSliderChange(){
  const v=parseInt(document.getElementById('mineSlider').value);
  _customPreset.mines=v;
  document.getElementById('customMinesVal').textContent=v;
  const total=_customPreset.size*_customPreset.size;
  const pct=Math.round(v/total*100);
  document.getElementById('customDensityEl').textContent=`${t('customDensity')} ${pct}%${pct>40?' ⚠️':''}`;
}
```

- [ ] **Step 7: Verify modal in browser**

Open `http://localhost:3456`. Click "🎮 更多模式" on map screen.
Expected: Modal appears with 3 mode cards. Clicking "自定义难度" toggles sub-panel. Preset buttons highlight when selected. Slider updates mine count and density.

- [ ] **Step 8: Commit**

```bash
git add index.html
git commit -m "feat: add More Modes modal with time attack, survival, custom difficulty entries"
```

---

### Task 3: Time Attack Mode

**Files:**
- Modify: `index.html` (JS only)

- [ ] **Step 1: Add time attack state fields and `startTimeAttack()`** — insert after `function onSliderChange(){...}`:

```js
// ─── Time Attack ─────────────────────────────────────────────────────────────
function startTimeAttack(){
  closeModes();
  state.mode='time-attack';
  state.taTimeLeft=180;
  state.taScore=0;
  state.taRoundsCleared=0;
  state.level=3; // fixed 9×9 board
  showGameScreen();
  initGame();
  // Hide star strip, show countdown in level chip area
  document.getElementById('starStrip').style.display='none';
}
function endTimeAttack(){
  clearInterval(state.taCountdown);state.taCountdown=null;
  const prev=parseInt(localStorage.getItem('ta-best')||'0');
  const isNew=state.taScore>prev;
  if(isNew)localStorage.setItem('ta-best',state.taScore);
  // Reuse overlay
  document.getElementById('overlayEmoji').textContent='⏱️';
  document.getElementById('overlayTitle').textContent=t('taOver');
  document.getElementById('overlayTitle').style.color='#7C3AED';
  document.getElementById('overlaySub').textContent=`${t('taRounds')}: ${state.taRoundsCleared}`;
  document.getElementById('overlayStars').textContent='';
  document.getElementById('overlayScore').textContent=`${t('taFinalScore')}: ${state.taScore.toLocaleString()}`;
  document.getElementById('overlayBest').textContent=isNew?t('newBest'):`${t('modesBestScore')}: ${prev.toLocaleString()}`;
  document.getElementById('overlayBtn').textContent=t('mapBtn');
  document.getElementById('overlay').classList.add('show');
  stopBGM();
}
function startTaCountdown(){
  clearInterval(state.taCountdown);
  state.taCountdown=setInterval(()=>{
    if(state.paused||state.gameOver)return;
    state.taTimeLeft--;
    updateTaTimerDisplay();
    if(state.taTimeLeft<=0){clearInterval(state.taCountdown);endTimeAttack();}
  },1000);
}
function updateTaTimerDisplay(){
  const m=Math.floor(state.taTimeLeft/60).toString().padStart(2,'0');
  const s=(state.taTimeLeft%60).toString().padStart(2,'0');
  // Show countdown in the timer display
  document.getElementById('timerDisplay').textContent=`${m}:${s}`;
  // Flash red when under 30s
  const panel=document.getElementById('timerDisplay').closest('.stat-panel');
  if(panel)panel.style.outline=state.taTimeLeft<=30?'2px solid #ef4444':'';
}
```

- [ ] **Step 2: Modify `initGame()` to handle time-attack** — find the line `clearInterval(state.timerInterval);clearTimeout(state.comboTimer);` near the end of `initGame()` and add a reset of `taCountdown`:

```js
// FIND (near end of initGame):
  clearInterval(state.timerInterval);clearTimeout(state.comboTimer);

// REPLACE WITH:
  clearInterval(state.timerInterval);clearTimeout(state.comboTimer);clearInterval(state.taCountdown);state.taCountdown=null;
```

Also find the line that calls `startBGM()` on first click (inside the `if(state.firstClick)` block in `revealCell()`):
```js
// FIND:
    state.firstClick=false;placeMines(r,c);startTimer();state.gameStarted=true;setPlayBtn(true);startBGM();

// REPLACE WITH:
    state.firstClick=false;placeMines(r,c);
    if(state.mode==='time-attack'){startTaCountdown();}else{startTimer();}
    state.gameStarted=true;setPlayBtn(true);startBGM();
```

- [ ] **Step 3: Modify `endGame()` to handle time-attack win** — find the `if(won){...}` block inside `endGame()`:

```js
// FIND:
    if(typeof state.level==='number'&&state.level<10){setUnlockedLevel(state.level+1);state._justUnlocked=state.level+1;}
    if(state._dailyMode){localStorage.setItem(getDailyKey()+'-done','1');unlockAch('dailyHero');}
    setTimeout(()=>{checkAchievements(true,stars);showOverlay(true);},800);

// REPLACE WITH:
    if(state.mode==='time-attack'){
      state.taScore+=state.score;state.taRoundsCleared++;
      // Auto-restart new board after short delay
      setTimeout(()=>{
        state.gameOver=false;state.won=false;
        initGame();
        // Keep countdown running — don't restart it
        startTaCountdown();
      },900);
      return;
    }
    if(typeof state.level==='number'&&state.level<10){setUnlockedLevel(state.level+1);state._justUnlocked=state.level+1;}
    if(state._dailyMode){localStorage.setItem(getDailyKey()+'-done','1');unlockAch('dailyHero');}
    setTimeout(()=>{checkAchievements(true,stars);showOverlay(true);},800);
```

- [ ] **Step 4: Add `taCountdown: null` to initial state object**

```js
// FIND (in state declaration):
  specials:[],boostActive:false,_justUnlocked:null,

// REPLACE WITH:
  specials:[],boostActive:false,_justUnlocked:null,
  mode:'classic',taTimeLeft:180,taScore:0,taRoundsCleared:0,taCountdown:null,
```

- [ ] **Step 5: Also show TA score in top bar during time-attack**

In `updateUI()`, after `document.getElementById('scoreDisplay').textContent=...`, add:
```js
// FIND the score display update:
  document.getElementById('scoreDisplay').textContent=state.score.toLocaleString();

// REPLACE WITH:
  document.getElementById('scoreDisplay').textContent=(state.mode==='time-attack'?(state.taScore+state.score):state.score).toLocaleString();
```

- [ ] **Step 6: Verify time attack in browser**

Open `http://localhost:3456`. Open More Modes → Time Attack.
Expected:
- 9×9 board loads, timer shows 3:00 counting down
- Winning the board auto-starts a new one, score accumulates
- Timer turns red outline under 30s
- When timer hits 0:00, overlay shows "时间到！" with final score
- Clicking back to map from overlay works

- [ ] **Step 7: Commit**

```bash
git add index.html
git commit -m "feat: add time attack mode — 3-minute countdown, auto-restart boards, cumulative score"
```

---

### Task 4: Survival Mode

**Files:**
- Modify: `index.html` (CSS, HTML, JS)

- [ ] **Step 1: Add CSS for survival progress bar** — add after `.custom-start-btn{...}`:

```css
/* ── Survival Progress ── */
.surv-progress{display:flex;align-items:center;gap:3px;padding:6px 14px;background:rgba(0,0,0,0.18);border-bottom:1px solid rgba(255,255,255,0.07);overflow-x:auto;flex-wrap:nowrap;}
.surv-pip{width:26px;height:26px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;flex-shrink:0;transition:all .3s;}
.surv-pip.done{background:#10b981;color:white;}
.surv-pip.current{background:#f59e0b;color:white;box-shadow:0 0 10px rgba(245,158,11,0.7);animation:survPulse 1s ease-in-out infinite;}
.surv-pip.locked{background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.25);}
.surv-arrow{color:rgba(255,255,255,0.15);font-size:10px;flex-shrink:0;}
@keyframes survPulse{0%,100%{box-shadow:0 0 8px rgba(245,158,11,0.6)}50%{box-shadow:0 0 18px rgba(245,158,11,0.9)}}
```

- [ ] **Step 2: Add survival progress bar HTML** — insert after `<div class="star-strip" id="starStrip" ...></div>`:

```html
  <!-- Survival progress bar -->
  <div class="surv-progress" id="survProgress" style="display:none"></div>
```

- [ ] **Step 3: Add survival state fields to state object** — add to the state declaration after `taCountdown:null,`:

```js
survLevel:1,survScore:0,
```

- [ ] **Step 4: Add `startSurvival()`, `endSurvival()`, `renderSurvProgress()` functions** — insert after `function endTimeAttack(){...}`:

```js
// ─── Survival Mode ────────────────────────────────────────────────────────────
function startSurvival(){
  closeModes();
  state.mode='survival';
  state.survLevel=1;
  state.survScore=0;
  state.level=state.survLevel;
  showGameScreen();
  initGame();
}
function renderSurvProgress(){
  const el=document.getElementById('survProgress');
  if(!el)return;
  el.style.display=state.mode==='survival'?'flex':'none';
  if(state.mode!=='survival')return;
  let html='';
  for(let i=1;i<=10;i++){
    if(i>1)html+=`<span class="surv-arrow">›</span>`;
    const cls=i<state.survLevel?'done':i===state.survLevel?'current':'locked';
    html+=`<div class="surv-pip ${cls}">${i}</div>`;
  }
  el.innerHTML=html;
}
function endSurvival(won){
  clearInterval(state.timerInterval);state.timerInterval=null;stopBGM();
  const reached=won?10:state.survLevel;
  const prev=parseInt(localStorage.getItem('surv-best')||'0');
  if(reached>prev)localStorage.setItem('surv-best',reached);
  document.getElementById('overlayEmoji').textContent=won?'🏆':'💀';
  document.getElementById('overlayTitle').textContent=t('survOver');
  document.getElementById('overlayTitle').style.color=won?'#16A34A':'#DC2626';
  document.getElementById('overlaySub').textContent=t('survReached').replace('{n}',reached);
  document.getElementById('overlayStars').textContent=won?'🏆🏆🏆':'';
  document.getElementById('overlayScore').textContent=`${t('taFinalScore')}: ${state.survScore.toLocaleString()}`;
  document.getElementById('overlayBest').textContent=reached>prev?t('newBest'):`${t('modesBestLevel')}: ${prev}`;
  document.getElementById('overlayBtn').textContent=t('mapBtn');
  document.getElementById('overlay').classList.add('show');
}
```

- [ ] **Step 5: Modify `initGame()` to handle survival** — find the line `const cfg=LEVELS[state.level];` in `initGame()`:

```js
// FIND:
  const cfg=LEVELS[state.level];

// REPLACE WITH:
  if(state.mode==='survival')state.level=state.survLevel;
  const cfg=LEVELS[Math.min(state.level,10)]||LEVELS[10];
```

Also find where `lives:MAX_LIVES` is set inside `initGame()`:

```js
// FIND:
    lives:MAX_LIVES,mineHits:0,combo:0,bestCombo:0,

// REPLACE WITH:
    lives:state.mode==='survival'?1:MAX_LIVES,mineHits:0,combo:0,bestCombo:0,
```

After `initGame()` body, add `renderSurvProgress()` call — find:
```js
// FIND (last lines of initGame, after renderGrid):
  setSpeech(pick(t('idle')));updateStars();

// REPLACE WITH:
  setSpeech(pick(t('idle')));updateStars();renderSurvProgress();
```

- [ ] **Step 6: Modify `endGame()` to handle survival win** — inside the `if(won)` block, after the time-attack block:

```js
// FIND (the block we added in Task 3 ends with):
    if(state._dailyMode){localStorage.setItem(getDailyKey()+'-done','1');unlockAch('dailyHero');}
    setTimeout(()=>{checkAchievements(true,stars);showOverlay(true);},800);

// REPLACE WITH:
    if(state._dailyMode){localStorage.setItem(getDailyKey()+'-done','1');unlockAch('dailyHero');}
    if(state.mode==='survival'){
      state.survScore+=state.score;
      if(state.survLevel>=10){endSurvival(true);return;}
      state.survLevel++;
      setTimeout(()=>{
        state.gameOver=false;state.won=false;
        initGame();
      },1000);
      return;
    }
    setTimeout(()=>{checkAchievements(true,stars);showOverlay(true);},800);
```

Also handle survival loss — inside `endGame()`'s `else` (lose) branch, add at the top:
```js
// FIND (start of else block):
  }else{
    revealAllMines();setSpeech('😅');

// REPLACE WITH:
  }else{
    if(state.mode==='survival'){setTimeout(()=>endSurvival(false),1200);revealAllMines();setSpeech('😅');setMascotMood('cry');updateUI();setPlayBtn(false);return;}
    revealAllMines();setSpeech('😅');
```

- [ ] **Step 7: Verify survival mode in browser**

Open More Modes → Survival.
Expected:
- Level 1 board loads, progress bar shows pip 1 pulsing amber
- Win → auto-advance to level 2, pip 1 turns green, pip 2 pulses
- Hit mine (only 1 life) → "生存结束" overlay showing "到达第 X 关"
- Completing all 10 levels → "🏆🏆🏆" overlay

- [ ] **Step 8: Commit**

```bash
git add index.html
git commit -m "feat: add survival mode — 1 life, progressive levels 1-10, level progress bar"
```

---

### Task 5: Custom Difficulty Mode

**Files:**
- Modify: `index.html` (JS only — HTML/CSS already added in Task 2)

- [ ] **Step 1: Add `startCustomGame()` function** — insert after `function onSliderChange(){...}`:

```js
function startCustomGame(){
  closeModes();
  state.mode='custom';
  state.level=`custom-${_customPreset.size}x${_customPreset.mines}`;
  // Store custom cfg for initGame to pick up
  state._customCfg={size:_customPreset.size,mines:_customPreset.mines};
  // Save last used for display
  localStorage.setItem('custom-last',JSON.stringify({size:_customPreset.size,mines:_customPreset.mines}));
  showGameScreen();
  initGame();
}
```

- [ ] **Step 2: Modify `initGame()` to handle custom mode**

```js
// FIND (the line we already modified in Task 4):
  if(state.mode==='survival')state.level=state.survLevel;
  const cfg=LEVELS[Math.min(state.level,10)]||LEVELS[10];

// REPLACE WITH:
  if(state.mode==='survival')state.level=state.survLevel;
  const cfg=state.mode==='custom'&&state._customCfg
    ? state._customCfg
    : (LEVELS[Math.min(state.level,10)]||LEVELS[10]);
```

- [ ] **Step 3: Modify `endGame()` to handle custom mode win**

Custom mode: no level unlock, no stars saved, just show overlay.

```js
// FIND (after the survival block in endGame won branch):
    setTimeout(()=>{checkAchievements(true,stars);showOverlay(true);},800);

// REPLACE WITH:
    if(state.mode==='custom'){setTimeout(()=>showOverlay(true),800);return;}
    setTimeout(()=>{checkAchievements(true,stars);showOverlay(true);},800);
```

Also fix `showOverlay()` to handle custom mode (no best score tracking by level):
```js
// FIND in showOverlay():
  const isNew=won&&setBest(state.level,state.score);
  if(won)setStars(state.level,stars);

// REPLACE WITH:
  const isNew=won&&state.mode==='classic'&&setBest(state.level,state.score);
  if(won&&state.mode==='classic')setStars(state.level,stars);
```

- [ ] **Step 4: Restore "classic" mode on map screen return**

In `showMapScreen()`, add mode reset:
```js
// FIND:
function showMapScreen(){
  currentScreen='map';

// REPLACE WITH:
function showMapScreen(){
  currentScreen='map';
  state.mode='classic';
  document.getElementById('survProgress').style.display='none';
  document.getElementById('starStrip').style.display='none';
```

- [ ] **Step 5: Show last custom settings in the modal**

In `openModes()`, after the `survBest` line, add:
```js
  // Restore last custom settings
  const lastCustom=JSON.parse(localStorage.getItem('custom-last')||'null');
  if(lastCustom){
    const preset=lastCustom.size===8?'easy':lastCustom.size===9?'med':'hard';
    selectPreset(preset);
    document.getElementById('mineSlider').value=lastCustom.mines;
    _customPreset={...lastCustom,preset};
    onSliderChange();
  }
```

- [ ] **Step 6: Verify custom difficulty in browser**

Open More Modes → click 自定义难度 to expand panel.
Expected:
- Select "困难" preset → slider range changes (10×10, max ~45 mines)
- Adjust slider → density % updates, ⚠️ shown above 40%
- Click "🚀 开始游戏" → game starts with correct grid size
- Win/lose → overlay shows score, no star tracking for custom
- Return to map → mode resets to classic

- [ ] **Step 7: Commit**

```bash
git add index.html
git commit -m "feat: add custom difficulty mode with 3 presets and mine count slider"
```

---

### Task 6: Polish — mode labels in top bar + applyLang hook

**Files:**
- Modify: `index.html` (JS only)

- [ ] **Step 1: Show mode name in level chip during non-classic modes**

In `updateUI()`, find where the level select value is set and add mode label:

```js
// FIND:
  document.getElementById('levelSelect').value=state.level;

// REPLACE WITH:
  if(state.mode==='time-attack'||state.mode==='survival'||state.mode==='custom'){
    // Hide level select, show mode label
    document.getElementById('levelSelect').style.display='none';
    let modeLabel=state.mode==='time-attack'?t('timeAttackName'):state.mode==='survival'?`${t('survivalName')} Lv${state.survLevel}`:t('customName');
    let el=document.getElementById('modeModeLabel');
    if(!el){el=document.createElement('div');el.id='modeModeLabel';el.style.cssText='font-family:Fredoka One,cursive;font-size:13px;color:white;';document.getElementById('levelSelect').parentNode.appendChild(el);}
    el.textContent=modeLabel;el.style.display='';
  } else {
    document.getElementById('levelSelect').style.display='';
    const ml=document.getElementById('modeModeLabel');if(ml)ml.style.display='none';
  }
```

- [ ] **Step 2: Hook `openModes()` into `applyLang()`**

```js
// FIND:
  if(currentScreen==='map')renderMapScreen();

// REPLACE WITH:
  if(currentScreen==='map')renderMapScreen();
  // Re-render modes modal text if open
  if(document.getElementById('modesModal').classList.contains('show'))openModes();
```

- [ ] **Step 3: Update sw.js cache version to v5**

```js
// FIND in sw.js:
const CACHE = 'star-sweeper-v4';

// REPLACE WITH:
const CACHE = 'star-sweeper-v5';
```

- [ ] **Step 4: Final verification — full flow test**

Run: `python -m http.server 3456`

Check all flows:
1. Classic game → star strip shows, stars update in real time ✅
2. Map → More Modes → Time Attack → countdown, auto-restart, final overlay ✅
3. Map → More Modes → Survival → progress bar, 1-life loss triggers end screen ✅
4. Map → More Modes → Custom → preset + slider → correct board ✅
5. Language toggle → all modal text switches zh↔en ✅
6. Return to map from any mode → resets to classic ✅

- [ ] **Step 5: Commit and push**

```bash
git add index.html sw.js
git commit -m "feat: mode label in top bar, applyLang hook for modes modal, sw cache v5"
git push
```
