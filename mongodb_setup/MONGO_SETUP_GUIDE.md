# MongoDB 一键启动指南

## 概述
本项目使用 Docker Compose 提供 MongoDB 数据库服务，包含完整的初始化脚本，确保团队成员获得一致的数据库结构。

## 快速启动

### 1. 首次启动（推荐）
```bash
# 停止并删除所有容器和数据卷
docker compose -f docker-compose.mongo.yml down -v

# 启动 MongoDB 服务
docker compose -f docker-compose.mongo.yml up -d
```

### 2. 日常启动
```bash
# 仅启动服务（保留现有数据）
docker compose -f docker-compose.mongo.yml up -d
```

## 服务说明

### MongoDB 服务
- **端口**: 27017
- **认证**: admin/admin123
- **数据库**: fakenews_db
- **连接字符串**: `mongodb://admin:admin123@127.0.0.1:27017/fakenews_db?authSource=admin`

### Mongo Express 管理界面
- **端口**: 8081
- **访问地址**: http://127.0.0.1:8081
- **认证**: 无需认证（仅本地访问）

## 初始化脚本

项目包含三个初始化脚本，按顺序执行：

### 001_create_collections.js
- 创建核心集合：`users`, `user_sessions`, `user_activity_log`, `detection_results`, `generation_results`
- 设置 $jsonSchema 字段校验
- 创建基础索引

### 002_indexes.js
- 创建复合索引优化查询性能
- 设置 TTL 索引自动清理过期数据：
  - 用户会话：7天
  - 活动日志：90天
  - 检测结果：1年
  - 生成结果：6个月
- 创建文本搜索索引

### 003_seed.js
- 插入演示数据：
  - 3个演示用户（admin, researcher, tester）
  - 检测结果示例
  - 生成结果示例
  - 用户活动日志示例

## 演示数据

### 演示用户
| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | admin | 管理员账户 |
| researcher | researcher123 | user | 研究员账户 |
| tester | tester123 | user | 测试账户 |

### 集合结构

#### users 集合
```javascript
{
  username: String,        // 用户名（唯一）
  email: String,           // 邮箱（唯一）
  password_hash: String,   // 密码哈希
  salt: String,            // 盐值
  role: String,            // 角色：'user' | 'admin'
  is_active: Boolean,      // 是否激活
  created_at: String,      // 创建时间
  last_login_at: String    // 最后登录时间
}
```

#### detection_results 集合
```javascript
{
  type: String,            // 检测类型：'baseline' | 'improved'
  text: String,           // 检测文本
  image_url_or_b64: String, // 图片URL或base64
  config: Object,         // 检测配置
  baseline: Object,       // 基线检测结果
  result: Object,         // 最终检测结果
  created_at: String      // 创建时间
}
```

#### generation_results 集合
```javascript
{
  topic: String,          // 生成主题
  strategy: String,       // 生成策略
  model_type: String,     // 模型类型
  params: Object,         // 生成参数
  result: Object,         // 生成结果
  created_at: String      // 创建时间
}
```

## 常用命令

### 查看服务状态
```bash
docker compose -f docker-compose.mongo.yml ps
```

### 查看日志
```bash
docker compose -f docker-compose.mongo.yml logs mongodb
```

### 停止服务
```bash
docker compose -f docker-compose.mongo.yml down
```

### 完全重置（删除所有数据）
```bash
docker compose -f docker-compose.mongo.yml down -v
docker compose -f docker-compose.mongo.yml up -d
```

## 故障排除

### 1. 端口冲突
如果 27017 或 8081 端口被占用：
```bash
# 查看端口占用
netstat -ano | findstr :27017
netstat -ano | findstr :8081

# 停止占用进程或修改 docker-compose.mongo.yml 中的端口映射
```

### 2. 权限问题
确保 Docker 有足够权限访问项目目录。

### 3. 初始化脚本失败
检查 MongoDB 容器日志：
```bash
docker compose -f docker-compose.mongo.yml logs mongodb
```

### 4. 连接问题
验证连接字符串格式：
```
mongodb://admin:admin123@127.0.0.1:27017/fakenews_db?authSource=admin
```

## 开发建议

1. **数据持久化**: 数据存储在 Docker 卷中，容器重启不会丢失数据
2. **备份策略**: 定期备份重要数据
3. **环境隔离**: 不同环境使用不同的数据库名称
4. **监控**: 使用 Mongo Express 监控数据库状态

## 更新说明

当需要更新数据库结构时：
1. 修改初始化脚本
2. 执行完全重置命令
3. 重新启动服务

注意：完全重置会删除所有现有数据，请谨慎操作。
