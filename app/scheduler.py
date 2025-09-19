from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .workflows.daily_reporter import run_daily_report
from .workflows.weekly_reporter import run_weekly_report

# Create a scheduler instance
scheduler = AsyncIOScheduler()

def setup_scheduler():
    """
    Adds the reporting jobs to the scheduler.
    """
    # Schedule the daily report to run at 22:05 (10:05 PM) server time
    scheduler.add_job(
        run_daily_report,
        trigger=CronTrigger(hour=22, minute=5),
        id="daily_report_job",
        name="Daily Report",
        replace_existing=True,
    )

    # Schedule the weekly report to run on Fridays at 18:00 (6:00 PM) server time
    scheduler.add_job(
        run_weekly_report,
        trigger=CronTrigger(day_of_week="fri", hour=22, minute=10),
        id="weekly_report_job",
        name="Weekly Report",
        replace_existing=True,
    )
    
    print("Scheduler setup complete. Jobs are scheduled.")
    return scheduler