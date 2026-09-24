-- Solmere Behavioral Transformation Pipeline
CREATE OR REPLACE VIEW clean_churn_view AS
SELECT 
    SubscriberID,
    Region,
    Plan,
    OnboardingScore,
    HasNegativeTicketPreRenewal,
    Cancelled,
    TotalSpent,
    -- Handle database null metrics for users with a clean support window
    COALESCE(DaysBeforeRenewalLastNegativeTicket, 0) AS DaysBeforeRenewalLastNegativeTicket
FROM raw_churn;
