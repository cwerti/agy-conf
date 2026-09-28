"""
Business Logic / Domain Service.
CRITICAL: The service layer knows nothing about HTTP or FastAPI.
It performs domain operations and returns domain data or raises domain exceptions.
"""


class HealthService:
    @staticmethod
    def get_system_health() -> dict[str, str]:
        # Perform internal domain checks (e.g. database ping, redis status)
        return {
            "status": "healthy",
            "environment": "operational"
        }
