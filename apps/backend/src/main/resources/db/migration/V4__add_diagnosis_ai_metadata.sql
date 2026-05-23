ALTER TABLE diagnoses
    ADD COLUMN profile_snapshot JSONB,
    ADD COLUMN ai_task_id VARCHAR(255),
    ADD COLUMN analysis_started_at TIMESTAMP,
    ADD COLUMN model_name VARCHAR(100),
    ADD COLUMN prompt_version VARCHAR(100),
    ADD COLUMN analysis_metadata JSONB,
    ADD COLUMN error_code VARCHAR(100),
    ADD COLUMN failed_step VARCHAR(100),
    ADD COLUMN failed_at TIMESTAMP,
    ADD COLUMN error_details JSONB;

ALTER TABLE jd_results
    ADD COLUMN match_details JSONB;
