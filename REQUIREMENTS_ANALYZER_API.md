# Requirements Analyzer API Documentation

## Overview

The Requirements Analyzer module provides comprehensive analysis of user requirements, extracting and structuring them into actionable specifications for frontend development. It ensures no ambiguity exists and provides complete, frontend-ready requirements.

## Core Classes

### RequirementAnalyzer

Main analysis engine that processes user requirements text and returns structured analysis.

```python
from src.core.requirement_analyzer import RequirementAnalyzer

analyzer = RequirementAnalyzer(config={
    'model_config': 'default'  # Model configuration name
})

# Process requirements
result = analyzer.process({
    'text': 'User requirements text in Chinese or English',
    'context': 'Additional context (optional)',
    'platform': 'web|mobile|desktop',
    'existing_analysis': previous_analysis  # For refinement (optional)
})
```

### Input Format

```python
input_data = {
    'text': str,        # Required: User requirements text
    'context': str,     # Optional: Additional context
    'platform': str,    # Required: Target platform (web, mobile, desktop)
    'existing_analysis': AnalysisResult  # Optional: Previous analysis to refine
}
```

### Output: AnalysisResult

```python
class AnalysisResult:
    requirements: List[Requirement]           # Structured requirements list
    project_overview: str                     # Project description
    target_audience: str                      # Target user audience
    platform: str                            # Target platform
    framework_recommendations: List[str]      # Recommended frameworks
    
    # Quality metrics (0.0 to 1.0)
    completeness_score: float               # How complete requirements are
    clarity_score: float                    # How clear requirements are
    feasibility_score: float                # How feasible requirements are
    
    # Analysis feedback
    gaps: List[str]                         # Missing information
    ambiguities: List[str]                  # Unclear requirements
    recommendations: List[str]              # Improvement suggestions
    
    # Development planning
    total_estimated_effort: str             # XS, S, M, L, XL
    development_phases: List[Dict]          # Phased development plan
```

## Requirement Structure

### Core Requirement

```python
class Requirement:
    id: str                                 # Unique identifier
    title: str                             # Brief requirement title
    description: str                       # Detailed description
    type: RequirementType                  # Requirement category
    priority: RequirementPriority          # Priority level
    status: RequirementStatus              # Analysis status
    
    # Detailed specifications
    component_spec: ComponentSpec          # UI component details
    layout_spec: LayoutSpec               # Layout specifications
    style_spec: StyleSpec                 # Styling requirements
    interaction_specs: List[InteractionSpec]  # Interaction behaviors
    
    # Relationships
    dependencies: List[str]                # Dependent requirement IDs
    conflicts: List[str]                   # Conflicting requirement IDs
    
    # Implementation details
    acceptance_criteria: List[str]         # Definition of done
    estimated_effort: str                  # XS, S, M, L, XL
    tags: List[str]                       # Classification tags
    
    # Metadata
    source: str                           # Original source text
    rationale: str                        # Why this requirement exists
    created_at: datetime
    updated_at: datetime
```

### Requirement Types

```python
class RequirementType(Enum):
    FUNCTIONAL = "functional"              # What the system should do
    UI_COMPONENT = "ui_component"         # Specific UI components
    LAYOUT = "layout"                     # Layout and positioning
    STYLING = "styling"                   # Visual styling
    INTERACTION = "interaction"           # User interactions
    DATA = "data"                         # Data requirements
    PERFORMANCE = "performance"           # Performance requirements
    ACCESSIBILITY = "accessibility"       # Accessibility features
    BUSINESS = "business"                 # Business logic
```

### Priority Levels

```python
class RequirementPriority(Enum):
    CRITICAL = "critical"    # Must have - core functionality
    HIGH = "high"           # Should have - important features
    MEDIUM = "medium"       # Could have - nice to have
    LOW = "low"            # Won't have this time
```

## Component Specifications

### ComponentSpec

Frontend-ready component specifications with all necessary details:

