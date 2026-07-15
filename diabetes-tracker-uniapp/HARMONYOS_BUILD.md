# 鸿蒙 App 构建指南

## 前置准备

### 1. 安装 HBuilderX
- 下载：https://www.dcloud.io/hbuilderx.html
- 选择 **App 开发版**（非 Alpha）

### 2. 安装 DevEco Studio（用于签名和调试）
- 下载：https://developer.huawei.com/consumer/cn/deveco-studio/
- 版本要求：≥ 5.0

### 3. 华为开发者账号
- 注册：https://developer.huawei.com
- 实名认证（上架必需）
- 创建应用 → 获取 App ID

## 本地构建步骤

### 步骤 1：拉取项目

```bash
git clone https://github.com/mclarenlm/diabetes-tracker-nas-app.git
cd diabetes-tracker-nas-app/diabetes-tracker-uniapp
```

### 步骤 2：安装依赖

```bash
npm install --registry https://registry.npmmirror.com
```

### 步骤 3：HBuilderX 打开项目

1. 打开 HBuilderX
2. 文件 → 导入 → 从本地目录导入
3. 选择 `diabetes-tracker-uniapp` 目录

### 步骤 4：配置鸿蒙

在 HBuilderX 中：
1. 打开 `manifest.json` → **App 鸿蒙配置**
2. 填写：
   - 应用包名：`com.mclaren.diabetes.tracker`
   - 应用名称：`糖尿病记录工具`
   - 版本号：`3.4.0`
3. 图标配置（可使用项目内置 SVG 图标）

### 步骤 5：运行到鸿蒙设备

HBuilderX 菜单栏：
```
运行 → 运行到手机或模拟器 → 运行到鸿蒙
```

首次运行会提示安装鸿蒙基座，按提示操作即可。

### 步骤 6：打包发布

```
发行 → 原生 App-鸿蒙 → 打包
```

生成 `.app` 文件后：
1. 登录华为 AppGallery Connect
2. 创建应用 → 上传软件包
3. 填写应用信息（截图、描述、隐私政策）
4. 提交审核

## 注意事项

### API 地址配置

鸿蒙 App 访问 NAS 上的 Flask 后端，需要在 `vite.config.js` 中或运行时配置 API 地址：

```js
// 开发环境（HBuilderX 预览）
const API_BASE = 'http://192.168.x.x:5088'  // 替换为 NAS 局域网 IP

// 如需通过公网访问，配置 DDNS 或内网穿透
```

### 权限说明

应用仅需以下权限，上架审核友好：
- `ohos.permission.INTERNET` — 网络访问
- `ohos.permission.STORE_PERSISTENT_DATA` — 数据存储

无需摄像头、位置、通讯录等敏感权限。

### 暗黑模式

`manifest.json` 已配置 `darkmode: true`，鸿蒙端自动跟随系统暗黑模式，无需额外开发。

### 离线能力

当前 PWA Service Worker 在鸿蒙 WebView 中不可用。如需离线能力，后续可使用 uni-app 的 `uni.setStorage` 实现本地缓存。

## 上架检查清单

- [ ] 应用图标 512×512 PNG
- [ ] 5 张应用截图（鸿蒙手机）
- [ ] 隐私政策 URL
- [ ] 应用描述（中文）
- [ ] 华为开发者账号实名认证
- [ ] 包名 `com.mclaren.diabetes.tracker` 已注册
