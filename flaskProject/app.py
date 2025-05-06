from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json
import logging
import os
from werkzeug.utils import secure_filename
import enum
#from llm.div.predict import predict as predict_label
#from llm.spark.SparkUltra import get_spark_chat
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置日志
logging.basicConfig(level=logging.DEBUG)

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/liiuxue'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'liiuxue_secret_key'

# 文件上传配置
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 限制上传文件大小为5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# 定义模型
class User(db.Model):
    __tablename__ = 'users'  # 显式指定表名
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # 增加密码字段长度
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
class policy_lda_topics(db.Model):
    __tablename__ = 'policy_lda_topics'
    topic_id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(255), nullable=False)
    topic_keywords = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'topic_id': self.topic_id,
            'topic_name': self.topic_name,
            'topic_keywords': self.topic_keywords
        }

class CategoryEnum(enum.Enum):
    News = 'News'
    Official_Policy = 'Official_Policy'
    Employment_Entrepreneurship = 'Employment_Entrepreneurship'

class policy_documents(db.Model):
    __tablename__ = 'policy_documents'

    policy_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_name = db.Column(db.String(255))
    source_url = db.Column(db.String(255))
    title = db.Column(db.String(255), nullable=False)
    date_published = db.Column(db.Date)
    unit_published = db.Column(db.String(225))
    content = db.Column(db.Text)
    image_url = db.Column(db.Text)
    topic_id = db.Column(db.Integer, db.ForeignKey('policy_lda_topics.topic_id', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    category = db.Column(db.Enum(CategoryEnum), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def to_dict(self):
        return {
            'policy_id': self.policy_id,
            'source_name': self.source_name,
            'source_url': self.source_url,
            'title': self.title,
            'date_published': self.date_published,
            'unit_published': self.unit_published,
            'content': self.content,
            'image_url': self.image_url,
            'topic_id': self.topic_id,
            'category': self.category.value,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S') if self.last_updated else None
        }
    
# class News(db.Model):
#     __tablename__ = 'news'  # 显式指定表名
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(200), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     title_en = db.Column(db.String(200))
#     content_en = db.Column(db.Text)
#     category = db.Column(db.Integer, nullable=False)  # 0-4 代表新闻类别
#     image_url = db.Column(db.String(255))
#     created_at = db.Column(db.DateTime, default=datetime.datetime.now)

#     def to_dict(self):
#         return {
#             'id': self.id,
#             'title': self.title,
#             'content': self.content,
#             'title_en': self.title_en, 
#             'content_en': self.content_en,
#             'category': self.category,
#             'image_url': self.image_url,
#             'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
#         }

# class Policy(db.Model):
#     __tablename__ = 'policies'  # 显式指定表名
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(200), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     title_en = db.Column(db.String(200))
#     content_en = db.Column(db.Text)
#     category = db.Column(db.Integer, nullable=False)  # 5-9 代表政策类别
#     image_url = db.Column(db.String(255))
#     created_at = db.Column(db.DateTime, default=datetime.datetime.now)

#     def to_dict(self):
#         return {
#             'id': self.id,
#             'title': self.title,
#             'content': self.content,
#             'title_en': self.title_en,
#             'content_en': self.content_en,
#             'category': self.category,
#             'image_url': self.image_url,
#             'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
#         }

class ChatRecord(db.Model):
    __tablename__ = 'chat_records'  # 显式指定表名
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_message': self.user_message,
            'ai_response': self.ai_response,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# 可视化类型模型
class VisualizationType(db.Model):
    __tablename__ = 'visualization_types'
    
    viz_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(50), unique=True, nullable=False)
    
    # 关联关系
    visualizations = db.relationship('Visualization', backref='type', lazy=True)
    
    def to_dict(self):
        return {
            'viz_type_id': self.viz_type_id,
            'type_name': self.type_name
        }

# 可视化图表模型
class Visualization(db.Model):
    __tablename__ = 'visualizations'
    
    viz_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    viz_name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    viz_analysis = db.Column(db.Text, nullable=True)
    category = db.Column(db.Enum(CategoryEnum), nullable=False)
    viz_type_id = db.Column(db.Integer, db.ForeignKey('visualization_types.viz_type_id'), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    def to_dict(self):
        return {
            'viz_id': self.viz_id,
            'viz_name': self.viz_name,
            'image_url': self.image_url,
            'viz_analysis': self.viz_analysis,
            'category': self.category.value,
            'viz_type_id': self.viz_type_id,
            'viz_type_name': self.type.type_name if self.type else None,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S') if self.last_updated else None
        }

# 首先创建数据库表格
with app.app_context():
    db.create_all()
    app.logger.info("所有数据库表已创建")
    
    # 初始化可视化类型数据
    if VisualizationType.query.count() == 0:
        try:
            viz_types = [
                VisualizationType(viz_type_id=1,type_name='Trend_Chart'),
                VisualizationType(viz_type_id=2,type_name='Timeline'),
                VisualizationType(viz_type_id=3,type_name='Attitude_Chart'),
                VisualizationType(viz_type_id=4,type_name='Keyword_Cloud')
            ]
            db.session.add_all(viz_types)
            db.session.commit()
            app.logger.info("可视化类型初始数据已创建")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"创建可视化类型数据失败: {str(e)}")
    
    # 初始化政策LDA主题数据
    if policy_lda_topics.query.count() == 0:
        try:
            """
            0	教育咨询
1	国际合作
2	全球化与来华留学
3	教育政策解读
4	在华发展机遇
5	学生服务与支持
6	教育与学习
7	政策与建设
8	国际关系与交流
9   就业与工作"""
            topics = [
                policy_lda_topics(topic_id=0, topic_name='教育咨询', topic_keywords='教育 咨询 留学 海外 指导'),
                policy_lda_topics(topic_id=1, topic_name='国际合作', topic_keywords='国际 合作 交流 项目 协议'),
                policy_lda_topics(topic_id=2, topic_name='全球化与来华留学', topic_keywords='全球化 来华 留学 国际学生 文化'),
                policy_lda_topics(topic_id=3, topic_name='教育政策解读', topic_keywords='教育 政策 解读 法规 规定'),
                policy_lda_topics(topic_id=4, topic_name='在华发展机遇', topic_keywords='发展 机遇 就业 创业 前景'),
                policy_lda_topics(topic_id=5, topic_name='学生服务与支持', topic_keywords='服务 支持 帮助 资源 辅导'),
                policy_lda_topics(topic_id=6, topic_name='教育与学习', topic_keywords='教育 学习 课程 培训 技能'),
                policy_lda_topics(topic_id=7, topic_name='政策与建设', topic_keywords='政策 建设 改革 发展 规划'),
                policy_lda_topics(topic_id=8, topic_name='国际关系与交流', topic_keywords='国际 关系 交流 合作 外交'),
                policy_lda_topics(topic_id=9, topic_name='就业与工作', topic_keywords='就业 工作 职业 求职 实习')
            ]
            # 单条插入以避免批量插入问题
            for topic in topics:
                existing = policy_lda_topics.query.filter_by(topic_id=topic.topic_id).first()
                if not existing:
                    db.session.add(topic)
                    db.session.commit()
            app.logger.info("政策LDA主题初始数据已创建")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"创建政策LDA主题数据失败: {str(e)}")
        
# 然后导入依赖模块（避免循环导入）
# from llm.div.predict import predict as predict_label
# from llm.spark.SparkUltra import get_spark_chat

# 首页路由
@app.route('/')
def hello_world():
    return jsonify({'message': 'Welcome to Liiuxue API'})

# 用户相关接口
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': '注册成功', 'user': new_user.to_dict()}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    return jsonify({
        'message': '登录成功',
        'user': user.to_dict()
    })


