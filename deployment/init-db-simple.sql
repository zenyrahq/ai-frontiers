-- AI Frontiers Database Initialization Script (Simplified)
-- Without pgvector extension for initial deployment

-- Content table
CREATE TABLE IF NOT EXISTS contents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content TEXT,
    original_url VARCHAR(1000) UNIQUE,
    source VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    tags TEXT[],
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    is_processed BOOLEAN DEFAULT FALSE
);

-- User table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

-- User action table
CREATE TABLE IF NOT EXISTS user_actions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER REFERENCES contents(id) ON DELETE CASCADE,
    action_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- API key table
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20),
    rate_limit INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Entity table
CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    aliases TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Entity relation table
CREATE TABLE IF NOT EXISTS entity_relations (
    id SERIAL PRIMARY KEY,
    source_entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
    target_entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
    relation_type VARCHAR(100) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    evidence TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_entity_id, target_entity_id, relation_type)
);

-- Content-Entity relation table
CREATE TABLE IF NOT EXISTS content_entities (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES contents(id) ON DELETE CASCADE,
    entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
    relevance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(content_id, entity_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_contents_category ON contents(category);
CREATE INDEX IF NOT EXISTS idx_contents_source ON contents(source);
CREATE INDEX IF NOT EXISTS idx_contents_published_at ON contents(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_contents_created_at ON contents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_contents_tags ON contents USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_contents_metadata ON contents USING GIN(metadata);

CREATE INDEX IF NOT EXISTS idx_user_actions_user_id ON user_actions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_actions_content_id ON user_actions(content_id);
CREATE INDEX IF NOT EXISTS idx_user_actions_created_at ON user_actions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_actions_type ON user_actions(action_type);

CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);

-- Update trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add update triggers
DROP TRIGGER IF EXISTS update_contents_updated_at ON contents;
CREATE TRIGGER update_contents_updated_at BEFORE UPDATE ON contents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_entities_updated_at ON entities;
CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial data
INSERT INTO entities (name, type, description) VALUES
('OpenAI', 'company', 'AI Research Company'),
('Anthropic', 'company', 'AI Safety Company'),
('GPT-4', 'model', 'OpenAI Large Language Model'),
('Claude', 'model', 'Anthropic Large Language Model'),
('Transformer', 'technology', 'Attention-based Neural Network Architecture')
ON CONFLICT (name) DO NOTHING;

-- Sample content
INSERT INTO contents (title, summary, source, category, tags, metadata) VALUES
('New Features in GPT-4', 'Detailed explanation of new features added to GPT-4', 'OpenAI Blog', 'nlp', ARRAY['gpt-4', 'openai', 'llm'], '{"author": "OpenAI Team"}'::jsonb),
('Claude 3 Release', 'Anthropic releases Claude 3', 'Anthropic Blog', 'nlp', ARRAY['claude', 'anthropic', 'llm'], '{"author": "Anthropic Team"}'::jsonb)
ON CONFLICT (original_url) DO NOTHING;

-- Popular content view
CREATE OR REPLACE VIEW popular_contents AS
SELECT
    c.id,
    c.title,
    c.category,
    c.source,
    c.view_count,
    c.like_count,
    COUNT(ua.id) as action_count
FROM contents c
LEFT JOIN user_actions ua ON c.id = ua.content_id
WHERE c.published_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY c.id
ORDER BY (c.view_count + c.like_count * 2 + COUNT(ua.id) * 3) DESC;

-- User activity summary view
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT
    u.id as user_id,
    u.email,
    COUNT(DISTINCT ua.content_id) as unique_contents_viewed,
    COUNT(CASE WHEN ua.action_type = 'like' THEN 1 END) as likes_given,
    COUNT(CASE WHEN ua.action_type = 'bookmark' THEN 1 END) as bookmarks_created,
    MAX(ua.created_at) as last_activity_at
FROM users u
LEFT JOIN user_actions ua ON u.id = ua.user_id
GROUP BY u.id, u.email;
