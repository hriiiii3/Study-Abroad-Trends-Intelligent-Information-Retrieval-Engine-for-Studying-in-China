# Liiuxue-deployment

这是一个前后端分离的留学资讯平台项目。

## 项目简介

当前来华留学生对于来华留学政策信息的搜寻与理解面临许多挑战：（1）留学生获取来华相关政策、新闻等信息渠道分散（2）官方政策网站、主流新闻媒体平台及核心论文数据库对于“政策对于来华留学生来华因素影响”“来华留学生就业创业”的权威数据与系统分析仍属空白，尤其在数据分布、趋势识别与实践路径方面，缺乏针对性整理与公开发布。

针对这些问题本项目致力于借助自然语言处理（NLP）技术、趋势预测SARIMA模型以及讯飞星火SPARK模型等，对来华留学生政策文件与新闻报道展开深度剖析。

通过系统收集、精准处理以及科学分析海量相关政策文件，结合 BERT 和 SPARK 等前沿算法与模型，全面探究这些政策在实际落地实施环节所取得的成效以及暴露出的问题，最终形成一个智能的查询分析系统平台。在此基础上，来华留学信息智能查询系统集全局搜索、政策查询、新闻查询、可视化洞察与分析、资源分类浏览、多维后台管理、自动预测分类等功能于一体，为用户提供全面、便捷的信息支持。此外，系统还提供AI智能服务，接入大模型提供实时在线咨询服务。在可视化洞察分析方面，系统通过图表等形式，直观展示政策新闻研究可视化、来华留学生就业创业可视化等信息，帮助用户快速理解相关情况。此外，系统还对收集到的政策文件、新闻资讯等文本数据接入自训练的BERT大模型辅助资源自动分类，按照不同的主题或领域生成分类标签，方便管理员管理资源与用户查找相关内容。

项目成果将为优化来华留学生的综合服务体系提供有力依据，为有意向来中国留学的留学生、政策制定者、教育管理者以及相关研究人员提供全面、便捷的信息支持，以推动教育国际化与文化交流，助力学术研究和决策支持，对于促进来华留学教育事业的高质量发展具有重要的现实意义和长远价值。

## 🎞️技术栈

**🚗前端 (vite-project):**

*   [Vue 3](https://vuejs.org/)
*   [Vite](https://vitejs.dev/)
*   [Vue Router](https://router.vuejs.org/)
*   [Pinia](https://pinia.vuejs.org/)
*   [Element Plus](https://element-plus.org/)
*   [Axios](https://axios-http.com/)

**🚕后端 (flaskProject):**

*   [Flask](https://flask.palletsprojects.com/)
*   [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
*   [Flask-CORS](https://flask-cors.readthedocs.io/)
*   [PyMySQL](https://github.com/PyMySQL/PyMySQL)
*   [MySQL](https://www.mysql.com/)

## 🚩主要功能

*   **用户系统**: 支持用户注册、登录和身份认证。
*   **内容管理**: 
    *   **官方政策**: 发布和管理留学相关的官方政策文件。
    *   **新闻资讯**: 提供最新的留学新闻和动态。
    *   **就业创业**: 分享就业和创业相关的资讯和机会。
*   **内容分类**: 对信息进行分类，方便用户查找。
*   **文件上传**: 支持图片等文件的上传。

## 🚀部署与运行

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
