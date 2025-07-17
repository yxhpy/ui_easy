"""
Requirements Validator - Validates completeness and quality of requirements
"""

from typing import List, Dict, Any, Tuple
import re
from .models import (
    Requirement, RequirementType, RequirementPriority, RequirementStatus,
    AnalysisResult
)

class RequirementValidator:
    """
    Validates requirements for completeness, clarity, and feasibility
    """
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.quality_metrics = self._initialize_quality_metrics()
    
    def validate_analysis_result(self, analysis: AnalysisResult) -> Dict[str, Any]:
        """
        Comprehensive validation of analysis result
        
        Returns:
            Dict with validation results, scores, and recommendations
        """
        validation_result = {
            'overall_score': 0.0,
            'category_scores': {},
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'validation_details': {}
        }
        
        # Validate individual requirements
        req_validation = self._validate_requirements(analysis.requirements)
        validation_result['validation_details']['requirements'] = req_validation
        
        # Validate project structure
        structure_validation = self._validate_project_structure(analysis)
        validation_result['validation_details']['structure'] = structure_validation
        
        # Validate completeness
        completeness_validation = self._validate_completeness(analysis)
        validation_result['validation_details']['completeness'] = completeness_validation
        
        # Calculate scores
        validation_result['category_scores'] = {
            'requirements_quality': req_validation['score'],
            'project_structure': structure_validation['score'],
            'completeness': completeness_validation['score']
        }
        
        # Calculate overall score
        validation_result['overall_score'] = sum(validation_result['category_scores'].values()) / len(validation_result['category_scores'])
        
        # Aggregate issues and recommendations
        validation_result['issues'].extend(req_validation['issues'])
        validation_result['issues'].extend(structure_validation['issues'])
        validation_result['issues'].extend(completeness_validation['issues'])
        
        validation_result['warnings'].extend(req_validation['warnings'])
        validation_result['warnings'].extend(structure_validation['warnings'])
        validation_result['warnings'].extend(completeness_validation['warnings'])
        
        validation_result['recommendations'].extend(req_validation['recommendations'])
        validation_result['recommendations'].extend(structure_validation['recommendations'])
        validation_result['recommendations'].extend(completeness_validation['recommendations'])
        
        return validation_result
    
    def _validate_requirements(self, requirements: List[Requirement]) -> Dict[str, Any]:
        """Validate individual requirements quality"""
        result = {
            'score': 0.0,
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'details': {}
        }
        
        if not requirements:
            result['issues'].append("No requirements found")
            return result
        
        total_score = 0.0
        requirement_details = {}
        
        for req in requirements:
            req_validation = self._validate_single_requirement(req)
            requirement_details[req.id] = req_validation
            total_score += req_validation['score']
            
            # Aggregate issues
            if req_validation['issues']:
                result['issues'].extend([f"Requirement '{req.title}': {issue}" for issue in req_validation['issues']])
            
            if req_validation['warnings']:
                result['warnings'].extend([f"Requirement '{req.title}': {warning}" for warning in req_validation['warnings']])
        
        result['score'] = total_score / len(requirements)
        result['details'] = requirement_details
        
        # Generate recommendations based on common issues
        self._generate_requirement_recommendations(result, requirements)
        
        return result
    
    def _validate_single_requirement(self, req: Requirement) -> Dict[str, Any]:
        """Validate a single requirement"""
        validation = {
            'score': 0.0,
            'issues': [],
            'warnings': [],
            'passed_rules': [],
            'failed_rules': []
        }
        
        total_rules = len(self.validation_rules)
        passed_rules = 0
        
        for rule_name, rule_func in self.validation_rules.items():
            try:
                result = rule_func(req)
                if result['passed']:
                    passed_rules += 1
                    validation['passed_rules'].append(rule_name)
                else:
                    validation['failed_rules'].append(rule_name)
                    if result.get('severity') == 'error':
                        validation['issues'].append(result['message'])
                    else:
                        validation['warnings'].append(result['message'])
            except Exception as e:
                validation['warnings'].append(f"Validation rule '{rule_name}' failed: {str(e)}")
        
        validation['score'] = passed_rules / total_rules
        return validation
    
    def _validate_project_structure(self, analysis: AnalysisResult) -> Dict[str, Any]:
        """Validate overall project structure and organization"""
        result = {
            'score': 0.0,
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        score_components = []
        
        # Check project overview
        if analysis.project_overview and len(analysis.project_overview.strip()) > 20:
            score_components.append(1.0)
        else:
            score_components.append(0.0)
            result['issues'].append("Project overview is missing or too brief")
        
        # Check target audience
        if analysis.target_audience and len(analysis.target_audience.strip()) > 10:
            score_components.append(1.0)
        else:
            score_components.append(0.0)
            result['issues'].append("Target audience is not defined")
        
        # Check platform specification
        if analysis.platform and analysis.platform.strip():
            score_components.append(1.0)
        else:
            score_components.append(0.5)
            result['warnings'].append("Platform is not clearly specified")
        
        # Check requirement distribution
        req_types = [req.type for req in analysis.requirements]
        unique_types = set(req_types)
        
        expected_types = {RequirementType.FUNCTIONAL, RequirementType.UI_COMPONENT}
        if unique_types.intersection(expected_types):
            score_components.append(1.0)
        else:
            score_components.append(0.0)
            result['issues'].append("Missing essential requirement types (functional or UI components)")
        
        result['score'] = sum(score_components) / len(score_components)
        return result
    
    def _validate_completeness(self, analysis: AnalysisResult) -> Dict[str, Any]:
        """Validate completeness of requirements coverage"""
        result = {
            'score': 0.0,
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        completeness_checks = []
        
        # Check requirement type coverage
        req_types = set(req.type for req in analysis.requirements)
        essential_types = {
            RequirementType.FUNCTIONAL,
            RequirementType.UI_COMPONENT,
            RequirementType.LAYOUT
        }
        
        covered_essential = req_types.intersection(essential_types)
        completeness_checks.append(len(covered_essential) / len(essential_types))
        
        if len(covered_essential) < len(essential_types):
            missing = essential_types - covered_essential
            result['warnings'].append(f"Missing requirement types: {[t.value for t in missing]}")
        
        # Check priority distribution
        priorities = [req.priority for req in analysis.requirements]
        has_critical = RequirementPriority.CRITICAL in priorities
        has_high = RequirementPriority.HIGH in priorities
        
        if has_critical or has_high:
            completeness_checks.append(1.0)
        else:
            completeness_checks.append(0.5)
            result['warnings'].append("No critical or high priority requirements identified")
        
        # Check acceptance criteria coverage
        reqs_with_criteria = [req for req in analysis.requirements if req.acceptance_criteria]
        criteria_coverage = len(reqs_with_criteria) / len(analysis.requirements) if analysis.requirements else 0
        completeness_checks.append(criteria_coverage)
        
        if criteria_coverage < 0.5:
            result['warnings'].append("Many requirements lack acceptance criteria")
        
        # Check component specifications
        ui_reqs = [req for req in analysis.requirements if req.type == RequirementType.UI_COMPONENT]
        ui_with_specs = [req for req in ui_reqs if req.component_spec]
        ui_spec_coverage = len(ui_with_specs) / len(ui_reqs) if ui_reqs else 1.0
        completeness_checks.append(ui_spec_coverage)
        
        if ui_spec_coverage < 0.7 and ui_reqs:
            result['warnings'].append("UI component requirements lack detailed specifications")
        
        result['score'] = sum(completeness_checks) / len(completeness_checks)
        return result
    
    def _generate_requirement_recommendations(self, result: Dict[str, Any], requirements: List[Requirement]):
        """Generate recommendations for improving requirements"""
        
        # Check for common issues
        issues_count = len(result['issues'])
        warnings_count = len(result['warnings'])
        
        if issues_count > len(requirements) * 0.3:
            result['recommendations'].append("Many requirements have critical issues - consider reviewing and refining them")
        
        if warnings_count > len(requirements) * 0.5:
            result['recommendations'].append("Consider adding more detail to requirements to improve clarity")
        
        # Check priority distribution
        priorities = [req.priority for req in requirements]
        critical_count = priorities.count(RequirementPriority.CRITICAL)
        
        if critical_count > len(requirements) * 0.5:
            result['recommendations'].append("Too many critical requirements - consider reprioritizing")
        elif critical_count == 0:
            result['recommendations'].append("Consider identifying critical requirements for prioritization")
        
        # Check for missing acceptance criteria
        missing_criteria = [req for req in requirements if not req.acceptance_criteria]
        if len(missing_criteria) > len(requirements) * 0.3:
            result['recommendations'].append("Add acceptance criteria to requirements for clearer implementation guidance")
    
    def _initialize_validation_rules(self) -> Dict[str, callable]:
        """Initialize requirement validation rules"""
        return {
            'has_title': self._rule_has_title,
            'has_description': self._rule_has_description,
            'title_length': self._rule_title_length,
            'description_length': self._rule_description_length,
            'has_acceptance_criteria': self._rule_has_acceptance_criteria,
            'no_vague_language': self._rule_no_vague_language,
            'specific_and_measurable': self._rule_specific_and_measurable,
            'has_priority': self._rule_has_priority,
            'realistic_priority': self._rule_realistic_priority,
            'component_has_spec': self._rule_component_has_spec,
            'interaction_has_spec': self._rule_interaction_has_spec
        }
    
    def _initialize_quality_metrics(self) -> Dict[str, callable]:
        """Initialize quality metrics"""
        return {
            'clarity_score': self._calculate_clarity_score,
            'completeness_score': self._calculate_completeness_score,
            'specificity_score': self._calculate_specificity_score
        }
    
    # Validation rules
    def _rule_has_title(self, req: Requirement) -> Dict[str, Any]:
        passed = bool(req.title and req.title.strip())
        return {
            'passed': passed,
            'message': "Requirement must have a title" if not passed else "",
            'severity': 'error' if not passed else 'info'
        }
    
    def _rule_has_description(self, req: Requirement) -> Dict[str, Any]:
        passed = bool(req.description and req.description.strip())
        return {
            'passed': passed,
            'message': "Requirement must have a description" if not passed else "",
            'severity': 'error' if not passed else 'info'
        }
    
    def _rule_title_length(self, req: Requirement) -> Dict[str, Any]:
        if not req.title:
            return {'passed': False, 'message': "No title to validate", 'severity': 'error'}
        
        length = len(req.title.strip())
        passed = 5 <= length <= 100
        
        message = ""
        if length < 5:
            message = "Title is too short (should be 5-100 characters)"
        elif length > 100:
            message = "Title is too long (should be 5-100 characters)"
        
        return {
            'passed': passed,
            'message': message,
            'severity': 'warning' if not passed else 'info'
        }
    
    def _rule_description_length(self, req: Requirement) -> Dict[str, Any]:
        if not req.description:
            return {'passed': False, 'message': "No description to validate", 'severity': 'error'}
        
        length = len(req.description.strip())
        passed = length >= 20
        
        return {
            'passed': passed,
            'message': "Description should be at least 20 characters" if not passed else "",
            'severity': 'warning' if not passed else 'info'
        }
    
    def _rule_has_acceptance_criteria(self, req: Requirement) -> Dict[str, Any]:
        passed = bool(req.acceptance_criteria and len(req.acceptance_criteria) > 0)
        return {
            'passed': passed,
            'message': "Requirement should have acceptance criteria" if not passed else "",
            'severity': 'warning' if not passed else 'info'
        }
    
    def _rule_no_vague_language(self, req: Requirement) -> Dict[str, Any]:
        vague_words = ['somehow', 'maybe', 'probably', 'might', 'could', 'should probably', 'perhaps']
        text = (req.title + ' ' + req.description).lower()
        
        found_vague = [word for word in vague_words if word in text]
        passed = len(found_vague) == 0
        
        return {
            'passed': passed,
            'message': f"Contains vague language: {', '.join(found_vague)}" if not passed else "",
            'severity': 'warning' if not passed else 'info'
        }
    
    def _rule_specific_and_measurable(self, req: Requirement) -> Dict[str, Any]:
        text = (req.title + ' ' + req.description).lower()
        
        # Look for specific indicators
        specific_indicators = ['must', 'shall', 'will', 'exactly', 'precisely', 'specific']
        measurable_indicators = ['number', 'amount', 'percentage', 'time', 'size', 'count', 'measure']
        
        has_specific = any(indicator in text for indicator in specific_indicators)
        has_measurable = any(indicator in text for indicator in measurable_indicators)
        
        passed = has_specific or has_measurable or req.acceptance_criteria
        
        return {
            'passed': passed,
            'message': "Requirement should be more specific and measurable" if not passed else "",
            'severity': 'warning' if not passed else 'info'
        }
    
    def _rule_has_priority(self, req: Requirement) -> Dict[str, Any]:
        passed = req.priority is not None
        return {
            'passed': passed,
            'message': "Requirement must have a priority" if not passed else "",
            'severity': 'error' if not passed else 'info'
        }
    
    def _rule_realistic_priority(self, req: Requirement) -> Dict[str, Any]:
        # Simple heuristic: if description is very short, probably shouldn't be critical
        if req.priority == RequirementPriority.CRITICAL:
            desc_length = len(req.description.strip()) if req.description else 0
            passed = desc_length >= 30 or bool(req.acceptance_criteria)
            
            return {
                'passed': passed,
                'message': "Critical requirements should have detailed description or acceptance criteria" if not passed else "",
                'severity': 'warning' if not passed else 'info'
            }
        
        return {'passed': True, 'message': "", 'severity': 'info'}
    
    def _rule_component_has_spec(self, req: Requirement) -> Dict[str, Any]:
        if req.type != RequirementType.UI_COMPONENT:
            return {'passed': True, 'message': "", 'severity': 'info'}
        
        passed = req.component_spec is not None
        return {
            'passed': passed,
            'message': "UI component requirement should have component specification" if not passed else "",
            'severity': 'warning' if not passed else 'info'
        }
    
    def _rule_interaction_has_spec(self, req: Requirement) -> Dict[str, Any]:
        if req.type != RequirementType.INTERACTION:
            return {'passed': True, 'message': "", 'severity': 'info'}
        
        passed = bool(req.interaction_specs)
        return {
            'passed': passed,
            'message': "Interaction requirement should have interaction specifications" if not passed else "",
            'severity': 'warning' if not passed else 'info'
        }
    
    # Quality metrics
    def _calculate_clarity_score(self, requirements: List[Requirement]) -> float:
        if not requirements:
            return 0.0
        
        total_score = 0.0
        for req in requirements:
            score = 1.0
            
            # Deduct for vague language
            vague_words = ['somehow', 'maybe', 'probably']
            text = (req.title + ' ' + req.description).lower()
            vague_count = sum(1 for word in vague_words if word in text)
            score -= vague_count * 0.2
            
            # Deduct for ambiguous status
            if req.status == RequirementStatus.AMBIGUOUS:
                score -= 0.3
            
            total_score += max(0.0, score)
        
        return total_score / len(requirements)
    
    def _calculate_completeness_score(self, requirements: List[Requirement]) -> float:
        if not requirements:
            return 0.0
        
        complete_count = 0
        for req in requirements:
            score = 0.0
            
            # Check basic completeness
            if req.title and req.description:
                score += 0.4
            
            if req.acceptance_criteria:
                score += 0.3
            
            if req.type != RequirementType.FUNCTIONAL:  # Type-specific completeness
                if req.type == RequirementType.UI_COMPONENT and req.component_spec:
                    score += 0.3
                elif req.type == RequirementType.INTERACTION and req.interaction_specs:
                    score += 0.3
                else:
                    score += 0.1
            else:
                score += 0.3
            
            complete_count += min(1.0, score)
        
        return complete_count / len(requirements)
    
    def _calculate_specificity_score(self, requirements: List[Requirement]) -> float:
        if not requirements:
            return 0.0
        
        total_score = 0.0
        for req in requirements:
            score = 0.5  # Base score
            
            # Check for specific language
            text = (req.title + ' ' + req.description).lower()
            specific_words = ['must', 'shall', 'exactly', 'specifically', 'precisely']
            if any(word in text for word in specific_words):
                score += 0.2
            
            # Check for measurable criteria
            if req.acceptance_criteria:
                score += 0.3
            
            total_score += min(1.0, score)
        
        return total_score / len(requirements)