# 修改密码接口
@app.route('/api/users/<int:user_id>/password', methods=['PUT'])
def change_password(user_id):
    data = request.get_json()
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'error': '旧密码和新密码不能为空'}), 400
    
    user = User.query.get_or_404(user_id)
    
    # 验证旧密码
    if not check_password_hash(user.password, old_password):
        return jsonify({'error': '旧密码不正确'}), 401
    
    # 更新密码
    user.password = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'})

@app.route('/api/users', methods=['GET'])
def get_users():
    # 返回所有用户，包括管理员
    users = User.query.all()
    return jsonify({'users': [user.to_dict() for user in users]})

# 获取单个用户信息
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'user': user.to_dict()})

#更新用户权限
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    
    user = User.query.get_or_404(user_id)
    
    # 更新用户名（如果提供）
    '''
    if 'username' in data:
        # 检查用户名是否已存在（排除当前用户）
        if User.query.filter(User.username == data['username'], User.id != user_id).first():
            return jsonify({'error': '用户名已存在'}), 400
        user.username = data['username']'''
    
    # 更新密码（如果提供
    '''
    if 'password' in data:
        user.password = generate_password_hash(data['password'])'''
    
    # 更新管理员状态（如果提供）
    if 'is_admin' in data:
        user.is_admin = bool(data['is_admin'])
    
    db.session.commit()
    
    return jsonify({'message': '用户更新成功', 'user': user.to_dict()})

