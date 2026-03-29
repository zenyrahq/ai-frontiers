-- AI Frontiers データベース初期化スクリプト

-- pgvector拡張をインストール（ベクトル検索用）
CREATE EXTENSION IF NOT EXISTS vector;

-- コンテンツテーブル
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
    embedding vector(384),  -- Sentence Transformersの出力次元数
    metadata JSONB,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    is_processed BOOLEAN DEFAULT FALSE
);

-- ユーザーテーブル
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

-- ユーザー行動テーブル（推薦システム用）
CREATE TABLE IF NOT EXISTS user_actions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER REFERENCES contents(id) ON DELETE CASCADE,
    action_type VARCHAR(20) NOT NULL,  -- view, like, bookmark, share
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- API キーテーブル
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20),  -- 表示用プレフィックス
    rate_limit INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- エンティティテーブル（知識グラフ用）
CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,  -- model, company, person, technology
    description TEXT,
    aliases TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- エンティティ関係テーブル（知識グラフ用）
CREATE TABLE IF NOT EXISTS entity_relations (
    id SERIAL PRIMARY KEY,
    source_entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
    target_entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
    relation_type VARCHAR(100) NOT NULL,  -- developed_by, uses, cites, etc.
    weight FLOAT DEFAULT 1.0,
    evidence TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_entity_id, target_entity_id, relation_type)
);

-- コンテンツ-エンティティ関連テーブル
CREATE TABLE IF NOT EXISTS content_entities (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES contents(id) ON DELETE CASCADE,
    entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
    relevance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(content_id, entity_id)
);

-- インデックス作成

-- コンテンツテーブルのインデックス
CREATE INDEX idx_contents_category ON contents(category);
CREATE INDEX idx_contents_source ON contents(source);
CREATE INDEX idx_contents_published_at ON contents(published_at DESC);
CREATE INDEX idx_contents_created_at ON contents(created_at DESC);
CREATE INDEX idx_contents_tags ON contents USING GIN(tags);
CREATE INDEX idx_contents_metadata ON contents USING GIN(metadata);
CREATE INDEX idx_contents_embedding ON contents USING ivfflat (embedding vector_cosine_ops);

-- ユーザー行動テーブルのインデックス
CREATE INDEX idx_user_actions_user_id ON user_actions(user_id);
CREATE INDEX idx_user_actions_content_id ON user_actions(content_id);
CREATE INDEX idx_user_actions_created_at ON user_actions(created_at DESC);
CREATE INDEX idx_user_actions_type ON user_actions(action_type);

-- エンティティテーブルのインデックス
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_entities_name ON entities(name);

-- エンティティ関係テーブルのインデックス
CREATE INDEX idx_entity_relations_source ON entity_relations(source_entity_id);
CREATE INDEX idx_entity_relations_target ON entity_relations(target_entity_id);
CREATE INDEX idx_entity_relations_type ON entity_relations(relation_type);

-- 更新トリガー関数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 各テーブルに更新トリガーを設定
CREATE TRIGGER update_contents_updated_at BEFORE UPDATE ON contents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 初期データ投入

-- カテゴリの例（参考用）
INSERT INTO entities (name, type, description) VALUES
('OpenAI', 'company', 'AI研究企業'),
('Anthropic', 'company', 'AI安全性企業'),
('GPT-4', 'model', 'OpenAIの大規模言語モデル'),
('Claude', 'model', 'Anthropicの大規模言語モデル'),
('Transformer', 'technology', '注意機構ベースのニューラルネットワークアーキテクチャ')
ON CONFLICT (name) DO NOTHING;

-- サンプルコンテンツ（テスト用）
INSERT INTO contents (title, summary, source, category, tags, metadata) VALUES
('GPT-4の新機能について', 'GPT-4に追加された新機能の詳細解説', 'OpenAI Blog', 'nlp', ARRAY['gpt-4', 'openai', 'llm'], '{"author": "OpenAI Team"}'::jsonb),
('Claude 3リリース', 'AnthropicがClaude 3をリリース', 'Anthropic Blog', 'nlp', ARRAY['claude', 'anthropic', 'llm'], '{"author": "Anthropic Team"}'::jsonb)
ON CONFLICT (original_url) DO NOTHING;

-- ビュー作成（分析用）

-- 人気コンテンツビュー
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

-- ユーザー活動サマリービュー
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

-- 完了メッセージ
DO $$
BEGIN
    RAISE NOTICE 'データベースの初期化が完了しました';
END $$;
