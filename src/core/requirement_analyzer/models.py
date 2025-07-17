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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentSpec':
        """Create ComponentSpec from dictionary"""
        children = []
        for child_data in data.get('children', []):
            if isinstance(child_data, dict):
                children.append(cls.from_dict(child_data))
            elif hasattr(child_data, 'to_dict'):
                children.append(child_data)
        
        return cls(
            name=data.get('name', ''),
            type=data.get('type', ''),
            properties=data.get('properties', {}),
            children=children,
            events=data.get('events', []),
            validation=data.get('validation'),
            accessibility=data.get('accessibility')
        )

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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LayoutSpec':
        """Create LayoutSpec from dictionary"""
        return cls(
            type=data.get('type', ''),
            sections=data.get('sections', []),
            responsive=data.get('responsive', True),
            breakpoints=data.get('breakpoints'),
            spacing=data.get('spacing'),
            alignment=data.get('alignment')
        )

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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StyleSpec':
        """Create StyleSpec from dictionary"""
        return cls(
            theme=data.get('theme'),
            colors=data.get('colors', {}),
            typography=data.get('typography', {}),
            spacing=data.get('spacing', {}),
            borders=data.get('borders', {}),
            shadows=data.get('shadows', {}),
            animations=data.get('animations', [])
        )

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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractionSpec':
        """Create InteractionSpec from dictionary"""
        return cls(
            trigger=data.get('trigger', ''),
            action=data.get('action', ''),
            target=data.get('target', ''),
            conditions=data.get('conditions', []),
            feedback=data.get('feedback'),
            validation=data.get('validation')
        )

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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Requirement':
        """Create Requirement from dictionary"""
        # Convert enum strings back to enum values
        req_type = RequirementType(data.get('type', 'functional'))
        priority = RequirementPriority(data.get('priority', 'medium'))
        status = RequirementStatus(data.get('status', 'identified'))
        
        # Convert nested specs
        component_spec = None
        if data.get('component_spec'):
            component_spec = ComponentSpec.from_dict(data['component_spec'])
        
        layout_spec = None
        if data.get('layout_spec'):
            layout_spec = LayoutSpec.from_dict(data['layout_spec'])
        
        style_spec = None
        if data.get('style_spec'):
            style_spec = StyleSpec.from_dict(data['style_spec'])
        
        interaction_specs = []
        for spec_data in data.get('interaction_specs', []):
            if isinstance(spec_data, dict):
                interaction_specs.append(InteractionSpec.from_dict(spec_data))
            elif hasattr(spec_data, 'to_dict'):
                interaction_specs.append(spec_data)
        
        # Convert timestamps
        created_at = datetime.now()
        updated_at = datetime.now()
        try:
            if data.get('created_at'):
                created_at = datetime.fromisoformat(data['created_at'])
            if data.get('updated_at'):
                updated_at = datetime.fromisoformat(data['updated_at'])
        except (ValueError, TypeError):
            pass  # Use default datetime if parsing fails
        
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            title=data.get('title', ''),
            description=data.get('description', ''),
            type=req_type,
            priority=priority,
            status=status,
            component_spec=component_spec,
            layout_spec=layout_spec,
            style_spec=style_spec,
            interaction_specs=interaction_specs,
            dependencies=data.get('dependencies', []),
            conflicts=data.get('conflicts', []),
            source=data.get('source', ''),
            rationale=data.get('rationale', ''),
            acceptance_criteria=data.get('acceptance_criteria', []),
            estimated_effort=data.get('estimated_effort'),
            tags=data.get('tags', []),
            created_at=created_at,
            updated_at=updated_at
        )

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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """Create AnalysisResult from dictionary"""
        # Convert requirement dicts back to Requirement objects
        requirements = []
        for req_data in data.get('requirements', []):
            if isinstance(req_data, dict):
                requirements.append(Requirement.from_dict(req_data))
            elif hasattr(req_data, 'to_dict'):  # Already a Requirement object
                requirements.append(req_data)
        
        return cls(
            requirements=requirements,
            project_overview=data.get('project_overview', ''),
            target_audience=data.get('target_audience', ''),
            platform=data.get('platform', ''),
            framework_recommendations=data.get('framework_recommendations', []),
            completeness_score=data.get('completeness_score', 0.0),
            clarity_score=data.get('clarity_score', 0.0),
            feasibility_score=data.get('feasibility_score', 0.0),
            gaps=data.get('gaps', []),
            ambiguities=data.get('ambiguities', []),
            recommendations=data.get('recommendations', []),
            total_estimated_effort=data.get('total_estimated_effort'),
            development_phases=data.get('development_phases', [])
        )
    
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