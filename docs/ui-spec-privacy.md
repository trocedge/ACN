> 交付规格：数据侧已就绪，界面层按本文件接入；本分支不改前端源码。

# 隐私弹窗文案（第 20 条）

1. 本站点仅展示公开的会议与竞赛截止日信息。
2. 不要求注册，不采集学生身份信息。
3. 第三方资源（已按 `index.html` 与 `public/privacy.html` 实测核实）：
   - Google AdSense：`ca-pub-2114972416819347`（`index.html` meta，广告）
   - Google Tag Manager / gtag：`G-RY374M6FJ8`（`index.html` 首屏后异步加载，访问统计）
   - 站内 `privacy-modal.js` / `privacy-modal.css` 为第一方组件，非第三方追踪
4. 浏览器本地存储仅用于语言偏好与引导关闭状态。
5. 关闭第三方统计的方式：浏览器阻止第三方 Cookie、使用隐私模式或安装广告拦截扩展；
   页面自身未提供开关，不做「站内可一键关闭」这类未核实的承诺。
6. 数据纠错入口：本仓库 Issues。

> 清单来源：`index.html` 第 16 / 73—81 行与 `public/privacy.html`；未发现其它第三方域名。
> 不做「不收集任何数据」这类绝对化承诺。