# 删除用户
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': '用户删除成功'})

# 新闻相关接口
@app.route('/api/news', methods=['GET'])
def get_news():
    news_list = policy_documents.query.filter_by(category=CategoryEnum.News).order_by(policy_documents.last_updated.desc()).all()
    
    result = []
    for news in news_list:
        news_dict = {
            'policy_id': news.policy_id,
            'title': news.title,
            'content': news.content,
            'image_url': news.image_url,
            'date_published': news.date_published.strftime('%Y-%m-%d') if news.date_published else None,
            'unit_published': news.unit_published,
            'source_name': news.source_name,
            'source_url': news.source_url,
            'topic_id': news.topic_id,
            'last_updated': news.last_updated.strftime('%Y-%m-%d %H:%M:%S') if news.last_updated else None
        }
        result.append(news_dict)
    
    return jsonify({'news': result})

@app.route('/api/news/<int:news_id>', methods=['GET'])
def get_news_detail(news_id):
    news = policy_documents.query.filter_by(policy_id=news_id, category=CategoryEnum.News).first_or_404()
    return jsonify({'news': news.to_dict()})

@app.route('/api/news', methods=['POST'])
def add_news():
    data = request.get_json()
    
    title = data.get('title')
    content = data.get('content')
    source_name = data.get('source_name')
    source_url = data.get('source_url')
    image_url = data.get('image_url')
    topic_id = data.get('topic_id', 0)  # 默认使用第一个主题
    unit_published = data.get('unit_published')
    date_published = data.get('date_published')
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    # 处理日期
    try:
        if date_published:
            date_published = datetime.datetime.strptime(date_published, '%Y-%m-%d').date()
        else:
            date_published = datetime.datetime.now().date()
    except ValueError:
        return jsonify({'error': '日期格式不正确，请使用YYYY-MM-DD格式'}), 400
    
    # 创建新闻
    new_news = policy_documents(
        title=title,
        content=content,
        source_name=source_name,
        source_url=source_url,
        image_url=image_url,
        category=CategoryEnum.News,
        topic_id=topic_id,
        unit_published=unit_published,
        date_published=date_published
    )
    
    db.session.add(new_news)
    db.session.commit()
    
    return jsonify({'message': '新闻添加成功', 'news': new_news.to_dict()}), 201

# 政策相关接口
@app.route('/api/policies', methods=['GET'])
def get_policies():
    policies = policy_documents.query.filter_by(category=CategoryEnum.Official_Policy).order_by(policy_documents.last_updated.desc()).all()
    
    result = []
    for policy in policies:
        policy_dict = {
            'policy_id': policy.policy_id,
            'title': policy.title,
            'content': policy.content,
            'image_url': policy.image_url,
            'date_published': policy.date_published.strftime('%Y-%m-%d') if policy.date_published else None,
            'unit_published': policy.unit_published,
            'source_name': policy.source_name,
            'source_url': policy.source_url,
            'topic_id': policy.topic_id,
            'last_updated': policy.last_updated.strftime('%Y-%m-%d %H:%M:%S') if policy.last_updated else None
        }
        result.append(policy_dict)
    
    return jsonify({'policies': result})

