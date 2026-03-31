from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt

# 创建 Flask 应用
app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 配置 JWT
app.config['JWT_SECRET_KEY'] = 'your-secret-key-with-at-least-32-bytes-length'  # 在生产环境中应该使用环境变量
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# 初始化数据库和 JWT
db = SQLAlchemy(app)
jwt = JWTManager(app)

# 定义用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        # 使用 bcrypt 加密密码
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        # 验证密码
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

# 创建数据库表
with app.app_context():
    db.create_all()

# 用户注册接口
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 检查必填字段
    if not data or 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    # 创建新用户
    new_user = User(
        username=data['username'],
        email=data['email']
    )
    new_user.set_password(data['password'])
    
    # 保存到数据库
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

# 用户登录接口
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # 检查必填字段
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    # 验证用户和密码
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401
    
    # 创建访问令牌（将用户 ID 转换为字符串）
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({'access_token': access_token}), 200

# 错误处理
@app.errorhandler(422)
def handle_unprocessable_entity(error):
    return jsonify({'message': 'Invalid request', 'error': str(error)}), 422

# 获取用户信息接口（需要登录）
@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    try:
        # 获取当前用户 ID（将字符串转换为整数）
        current_user_id = int(get_jwt_identity())
        
        # 查找用户
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # 返回用户信息（不包含密码）
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        }), 200
    except Exception as e:
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

# 修改用户信息接口（需要登录）
@app.route('/user', methods=['PUT'])
@jwt_required()
def update_user():
    try:
        # 获取当前用户 ID（将字符串转换为整数）
        current_user_id = int(get_jwt_identity())
        
        # 查找用户
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        # 更新用户信息
        if 'username' in data:
            # 检查新用户名是否已存在
            if User.query.filter_by(username=data['username']).filter(User.id != current_user_id).first():
                return jsonify({'message': 'Username already exists'}), 400
            user.username = data['username']
        
        if 'email' in data:
            # 检查新邮箱是否已存在
            if User.query.filter_by(email=data['email']).filter(User.id != current_user_id).first():
                return jsonify({'message': 'Email already exists'}), 400
            user.email = data['email']
        
        if 'password' in data:
            user.set_password(data['password'])
        
        # 保存到数据库
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
