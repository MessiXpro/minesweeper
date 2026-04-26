# ⭐ 星星扫雷 · Star Sweeper

一款专为小朋友设计的卡通扫雷游戏，支持 iPad PWA 安装。

🎮 **立即游玩** → [messixpro.github.io/minesweeper](https://messixpro.github.io/minesweeper/)

---

## 特色功能

### 🗺️ 冒险地图
五个主题关卡逐步解锁，完成当前关才能进入下一关：

| 关卡 | 场景 | 格子 | 地雷 |
|------|------|------|------|
| 1 | 🌲 森林 | 6×6 | 4 |
| 2 | 🏜️ 沙漠 | 8×8 | 10 |
| 3 | 🌊 海洋 | 9×9 | 15 |
| 4 | ⛰️ 雪山 | 10×10 | 22 |
| 5 | 🚀 太空 | 10×10 | 30 |

### ⭐ 特殊格子
每局随机埋入惊喜，揭开有奖励：

- ⭐ **幸运星** — 双倍积分
- 💎 **宝箱** — +1 提示次数
- ⚡ **加速器** — 计时器暂停 5 秒

### 🐱 活灵活现的角色
- 猫咪有四种表情：开心 / 惊吓 / 加油 / 哭泣
- 连击 ≥3 猫咪进入兴奋状态，连击 ≥6 发出彩虹光
- 点击猫咪听鼓励，30 秒无操作自动说话
- 乌龟同步反应：胜利探头、踩雷缩壳

---

## iPad 安装（PWA）

1. Safari 打开 [messixpro.github.io/minesweeper](https://messixpro.github.io/minesweeper/)
2. 点底部分享按钮 `⬆️`
3. 选「添加到主屏幕」
4. 点「添加」

安装后全屏运行、断网可玩，体验与原生 App 相同。

---

## 技术栈

- 纯原生 HTML / CSS / JavaScript，无任何依赖
- 单文件架构（`index.html`）
- PWA：Web App Manifest + Service Worker 离线缓存
- 动画：纯 CSS `@keyframes`
- 存储：`localStorage`（解锁进度、最佳星级、成就）
