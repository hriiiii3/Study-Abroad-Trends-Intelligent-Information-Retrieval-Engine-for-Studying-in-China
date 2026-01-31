# Liiuxue-deployment

这是一个前后端分离的留学资讯平台项目。

## 项目简介

本系统旨在为留学生提供一个全面的信息服务平台，整合了最新的官方政策、新闻资讯以及就业创业信息。项目采用前后端分离的架构，前端负责用户交互和数据展示，后端提供数据接口和业务逻辑处理。

## 技术栈

**前端 (vite-project):**

*   [Vue 3](https://vuejs.org/)
*   [Vite](https://vitejs.dev/)
*   [Vue Router](https://router.vuejs.org/)
*   [Pinia](https://pinia.vuejs.org/)
*   [Element Plus](https://element-plus.org/)
*   [Axios](https://axios-http.com/)

**后端 (flaskProject):**

*   [Flask](https://flask.palletsprojects.com/)
*   [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
*   [Flask-CORS](https://flask-cors.readthedocs.io/)
*   [PyMySQL](https://github.com/PyMySQL/PyMySQL)
*   [MySQL](https://www.mysql.com/)

## 主要功能

*   **用户系统**: 支持用户注册、登录和身份认证。
*   **内容管理**: 
    *   **官方政策**: 发布和管理留学相关的官方政策文件。
    *   **新闻资讯**: 提供最新的留学新闻和动态。
    *   **就业创业**: 分享就业和创业相关的资讯和机会。
*   **内容分类**: 对信息进行分类，方便用户查找。
*   **文件上传**: 支持图片等文件的上传。

## 部署与运行

### 1. 后端 (flaskProject)

**a. 安装依赖:**

首先，建议创建一个 Python 虚拟环境。然后在 `flaskProject` 目录下运行：

```bash
pip install -r requirements.txt
```
**b. 配置数据库:**
```bash
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://YOUR_USERNAME:YOUR_PASSWORD@YOUR_HOST/YOUR_DATABASE'
```
**c. 启动服务:**
```bash
python app.py
```
### 2.前端 (vite-project)
**a.安装依赖:**
```bash
npm install
# 或者
yarn install
```

**b.启动项目**
```bash
npm run dev
# 或者
yarn dev
```
### 目录结构
```bash
Liiuxue-deployment/
├── README.md          # <--- 就是这个总的 README 文件
├── flaskProject/      # 后端 Flask 项目
│   ├── app.py         # Flask 应用主文件
│   ├── requirements.txt # Python 依赖
│   └── ...
└── vite-project/        # 前端 Vite + Vue 项目
    ├── src/           # 前端源码
    ├── package.json   # Node.js 依赖和脚本
    └── ...
```
