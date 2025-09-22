from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .workflows.daily_reporter import run_daily_report
from .workflows.weekly_reporter import run_weekly_report
from .workflows.monthly_reporter import run_monthly_report
from .workflows.yearly_reporter import run_yearly_report

# Create a scheduler instance
scheduler = AsyncIOScheduler(timezone="UTC")

def setup_scheduler():
    """
    Adds the reporting jobs to the scheduler.
    """
    # Schedule the daily report to run at 22:05 UTC (after market close)
    scheduler.add_job(
        run_daily_report,
        trigger=CronTrigger(hour=20, minute=5, timezone='UTC'),
        id="daily_report_job",
        name="Daily Report",
        replace_existing=True,
    )

    # Schedule the weekly report to run on Fridays at 22:10 UTC
    scheduler.add_job(
        run_weekly_report,
        trigger=CronTrigger(day_of_week="fri", hour=20, minute=10, timezone='UTC'),
        id="weekly_report_job",
        name="Weekly Report",
        replace_existing=True,
    )
    
    # Schedule the monthly report to run on the last Friday of the month at 22:15 UTC
    scheduler.add_job(
        run_monthly_report,
        trigger=CronTrigger(day_of_week="fri", day="last", hour=20, minute=15, timezone='UTC'),
        id="monthly_report_job",
        name="Monthly Report",
        replace_existing=True,
    )

    # Schedule the yearly report to run on the last Friday of December at 22:20 UTC
    scheduler.add_job(
        run_yearly_report,
        trigger=CronTrigger(month=12, day_of_week="fri", day="last", hour=20, minute=10, timezone='UTC'),
        id="yearly_report_job",
        name="Yearly Report",
        replace_existing=True,
    )

    print("Scheduler setup complete. Jobs are scheduled.")
    return scheduler