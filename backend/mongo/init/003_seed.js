// Demo data insertion
// This script will be automatically executed when the container first starts (after 001_create_collections.js and 002_indexes.js)

const dbName = process.env.MONGO_INITDB_DATABASE || 'fakenews_db';
const db = db.getSiblingDB(dbName);

// === Demo User Data ===
const demoUsers = [
  {
    username: 'admin',
    email: 'admin@fakenews.com',
    password_hash: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J8Kz8Kz8K', // password: admin123
    salt: 'salt_admin',
    role: 'admin',
    is_active: true,
    created_at: new Date().toISOString(),
    last_login_at: new Date().toISOString()
  },
  {
    username: 'researcher',
    email: 'researcher@fakenews.com',
    password_hash: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J8Kz8Kz8K', // password: researcher123
    salt: 'salt_researcher',
    role: 'user',
    is_active: true,
    created_at: new Date().toISOString(),
    last_login_at: new Date().toISOString()
  },
  {
    username: 'tester',
    email: 'tester@fakenews.com',
    password_hash: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J8Kz8Kz8K', // password: tester123
    salt: 'salt_tester',
    role: 'user',
    is_active: true,
    created_at: new Date().toISOString(),
    last_login_at: null
  }
];

// Insert demo users (if not exists)
demoUsers.forEach(user => {
  if (db.users.countDocuments({ username: user.username }) === 0) {
    db.users.insertOne(user);
    print(`Inserted demo user: ${user.username}`);
  }
});

// === Demo Detection Results ===
const demoDetectionResults = [
  {
    type: 'baseline',
    text: 'Breaking: Scientists discover that drinking water causes 100% mortality rate in laboratory mice.',
    image_url_or_b64: null,
    config: {
      models: ['roberta', 'clip', 'gpt4'],
      confidence_threshold: 0.7
    },
    baseline: {
      roberta_score: 0.95,
      clip_score: 0.88,
      gpt4_score: 0.92
    },
    result: {
      final_prediction: 'fake',
      confidence: 0.92,
      model_scores: {
        roberta: 0.95,
        clip: 0.88,
        gpt4: 0.92
      },
      reasoning: 'This claim contradicts basic scientific knowledge about water consumption.',
      detailed_report: {
        linguistic_analysis: 'Uses sensational language typical of fake news',
        factual_verification: 'Contradicts established medical knowledge',
        source_credibility: 'No credible source provided'
      }
    },
    created_at: new Date().toISOString()
  },
  {
    type: 'improved',
    text: 'New study shows that regular exercise can improve cognitive function in elderly patients.',
    image_url_or_b64: null,
    config: {
      enable_rhetorical_analysis: true,
      enable_consistency_check: true,
      enable_fact_verification: true
    },
    baseline: null,
    result: {
      final_prediction: 'real',
      confidence: 0.87,
      rhetorical_analysis: {
        emotional_appeal: 'moderate',
        sensationalism_score: 0.2,
        credibility_indicators: 0.8
      },
      consistency_check: {
        internal_consistency: 0.9,
        external_consistency: 0.85
      },
      fact_verification: {
        wikipedia_score: 0.8,
        tavily_score: 0.75,
        overall_verification: 0.78
      },
      detailed_report: {
        linguistic_analysis: 'Uses moderate, scientific language',
        factual_verification: 'Supported by multiple credible sources',
        source_credibility: 'High - references peer-reviewed studies'
      }
    },
    created_at: new Date().toISOString()
  }
];

// Insert demo detection results
demoDetectionResults.forEach((result, index) => {
  if (db.detection_results.countDocuments({ text: result.text }) === 0) {
    db.detection_results.insertOne(result);
    print(`Inserted demo detection result ${index + 1}`);
  }
});

// === Demo Generation Results ===
const demoGenerationResults = [
  {
    topic: 'technology',
    strategy: 'sensational_headlines',
    model_type: 'gpt-4o',
    params: {
      temperature: 0.8,
      max_tokens: 500,
      creativity_level: 'high'
    },
    result: {
      content: 'BREAKING: New AI Technology Can Read Your Mind Through WiFi Signals!',
      strategy_used: 'sensational_headlines',
      generation_quality: 0.85,
      believability_score: 0.72,
      detection_difficulty: 'medium',
      metadata: {
        word_count: 12,
        emotional_tone: 'sensational',
        target_audience: 'general_public'
      }
    },
    created_at: new Date().toISOString()
  },
  {
    topic: 'health',
    strategy: 'misleading_statistics',
    model_type: 'gpt-4o',
    params: {
      temperature: 0.7,
      max_tokens: 400,
      creativity_level: 'medium'
    },
    result: {
      content: 'Study reveals that 95% of people who eat vegetables develop serious health problems within 5 years.',
      strategy_used: 'misleading_statistics',
      generation_quality: 0.78,
      believability_score: 0.65,
      detection_difficulty: 'high',
      metadata: {
        word_count: 18,
        emotional_tone: 'alarming',
        target_audience: 'health_conscious'
      }
    },
    created_at: new Date().toISOString()
  },
  {
    topic: 'politics',
    strategy: 'conspiracy_theory',
    model_type: 'gpt-4o',
    params: {
      temperature: 0.9,
      max_tokens: 600,
      creativity_level: 'high'
    },
    result: {
      content: 'Leaked documents reveal that world leaders have been secretly controlling weather patterns for decades to manipulate global economies.',
      strategy_used: 'conspiracy_theory',
      generation_quality: 0.82,
      believability_score: 0.58,
      detection_difficulty: 'medium',
      metadata: {
        word_count: 20,
        emotional_tone: 'conspiratorial',
        target_audience: 'conspiracy_theorists'
      }
    },
    created_at: new Date().toISOString()
  }
];

// Insert demo generation results
demoGenerationResults.forEach((result, index) => {
  if (db.generation_results.countDocuments({ 
    topic: result.topic, 
    strategy: result.strategy,
    "result.content": result.result.content
  }) === 0) {
    db.generation_results.insertOne(result);
    print(`Inserted demo generation result ${index + 1}`);
  }
});

// === Demo User Activity Logs ===
const demoActivityLogs = [
  {
    user_id: 'admin',
    activity_type: 'login',
    activity_description: 'User logged in successfully',
    created_at: new Date().toISOString()
  },
  {
    user_id: 'researcher',
    activity_type: 'detection_request',
    activity_description: 'Performed fake news detection on text sample',
    created_at: new Date().toISOString()
  },
  {
    user_id: 'tester',
    activity_type: 'generation_request',
    activity_description: 'Generated fake news content using conspiracy theory strategy',
    created_at: new Date().toISOString()
  }
];

// Insert demo activity logs
demoActivityLogs.forEach((log, index) => {
  if (db.user_activity_log.countDocuments({ 
    user_id: log.user_id,
    activity_type: log.activity_type,
    created_at: log.created_at
  }) === 0) {
    db.user_activity_log.insertOne(log);
    print(`Inserted demo activity log ${index + 1}`);
  }
});

print("=== Demo Data Insertion Complete ===");
print("Inserted the following demo data:");
print("- 3 demo users (admin, researcher, tester)");
print("- 2 detection result examples");
print("- 3 generation result examples");
print("- 3 user activity log examples");
print("");
print("Demo user login credentials:");
print("- admin / admin123");
print("- researcher / researcher123");
print("- tester / tester123");
