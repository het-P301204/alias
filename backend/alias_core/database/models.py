"""SQLite column definitions — used by init_db and queries."""

EXPERIMENTS_DDL = """
CREATE TABLE IF NOT EXISTS experiments (
    id                      TEXT PRIMARY KEY,
    scenario_id             TEXT NOT NULL,
    mode                    TEXT NOT NULL,
    config_json             TEXT NOT NULL,
    status                  TEXT NOT NULL DEFAULT 'ready',
    started_at              TEXT,
    completed_at            TEXT,
    duration_ms             INTEGER,
    input_summary           TEXT,
    expected_outcome        TEXT,
    actual_outcome          TEXT,
    evidence_json           TEXT,
    defensive_control_json  TEXT,
    error_detail            TEXT,
    reproducibility_json    TEXT,
    is_sample               INTEGER DEFAULT 0
)
"""

SCENARIO_CONFIGS_DDL = """
CREATE TABLE IF NOT EXISTS scenario_configs (
    scenario_id  TEXT PRIMARY KEY,
    config_json  TEXT NOT NULL
)
"""

SETTINGS_DDL = """
CREATE TABLE IF NOT EXISTS settings (
    key    TEXT PRIMARY KEY,
    value  TEXT NOT NULL
)
"""