```python
class ComponentSpec:
    name: str              # Component name (e.g., "LoginButton")
    type: str              # Component type (button, input, form, card, modal, etc.)
    properties: Dict       # Component properties
    children: List         # Child components
    events: List[str]      # Supported events (click, hover, submit, etc.)
    validation: Dict       # Validation rules
    accessibility: Dict    # Accessibility attributes
```

#### Example Component Spec

```json
{
    "name": "TaskCard",
    "type": "card",
    "properties": {
        "title": "string",
        "status": "pending|in_progress|completed",
        "priority": "low|medium|high|critical",
        "due_date": "date",
        "description": "string",
        "assignee": "user_object"
    },
    "children": [
        {
            "name": "TaskActions",
            "type": "button_group",
            "properties": {
                "actions": ["edit", "delete", "complete"]
            }
        }
    ],
    "events": ["click", "hover", "drag_start", "drag_end"],
    "validation": {
        "rules": ["required:title", "date:due_date"],
        "messages": {
            "required": "标题不能为空",
            "date": "请输入有效日期"
        }
    },
    "accessibility": {
        "aria-label": "任务卡片",
        "role": "button",
        "keyboard_navigation": true,
        "screen_reader_text": "任务: {title}, 状态: {status}"
    }
}
```

## Layout Specifications

### LayoutSpec

Complete layout structure with responsive design details:

```python
class LayoutSpec:
    type: str                    # grid, flex, absolute, flow
    sections: List[Dict]         # Layout sections
    responsive: bool             # Responsive design enabled
    breakpoints: Dict[str, int]  # Responsive breakpoints
    spacing: Dict               # Spacing configuration
    alignment: Dict             # Alignment settings
```

#### Example Layout Spec

```json
{
    "type": "grid",
    "sections": [
        {
            "name": "sidebar",
            "position": "left",
            "size": "250px",
            "components": ["navigation", "user_profile"],
            "responsive_behavior": {
                "mobile": "hidden",
                "tablet": "collapsible"
            }
        },
        {
            "name": "header",
            "position": "top",
            "size": "60px",
            "components": ["breadcrumbs", "search", "notifications"]
        },
        {
            "name": "main_content",
            "position": "center",
            "size": "1fr",
            "components": ["task_list", "task_filters"]
        }
    ],
    "responsive": true,
    "breakpoints": {
        "mobile": 768,
        "tablet": 1024,
        "desktop": 1200
    },
    "spacing": {
        "padding": "16px",
        "margin": "8px",
        "gap": "12px"
    },
    "alignment": {
        "horizontal": "space-between",
        "vertical": "flex-start"
    }
}
```

## Interaction Specifications

### InteractionSpec

Detailed user interaction behaviors:

```python
class InteractionSpec:
    trigger: str              # click, hover, scroll, keyboard, etc.
    action: str               # navigate, submit, validate, show, hide, etc.
    target: str               # Affected component or page
    conditions: List[str]     # Pre-conditions
    feedback: str             # User feedback (visual/audio)
    validation: Dict          # Validation requirements
```

#### Example Interaction Specs

```json
[
    {
        "trigger": "click",
        "action": "navigate",
        "target": "task_detail_page",
        "conditions": ["user_authenticated", "task_exists"],
        "feedback": "页面过渡动画，加载指示器",
        "validation": {
            "check_permissions": true,
            "validate_task_id": true
        }
    },
    {
        "trigger": "drag",
        "action": "reorder",
        "target": "task_list",
        "conditions": ["user_has_edit_permission"],
        "feedback": "拖拽预览，放置区域高亮",
        "validation": {
            "validate_drop_zone": true,
            "check_task_status": true
        }
    },
    {
        "trigger": "form_submit",
        "action": "create_task",
        "target": "task_form",
        "conditions": ["form_valid"],
        "feedback": "成功消息，返回任务列表",
        "validation": {
            "required_fields": ["title", "due_date"],
            "field_validation": {
                "title": "min_length:3,max_length:100",
                "due_date": "future_date"
            }
        }
    }
]
```

## Validation System

### RequirementValidator

