"""
Data models for requirements analysis
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import uuid
from datetime import datetime

class RequirementType(Enum):
    """Types of requirements"""
    FUNCTIONAL = "functional"        # What the system should do
    UI_COMPONENT = "ui_component"   # Specific UI components needed
    LAYOUT = "layout"               # Layout and positioning
    STYLING = "styling"             # Visual styling and theming
    INTERACTION = "interaction"     # User interactions and behaviors
    DATA = "data"                   # Data requirements
    PERFORMANCE = "performance"     # Performance requirements
    ACCESSIBILITY = "accessibility" # Accessibility requirements
    BUSINESS = "business"           # Business logic requirements

class RequirementPriority(Enum):
    """Priority levels for requirements"""
    CRITICAL = "critical"    # Must have - core functionality
    HIGH = "high"           # Should have - important features
    MEDIUM = "medium"       # Could have - nice to have
    LOW = "low"            # Won't have this time - future consideration

class RequirementStatus(Enum):
    """Status of requirement analysis"""
    IDENTIFIED = "identified"       # Requirement identified
    ANALYZED = "analyzed"          # Requirement analyzed and structured
    VALIDATED = "validated"        # Requirement validated for completeness
    READY = "ready"               # Ready for implementation
    INCOMPLETE = "incomplete"      # Missing information
    AMBIGUOUS = "ambiguous"       # Needs clarification

@dataclass
class ComponentSpec:
    """Specification for a UI component"""
    name: str
    type: str  # button, input, form, card, modal, etc.
    properties: Dict[str, Any] = field(default_factory=dict)
    children: List['ComponentSpec'] = field(default_factory=list)
    events: List[str] = field(default_factory=list)  # click, hover, submit, etc.
    validation: Optional[Dict[str, Any]] = None
    accessibility: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.type,
            'properties': self.properties,
            'children': [child.to_dict() for child in self.children],
            'events': self.events,
            'validation': self.validation,
            'accessibility': self.accessibility
        }

@dataclass
class LayoutSpec:
    """Specification for layout structure"""
    type: str  # grid, flex, absolute, flow, etc.
    sections: List[Dict[str, Any]] = field(default_factory=list)
    responsive: bool = True
    breakpoints: Optional[Dict[str, int]] = None
    spacing: Optional[Dict[str, Union[int, str]]] = None
    alignment: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'sections': self.sections,
            'responsive': self.responsive,
            'breakpoints': self.breakpoints,
            'spacing': self.spacing,
            'alignment': self.alignment
        }

@dataclass
class StyleSpec:
    """Specification for styling requirements"""
    theme: Optional[str] = None
    colors: Dict[str, str] = field(default_factory=dict)
    typography: Dict[str, Any] = field(default_factory=dict)
    spacing: Dict[str, Union[int, str]] = field(default_factory=dict)
    borders: Dict[str, Any] = field(default_factory=dict)
    shadows: Dict[str, str] = field(default_factory=dict)
    animations: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'theme': self.theme,
            'colors': self.colors,
            'typography': self.typography,
            'spacing': self.spacing,
            'borders': self.borders,
            'shadows': self.shadows,
            'animations': self.animations
        }

@dataclass
class InteractionSpec:
    """Specification for user interactions"""
    trigger: str  # click, hover, scroll, keyboard, etc.
    action: str   # navigate, submit, validate, show, hide, etc.
    target: str   # component or page affected
    conditions: List[str] = field(default_factory=list)
    feedback: Optional[str] = None  # visual/audio feedback
    validation: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trigger': self.trigger,
            'action': self.action,
            'target': self.target,
            'conditions': self.conditions,
            'feedback': self.feedback,
            'validation': self.validation
        }

@dataclass
class Requirement:
    """A single requirement with detailed specifications"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    type: RequirementType = RequirementType.FUNCTIONAL
    priority: RequirementPriority = RequirementPriority.MEDIUM
    status: RequirementStatus = RequirementStatus.IDENTIFIED
    
    # Detailed specifications
    component_spec: Optional[ComponentSpec] = None
    layout_spec: Optional[LayoutSpec] = None
    style_spec: Optional[StyleSpec] = None
    interaction_specs: List[InteractionSpec] = field(default_factory=list)
    
    # Relationships
    dependencies: List[str] = field(default_factory=list)  # IDs of dependent requirements
    conflicts: List[str] = field(default_factory=list)     # IDs of conflicting requirements
    
    # Metadata
    source: str = ""  # Where this requirement came from
    rationale: str = ""  # Why this requirement exists
    acceptance_criteria: List[str] = field(default_factory=list)
    estimated_effort: Optional[str] = None  # XS, S, M, L, XL
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert requirement to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type.value,
            'priority': self.priority.value,
            'status': self.status.value,
            'component_spec': self.component_spec.to_dict() if self.component_spec else None,
            'layout_spec': self.layout_spec.to_dict() if self.layout_spec else None,
            'style_spec': self.style_spec.to_dict() if self.style_spec else None,
            'interaction_specs': [spec.to_dict() for spec in self.interaction_specs],
            'dependencies': self.dependencies,
            'conflicts': self.conflicts,
            'source': self.source,
            'rationale': self.rationale,
            'acceptance_criteria': self.acceptance_criteria,
            'estimated_effort': self.estimated_effort,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class AnalysisResult:
    """Result of requirements analysis"""
    requirements: List[Requirement] = field(default_factory=list)
    project_overview: str = ""
    target_audience: str = ""
    platform: str = ""  # web, mobile, desktop
    framework_recommendations: List[str] = field(default_factory=list)
    
    # Analysis metadata
    completeness_score: float = 0.0  # 0.0 to 1.0
    clarity_score: float = 0.0       # 0.0 to 1.0
    feasibility_score: float = 0.0   # 0.0 to 1.0
    
    gaps: List[str] = field(default_factory=list)           # Missing information
    ambiguities: List[str] = field(default_factory=list)    # Unclear requirements
    recommendations: List[str] = field(default_factory=list) # Improvement suggestions
    
    # Development estimates
    total_estimated_effort: Optional[str] = None
    development_phases: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis result to dictionary"""
        return {
            'requirements': [req.to_dict() for req in self.requirements],
            'project_overview': self.project_overview,
            'target_audience': self.target_audience,
            'platform': self.platform,
            'framework_recommendations': self.framework_recommendations,
            'completeness_score': self.completeness_score,
            'clarity_score': self.clarity_score,
            'feasibility_score': self.feasibility_score,
            'gaps': self.gaps,
            'ambiguities': self.ambiguities,
            'recommendations': self.recommendations,
            'total_estimated_effort': self.total_estimated_effort,
            'development_phases': self.development_phases
        }
    
    def get_requirements_by_type(self, req_type: RequirementType) -> List[Requirement]:
        """Get all requirements of a specific type"""
        return [req for req in self.requirements if req.type == req_type]
    
    def get_requirements_by_priority(self, priority: RequirementPriority) -> List[Requirement]:
        """Get all requirements of a specific priority"""
        return [req for req in self.requirements if req.priority == priority]
    
    def get_critical_requirements(self) -> List[Requirement]:
        """Get all critical requirements"""
        return self.get_requirements_by_priority(RequirementPriority.CRITICAL)
    
    def get_incomplete_requirements(self) -> List[Requirement]:
        """Get requirements that need more information"""
        return [req for req in self.requirements 
                if req.status in [RequirementStatus.INCOMPLETE, RequirementStatus.AMBIGUOUS]]