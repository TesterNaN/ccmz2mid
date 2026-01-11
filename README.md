# 🎵 ccmz2mid - 虫虫钢琴 CCMZ 格式转换器

[![License: GPLv3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Python](https://img.shields.io/badge/Python-3.6+-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

> **专为虫虫钢琴(gangqinpu.com)设计的 CCMZ 加密格式转换工具**  
> 将虫虫钢琴私有加密格式转换为标准 MIDI 文件，让音乐回归开放标准！

## 🌟 项目亮点

- 🔓 **完美解密**：支持虫虫钢琴 CCMZ v1/v2 双版本加密格式
- 🎵 **高保真转换**：完整保留速度、拍号、力度等所有音乐信息
- 🌐 **一键下载**：支持直接从虫虫钢琴网站下载并转换
- 🖥️ **跨平台**：Windows/macOS/Linux 全平台支持
- 🚀 **交互式界面**：直观的菜单驱动，无需记忆命令

## 📋 目录

- [🎯 功能特点](#-功能特点)
- [🛠️ 安装与使用](#️-安装与使用)
- [📖 使用教程](#-使用教程)
- [🔧 技术细节](#-技术细节)
- [🤝 贡献指南](#-贡献指南)
- [📄 许可证](#-许可证)
- [⚠️ 免责声明](#️-免责声明)

## 🎯 功能特点

### 核心功能
- ✅ **CCMZ 解密**：支持虫虫钢琴 v1/v2 加密格式
- ✅ **midi.json 解析**：精确解析虫虫钢琴 MIDI 数据结构
- ✅ **标准 MIDI 输出**：生成兼容所有播放器的 MIDI 文件
- ✅ **交互式操作**：友好的菜单界面，引导用户完成操作

### 支持的音乐元素
- 🎹 **音符事件**：Note On/Off，完整力度信息
- 🎚️ **控制信息**：音色变化、控制变化、弯音轮
- 🎼 **时间信息**：速度变化、拍号变化、小节划分
- 🎛️ **多轨道**：保持原始轨道分离和通道分配

## 🛠️ 安装与使用

### 环境要求
- Python 3.6 或更高版本
- 网络连接（用于下载功能）

### 安装方法

#### 1. 下载项目
```bash
# 克隆项目
git clone https://github.com/TesterNaN/ccmz2mid.git
cd ccmz2mid
```

#### 2. 安装依赖
```bash
# 安装必需的 mido 库
pip install mido
```

#### 3. 运行程序
```bash
python ccmz2mid.py
```


## 📖 使用教程

### 获取虫虫钢琴 CCMZ 文件

1. **访问虫虫钢琴网站**：https://www.gangqinpu.com/
2. **查找乐谱**：搜索或浏览你想要的钢琴谱
3. **下载 CCMZ 文件**：
   - 部分乐谱提供 CCMZ 格式下载
   - 右键复制下载链接（通常是 .ccmz 结尾）

### 程序使用方法

#### 启动程序
```bash
python ccmz2mid.py
```

程序启动后将显示如下界面：
```
============================
🎵 CCMZ 到 MIDI 转换工具
============================

请选择操作:
1. 从 URL 下载并转换 CCMZ 文件
2. 转换本地 CCMZ 文件
3. 使用示例 URL 测试
4. 退出
----------------------------------------
请选择 (1-4):
```

### 操作选项详解

#### 选项1：从 URL 下载并转换 CCMZ 文件
```
步骤：
1. 输入虫虫钢琴 CCMZ 文件的完整 URL
2. 输入输出 MIDI 文件名（可选，默认为 output.mid）
3. 选择是否保留临时文件（默认不保留）
4. 程序自动下载、解密、转换
```

#### 选项2：转换本地 CCMZ 文件
```
步骤：
1. 输入本地 CCMZ 文件路径
2. 输入输出 MIDI 文件名（可选，自动基于输入文件名生成）
3. 选择是否保留临时文件（默认不保留）
4. 程序自动解密、转换
```

#### 选项3：使用示例 URL 测试
```
功能：
- 使用内置的示例 URL 进行测试
- 适合首次使用验证功能是否正常
- 示例文件来自虫虫钢琴公开资源
```

#### 选项4：退出程序
```
退出转换工具
```

### 转换示例

#### 示例1：在线转换
```
请选择 (1-4): 1
请输入 CCMZ 文件 URL [https://s201.lzjoy.com/res/statics/fileupload/ccmz/...]:
请输入输出 MIDI 文件名 [output.mid]: 月光奏鸣曲.mid
是否保留临时文件? (y/n) [n]: n

📥 正在从 https://... 下载 CCMZ 文件...
✅ 下载完成: downloaded.ccmz (15,432 字节)

🔧 开始处理 CCMZ 文件: downloaded.ccmz
📁 临时工作目录: /tmp/ccmz_to_midi_abc123

📂 步骤1: 提取 CCMZ 文件...
🔍 正在提取 CCMZ 文件: downloaded.ccmz
📄 文件大小: 15,432 字节
📊 CCMZ 版本: 2
🔓 使用版本2解密（奇偶转换）...
✅ 解密完成
💾 已保存解密文件: /tmp/.../decrypted.zip
📦 ZIP 包含 1 个文件:
  📁 midi.json (8,765 字节)
🎯 找到 JSON 文件: /tmp/.../midi.json

🎵 步骤2: 转换为 MIDI 格式...
📖 正在加载 JSON 文件: /tmp/.../midi.json
📊 分析数据结构...
  事件数量: 1,520
  轨道数量: 3
  小节数量: 12
  速度变化: 2 处
  拍号变化: 1 处
  音符事件: 856
🔄 开始转换 JSON 到 MIDI...
🎵 速度映射: 2 个速度点
🎼 拍号映射: 1 个拍号点
📁 事件分组: 3 个轨道
📝 元数据轨道创建完成: 5 个事件
  轨道 0: 512 个事件 -> 512 个MIDI事件
  轨道 1: 324 个事件 -> 324 个MIDI事件
  轨道 2: 684 个事件 -> 684 个MIDI事件
✅ 转换完成: 4 个轨道，1,525 个MIDI事件
💾 MIDI 文件已保存: 月光奏鸣曲.mid
  文件格式: 1
  时间精度: 480 ticks/beat
  轨道数量: 4
  总时长: 125.6 秒

🎉 转换完成！MIDI 文件已保存为: 月光奏鸣曲.mid
```

#### 示例2：本地转换
```
请选择 (1-4): 2
请输入 CCMZ 文件路径: /音乐/虫虫钢琴/梦中的婚礼.ccmz
请输入输出 MIDI 文件名 [梦中的婚礼.mid]: 
是否保留临时文件? (y/n) [n]: y

🔧 开始处理 CCMZ 文件: /音乐/虫虫钢琴/梦中的婚礼.ccmz
📁 临时工作目录: /tmp/ccmz_to_midi_def456

...（转换过程类似）...

🎉 转换完成！MIDI 文件已保存为: 梦中的婚礼.mid
📁 临时文件保留在: /tmp/ccmz_to_midi_def456
```


## 🤝 贡献指南

### 如何贡献
1. **Fork 本仓库**
2. **创建特性分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **提交更改**
   ```bash
   git commit -m '添加了很棒的功能'
   ```
4. **推送到分支**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **开启 Pull Request**

### 开发环境设置
```bash
# 1. 克隆仓库
git clone https://github.com/TesterNaN/ccmz2mid.git
cd ccmz2mid

# 2. 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install mido
```


## 📄 许可证

本项目采用 **GNU General Public License v3.0** 开源许可证。


## ⚠️ 免责声明

### 合法使用
1. **版权尊重**：本工具仅用于**个人学习、研究和备份**目的
2. **禁止商用**：请勿将转换后的 MIDI 文件用于商业用途
3. **遵守条款**：使用前请阅读虫虫钢琴网站的服务条款

### 责任声明
- 本工具为开源项目，作者不承担任何使用后果
- 请确保你有权转换相关乐谱文件
- 支持正版音乐，尊重创作者权益

### 项目初衷
本项目的目标是：
- 🔓 **技术研究**：研究音乐文件格式转换技术
- 💾 **数据备份**：帮助用户备份个人收藏的乐谱
- 🎵 **格式开放**：推动音乐格式的开放和互操作性

---

## 📞 联系与支持

### 问题反馈
- 🐛 **Bug 报告**：[GitHub Issues](https://github.com/TesterNaN/ccmz2mid/issues)
- 💡 **功能建议**：通过 Issue 提交
- ❓ **使用问题**：查看常见问题或提交 Issue

### 星标支持
如果这个项目对你有帮助，请点个 ⭐ Star 支持！

---

*感谢虫虫钢琴(gangqinpu.com)为广大音乐爱好者提供的优质乐谱资源！*
