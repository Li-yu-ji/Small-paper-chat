# 小纸聊天 [中文](https://github.com/Li-yu-ji/small-paper-chat/edit/main/README.md) [English](https://github.com/Li-yu-ji/small-paper-chat/blob/main/English-READEME) [日本語](https://github.com/Li-yu-ji/small-paper-chat/blob/main/Japan-RADEME)

一个基于 Flask 和 WebSocket 的实时聊天应用。

## 功能特点

### 基础聊天功能
- 实时消息发送和接收
- 支持公共聊天和私人聊天
- 聊天记录持久化存储
- 用户在线状态显示
- 输入状态提示（"正在输入..."）

### 消息功能
- 支持 Emoji 表情
- 链接预览功能（自动展示链接标题、描述和图片）
- @用户提醒功能
- 消息撤回（2分钟内）
- 消息删除（单条/批量）

### 用户功能
- 用户状态管理（在线、离开、忙碌）
- 用户列表实时更新
- 新消息提醒（桌面通知）

### 特色功能
1. **消息撤回**
   - 2分钟内可撤回消息
   - 撤回后显示"此消息已被撤回"
   - 所有用户可见撤回状态

2. **@功能**
   - 在消息中使用@提及用户
   - 双击用户名快速@
   - 被@用户收到特殊提醒
   - @消息特殊高亮显示

3. **消息删除**
   - 支持单条消息删除
   - 支持按类型批量删除（全部/公共/私聊）
   - 只能删除自己的消息

4. **通知系统**
   - 桌面通知支持
   - 新消息提醒
   - @提醒
   - 私聊提醒

## 技术栈
- 后端：Flask + Flask-SocketIO + SQLAlchemy
- 前端：HTML5 + CSS3 + JavaScript
- 数据库：SQLite
- WebSocket：Socket.IO
- 其他：
  - emoji-picker-element（表情选择器）
  - Font Awesome（图标）
  - BeautifulSoup4（链接预览）

## 安装和运行

1. 安装依赖：

依赖列表：
- Flask==3.0.0（Web框架）
- Flask-SocketIO==5.3.6（WebSocket支持）
- python-socketio==5.10.0（Socket.IO Python实现）
- python-engineio==4.8.0（Engine.IO Python实现）
- Flask-SQLAlchemy==3.1.1（数据库ORM）
- requests==2.31.0（HTTP客户端，用于链接预览）
- beautifulsoup4==4.12.2（HTML解析，用于链接预览）

2. 运行应用：
`python app.py`

3. 访问应用：
打开浏览器访问 `http://localhost:4545`

## 使用说明

### 1. 开始聊天
- 输入用户名并点击"进入聊天"
- 用户名不能重复
- 登录后自动显示在线用户列表

### 2. 发送消息
- 在输入框输入消息
- 点击发送按钮或按回车键发送
- 点击表情按钮插入表情

### 3. 私聊
- 点击用户列表中的用户名开始私聊
- 使用"切换到公共聊天"按钮返回公共聊天

### 4. @功能
- 在消息中输入@+用户名
- 或双击用户列表中的用户名快速@
- 被@的用户会收到提醒

### 5. 消息管理
- 鼠标悬停在消息上显示操作按钮
- 蓝色按钮用于撤回（2分钟内）
- 红色按钮用于删除
- 使用顶部按钮批量删除消息

### 6. 状态管理
- 使用状态选择器切换状态
- 可选状态：在线、离开、忙碌
- 状态会实时同步给其他用户

## 注意事项
1. 消息撤回限制在2分钟内
2. 只能删除/撤回自己的消息
3. 首次使用需要授权桌面通知
4. 建议使用现代浏览器以获得最佳体验

## 贡献
欢迎提交 Issue 和 Pull Request！

## 许可证
MIT License
