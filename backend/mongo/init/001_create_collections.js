// Initialize database, collections, validators and indexes
// This script will be automatically executed when the container first starts

const dbName = process.env.MONGO_INITDB_DATABASE || 'fakenews_db';
const db = db.getSiblingDB(dbName);

// users collection + validation
if (!db.getCollectionNames().includes('users')) {
  db.createCollection('users', {
    validator: {
      $jsonSchema: {
        bsonType: 'object',
        required: ['username', 'email', 'password_hash', 'role', 'is_active', 'created_at'],
        properties: {
          username: { bsonType: 'string', minLength: 3 },
          email: { bsonType: 'string', pattern: '@' },
          password_hash: { bsonType: 'string' },
          salt: { bsonType: 'string' },
          role: { enum: ['user', 'admin'] },
          is_active: { bsonType: 'bool' },
          created_at: { bsonType: 'string' }
        },
        additionalProperties: false
      }
    },
    validationLevel: 'strict',
    validationAction: 'error'
  });
}
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ email: 1 }, { unique: true });

// user_sessions collection + validation
if (!db.getCollectionNames().includes('user_sessions')) {
  db.createCollection('user_sessions', {
    validator: {
      $jsonSchema: {
        bsonType: 'object',
        required: ['user_id', 'session_token', 'is_active', 'expires_at'],
        properties: {
          user_id: { bsonType: ['objectId', 'string'] },
          session_token: { bsonType: 'string' },
          is_active: { bsonType: 'bool' },
          expires_at: { bsonType: 'string' },
          ip_address: { bsonType: ['string', 'null'] }
        }
      }
    },
    validationLevel: 'moderate',
    validationAction: 'error'
  });
}
db.user_sessions.createIndex({ session_token: 1 }, { unique: true });
db.user_sessions.createIndex({ user_id: 1, is_active: 1 });

// user_activity_log collection
if (!db.getCollectionNames().includes('user_activity_log')) {
  db.createCollection('user_activity_log', {
    validator: {
      $jsonSchema: {
        bsonType: 'object',
        required: ['user_id', 'activity_type', 'created_at'],
        properties: {
          user_id: { bsonType: ['objectId', 'string'] },
          activity_type: { bsonType: 'string' },
          activity_description: { bsonType: ['string', 'null'] },
          created_at: { bsonType: 'string' }
        }
      }
    },
    validationLevel: 'moderate',
    validationAction: 'error'
  });
}
db.user_activity_log.createIndex({ user_id: 1, created_at: -1 });

// detection_results collection + validation
if (!db.getCollectionNames().includes('detection_results')) {
  db.createCollection('detection_results', {
    validator: {
      $jsonSchema: {
        bsonType: 'object',
        required: ['type', 'text', 'result', 'created_at'],
        properties: {
          type: { enum: ['baseline', 'improved'] },
          text: { bsonType: 'string' },
          image_url_or_b64: { bsonType: ['string', 'null'] },
          config: { bsonType: ['object', 'null'] },
          baseline: { bsonType: ['object', 'null'] },
          result: { bsonType: 'object' },
          created_at: { bsonType: 'string' }
        },
        additionalProperties: true
      }
    },
    validationLevel: 'strict',
    validationAction: 'error'
  });
}
db.detection_results.createIndex({ created_at: -1 });
db.detection_results.createIndex({ type: 1, created_at: -1 });

// generation_results collection + validation
if (!db.getCollectionNames().includes('generation_results')) {
  db.createCollection('generation_results', {
    validator: {
      $jsonSchema: {
        bsonType: 'object',
        required: ['topic', 'strategy', 'result', 'created_at'],
        properties: {
          topic: { bsonType: 'string' },
          strategy: { bsonType: 'string' },
          model_type: { bsonType: ['string', 'null'] },
          params: { bsonType: ['object', 'null'] },
          result: { bsonType: 'object' },
          created_at: { bsonType: 'string' }
        },
        additionalProperties: true
      }
    },
    validationLevel: 'strict',
    validationAction: 'error'
  });
}
db.generation_results.createIndex({ created_at: -1 });
db.generation_results.createIndex({ topic: 1, created_at: -1 });

// Initial example user (if not exists)
if (db.users.countDocuments({ username: 'testuser' }) === 0) {
  db.users.insertOne({
    username: 'testuser',
    email: 'testuser@example.com',
    password_hash: 'placeholder',
    salt: 'placeholder',
    role: 'user',
    is_active: true,
    created_at: new Date().toISOString()
  });
}
