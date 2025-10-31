-- Email AI Agent - Supabase Database Schema
-- This schema stores email categories, communication patterns, and response rules

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- EMAIL CATEGORIES TABLE
-- ============================================================================
-- Stores hierarchical categories (e.g., Work > Project A, Hockey > Team A)
CREATE TABLE IF NOT EXISTS email_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    parent_id UUID REFERENCES email_categories(id) ON DELETE CASCADE,
    description TEXT,
    email_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster hierarchy queries
CREATE INDEX IF NOT EXISTS idx_categories_parent ON email_categories(parent_id);

-- ============================================================================
-- COMMUNICATION PATTERNS TABLE
-- ============================================================================
-- Stores analyzed communication patterns for each category
CREATE TABLE IF NOT EXISTS communication_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES email_categories(id) ON DELETE CASCADE,
    avg_length INT,
    tone TEXT,  -- e.g., "formal", "casual", "friendly"
    formality TEXT,  -- e.g., "high", "medium", "low"
    common_phrases JSONB,  -- Array of frequently used phrases
    avg_response_time TEXT,  -- e.g., "within 24 hours", "same day"
    typical_greeting TEXT,
    typical_closing TEXT,
    analyzed_email_count INT DEFAULT 0,
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster category lookups
CREATE INDEX IF NOT EXISTS idx_patterns_category ON communication_patterns(category_id);

-- ============================================================================
-- RESPONSE RULES TABLE
-- ============================================================================
-- Stores rules for generating draft responses for each category
CREATE TABLE IF NOT EXISTS response_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES email_categories(id) ON DELETE CASCADE,
    tone_template TEXT NOT NULL,  -- Instructions for tone
    style_guide TEXT NOT NULL,  -- Instructions for style
    length_target TEXT,  -- e.g., "brief (2-3 sentences)", "detailed (1-2 paragraphs)"
    example_phrases JSONB,  -- Array of example phrases to use
    do_use JSONB,  -- Array of things to include
    do_not_use JSONB,  -- Array of things to avoid
    context_instructions TEXT,  -- Special instructions for this category
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(category_id)  -- One rule set per category
);

-- Index for faster category lookups
CREATE INDEX IF NOT EXISTS idx_rules_category ON response_rules(category_id);

-- ============================================================================
-- EMAIL CLASSIFICATIONS TABLE
-- ============================================================================
-- Stores which category each email belongs to
CREATE TABLE IF NOT EXISTS email_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id TEXT UNIQUE NOT NULL,  -- Gmail message ID
    gmail_thread_id TEXT,  -- Gmail thread ID
    subject TEXT,
    sender TEXT,
    category_id UUID REFERENCES email_categories(id) ON DELETE SET NULL,
    confidence FLOAT,  -- Classification confidence (0.0 to 1.0)
    email_date TIMESTAMPTZ,
    classified_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_classifications_email ON email_classifications(email_id);
CREATE INDEX IF NOT EXISTS idx_classifications_category ON email_classifications(category_id);
CREATE INDEX IF NOT EXISTS idx_classifications_date ON email_classifications(email_date);

-- ============================================================================
-- GENERATED DRAFTS TABLE
-- ============================================================================
-- Stores generated draft responses for tracking/auditing
CREATE TABLE IF NOT EXISTS generated_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id TEXT REFERENCES email_classifications(email_id) ON DELETE CASCADE,
    category_id UUID REFERENCES email_categories(id) ON DELETE SET NULL,
    draft_content TEXT NOT NULL,
    draft_subject TEXT,
    applied_rules JSONB,  -- Which rules were used
    langsmith_run_id TEXT,  -- For tracing in LangSmith
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_drafts_email ON generated_drafts(email_id);
CREATE INDEX IF NOT EXISTS idx_drafts_langsmith ON generated_drafts(langsmith_run_id);

-- ============================================================================
-- INBOX SCAN METADATA TABLE
-- ============================================================================
-- Stores metadata about inbox scans (when last scanned, etc.)
CREATE TABLE IF NOT EXISTS inbox_scan_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_type TEXT NOT NULL,  -- "full" or "incremental"
    emails_scanned INT NOT NULL,
    categories_identified INT,
    scan_started_at TIMESTAMPTZ NOT NULL,
    scan_completed_at TIMESTAMPTZ,
    status TEXT NOT NULL,  -- "in_progress", "completed", "failed"
    error_message TEXT,
    langsmith_run_id TEXT
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_scan_metadata_status ON inbox_scan_metadata(status);
CREATE INDEX IF NOT EXISTS idx_scan_metadata_completed ON inbox_scan_metadata(scan_completed_at);

-- ============================================================================
-- VIEWS FOR EASY QUERYING
-- ============================================================================

-- View: Category hierarchy with email counts
CREATE OR REPLACE VIEW category_hierarchy AS
WITH RECURSIVE category_tree AS (
    -- Base case: root categories
    SELECT
        id,
        name,
        parent_id,
        description,
        email_count,
        name as full_path,
        0 as depth
    FROM email_categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive case: child categories
    SELECT
        c.id,
        c.name,
        c.parent_id,
        c.description,
        c.email_count,
        ct.full_path || ' > ' || c.name as full_path,
        ct.depth + 1 as depth
    FROM email_categories c
    INNER JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree
ORDER BY full_path;

-- View: Categories with patterns and rules
CREATE OR REPLACE VIEW categories_with_details AS
SELECT
    c.id,
    c.name,
    c.parent_id,
    c.description,
    c.email_count,
    p.tone,
    p.formality,
    p.avg_length,
    r.tone_template,
    r.style_guide,
    r.length_target
FROM email_categories c
LEFT JOIN communication_patterns p ON c.id = p.category_id
LEFT JOIN response_rules r ON c.id = r.category_id;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Update email count for a category
CREATE OR REPLACE FUNCTION update_category_email_count(cat_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE email_categories
    SET email_count = (
        SELECT COUNT(*)
        FROM email_classifications
        WHERE category_id = cat_id
    ),
    updated_at = NOW()
    WHERE id = cat_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Get category path (for breadcrumbs)
CREATE OR REPLACE FUNCTION get_category_path(cat_id UUID)
RETURNS TEXT AS $$
DECLARE
    path TEXT;
BEGIN
    SELECT full_path INTO path
    FROM category_hierarchy
    WHERE id = cat_id;

    RETURN path;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Uncomment to insert sample categories
-- INSERT INTO email_categories (name, description) VALUES
--     ('Work', 'Work-related emails'),
--     ('Personal', 'Personal emails'),
--     ('Hockey', 'Hockey team communications'),
--     ('Organizational', 'Organizational changes and announcements');
