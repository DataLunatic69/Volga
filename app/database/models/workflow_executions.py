'''
id (uuid, PK)
workflow_type (enum: viewing_reminder, post_viewing_followup, nurture_campaign, re_engagement)
contact_id (uuid, FK → leads)
agency_id (uuid, FK → agencies)
status (enum: pending, running, completed, failed, cancelled)
scheduled_for (timestamp)
executed_at (timestamp)
execution_context (jsonb)
result (jsonb)
error_message (text)
retry_count (integer)
created_at (timestamp)
updated_at (timestamp)


'''