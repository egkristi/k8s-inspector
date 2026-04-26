"""k8s-inspector 2.0 - FastAPI Main Application."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from typing import Dict, List

from .core.config import settings
from .core.database import init_db, close_db
from .api import clusters, insights, cost, security, webhooks
from .services.cluster_service import cluster_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Active WebSocket connections
active_connections: Dict[int, List[WebSocket]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🐦‍⬛ Starting k8s-inspector 2.0...")
    await init_db()
    logger.info("✅ Database initialized")
    
    # Start background tasks
    asyncio.create_task(poll_clusters())
    
    yield
    
    # Shutdown
    logger.info("Shutting down k8s-inspector...")
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="The Intelligent Kubernetes Inspector",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(clusters.router, prefix=f"{settings.API_PREFIX}/clusters", tags=["Clusters"])
app.include_router(insights.router, prefix=f"{settings.API_PREFIX}/insights", tags=["Insights"])
app.include_router(cost.router, prefix=f"{settings.API_PREFIX}/cost", tags=["Cost"])
app.include_router(security.router, prefix=f"{settings.API_PREFIX}/security", tags=["Security"])
app.include_router(webhooks.router, prefix=f"{settings.API_PREFIX}/webhooks", tags=["Webhooks"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.websocket("/ws/cluster/{cluster_id}")
async def websocket_endpoint(websocket: WebSocket, cluster_id: int):
    """WebSocket endpoint for real-time cluster updates."""
    await websocket.accept()
    
    if cluster_id not in active_connections:
        active_connections[cluster_id] = []
    active_connections[cluster_id].append(websocket)
    
    logger.info(f"WebSocket client connected for cluster {cluster_id}")
    
    try:
        while True:
            # Receive messages from client (e.g., commands)
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received from cluster {cluster_id}: {message.get('type')}")
            
            # Handle client messages
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for cluster {cluster_id}")
    finally:
        if cluster_id in active_connections:
            active_connections[cluster_id].remove(websocket)


async def broadcast_to_cluster(cluster_id: int, message: dict):
    """Broadcast message to all WebSocket clients for a cluster."""
    if cluster_id in active_connections:
        disconnected = []
        for connection in active_connections[cluster_id]:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            active_connections[cluster_id].remove(conn)


async def poll_clusters():
    """Background task to poll clusters periodically."""
    logger.info("Starting cluster polling task...")
    
    while True:
        try:
            # TODO: Load active clusters from database
            # For now, just log
            logger.debug("Polling clusters...")
            
            await asyncio.sleep(settings.CLUSTER_POLL_INTERVAL_SECONDS)
            
        except Exception as e:
            logger.error(f"Error in cluster polling: {e}")
            await asyncio.sleep(5)  # Quick retry on error


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
