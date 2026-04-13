"""Database models for insights, alerts, and recommendations."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Float, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Insight(Base):
    """AI-generated insights from cluster analysis."""
    
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=False, index=True)
    
    # Insight classification
    category = Column(String(50), index=True)  # cost, security, performance, reliability
    severity = Column(String(20))  # critical, high, medium, low, info
    insight_type = Column(String(50))  # anomaly, prediction, optimization, compliance
    
    # Content
    title = Column(String(500), nullable=False)
    description = Column(Text)
    root_cause = Column(Text)
    
    # Evidence
    affected_resources = Column(JSON, default=list)  # [{kind, name, namespace}]
    metrics_snapshot = Column(JSON, default=dict)  # Relevant metrics at time of insight
    confidence_score = Column(Float)  # 0-1, ML confidence
    
    # Action
    recommendation = Column(Text)
    auto_fix_available = Column(Boolean, default=False)
    auto_fix_playbook = Column(String(255))  # Reference to playbook
    estimated_impact = Column(String(500))  # e.g., "Save $340/month"
    
    # Status
    status = Column(String(20), default="new")  # new, acknowledged, resolved, dismissed
    acknowledged_by = Column(String(255))
    acknowledged_at = Column(DateTime(timezone=True))
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    resolved_at = Column(DateTime(timezone=True))
    
    # Cluster relationship
    cluster = relationship("Cluster", backref="insights")


class Alert(Base):
    """Real-time alerts triggered by insights or thresholds."""
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=False)
    insight_id = Column(Integer, ForeignKey("insights.id"), nullable=True)
    
    # Alert details
    title = Column(String(500), nullable=False)
    message = Column(Text)
    severity = Column(String(20))  # critical, warning, info
    
    # State
    status = Column(String(20), default="firing")  # firing, acknowledged, resolved, silenced
    firing_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(String(255))
    resolved_at = Column(DateTime(timezone=True))
    
    # Deduplication
    fingerprint = Column(String(255), index=True)  # For deduplication
    group_label = Column(String(255))  # For grouping related alerts
    
    # Notifications
    notifications_sent = Column(Integer, default=0)
    last_notification_at = Column(DateTime(timezone=True))
    
    # Metadata
    labels = Column(JSON, default=dict)
    annotations = Column(JSON, default=dict)
    
    # Relationships
    cluster = relationship("Cluster", backref="alerts")
    insight = relationship("Insight", backref="alerts")


class Recommendation(Base):
    """Actionable recommendations with tracking."""
    
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=False)
    insight_id = Column(Integer, ForeignKey("insights.id"), nullable=True)
    
    # Recommendation details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # cost_optimization, security, performance, reliability
    
    # Impact
    estimated_savings = Column(Float)  # In USD/month
    estimated_savings_currency = Column(String(3), default="USD")
    effort_level = Column(String(20))  # low, medium, high
    risk_level = Column(String(20))  # low, medium, high
    
    # Implementation
    implementation_steps = Column(JSON, default=list)  # [{step, command, description}]
    auto_fix_available = Column(Boolean, default=False)
    auto_fix_playbook = Column(String(255))
    
    # Status
    status = Column(String(20), default="pending")  # pending, in_progress, implemented, rejected
    implemented_at = Column(DateTime(timezone=True))
    implemented_by = Column(String(255))
    
    # Tracking
    actual_savings = Column(Float)  # Tracked after implementation
    roi_days = Column(Integer)  # Days to break-even
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cluster = relationship("Cluster", backref="recommendations")
    insight = relationship("Insight", backref="recommendations")
