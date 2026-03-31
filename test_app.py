import pytest
from app import app, db, User

@pytest.fixture
def client():
    # 配置测试环境
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # 创建测试客户端
    client = app.test_client()
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    yield client
    
    # 清理数据库
    with app.app_context():
        db.drop_all()

# 测试用户注册
def test_register(client):
    # 正常注册
    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'testpassword',
        'email': 'test@example.com'
    })
    assert response.status_code == 201
    assert response.json == {'message': 'User created successfully'}
    
    # 测试重复注册
    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'testpassword',
        'email': 'test@example.com'
    })
    assert response.status_code == 400
    assert response.json == {'message': 'Username already exists'}
    
    # 测试邮箱重复
    response = client.post('/register', json={
        'username': 'testuser2',
        'password': 'testpassword',
        'email': 'test@example.com'
    })
    assert response.status_code == 400
    assert response.json == {'message': 'Email already exists'}
    
    # 测试缺少字段
    response = client.post('/register', json={
        'username': 'testuser3'
    })
    assert response.status_code == 400
    assert response.json == {'message': 'Missing required fields'}

# 测试用户登录
def test_login(client):
    # 先注册一个用户
    client.post('/register', json={
        'username': 'testuser',
        'password': 'testpassword',
        'email': 'test@example.com'
    })
    
    # 正常登录
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
    
    # 测试密码错误
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json == {'message': 'Invalid username or password'}
    
    # 测试用户不存在
    response = client.post('/login', json={
        'username': 'nonexistent',
        'password': 'testpassword'
    })
    assert response.status_code == 401
    assert response.json == {'message': 'Invalid username or password'}
    
    # 测试缺少字段
    response = client.post('/login', json={
        'username': 'testuser'
    })
    assert response.status_code == 400
    assert response.json == {'message': 'Missing required fields'}

# 测试获取用户信息
def test_get_user(client):
    # 先注册并登录
    client.post('/register', json={
        'username': 'testuser',
        'password': 'testpassword',
        'email': 'test@example.com'
    })
    
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    access_token = login_response.json['access_token']
    
    # 带令牌访问
    response = client.get('/user', headers={
        'Authorization': f'Bearer {access_token}'
    })
    print(f"Response status: {response.status_code}")
    print(f"Response json: {response.json}")
    assert response.status_code == 200
    assert response.json['username'] == 'testuser'
    assert response.json['email'] == 'test@example.com'
    
    # 不带令牌访问
    response = client.get('/user')
    assert response.status_code == 401

# 测试修改用户信息
def test_update_user(client):
    # 先注册并登录
    client.post('/register', json={
        'username': 'testuser',
        'password': 'testpassword',
        'email': 'test@example.com'
    })
    
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    access_token = login_response.json['access_token']
    
    # 修改用户名和邮箱
    response = client.put('/user', headers={
        'Authorization': f'Bearer {access_token}'
    }, json={
        'username': 'newusername',
        'email': 'newemail@example.com'
    })
    assert response.status_code == 200
    assert response.json == {'message': 'User updated successfully'}
    
    # 验证修改是否成功
    response = client.get('/user', headers={
        'Authorization': f'Bearer {access_token}'
    })
    assert response.status_code == 200
    assert response.json['username'] == 'newusername'
    assert response.json['email'] == 'newemail@example.com'
    
    # 测试修改密码
    response = client.put('/user', headers={
        'Authorization': f'Bearer {access_token}'
    }, json={
        'password': 'newpassword'
    })
    assert response.status_code == 200
    assert response.json == {'message': 'User updated successfully'}
    
    # 验证新密码是否生效
    response = client.post('/login', json={
        'username': 'newusername',
        'password': 'newpassword'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
    
    # 测试修改为已存在的用户名
    client.post('/register', json={
        'username': 'existinguser',
        'password': 'testpassword',
        'email': 'existing@example.com'
    })
    
    response = client.put('/user', headers={
        'Authorization': f'Bearer {access_token}'
    }, json={
        'username': 'existinguser'
    })
    assert response.status_code == 400
    assert response.json == {'message': 'Username already exists'}
    
    # 不带令牌访问
    response = client.put('/user', json={
        'username': 'testuser'
    })
    assert response.status_code == 401
