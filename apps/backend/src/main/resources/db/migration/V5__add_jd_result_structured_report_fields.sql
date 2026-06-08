ALTER TABLE jd_results
    ADD COLUMN strengths JSONB,
    ADD COLUMN related_experiences JSONB,
    ADD COLUMN gaps JSONB,
    ADD COLUMN resume_highlights JSONB,
    ADD COLUMN strategy_advice JSONB;
