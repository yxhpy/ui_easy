"""
Requirements Analyzer - Main analysis engine for extracting and structuring requirements
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from core.base_module import BaseModule
from models.model_factory import ModelFactory
from .models import (
    Requirement, RequirementType, RequirementPriority, RequirementStatus,
    ComponentSpec, LayoutSpec, StyleSpec, InteractionSpec, AnalysisResult
)

class RequirementAnalyzer(BaseModule):
    """
    Analyzes user input to extract and structure UI/UX requirements
    """
    
    def __init__(self, config):
        super().__init__("RequirementAnalyzer", config)
        self.model_factory = ModelFactory(config)
        
        # Analysis prompts for different aspects
        self.prompts = {
            'initial_analysis': self._get_initial_analysis_prompt(),
            'component_extraction': self._get_component_extraction_prompt(),
            'layout_analysis': self._get_layout_analysis_prompt(),
            'styling_analysis': self._get_styling_analysis_prompt(),
            'interaction_analysis': self._get_interaction_analysis_prompt(),
            'validation': self._get_validation_prompt()
        }
    
    def process(self, input_data: Dict[str, Any]) -> AnalysisResult:
        """
        Process user requirements and return structured analysis
        
        Args:
            input_data: {
                'text': str,  # User requirements text
                'context': str,  # Additional context (optional)
                'platform': str,  # Target platform (web, mobile, desktop)
                'existing_analysis': AnalysisResult  # Previous analysis to refine (optional)
            }
        
        Returns:
            AnalysisResult: Structured requirements analysis
        """
        requirements_text = input_data.get('text', '')
        context = input_data.get('context', '')
        platform = input_data.get('platform', 'web')
        existing_analysis = input_data.get('existing_analysis')
        
        if not requirements_text.strip():
            raise ValueError("Requirements text cannot be empty")
        
        self.update_progress(10, "Starting requirements analysis...")
        
        # Step 1: Initial analysis and project overview
        self.update_progress(20, "Analyzing project overview...")
        project_overview, target_audience = self._analyze_project_overview(requirements_text, context)
        
        # Step 2: Extract and categorize requirements
        self.update_progress(40, "Extracting requirements...")
        requirements = self._extract_requirements(requirements_text, context, platform)
        
        # Step 3: Analyze components
        self.update_progress(60, "Analyzing UI components...")
        self._analyze_components(requirements, requirements_text)
        
        # Step 4: Analyze layout and interactions
        self.update_progress(80, "Analyzing layout and interactions...")
        self._analyze_layout_and_interactions(requirements, requirements_text)
        
        # Step 5: Validate and score
        self.update_progress(90, "Validating requirements...")
        analysis_result = self._validate_and_score(
            requirements, project_overview, target_audience, platform, requirements_text
        )
        
        self.update_progress(100, "Requirements analysis completed")
        return analysis_result
    
    def _analyze_project_overview(self, requirements_text: str, context: str) -> Tuple[str, str]:
        """Extract project overview and target audience"""
        try:
            # 直接使用default模型配置
            model = self.model_factory.create_model('default')
            
            prompt = f"""
            Analyze the following requirements and provide:
            1. A concise project overview (2-3 sentences)
            2. Target audience description
            
            Requirements:
            {requirements_text}
            
            Context:
            {context}
            
            Return as JSON:
            {{
                "project_overview": "Brief description of what this project aims to achieve",
                "target_audience": "Who will use this application"
            }}
            """
            
            # 尝试使用流式输出
            response = ""
            try:
                # 发送分析开始的提示
                self.streaming_text_updated.emit("🔍 正在分析项目概述...\n\n")
                
                if hasattr(model, 'generate_stream'):
                    for chunk in model.generate_stream(prompt):
                        response += chunk
                        self.streaming_text_updated.emit(chunk)
                else:
                    response = model.generate(prompt)
                    self.streaming_text_updated.emit(response)
            except Exception as stream_error:
                # 流式输出失败，使用普通输出
                response = model.generate(prompt)
                self.streaming_text_updated.emit(response)
            
            self.streaming_text_updated.emit("\n\n" + "="*50 + "\n\n")
            
            try:
                result = json.loads(response)
                # 检查result是否为字典
                if isinstance(result, dict):
                    return result.get('project_overview', ''), result.get('target_audience', '')
                elif isinstance(result, list) and len(result) > 0:
                    # 如果返回的是列表，尝试从第一个元素获取信息
                    first_item = result[0]
                    if isinstance(first_item, dict):
                        return first_item.get('project_overview', ''), first_item.get('target_audience', '')
                    else:
                        # 如果列表元素不是字典，使用fallback
                        return self._extract_overview_fallback(response)
                else:
                    # 其他情况使用fallback
                    return self._extract_overview_fallback(response)
            except json.JSONDecodeError:
                # Fallback parsing
                return self._extract_overview_fallback(response)
                
        except Exception as e:
            self.error_occurred.emit(f"Error analyzing project overview: {str(e)}")
            return "", ""
    
    def _extract_requirements(self, requirements_text: str, context: str, platform: str) -> List[Requirement]:
        """Extract individual requirements from text"""
        try:
            model = self.model_factory.create_model('default')
            
            prompt = self.prompts['initial_analysis'].format(
                requirements_text=requirements_text,
                context=context,
                platform=platform
            )
            
            # 流式输出需求提取过程
            response = ""
            try:
                self.streaming_text_updated.emit("📋 正在提取和分类需求...\n\n")
                
                if hasattr(model, 'generate_stream'):
                    for chunk in model.generate_stream(prompt):
                        response += chunk
                        self.streaming_text_updated.emit(chunk)
                else:
                    response = model.generate(prompt)
                    self.streaming_text_updated.emit(response)
            except Exception:
                response = model.generate(prompt)
                self.streaming_text_updated.emit(response)
            
            self.streaming_text_updated.emit("\n\n" + "="*50 + "\n\n")
            
            # Parse the response and create Requirement objects
            return self._parse_requirements_response(response, requirements_text)
            
        except Exception as e:
            self.error_occurred.emit(f"Error extracting requirements: {str(e)}")
            return []
    
    def _analyze_components(self, requirements: List[Requirement], original_text: str):
        """Analyze and add component specifications to requirements"""
        ui_requirements = [req for req in requirements if req.type == RequirementType.UI_COMPONENT]
        
        if not ui_requirements:
            self.streaming_text_updated.emit("⚠️ 未找到UI组件需求，跳过组件分析。\n\n")
            return
        
        try:
            model = self.model_factory.create_model('default')
            
            self.streaming_text_updated.emit(f"🎨 正在分析 {len(ui_requirements)} 个UI组件...\n\n")
            
            for i, requirement in enumerate(ui_requirements, 1):
                self.streaming_text_updated.emit(f"分析组件 {i}/{len(ui_requirements)}: {requirement.title}\n")
                
                prompt = self.prompts['component_extraction'].format(
                    requirement_title=requirement.title,
                    requirement_description=requirement.description,
                    original_text=original_text
                )
                
                response = ""
                try:
                    if hasattr(model, 'generate_stream'):
                        for chunk in model.generate_stream(prompt):
                            response += chunk
                            self.streaming_text_updated.emit(chunk)
                    else:
                        response = model.generate(prompt)
                        self.streaming_text_updated.emit(response)
                except Exception:
                    response = model.generate(prompt)
                    self.streaming_text_updated.emit(response)
                
                component_spec = self._parse_component_spec(response)
                
                if component_spec:
                    requirement.component_spec = component_spec
                    requirement.status = RequirementStatus.ANALYZED
                    self.streaming_text_updated.emit(f"\n✅ 组件 {requirement.title} 分析完成\n\n")
                else:
                    self.streaming_text_updated.emit(f"\n⚠️ 组件 {requirement.title} 分析失败\n\n")
            
            self.streaming_text_updated.emit("="*50 + "\n\n")
                    
        except Exception as e:
            self.error_occurred.emit(f"Error analyzing components: {str(e)}")
    
    def _analyze_layout_and_interactions(self, requirements: List[Requirement], original_text: str):
        """Analyze layout and interaction requirements"""
        layout_requirements = [req for req in requirements if req.type == RequirementType.LAYOUT]
        interaction_requirements = [req for req in requirements if req.type == RequirementType.INTERACTION]
        
        try:
            model = self.model_factory.create_model('default')
            
            # Analyze layout requirements
            for requirement in layout_requirements:
                prompt = self.prompts['layout_analysis'].format(
                    requirement_description=requirement.description,
                    original_text=original_text
                )
                
                response = model.generate(prompt)
                layout_spec = self._parse_layout_spec(response)
                
                if layout_spec:
                    requirement.layout_spec = layout_spec
                    requirement.status = RequirementStatus.ANALYZED
            
            # Analyze interaction requirements
            for requirement in interaction_requirements:
                prompt = self.prompts['interaction_analysis'].format(
                    requirement_description=requirement.description,
                    original_text=original_text
                )
                
                response = model.generate(prompt)
                interaction_specs = self._parse_interaction_specs(response)
                
                if interaction_specs:
                    requirement.interaction_specs = interaction_specs
                    requirement.status = RequirementStatus.ANALYZED
                    
        except Exception as e:
            self.error_occurred.emit(f"Error analyzing layout and interactions: {str(e)}")
    
    def _validate_and_score(self, requirements: List[Requirement], project_overview: str, 
                           target_audience: str, platform: str, original_text: str) -> AnalysisResult:
        """Validate requirements and create analysis result with scores"""
        
        # Calculate completeness score
        total_reqs = len(requirements)
        analyzed_reqs = len([req for req in requirements if req.status == RequirementStatus.ANALYZED])
        completeness_score = analyzed_reqs / total_reqs if total_reqs > 0 else 0.0
        
        # Identify gaps and ambiguities
        gaps = self._identify_gaps(requirements, original_text)
        ambiguities = self._identify_ambiguities(requirements)
        
        # Calculate clarity score based on ambiguities
        clarity_score = max(0.0, 1.0 - (len(ambiguities) / max(total_reqs, 1)) * 0.5)
        
        # Calculate feasibility score (simplified)
        feasibility_score = self._calculate_feasibility_score(requirements)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(requirements, gaps, ambiguities)
        
        # Estimate development effort
        total_effort, phases = self._estimate_development_effort(requirements)
        
        # Framework recommendations based on requirements
        framework_recommendations = self._recommend_frameworks(requirements, platform)
        
        return AnalysisResult(
            requirements=requirements,
            project_overview=project_overview,
            target_audience=target_audience,
            platform=platform,
            framework_recommendations=framework_recommendations,
            completeness_score=completeness_score,
            clarity_score=clarity_score,
            feasibility_score=feasibility_score,
            gaps=gaps,
            ambiguities=ambiguities,
            recommendations=recommendations,
            total_estimated_effort=total_effort,
            development_phases=phases
        )
    
    def _parse_requirements_response(self, response: str, original_text: str) -> List[Requirement]:
        """Parse AI response into Requirement objects"""
        requirements = []
        
        try:
            # 清理响应，移除markdown代码块标记
            cleaned_response = response.strip()
            
            # 移除 ```json 和 ``` 标记
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # 移除 ```json
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]   # 移除 ```
            
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # 移除结尾的 ```
            
            cleaned_response = cleaned_response.strip()
            
            # Try to parse as JSON first
            if cleaned_response.startswith('{') or cleaned_response.startswith('['):
                data = json.loads(cleaned_response)
                
                # 处理不同的数据结构
                if isinstance(data, dict):
                    if 'requirements' in data:
                        data = data['requirements']
                    else:
                        # 如果是单个需求对象的字典，包装成列表
                        data = [data]
                elif isinstance(data, list):
                    # 已经是列表，直接使用
                    pass
                else:
                    # 不支持的数据类型，使用fallback
                    requirements = self._parse_requirements_text(cleaned_response, original_text)
                    return requirements
                
                # 确保data是列表
                if not isinstance(data, list):
                    data = [data]
                
                for item in data:
                    req = self._create_requirement_from_dict(item, original_text)
                    if req:
                        requirements.append(req)
            else:
                # Fallback to text parsing
                requirements = self._parse_requirements_text(cleaned_response, original_text)
                
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # Fallback to text parsing
            self.error_occurred.emit(f"JSON parsing failed: {str(e)}, using text parsing fallback")
            requirements = self._parse_requirements_text(response, original_text)
        
        return requirements
    
    def _create_requirement_from_dict(self, data: Dict[str, Any], source: str) -> Optional[Requirement]:
        """Create a Requirement object from dictionary data"""
        try:
            # 首先检查data是否为字典类型
            if not isinstance(data, dict):
                self.error_occurred.emit(f"Expected dict but got {type(data).__name__}: {data}")
                return None
            
            req_type = RequirementType(data.get('type', 'functional'))
            priority = RequirementPriority(data.get('priority', 'medium'))
            
            return Requirement(
                title=data.get('title', ''),
                description=data.get('description', ''),
                type=req_type,
                priority=priority,
                source=source,
                rationale=data.get('rationale', ''),
                acceptance_criteria=data.get('acceptance_criteria', []),
                estimated_effort=data.get('estimated_effort'),
                tags=data.get('tags', [])
            )
        except (ValueError, KeyError) as e:
            self.error_occurred.emit(f"Error creating requirement: {str(e)}")
            return None
    
    def _parse_requirements_text(self, response: str, source: str) -> List[Requirement]:
        """Fallback text parsing for requirements"""
        requirements = []
        
        # Simple pattern matching for requirement-like text
        lines = response.split('\n')
        current_req = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for numbered items or bullet points
            if re.match(r'^\d+\.', line) or line.startswith('- ') or line.startswith('* '):
                if current_req:
                    requirements.append(current_req)
                
                title = re.sub(r'^\d+\.|^[-*]\s*', '', line).strip()
                current_req = Requirement(
                    title=title,
                    description=title,
                    source=source
                )
            elif current_req and line:
                # Add to description
                current_req.description += ' ' + line
        
        if current_req:
            requirements.append(current_req)
        
        return requirements
    
    def _parse_component_spec(self, response: str) -> Optional[ComponentSpec]:
        """Parse component specification from AI response"""
        try:
            # 清理响应，移除markdown代码块标记
            cleaned_response = response.strip()
            
            # 移除 ```json 和 ``` 标记
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # 移除 ```json
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]   # 移除 ```
            
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # 移除结尾的 ```
            
            cleaned_response = cleaned_response.strip()
            
            # 处理单个对象
            if cleaned_response.startswith('{'):
                data = json.loads(cleaned_response)
                return self._create_component_spec_from_data(data)
            
            # 处理数组格式 - 通常取第一个主要组件
            elif cleaned_response.startswith('['):
                data_array = json.loads(cleaned_response)
                if isinstance(data_array, list) and len(data_array) > 0:
                    # 如果是数组，尝试找到主要组件（通常是第一个）
                    main_component = data_array[0]
                    
                    # 创建主组件规格
                    component_spec = self._create_component_spec_from_data(main_component)
                    
                    # 如果有子组件，将其作为children添加
                    if len(data_array) > 1:
                        for child_data in data_array[1:]:
                            child_spec = self._create_component_spec_from_data(child_data)
                            if child_spec:
                                component_spec.children.append(child_spec)
                    
                    return component_spec
            
            # 尝试从文本中提取组件信息（fallback）
            return self._parse_component_spec_fallback(cleaned_response)
            
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            # 如果JSON解析失败，尝试文本解析
            fallback_result = self._parse_component_spec_fallback(response)
            if fallback_result is None:
                # 如果fallback也失败，记录错误
                self.error_occurred.emit(f"Component spec parsing failed: {str(e)}")
            return fallback_result
        except Exception as e:
            # 记录错误但不中断流程
            self.error_occurred.emit(f"Component spec parsing error: {str(e)}")
            return None
    
    def _create_component_spec_from_data(self, data: Dict[str, Any]) -> ComponentSpec:
        """从数据字典创建ComponentSpec对象"""
        # 处理children字段
        children = []
        if 'children' in data:
            children_data = data['children']
            if isinstance(children_data, list):
                for child_name in children_data:
                    # 如果children是字符串数组，创建简单的子组件
                    if isinstance(child_name, str):
                        children.append(ComponentSpec(
                            name=child_name,
                            type="reference",  # 标记为引用类型
                            properties={}
                        ))
                    elif isinstance(child_name, dict):
                        children.append(self._create_component_spec_from_data(child_name))
        
        return ComponentSpec(
            name=data.get('name', 'UnknownComponent'),
            type=data.get('type', 'unknown'),
            properties=data.get('properties', {}),
            children=children,
            events=data.get('events', []),
            validation=data.get('validation'),
            accessibility=data.get('accessibility')
        )
    
    def _parse_component_spec_fallback(self, response: str) -> Optional[ComponentSpec]:
        """从非结构化文本中解析组件规格（fallback方法）"""
        try:
            # 基本的文本解析逻辑
            lines = response.split('\n')
            component_name = None
            component_type = None
            properties = {}
            events = []
            found_valid_content = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 查找组件名称
                if '"name"' in line or 'name:' in line:
                    # 简单的名称提取
                    if ':' in line:
                        component_name = line.split(':')[-1].strip().strip('"\'')
                        found_valid_content = True
                
                # 查找组件类型
                if '"type"' in line or 'type:' in line:
                    if ':' in line:
                        component_type = line.split(':')[-1].strip().strip('"\'')
                        found_valid_content = True
                
                # 查找事件
                if 'event' in line.lower() and ('[' in line or 'click' in line or 'hover' in line):
                    # 简单的事件提取
                    if 'click' in line:
                        events.append('click')
                        found_valid_content = True
                    if 'hover' in line:
                        events.append('hover')
                        found_valid_content = True
                    if 'submit' in line:
                        events.append('submit')
                        found_valid_content = True
            
            # 只有找到有效内容才返回组件
            if found_valid_content and component_name and component_type:
                return ComponentSpec(
                    name=component_name,
                    type=component_type,
                    properties=properties,
                    events=events,
                    validation=None,
                    accessibility=None
                )
        
        except Exception:
            pass
        
        return None
    
    def _parse_layout_spec(self, response: str) -> Optional[LayoutSpec]:
        """Parse layout specification from AI response"""
        try:
            if response.strip().startswith('{'):
                data = json.loads(response)
                return LayoutSpec(
                    type=data.get('type', 'flow'),
                    sections=data.get('sections', []),
                    responsive=data.get('responsive', True),
                    breakpoints=data.get('breakpoints'),
                    spacing=data.get('spacing'),
                    alignment=data.get('alignment')
                )
        except (json.JSONDecodeError, KeyError):
            pass
        
        return None
    
    def _parse_interaction_specs(self, response: str) -> List[InteractionSpec]:
        """Parse interaction specifications from AI response"""
        specs = []
        
        try:
            if response.strip().startswith('['):
                data = json.loads(response)
            elif response.strip().startswith('{') and 'interactions' in response:
                data = json.loads(response)['interactions']
            else:
                return specs
            
            for item in data:
                spec = InteractionSpec(
                    trigger=item.get('trigger', ''),
                    action=item.get('action', ''),
                    target=item.get('target', ''),
                    conditions=item.get('conditions', []),
                    feedback=item.get('feedback'),
                    validation=item.get('validation')
                )
                specs.append(spec)
                
        except (json.JSONDecodeError, KeyError):
            pass
        
        return specs
    
    def _identify_gaps(self, requirements: List[Requirement], original_text: str) -> List[str]:
        """Identify missing information in requirements"""
        gaps = []
        
        # Check for common missing elements
        has_ui_components = any(req.type == RequirementType.UI_COMPONENT for req in requirements)
        has_layout = any(req.type == RequirementType.LAYOUT for req in requirements)
        has_styling = any(req.type == RequirementType.STYLING for req in requirements)
        has_interactions = any(req.type == RequirementType.INTERACTION for req in requirements)
        
        if not has_ui_components:
            gaps.append("No specific UI components identified")
        if not has_layout:
            gaps.append("Layout structure not defined")
        if not has_styling:
            gaps.append("Visual styling requirements missing")
        if not has_interactions:
            gaps.append("User interaction patterns not specified")
        
        # Check for incomplete requirements
        for req in requirements:
            if not req.description.strip():
                gaps.append(f"Requirement '{req.title}' lacks description")
            if not req.acceptance_criteria:
                gaps.append(f"Acceptance criteria missing for '{req.title}'")
        
        return gaps
    
    def _identify_ambiguities(self, requirements: List[Requirement]) -> List[str]:
        """Identify ambiguous or unclear requirements"""
        ambiguities = []
        
        # Look for vague language
        vague_words = ['somehow', 'maybe', 'probably', 'might', 'could', 'should probably']
        
        for req in requirements:
            text = (req.title + ' ' + req.description).lower()
            
            for word in vague_words:
                if word in text:
                    ambiguities.append(f"Vague language in '{req.title}': contains '{word}'")
                    req.status = RequirementStatus.AMBIGUOUS
                    break
            
            # Check for contradictory requirements
            if 'simple' in text and 'complex' in text:
                ambiguities.append(f"Contradictory complexity requirements in '{req.title}'")
        
        return ambiguities
    
    def _calculate_feasibility_score(self, requirements: List[Requirement]) -> float:
        """Calculate feasibility score based on requirements complexity"""
        if not requirements:
            return 1.0
        
        total_score = 0.0
        
        for req in requirements:
            # Simple scoring based on requirement type and complexity
            base_score = 1.0
            
            if req.type == RequirementType.FUNCTIONAL:
                base_score = 0.9
            elif req.type == RequirementType.UI_COMPONENT:
                base_score = 0.95
            elif req.type == RequirementType.PERFORMANCE:
                base_score = 0.7
            elif req.type == RequirementType.ACCESSIBILITY:
                base_score = 0.8
            
            # Adjust based on priority (critical requirements might be more complex)
            if req.priority == RequirementPriority.CRITICAL:
                base_score *= 0.9
            elif req.priority == RequirementPriority.LOW:
                base_score *= 1.1
            
            total_score += base_score
        
        return min(1.0, total_score / len(requirements))
    
    def _generate_recommendations(self, requirements: List[Requirement], gaps: List[str], 
                                ambiguities: List[str]) -> List[str]:
        """Generate recommendations for improving requirements"""
        recommendations = []
        
        if gaps:
            recommendations.append("Address missing requirements to ensure complete specification")
        
        if ambiguities:
            recommendations.append("Clarify ambiguous requirements to avoid implementation confusion")
        
        # Check requirement balance
        critical_count = len([req for req in requirements if req.priority == RequirementPriority.CRITICAL])
        total_count = len(requirements)
        
        if critical_count > total_count * 0.5:
            recommendations.append("Consider reducing critical requirements - too many critical items may impact delivery")
        
        if critical_count == 0:
            recommendations.append("Identify critical requirements to prioritize development effort")
        
        return recommendations
    
    def _estimate_development_effort(self, requirements: List[Requirement]) -> Tuple[str, List[Dict[str, Any]]]:
        """Estimate development effort and phases"""
        # Simple effort estimation based on requirement types and priorities
        effort_points = 0
        
        for req in requirements:
            base_points = 1
            
            if req.type == RequirementType.UI_COMPONENT:
                base_points = 2
            elif req.type == RequirementType.LAYOUT:
                base_points = 3
            elif req.type == RequirementType.INTERACTION:
                base_points = 2
            elif req.type == RequirementType.PERFORMANCE:
                base_points = 4
            
            # Adjust for priority
            if req.priority == RequirementPriority.CRITICAL:
                base_points *= 1.5
            elif req.priority == RequirementPriority.HIGH:
                base_points *= 1.2
            
            effort_points += base_points
        
        # Convert to effort estimate
        if effort_points <= 10:
            total_effort = "S (Small - 1-2 weeks)"
        elif effort_points <= 25:
            total_effort = "M (Medium - 3-4 weeks)"
        elif effort_points <= 50:
            total_effort = "L (Large - 1-2 months)"
        else:
            total_effort = "XL (Extra Large - 2+ months)"
        
        # Create development phases
        phases = [
            {
                "name": "Foundation",
                "description": "Core setup and critical components",
                "requirements": [req.id for req in requirements if req.priority == RequirementPriority.CRITICAL],
                "estimated_duration": "20-30% of total effort"
            },
            {
                "name": "Core Features",
                "description": "Main functionality implementation",
                "requirements": [req.id for req in requirements if req.priority == RequirementPriority.HIGH],
                "estimated_duration": "40-50% of total effort"
            },
            {
                "name": "Enhancement",
                "description": "Additional features and polish",
                "requirements": [req.id for req in requirements if req.priority in [RequirementPriority.MEDIUM, RequirementPriority.LOW]],
                "estimated_duration": "20-30% of total effort"
            }
        ]
        
        return total_effort, phases
    
    def _recommend_frameworks(self, requirements: List[Requirement], platform: str) -> List[str]:
        """Recommend frameworks based on requirements and platform"""
        recommendations = []
        
        if platform == 'web':
            has_complex_interactions = any(
                req.type == RequirementType.INTERACTION and len(req.interaction_specs) > 2
                for req in requirements
            )
            
            has_many_components = len([req for req in requirements if req.type == RequirementType.UI_COMPONENT]) > 10
            
            if has_complex_interactions or has_many_components:
                recommendations.extend(['React', 'Vue.js', 'Angular'])
            else:
                recommendations.extend(['HTML/CSS/JavaScript', 'Alpine.js', 'Svelte'])
        
        elif platform == 'mobile':
            recommendations.extend(['React Native', 'Flutter', 'Swift/SwiftUI', 'Kotlin/Jetpack Compose'])
        
        elif platform == 'desktop':
            recommendations.extend(['Electron', 'Tauri', 'PyQt/PySide', 'JavaFX'])
        
        return recommendations
    
    def _extract_overview_fallback(self, response: str) -> Tuple[str, str]:
        """Fallback method to extract overview from unstructured response"""
        lines = response.split('\n')
        overview = ""
        audience = ""
        
        for line in lines:
            line = line.strip()
            if 'overview' in line.lower() or 'project' in line.lower():
                overview = line
            elif 'audience' in line.lower() or 'user' in line.lower():
                audience = line
        
        return overview, audience
    
    # Prompt templates
    def _get_initial_analysis_prompt(self) -> str:
        return """
        Analyze the following requirements text and extract individual requirements. 
        Categorize each requirement by type and priority.
        
        Requirements text:
        {requirements_text}
        
        Additional context:
        {context}
        
        Target platform: {platform}
        
        Return a JSON array of requirements with this structure:
        [
            {{
                "title": "Brief requirement title",
                "description": "Detailed description",
                "type": "functional|ui_component|layout|styling|interaction|data|performance|accessibility|business",
                "priority": "critical|high|medium|low",
                "rationale": "Why this requirement exists",
                "acceptance_criteria": ["criteria 1", "criteria 2"],
                "estimated_effort": "XS|S|M|L|XL",
                "tags": ["tag1", "tag2"]
            }}
        ]
        
        Ensure requirements are:
        1. Specific and actionable
        2. Properly categorized
        3. Realistically prioritized
        4. Include clear acceptance criteria
        """
    
    def _get_component_extraction_prompt(self) -> str:
        return """
        For the UI component requirement: "{requirement_title}"
        Description: {requirement_description}
        
        Based on the original requirements: {original_text}
        
        Extract detailed component specification. Return as JSON - either a single component object or an array if multiple related components are involved:
        
        For single component:
        {{
            "name": "ComponentName",
            "type": "button|input|form|card|modal|navigation|list|etc",
            "properties": {{
                "size": "small|medium|large",
                "variant": "primary|secondary|outline",
                "placeholder": "text",
                "required": true,
                "grid": {{"enabled": true, "columns": {{"xs": 1, "md": 2}}}},
                "other_props": "value"
            }},
            "events": ["click", "hover", "submit", "change", "scroll"],
            "validation": {{
                "rules": ["required", "email", "minLength:3"],
                "messages": {{"required": "This field is required"}}
            }},
            "accessibility": {{
                "aria-label": "Descriptive label",
                "role": "button",
                "keyboard_navigation": true
            }},
            "children": ["ChildComponentName"]
        }}
        
        For multiple related components (like a list and its items):
        [
            {{
                "name": "ParentComponent",
                "type": "list|container|form",
                "properties": {{ ... }},
                "events": [ ... ],
                "children": ["ChildComponent"]
            }},
            {{
                "name": "ChildComponent", 
                "type": "card|item|field",
                "properties": {{ ... }},
                "events": [ ... ]
            }}
        ]
        
        Ensure all component specifications are detailed and include realistic properties, events, validation rules and accessibility features.
        """
    
    def _get_layout_analysis_prompt(self) -> str:
        return """
        For the layout requirement: {requirement_description}
        
        Based on the original requirements: {original_text}
        
        Analyze and provide layout specification as JSON:
        {{
            "type": "grid|flex|absolute|flow",
            "sections": [
                {{
                    "name": "header",
                    "position": "top",
                    "size": "auto",
                    "components": ["navigation", "logo"]
                }},
                {{
                    "name": "main",
                    "position": "center",
                    "size": "1fr",
                    "components": ["content"]
                }}
            ],
            "responsive": true,
            "breakpoints": {{
                "mobile": 768,
                "tablet": 1024,
                "desktop": 1200
            }},
            "spacing": {{
                "padding": "16px",
                "margin": "8px",
                "gap": "12px"
            }},
            "alignment": {{
                "horizontal": "center|left|right|space-between",
                "vertical": "top|center|bottom|space-around"
            }}
        }}
        """
    
    def _get_styling_analysis_prompt(self) -> str:
        return """
        Analyze styling requirements and provide specification as JSON:
        {{
            "theme": "light|dark|auto",
            "colors": {{
                "primary": "#007bff",
                "secondary": "#6c757d",
                "background": "#ffffff",
                "text": "#333333"
            }},
            "typography": {{
                "font_family": "Arial, sans-serif",
                "font_sizes": {{
                    "small": "12px",
                    "medium": "16px",
                    "large": "24px"
                }},
                "line_height": "1.5"
            }},
            "spacing": {{
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px"
            }},
            "borders": {{
                "radius": "4px",
                "width": "1px",
                "style": "solid"
            }},
            "shadows": {{
                "small": "0 1px 3px rgba(0,0,0,0.1)",
                "medium": "0 4px 6px rgba(0,0,0,0.1)"
            }},
            "animations": [
                {{
                    "name": "fadeIn",
                    "duration": "0.3s",
                    "easing": "ease-in-out"
                }}
            ]
        }}
        """
    
    def _get_interaction_analysis_prompt(self) -> str:
        return """
        For the interaction requirement: {requirement_description}
        
        Based on the original requirements: {original_text}
        
        Extract interaction specifications as JSON array:
        [
            {{
                "trigger": "click|hover|scroll|keyboard|focus",
                "action": "navigate|submit|validate|show|hide|transform",
                "target": "component_id_or_page",
                "conditions": ["user_logged_in", "form_valid"],
                "feedback": "visual|audio|haptic feedback description",
                "validation": {{
                    "rules": ["required_fields"],
                    "error_handling": "show_message"
                }}
            }}
        ]
        """
    
    def _get_validation_prompt(self) -> str:
        return """
        Review the following requirements for completeness and clarity:
        {requirements}
        
        Identify:
        1. Missing information
        2. Ambiguous requirements
        3. Conflicting requirements
        4. Implementation feasibility issues
        
        Return as JSON:
        {{
            "gaps": ["missing item 1", "missing item 2"],
            "ambiguities": ["unclear requirement 1"],
            "conflicts": ["requirement A conflicts with B"],
            "feasibility_issues": ["complex requirement may need breakdown"]
        }}
        """