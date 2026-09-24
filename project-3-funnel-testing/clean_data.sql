-- Tallywell A/B Test Variant Metrics Calculation
CREATE OR REPLACE VIEW funnel_experiment_view AS
SELECT 
    UserID,
    AssignedVariant,
    StepReached,
    DurationMin,
    DeviceType,
    CompletedSignup
FROM raw_funnel;
