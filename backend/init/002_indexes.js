// Additional indexes and TTL settings
// This script will be automatically executed when the container first starts (after 001_create_collections.js)

const dbName = process.env.MONGO_INITDB_DATABASE || 'fakenews_db';
const db = db.getSiblingDB(dbName);

// === Compound Index Optimization ===

// users collection: compound query indexes
try {
  db.users.createIndex({ role: 1, is_active: 1, created_at: -1 });
  db.users.createIndex({ is_active: 1, last_login_at: -1 });
} catch (e) {
  print("Users compound indexes already exist or failed:", e.message);
}

// user_sessions collection: session management indexes
try {
  db.user_sessions.createIndex({ user_id: 1, expires_at: 1 });
  db.user_sessions.createIndex({ is_active: 1, expires_at: 1 });
  // TTL index: automatically delete expired sessions (7 days)
  db.user_sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 604800 });
} catch (e) {
  print("User sessions indexes already exist or failed:", e.message);
}

// user_activity_log collection: activity log indexes
try {
  db.user_activity_log.createIndex({ user_id: 1, activity_type: 1, created_at: -1 });
  db.user_activity_log.createIndex({ activity_type: 1, created_at: -1 });
  // TTL index: automatically delete activity logs older than 90 days
  db.user_activity_log.createIndex({ created_at: 1 }, { expireAfterSeconds: 7776000 });
} catch (e) {
  print("User activity log indexes already exist or failed:", e.message);
}

// detection_results collection: detection result query optimization
try {
  db.detection_results.createIndex({ type: 1, created_at: -1 });
  db.detection_results.createIndex({ "result.final_prediction": 1, created_at: -1 });
  db.detection_results.createIndex({ "result.confidence": 1, created_at: -1 });
  // TTL index: automatically delete detection results older than 1 year
  db.detection_results.createIndex({ created_at: 1 }, { expireAfterSeconds: 31536000 });
} catch (e) {
  print("Detection results indexes already exist or failed:", e.message);
}

// generation_results collection: generation result query optimization
try {
  db.generation_results.createIndex({ topic: 1, strategy: 1, created_at: -1 });
  db.generation_results.createIndex({ strategy: 1, created_at: -1 });
  db.generation_results.createIndex({ model_type: 1, created_at: -1 });
  // TTL index: automatically delete generation results older than 6 months
  db.generation_results.createIndex({ created_at: 1 }, { expireAfterSeconds: 15552000 });
} catch (e) {
  print("Generation results indexes already exist or failed:", e.message);
}

// === Text Search Indexes ===
try {
  // Create text index for detection text (supports full-text search)
  db.detection_results.createIndex({ text: "text" });
  // Create text index for generation content
  db.generation_results.createIndex({ "result.content": "text" });
} catch (e) {
  print("Text search indexes already exist or failed:", e.message);
}

// === Performance Monitoring Indexes ===
try {
  // Create indexes for statistical analysis
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

print("=== Index Creation Complete ===");
print("Created compound indexes, TTL indexes and text search indexes");
print("TTL Settings:");
print("- User sessions: auto-expire after 7 days");
print("- Activity logs: auto-expire after 90 days");
print("- Detection results: auto-expire after 1 year");
print("- Generation results: auto-expire after 6 months");