Comprehensive validation with quality scoring:

```python
from src.core.requirement_analyzer.validator import RequirementValidator

validator = RequirementValidator()
validation_result = validator.validate_analysis_result(analysis_result)
```

### Validation Result

```python
validation_result = {
    'overall_score': 0.85,                    # Overall quality score (0.0-1.0)
    'category_scores': {
        'requirements_quality': 0.90,         # Individual requirement quality
        'project_structure': 0.80,            # Project organization
        'completeness': 0.85                  # Coverage completeness
    },
    'issues': [                               # Critical issues to fix
        "Requirement 'User Login': Missing acceptance criteria",
        "Component spec missing for UI requirement"
    ],
    'warnings': [                             # Quality warnings
        "Some requirements lack detailed descriptions",
        "Consider adding more specific acceptance criteria"
    ],
    'recommendations': [                      # Improvement suggestions
        "Add accessibility requirements for better user experience",
        "Consider breaking down complex requirements into smaller ones"
    ]
}
```

## Usage Examples

### Complete Analysis Workflow

```python
from src.core.requirement_analyzer import RequirementAnalyzer
from src.core.requirement_analyzer.validator import RequirementValidator

# Initialize
analyzer = RequirementAnalyzer()
validator = RequirementValidator()

# Process requirements
requirements_text = """
我需要一个任务管理系统，包含以下功能：
1. 用户登录和注册
2. 创建和编辑任务
3. 任务列表显示
4. 任务状态管理
5. 响应式设计
"""

result = analyzer.process({
    'text': requirements_text,
    'context': '面向团队协作的任务管理工具',
    'platform': 'web'
})

# Validate results
validation = validator.validate_analysis_result(result)

# Access structured data
for requirement in result.requirements:
    print(f"需求: {requirement.title}")
    print(f"类型: {requirement.type.value}")
    print(f"优先级: {requirement.priority.value}")
    
    if requirement.component_spec:
        print(f"组件: {requirement.component_spec.name}")
        print(f"属性: {requirement.component_spec.properties}")
    
    if requirement.interaction_specs:
        for interaction in requirement.interaction_specs:
            print(f"交互: {interaction.trigger} -> {interaction.action}")

# Get framework recommendations
print("推荐框架:", result.framework_recommendations)

# Check development phases
for phase in result.development_phases:
    print(f"阶段: {phase['name']} - {phase['estimated_duration']}")
```

### Filtering Requirements

```python
# Get requirements by type
ui_components = result.get_requirements_by_type(RequirementType.UI_COMPONENT)
functional_reqs = result.get_requirements_by_type(RequirementType.FUNCTIONAL)

# Get by priority
critical_reqs = result.get_critical_requirements()
high_priority = result.get_requirements_by_priority(RequirementPriority.HIGH)

# Get incomplete requirements
incomplete = result.get_incomplete_requirements()
```

### JSON Serialization

```python
# Convert to JSON for frontend consumption
analysis_json = result.to_dict()

# Individual requirement to JSON
requirement_json = requirement.to_dict()

# Component spec to JSON
component_json = component_spec.to_dict()
```

## Quality Assurance

The Requirements Analyzer ensures:

1. **No Ambiguity**: All requirements are validated for clarity
2. **Complete Coverage**: Identifies missing requirements and gaps
3. **Implementation Ready**: Provides detailed specifications for development
4. **Quality Scoring**: Quantifies requirement quality with actionable feedback
5. **Structured Output**: Frontend-consumable JSON format

## Integration Notes

- Compatible with existing PyQt5 architecture
- Uses configured AI models (OpenAI, DeepSeek, etc.)
- Follows established module patterns
- Provides PyQt5 signals for progress tracking
- Supports both English and Chinese requirements text

## Error Handling

The analyzer handles various edge cases:
- Empty or minimal input
- Missing model configuration (falls back to mock model)
- Invalid JSON responses from AI models
- Network/API failures
- Malformed requirement text

All errors are captured and reported through the PyQt5 signal system for proper UI feedback.