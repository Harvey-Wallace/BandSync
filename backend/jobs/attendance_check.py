"""
Background job scheduler for admin attendance notifications

This script should be run periodically (every 5 minutes) to check for
events that need attendance reports sent to admins.
"""

from datetime import datetime
from services.admin_attendance_service import AdminAttendanceService
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_attendance_check():
    """Run the attendance report check"""
    logger.info("Starting admin attendance report check...")
    
    try:
        AdminAttendanceService.check_and_send_attendance_reports()
        logger.info("Admin attendance report check completed successfully")
    except Exception as e:
        logger.error(f"Error in attendance report check: {str(e)}")

if __name__ == "__main__":
    run_attendance_check()
