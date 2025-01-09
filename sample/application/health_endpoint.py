from fastapi import APIRouter

router = APIRouter()


@router.get("/health/liveness", tags=["health"])
async def liveness_check():
    """
    Liveness check to monitor if the application is running.
    Returns 200 OK if the application is alive.

    deployment.yaml :

    livenessProbe:
      httpGet:
        path: /health/liveness
        port: 80
      initialDelaySeconds: 3
      periodSeconds: 10
    """
    return {"status": "alive"}


@router.get("/health/readiness", tags=["health"])
async def readiness_check():
    """
    Readiness check to monitor if the application is ready to serve traffic.
    Add checks for database connections, external services, etc., here.
    Returns 200 OK if the application is ready.

    deployment.yaml :

    readinessProbe:
        httpGet:
            path: /readiness
            port: 80
        initialDelaySeconds: 5
        periodSeconds: 5
    """
    # # Example: Add logic to verify database connection or other dependencies
    # db_connected = True  # Replace with actual check
    # if not db_connected:
    #     return {"status": "not ready"}, 503

    return {"status": "up"}
