"""Database models for cluster management."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Float, Text
from sqlalchemy.sql import func
from ..core.database import Base


class Cluster(Base):
    """Kubernetes cluster registration."""
    
    __tablename__ = "clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    kubeconfig_secret = Column(String(255), nullable=False)  # Reference to Kubernetes secret
    cluster_type = Column(String(50))  # kubernetes, openshift, eks, gke, aks
    api_url = Column(String(500))
    version = Column(String(50))
    
    # Status
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    health_score = Column(Float, default=100.0)  # 0-100
    
    # Metadata
    node_count = Column(Integer, default=0)
    namespace_count = Column(Integer, default=0)
    pod_count = Column(Integer, default=0)
    
    # Cost tracking
    monthly_cost_estimate = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional config
    config = Column(JSON, default=dict)
    labels = Column(JSON, default=list)


class ClusterScan(Base):
    """Historical scan results for a cluster."""
    
    __tablename__ = "cluster_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, nullable=False, index=True)
    
    # Scan metadata
    scan_type = Column(String(50))  # full, incremental, security, cost
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Results summary
    health_score = Column(Float)
    security_score = Column(Float)
    cost_estimate = Column(Float)
    issues_found = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    
    # Full results stored as JSON
    results = Column(JSON, default=dict)
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ClusterMetric(Base):
    """Time-series metrics for clusters (TimescaleDB hypertable)."""
    
    __tablename__ = "cluster_metrics"
    
    # TimescaleDB requires time as part of primary key
    time = Column(DateTime(timezone=True), primary_key=True, index=True)
    cluster_id = Column(Integer, primary_key=True, index=True)
    
    # Resource metrics
    cpu_usage_percent = Column(Float)
    memory_usage_percent = Column(Float)
    disk_usage_percent = Column(Float)
    network_rx_bytes = Column(Float)
    network_tx_bytes = Column(Float)
    
    # Pod metrics
    pod_count = Column(Integer)
    pending_pods = Column(Integer)
    failed_pods = Column(Integer)
    restarting_pods = Column(Integer)
    
    # Node metrics
    node_count = Column(Integer)
    ready_nodes = Column(Integer)
    not_ready_nodes = Column(Integer)
    
    # Cost metrics
    hourly_cost = Column(Float)
    
    # Metadata
    metric_type = Column(String(50))  # resource, pod, node, cost
    labels = Column(JSON, default=dict)
