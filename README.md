# Flask 用户系统

这是一个使用 Flask 实现的完整用户系统，包含用户注册、登录、用户管理等功能。

## 功能特点

- 用户注册：支持用户名、密码、邮箱注册，密码使用 bcrypt 加密存储
- 用户登录：登录成功后返回 JWT token
- 用户管理：只有登录用户才能访问，可以查看、修改自己的信息
- 所有接口返回 JSON 格式，适配移动端调用

## 技术栈

- Flask：Web 框架
- SQLite：数据库
- Flask-JWT-Extended：JWT 认证
- Flask-SQLAlchemy：ORM
- bcrypt：密码加密
- pytest：单元测试

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

应用将在 http://localhost:5000 运行。

### 3. 运行测试

```bash
pytest test_app.py
```

### 4. 部署

使用提供的部署脚本：

```bash
./deploy.sh
```

或者手动部署：

```bash
# 构建 Docker 镜像
docker-compose build

# 启动容器
docker-compose up -d
```

## API 接口

### 1. 用户注册

- **URL**：`/register`
- **方法**：`POST`
- **请求体**：
  ```json
  {
    "username": "testuser",
    "password": "testpassword",
    "email": "test@example.com"
  }
  ```
- **响应**：
  ```json
  {
    "message": "User created successfully"
  }
  ```

### 2. 用户登录

- **URL**：`/login`
- **方法**：`POST`
- **请求体**：
  ```json
  {
    "username": "testuser",
    "password": "testpassword"
  }
  ```
- **响应**：
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

### 3. 获取用户信息

- **URL**：`/user`
- **方法**：`GET`
- **请求头**：`Authorization: Bearer <access_token>`
- **响应**：
  ```json
  {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  }
  ```

### 4. 修改用户信息

- **URL**：`/user`
- **方法**：`PUT`
- **请求头**：`Authorization: Bearer <access_token>`
- **请求体**：
  ```json
  {
    "username": "newusername",
    "email": "newemail@example.com",
    "password": "newpassword"
  }
  ```
- **响应**：
  ```json
  {
    "message": "User updated successfully"
  }
  ```
