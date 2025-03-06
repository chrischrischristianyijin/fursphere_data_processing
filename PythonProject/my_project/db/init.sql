CREATE TABLE survey_data (
    submission_id SERIAL PRIMARY KEY,  -- Unique ID per submission
    email TEXT NOT NULL,               -- Email stored separately
    ip TEXT NOT NULL,                   -- IP stored separately
    input_data JSONB NOT NULL,         -- Stores full JSON from frontend
    ai_output JSONB,                   -- AI response stored separately
    created_at TIMESTAMP DEFAULT NOW() -- Timestamp
);