@app.route('/api/policies/<int:policy_id>', methods=['GET'])
def get_policy_detail(policy_id):
    policy = policy_documents.query.filter_by(policy_id=policy_id, category=CategoryEnum.Official_Policy).first_or_404()
    return jsonify({'policy': policy.to_dict()})

@app.route('/api/policies', methods=['POST'])
def add_policy():
    data = request.get_json()
    
    title = data.get('title')
    content = data.get('content')
    source_name = data.get('source_name')
    source_url = data.get('source_url')
    image_url = data.get('image_url')
    topic_id = data.get('topic_id', 7)  # 默认使用"政策与建设"主题
    unit_published = data.get('unit_published')
    date_published = data.get('date_published')
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    # 处理日期
    try:
        if date_published:
            date_published = datetime.datetime.strptime(date_published, '%Y-%m-%d').date()
        else:
            date_published = datetime.datetime.now().date()
    except ValueError:
        return jsonify({'error': '日期格式不正确，请使用YYYY-MM-DD格式'}), 400
    
    # 创建政策
    new_policy = policy_documents(
        title=title,
        content=content,
        source_name=source_name,
        source_url=source_url,
        image_url=image_url,
        category=CategoryEnum.Official_Policy,
        topic_id=topic_id,
        unit_published=unit_published,
        date_published=date_published
    )
    
    db.session.add(new_policy)
    db.session.commit()
    
    return jsonify({'message': '政策添加成功', 'policy': new_policy.to_dict()}), 201

