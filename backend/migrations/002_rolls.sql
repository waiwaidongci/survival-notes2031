-- Roll cluster bootstrap upgrade: source roll per specimen, fixed seed per run.
-- Existing rows keep NULL roll_no; studies on cohorts with missing roll numbers are rejected until data is completed.
ALTER TABLE specimens ADD COLUMN roll_no VARCHAR(40) NULL;
CREATE INDEX specimen_roll_idx ON specimens (cohort_id, roll_no);
ALTER TABLE survival_runs ADD COLUMN seed INT NOT NULL DEFAULT 20261113;
