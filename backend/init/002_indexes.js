// 补充索引与 TTL 设置
// 该脚本会在容器首次启动时自动执行（在 001_create_collections.js 之后）

const dbName = process.env.MONGO_INITDB_DATABASE || 'fakenews_db';
const db = db.getSiblingDB(dbName);

// === 复合索引优化 ===

// users 集合：复合查询索引
try {
  db.users.createIndex({ role: 1, is_active: 1, created_at: -1 });
  db.users.createIndex({ is_active: 1, last_login_at: -1 });
} catch (e) {
  print("Users compound indexes already exist or failed:", e.message);
}

// user_sessions 集合：会话管理索引
try {
  db.user_sessions.createIndex({ user_id: 1, expires_at: 1 });
  db.user_sessions.createIndex({ is_active: 1, expires_at: 1 });
  // TTL 索引：自动删除过期会话（7天）
  db.user_sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 604800 });
} catch (e) {
  print("User sessions indexes already exist or failed:", e.message);
}

// user_activity_log 集合：活动日志索引
try {
  db.user_activity_log.createIndex({ user_id: 1, activity_type: 1, created_at: -1 });
  db.user_activity_log.createIndex({ activity_type: 1, created_at: -1 });
  // TTL 索引：自动删除90天前的活动日志
  db.user_activity_log.createIndex({ created_at: 1 }, { expireAfterSeconds: 7776000 });
} catch (e) {
  print("User activity log indexes already exist or failed:", e.message);
}

// detection_results 集合：检测结果查询优化
try {
  db.detection_results.createIndex({ type: 1, created_at: -1 });
  db.detection_results.createIndex({ "result.final_prediction": 1, created_at: -1 });
  db.detection_results.createIndex({ "result.confidence": 1, created_at: -1 });
  // TTL 索引：自动删除1年前的检测结果
  db.detection_results.createIndex({ created_at: 1 }, { expireAfterSeconds: 31536000 });
} catch (e) {
  print("Detection results indexes already exist or failed:", e.message);
}

// generation_results 集合：生成结果查询优化
try {
  db.generation_results.createIndex({ topic: 1, strategy: 1, created_at: -1 });
  db.generation_results.createIndex({ strategy: 1, created_at: -1 });
  db.generation_results.createIndex({ model_type: 1, created_at: -1 });
  // TTL 索引：自动删除6个月前的生成结果
  db.generation_results.createIndex({ created_at: 1 }, { expireAfterSeconds: 15552000 });
} catch (e) {
  print("Generation results indexes already exist or failed:", e.message);
}

// === 文本搜索索引 ===
try {
  // 为检测文本创建文本索引（支持全文搜索）
  db.detection_results.createIndex({ text: "text" });
  // 为生成内容创建文本索引
  db.generation_results.createIndex({ "result.content": "text" });
} catch (e) {
  print("Text search indexes already exist or failed:", e.message);
}

// === 性能监控索引 ===
try {
  // 创建用于统计分析的索引
  db.detection_results.createIndex({ 
    type: 1, 
    "result.final_prediction": 1, 
    created_at: 1 
  });
  
  db.generation_results.createIndex({ 
    topic: 1, 
    strategy: 1, 
    model_type: 1, 
    created_at: 1 
  });
} catch (e) {
  print("Analytics indexes already exist or failed:", e.message);
}

print("=== 索引创建完成 ===");
print("已创建复合索引、TTL索引和文本搜索索引");
print("TTL 设置：");
print("- 用户会话：7天自动过期");
print("- 活动日志：90天自动过期");
print("- 检测结果：1年自动过期");
print("- 生成结果：6个月自动过期");