# 搜索接口
@app.route('/api/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '')
    search_type = request.args.get('type', 'all')  # all, news, policy
    
    if not keyword:
        return jsonify({'error': '搜索关键词不能为空'}), 400
    
    results = []
    
    if search_type == 'all' or search_type == 'news':
        news_results = policy_documents.query.filter(
            policy_documents.category == CategoryEnum.News,
            (policy_documents.title.like(f'%{keyword}%')) | 
            (policy_documents.content.like(f'%{keyword}%'))
        ).all()
        results.extend([{'type': 'news', **news.to_dict()} for news in news_results])
    
    if search_type == 'all' or search_type == 'policy':
        policy_results = policy_documents.query.filter(
            policy_documents.category == CategoryEnum.Official_Policy,
            (policy_documents.title.like(f'%{keyword}%')) | 
            (policy_documents.content.like(f'%{keyword}%'))
        ).all()
        results.extend([{'type': 'policy', **policy.to_dict()} for policy in policy_results])
    
    return jsonify({'results': results})

# AI聊天接口
'''
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    
    user_id = data.get('user_id')
    message = data.get('message')
    
    if not message:
        return jsonify({'error': '消息不能为空'}), 400
    
    try:
        spark_chat = get_spark_chat()
        response = spark_chat.chat(message)
        #response = "AI服务暂时不可用，请稍后再试。" # 临时替代响应
    except Exception as e:
        app.logger.error(f"AI聊天错误: {str(e)}")
        response = "抱歉，AI服务暂时不可用，请稍后再试。"
    
    # 记录聊天记录
    if user_id:
        chat_record = ChatRecord(
            user_id=user_id,
            user_message=message,
            ai_response=response
        )
        db.session.add(chat_record)
        db.session.commit()
    
    return jsonify({
        'message': response
    })

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': '用户ID不能为空'}), 400
    
    history = ChatRecord.query.filter_by(user_id=user_id).order_by(ChatRecord.created_at.asc()).all()
    
    return jsonify({
        'history': [record.to_dict() for record in history]
    })
'''
# 创建管理员账号
def create_admin():
    try:
        # 检查管理员是否已经存在
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            app.logger.info("管理员账号创建成功")
        else:
            app.logger.info("管理员账号已存在")
    except Exception as e:
        app.logger.error(f"创建管理员账号失败: {str(e)}")

# 创建管理员账号
with app.app_context():
    create_admin()

# 文件上传相关函数
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 图片上传接口
@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400
    
    # 保存文件
    try:
        filename = secure_filename(file.filename)
        # 添加时间戳避免文件名冲突
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        new_filename = f"{timestamp}_{filename}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(file_path)
        
        # 构建URL路径
        file_url = f"/static/uploads/{new_filename}"
        
        return jsonify({
            'message': '图片上传成功',
            'url': file_url
        }), 200
    except Exception as e:
        app.logger.error(f"图片上传错误: {str(e)}")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

# 更新新闻接口
@app.route('/api/news/<int:news_id>', methods=['PUT'])
def update_news(news_id):
    news = policy_documents.query.filter_by(policy_id=news_id, category=CategoryEnum.News).first_or_404()
    data = request.get_json()
    
    title = data.get('title')
    content = data.get('content')
    source_name = data.get('source_name')
    source_url = data.get('source_url')
    image_url = data.get('image_url')
    topic_id = data.get('topic_id')
    unit_published = data.get('unit_published')
    date_published = data.get('date_published')
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    # 更新新闻
    news.title = title
    news.content = content
    
    if source_name is not None:
        news.source_name = source_name
    if source_url is not None:
        news.source_url = source_url
    if image_url is not None:
        news.image_url = image_url
    if topic_id is not None:
        news.topic_id = topic_id
    if unit_published is not None:
        news.unit_published = unit_published
    
    # 处理日期
    if date_published is not None:
        try:
            news.date_published = datetime.datetime.strptime(date_published, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式不正确，请使用YYYY-MM-DD格式'}), 400
    
    db.session.commit()
    
    return jsonify({'message': '新闻更新成功', 'news': news.to_dict()})

# 更新政策接口
@app.route('/api/policies/<int:policy_id>', methods=['PUT'])
def update_policy(policy_id):
    policy = policy_documents.query.filter_by(policy_id=policy_id, category=CategoryEnum.Official_Policy).first_or_404()
    data = request.get_json()
    
    title = data.get('title')
    content = data.get('content')
    source_name = data.get('source_name')
    source_url = data.get('source_url')
    image_url = data.get('image_url')
    topic_id = data.get('topic_id')
    unit_published = data.get('unit_published')
    date_published = data.get('date_published')
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    # 更新政策
    policy.title = title
    policy.content = content
    
    if source_name is not None:
        policy.source_name = source_name
    if source_url is not None:
        policy.source_url = source_url
    if image_url is not None:
        policy.image_url = image_url
    if topic_id is not None:
        policy.topic_id = topic_id
    if unit_published is not None:
        policy.unit_published = unit_published
    
    # 处理日期
    if date_published is not None:
        try:
            policy.date_published = datetime.datetime.strptime(date_published, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式不正确，请使用YYYY-MM-DD格式'}), 400
    
    db.session.commit()
    
    return jsonify({'message': '政策更新成功', 'policy': policy.to_dict()})

# 删除新闻接口
@app.route('/api/news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    news = policy_documents.query.filter_by(policy_id=news_id, category=CategoryEnum.News).first_or_404()
    
    db.session.delete(news)
    db.session.commit()
    
    return jsonify({'message': '新闻删除成功'})

# 删除政策接口
@app.route('/api/policies/<int:policy_id>', methods=['DELETE'])
def delete_policy(policy_id):
    policy = policy_documents.query.filter_by(policy_id=policy_id, category=CategoryEnum.Official_Policy).first_or_404()
    
    db.session.delete(policy)
    db.session.commit()
    
    return jsonify({'message': '政策删除成功'})

# 获取可视化类型
@app.route('/api/visualization-types', methods=['GET'])
def get_visualization_types():
    types = VisualizationType.query.all()
    return jsonify({'types': [t.to_dict() for t in types]})

# 添加可视化类型
@app.route('/api/visualization-types', methods=['POST'])
def add_visualization_type():
    data = request.get_json()
    
    type_name = data.get('type_name')
    if not type_name:
        return jsonify({'error': '类型名称不能为空'}), 400
    
    # 检查是否已存在同名类型
    if VisualizationType.query.filter_by(type_name=type_name).first():
        return jsonify({'error': '已存在同名可视化类型'}), 400
    
    new_type = VisualizationType(type_name=type_name)
    db.session.add(new_type)
    db.session.commit()
    
    return jsonify({'message': '可视化类型添加成功', 'type': new_type.to_dict()}), 201

# 更新可视化类型
@app.route('/api/visualization-types/<int:type_id>', methods=['PUT'])
def update_visualization_type(type_id):
    data = request.get_json()
    
    type_name = data.get('type_name')
    if not type_name:
        return jsonify({'error': '类型名称不能为空'}), 400
    
    viz_type = VisualizationType.query.get_or_404(type_id)
    
    # 检查是否已存在同名类型（排除自身）
    existing = VisualizationType.query.filter_by(type_name=type_name).first()
    if existing and existing.viz_type_id != type_id:
        return jsonify({'error': '已存在同名可视化类型'}), 400
    
    viz_type.type_name = type_name
    db.session.commit()
    
    return jsonify({'message': '可视化类型更新成功', 'type': viz_type.to_dict()})

# 删除可视化类型
@app.route('/api/visualization-types/<int:type_id>', methods=['DELETE'])
def delete_visualization_type(type_id):
    # 检查是否有可视化使用该类型
    if Visualization.query.filter_by(viz_type_id=type_id).first():
        return jsonify({'error': '该类型下有可视化数据，无法删除'}), 400
    
    viz_type = VisualizationType.query.get_or_404(type_id)
    db.session.delete(viz_type)
    db.session.commit()
    
    return jsonify({'message': '可视化类型删除成功'})

# 获取可视化列表
@app.route('/api/visualizations', methods=['GET'])
def get_visualizations():
    category = request.args.get('category')
    viz_type_id = request.args.get('viz_type_id')
    
    query = Visualization.query
    
    if category:
        try:
            category_enum = CategoryEnum[category]
            query = query.filter_by(category=category_enum)
        except (KeyError, ValueError):
            return jsonify({'error': '无效的分类参数'}), 400
    
    if viz_type_id:
        try:
            viz_type_id = int(viz_type_id)
            query = query.filter_by(viz_type_id=viz_type_id)
        except ValueError:
            return jsonify({'error': '无效的类型ID参数'}), 400
    
    visualizations = query.order_by(Visualization.last_updated.desc()).all()
    return jsonify({'visualizations': [v.to_dict() for v in visualizations]})

# 获取单个可视化
@app.route('/api/visualizations/<int:viz_id>', methods=['GET'])
def get_visualization(viz_id):
    viz = Visualization.query.get_or_404(viz_id)
    return jsonify({'visualization': viz.to_dict()})

# 添加可视化
@app.route('/api/visualizations', methods=['POST'])
def add_visualization():
    data = request.get_json()
    
    viz_name = data.get('viz_name')
    viz_analysis = data.get('viz_analysis')
    image_url = data.get('image_url')
    category = data.get('category')
    viz_type_id = data.get('viz_type_id')
    
    if not viz_name or not category or not viz_type_id:
        return jsonify({'error': '名称、分类和类型不能为空'}), 400
    
    # 验证类别
    try:
        category = CategoryEnum[category]
    except (KeyError, ValueError):
        return jsonify({'error': '无效的分类'}), 400
    
    # 验证类型ID
    if not VisualizationType.query.get(viz_type_id):
        return jsonify({'error': '无效的可视化类型ID'}), 400
    
    # 创建可视化
    new_viz = Visualization(
        viz_name=viz_name,
        viz_analysis=viz_analysis,
        image_url=image_url,
        category=category,
        viz_type_id=viz_type_id
    )
    
    db.session.add(new_viz)
    db.session.commit()
    
    return jsonify({'message': '可视化添加成功', 'visualization': new_viz.to_dict()}), 201

# 更新可视化
@app.route('/api/visualizations/<int:viz_id>', methods=['PUT'])
def update_visualization(viz_id):
    data = request.get_json()
    
    viz_name = data.get('viz_name')
    viz_analysis = data.get('viz_analysis')
    image_url = data.get('image_url')
    category = data.get('category')
    viz_type_id = data.get('viz_type_id')
    
    if not viz_name or not category or not viz_type_id:
        return jsonify({'error': '名称、分类和类型不能为空'}), 400
    
    visualization = Visualization.query.get_or_404(viz_id)
    
    # 验证类别
    try:
        category = CategoryEnum[category]
    except (KeyError, ValueError):
        return jsonify({'error': '无效的分类'}), 400
    
    # 验证类型ID
    if not VisualizationType.query.get(viz_type_id):
        return jsonify({'error': '无效的可视化类型ID'}), 400
    
    # 更新可视化
    visualization.viz_name = viz_name
    visualization.viz_analysis = viz_analysis
    visualization.image_url = image_url
    visualization.category = category
    visualization.viz_type_id = viz_type_id
    
    db.session.commit()
    
    return jsonify({'message': '可视化更新成功', 'visualization': visualization.to_dict()})

# 删除可视化
@app.route('/api/visualizations/<int:viz_id>', methods=['DELETE'])
def delete_visualization(viz_id):
    visualization = Visualization.query.get_or_404(viz_id)
    db.session.delete(visualization)
    db.session.commit()
    
    return jsonify({'message': '可视化删除成功'})

# 获取政策主题接口
@app.route('/api/policy-topics', methods=['GET'])
def get_policy_topics():
    topics = policy_lda_topics.query.all()
    return jsonify({'topics': [topic.to_dict() for topic in topics]})

# 添加主题
@app.route('/api/policy-topics', methods=['POST'])
def add_topic():
    # 验证用户是否为管理员
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': '需要用户ID'}), 400
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': '权限不足'}), 403
        
    data = request.get_json()
    topic_name = data.get('topic_name')
    
    if not topic_name:
        return jsonify({'error': '主题名称不能为空'}), 400
    
    # 确定最大的主题ID值
    max_topic = policy_lda_topics.query.order_by(policy_lda_topics.topic_id.desc()).first()
    next_id = max_topic.topic_id + 1 if max_topic else 0
    
    # 创建新主题
    new_topic = policy_lda_topics(
        topic_id=next_id,
        topic_name=topic_name
    )
    
    db.session.add(new_topic)
    db.session.commit()
    
    return jsonify({'message': '主题添加成功', 'topic': new_topic.to_dict()}), 201

# 更新主题
@app.route('/api/policy-topics/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    # 验证用户是否为管理员
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': '需要用户ID'}), 400
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': '权限不足'}), 403
        
    topic = policy_lda_topics.query.get_or_404(topic_id)
    data = request.get_json()
    
    topic_name = data.get('topic_name')
    if not topic_name:
        return jsonify({'error': '主题名称不能为空'}), 400
    
    topic.topic_name = topic_name
    db.session.commit()
    
    return jsonify({'message': '主题更新成功', 'topic': topic.to_dict()})

# 删除主题
@app.route('/api/policy-topics/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    # 验证用户是否为管理员
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': '需要用户ID'}), 400
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': '权限不足'}), 403
    
    # 检查是否有文章使用该主题
    if policy_documents.query.filter_by(topic_id=topic_id).first():
        return jsonify({'error': '该主题下有文章，无法删除'}), 400
    
    topic = policy_lda_topics.query.get_or_404(topic_id)
    db.session.delete(topic)
    db.session.commit()
    
    return jsonify({'message': '主题删除成功'})

# 主题预测接口
'''
@app.route('/api/predict-topic', methods=['POST'])
def predict_topic():
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'error': '文本内容不能为空'}), 400
    
    try:
        topic_id = predict_label(text)
        
        return jsonify({
            'message': '预测成功',
            'topic_id': int(topic_id)
        })
    except Exception as e:
        app.logger.error(f"主题预测错误: {str(e)}")
        return jsonify({'error': f'预测失败: {str(e)}'}), 500
'''
if __name__ == '__main__':
    app.run(debug=True)
