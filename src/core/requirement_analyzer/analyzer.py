"""
Requirements Analyzer - Main analysis engine for extracting and structuring requirements
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from core.base_module import BaseModule
from models.model_factory import ModelFactory
from ui.localization import tr
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
        self.config = config
        
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
                'phase': str,  # 'list' for requirement list extraction, 'detail' for detailed analysis
                'requirement_list': List[Dict]  # For detailed analysis phase
            }
        
        Returns:
            AnalysisResult: Structured requirements analysis
        """
        requirements_text = input_data.get('text', '')
        context = input_data.get('context', '')
        platform = input_data.get('platform', 'web')
        existing_analysis = input_data.get('existing_analysis')
        phase = input_data.get('phase', 'complete')  # 'list', 'detail', or 'complete'
        requirement_list = input_data.get('requirement_list', [])
        
        if not requirements_text.strip() and phase != 'detail':
            raise ValueError("Requirements text cannot be empty")
        
        # Phase 1: Extract requirement list only
        if phase == 'list':
            return self._extract_requirement_list_only(requirements_text, context, platform)
        
        # Phase 2: Detailed analysis of specific requirements
        elif phase == 'detail':
            return self._analyze_requirements_in_detail(requirement_list, requirements_text, context, platform)
        
        # Complete analysis (original behavior)
        else:
            return self._complete_analysis(requirements_text, context, platform, existing_analysis)
        
    def _extract_requirement_list_only(self, requirements_text: str, context: str, platform: str) -> AnalysisResult:
        """Phase 1: Extract only the requirement list to ensure completeness"""
        self.update_progress(10, tr("starting_requirements_list_extraction"))
        
        # Step 1: Project overview
        self.update_progress(30, tr("analyzing_requirements_overview"))
        project_overview, target_audience = self._analyze_project_overview(requirements_text, context)
        
        # Step 2: Extract requirement list with minimal details
        self.update_progress(70, tr("extracting_requirements_list"))
        requirements = self._extract_requirements_list(requirements_text, context, platform)
        
        self.update_progress(100, tr("requirements_list_extraction_completed"))
        
        # Return minimal result with just the list
        return AnalysisResult(
            requirements=requirements,
            project_overview=project_overview,
            target_audience=target_audience,
            platform=platform,
            framework_recommendations=[],
            completeness_score=0.3,  # Partial completion
            clarity_score=0.5,
            feasibility_score=0.8,
            gaps=[],
            ambiguities=[],
            recommendations=[tr("recommendation_proceed_detailed_analysis")],
            total_estimated_effort="TBD",
            development_phases=[]
        )
    
    def _analyze_requirements_in_detail(self, requirement_list: List[Dict], original_text: str, 
                                       context: str, platform: str) -> AnalysisResult:
        """Phase 2: Detailed analysis of each requirement"""
        self.update_progress(10, tr("starting_detailed_analysis"))
        
        # Convert requirement list to Requirement objects
        requirements = []
        for req_data in requirement_list:
            req = self._create_requirement_from_dict(req_data, original_text)
            if req:
                requirements.append(req)
        
        # Analyze each requirement in detail
        total_reqs = len(requirements)
        
        for i, requirement in enumerate(requirements):
            progress = 20 + (60 * (i + 1) // total_reqs)
            self.update_progress(progress, tr("analyzing_requirement_detail").format(
                current=i+1, total=total_reqs, title=requirement.title[:30]
            ))
            
            # Detailed component analysis for UI components
            if requirement.type == RequirementType.UI_COMPONENT:
                self._analyze_single_component(requirement, original_text)
            
            # Layout analysis for layout requirements
            elif requirement.type == RequirementType.LAYOUT:
                self._analyze_single_layout(requirement, original_text)
            
            # Interaction analysis
            elif requirement.type == RequirementType.INTERACTION:
                self._analyze_single_interaction(requirement, original_text)
        
        # Final validation and scoring
        self.update_progress(90, tr("validating_requirements"))
        analysis_result = self._validate_and_score(
            requirements, "", "", platform, original_text
        )
        
        self.update_progress(100, tr("detailed_analysis_completed"))
        return analysis_result
    
    def _complete_analysis(self, requirements_text: str, context: str, platform: str, 
                          existing_analysis: Optional[AnalysisResult]) -> AnalysisResult:
        """Original complete analysis flow"""
        self.update_progress(10, tr("starting_requirements_analysis"))
        
        # Step 1: Initial analysis and project overview
        self.update_progress(20, tr("analyzing_requirements_overview"))
        project_overview, target_audience = self._analyze_project_overview(requirements_text, context)
        
        # Step 2: Extract and categorize requirements
        self.update_progress(40, tr("extracting_categorizing_requirements"))
        requirements = self._extract_requirements(requirements_text, context, platform)
        
        # Step 3: Analyze components
        self.update_progress(60, tr("analyzing_ui_components_phase"))
        self._analyze_components(requirements, requirements_text)
        
        # Step 4: Analyze layout and interactions
        self.update_progress(80, tr("analyzing_layout_interactions"))
        self._analyze_layout_and_interactions(requirements, requirements_text)
        
        # Step 5: Validate and score
        self.update_progress(90, tr("validating_requirements"))
        analysis_result = self._validate_and_score(
            requirements, project_overview, target_audience, platform, requirements_text
        )
        
        self.update_progress(100, tr("requirements_analysis_completed"))
        return analysis_result
    
    def _analyze_project_overview(self, requirements_text: str, context: str) -> Tuple[str, str]:
        """Extract project overview and target audience"""
        try:
            # 使用模块配置指定的模型
            module_config = self.config.get_module_config("requirement_analyzer")
            model_config_name = module_config.model_config if module_config else self.config.get_app_setting("default_model")
            model = self.model_factory.get_model(model_config_name)
            
            prompt = f"""
            {self._get_language_instruction()}
            
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
                self.streaming_text_updated.emit(tr("analyzing_project_overview") + "\n\n")
                
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
            # 使用模块配置指定的模型
            module_config = self.config.get_module_config("requirement_analyzer")
            model_config_name = module_config.model_config if module_config else self.config.get_app_setting("default_model")
            model = self.model_factory.get_model(model_config_name)
            
            prompt = self.prompts['initial_analysis'].format(
                language_instruction=self._get_language_instruction(),
                requirements_text=requirements_text,
                context=context,
                platform=platform
            )
            
            # 流式输出需求提取过程
            response = ""
            try:
                self.streaming_text_updated.emit(tr("extracting_requirements") + "\n\n")
                
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
    
    def _extract_requirements_list(self, requirements_text: str, context: str, platform: str) -> List[Requirement]:
        """Extract basic requirement list with minimal details for first phase"""
        try:
            # 使用模块配置指定的模型
            module_config = self.config.get_module_config("requirement_analyzer")
            model_config_name = module_config.model_config if module_config else self.config.get_app_setting("default_model")
            model = self.model_factory.get_model(model_config_name)
            
            prompt = self._get_requirement_list_prompt().format(
                language_instruction=self._get_language_instruction(),
                requirements_text=requirements_text,
                context=context,
                platform=platform
            )
            
            # 流式输出需求列表提取过程
            response = ""
            try:
                self.streaming_text_updated.emit(tr("extracting_requirements_list") + "\n\n")
                
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
            
            # Parse the response and create basic Requirement objects
            return self._parse_requirements_response(response, requirements_text)
            
        except Exception as e:
            self.error_occurred.emit(f"Error extracting requirements list: {str(e)}")
            return []
    
    def _analyze_single_component(self, requirement: Requirement, original_text: str):
        """Analyze a single UI component requirement in detail"""
        try:
            module_config = self.config.get_module_config("requirement_analyzer")
            model_config_name = module_config.model_config if module_config else self.config.get_app_setting("default_model")
            model = self.model_factory.get_model(model_config_name)
            
            self.streaming_text_updated.emit(tr("analyzing_component_detail").format(title=requirement.title) + "\n")
            
            prompt = self.prompts['component_extraction'].format(
                language_instruction=self._get_language_instruction(),
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
            
            # 解析详细需求分析结果并更新需求对象
            analysis_result = self._parse_detailed_analysis(response)
            
            if analysis_result:
                self._update_requirement_with_analysis(requirement, analysis_result)
                requirement.status = RequirementStatus.ANALYZED
                self.streaming_text_updated.emit("\n" + tr("component_analysis_complete").format(title=requirement.title) + "\n\n")
            else:
                self.streaming_text_updated.emit("\n" + tr("component_analysis_failed").format(title=requirement.title) + "\n\n")
                
        except Exception as e:
            self.error_occurred.emit(f"Error analyzing component {requirement.title}: {str(e)}")
    
    def _analyze_single_layout(self, requirement: Requirement, original_text: str):
        """Analyze a single layout requirement in detail"""
        try:
            module_config = self.config.get_module_config("requirement_analyzer")
            model_config_name = module_config.model_config if module_config else self.config.get_app_setting("default_model")
            model = self.model_factory.get_model(model_config_name)
            
            self.streaming_text_updated.emit(tr("analyzing_layout_detail").format(title=requirement.title) + "\n")
            
            prompt = self.prompts['layout_analysis'].format(
                language_instruction=self._get_language_instruction(),
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
            
            # 解析详细需求分析结果并更新需求对象
            analysis_result = self._parse_detailed_analysis(response)
            
            if analysis_result:
                self._update_requirement_with_analysis(requirement, analysis_result)
                requirement.status = RequirementStatus.ANALYZED
                self.streaming_text_updated.emit("\n" + tr("layout_analysis_complete").format(title=requirement.title) + "\n\n")
            else:
                requirement.status = RequirementStatus.INCOMPLETE
                self.streaming_text_updated.emit("\n" + tr("layout_analysis_failed").format(title=requirement.title) + "\n\n")
                
        except Exception as e:
            self.error_occurred.emit(f"Error analyzing layout {requirement.title}: {str(e)}")
    
    def _analyze_single_interaction(self, requirement: Requirement, original_text: str):
        """Analyze a single interaction requirement in detail"""
        try:
            module_config = self.config.get_module_config("requirement_analyzer")
            model_config_name = module_config.model_config if module_config else self.config.get_app_setting("default_model")
            model = self.model_factory.get_model(model_config_name)
            
            self.streaming_text_updated.emit(tr("analyzing_interaction_detail").format(title=requirement.title) + "\n")
            
            prompt = self.prompts['interaction_analysis'].format(
                language_instruction=self._get_language_instruction(),
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
            
            # 解析详细需求分析结果并更新需求对象
            analysis_result = self._parse_detailed_analysis(response)
            
            if analysis_result:
                self._update_requirement_with_analysis(requirement, analysis_result)
                requirement.status = RequirementStatus.ANALYZED
                self.streaming_text_updated.emit("\n" + tr("interaction_analysis_complete").format(title=requirement.title) + "\n\n")
            else:
                requirement.status = RequirementStatus.INCOMPLETE
                self.streaming_text_updated.emit("\n" + tr("interaction_analysis_failed").format(title=requirement.title) + "\n\n")
                
        except Exception as e:
            self.error_occurred.emit(f"Error analyzing interaction {requirement.title}: {str(e)}")
    
    def _analyze_components(self, requirements: List[Requirement], original_text: str):
        """Analyze and add component specifications to requirements"""
        ui_requirements = [req for req in requirements if req.type == RequirementType.UI_COMPONENT]
        
        if not ui_requirements:
            self.streaming_text_updated.emit(tr("no_ui_components_found") + "\n\n")
            return
        
        try:
            # 使用模块配置指定的模型
            module_config = self.config.get_module_config("requirement_analyzer")
            model_config_name = module_config.model_config if module_config else self.config.get_app_setting("default_model")
            model = self.model_factory.get_model(model_config_name)
            
            self.streaming_text_updated.emit(tr("analyzing_ui_components").format(count=len(ui_requirements)) + "\n\n")
            
            for i, requirement in enumerate(ui_requirements, 1):
                self.streaming_text_updated.emit(tr("analyzing_component").format(current=i, total=len(ui_requirements), title=requirement.title) + "\n")
                
                prompt = self.prompts['component_extraction'].format(
                    language_instruction=self._get_language_instruction(),
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
                
                # 解析详细需求分析结果并更新需求对象
                analysis_result = self._parse_detailed_analysis(response)
                
                if analysis_result:
                    self._update_requirement_with_analysis(requirement, analysis_result)
                    requirement.status = RequirementStatus.ANALYZED
                    self.streaming_text_updated.emit("\n" + tr("component_analysis_complete").format(title=requirement.title) + "\n\n")
                else:
                    requirement.status = RequirementStatus.INCOMPLETE
                    self.streaming_text_updated.emit("\n" + tr("component_analysis_failed").format(title=requirement.title) + "\n\n")
                    # 记录调试信息
                    self.streaming_text_updated.emit(f"调试信息：AI响应内容：{response[:300]}...\n\n")
            
            self.streaming_text_updated.emit("="*50 + "\n\n")
                    
        except Exception as e:
            self.error_occurred.emit(f"Error analyzing components: {str(e)}")
    
    def _analyze_layout_and_interactions(self, requirements: List[Requirement], original_text: str):
        """Analyze layout and interaction requirements"""
        layout_requirements = [req for req in requirements if req.type == RequirementType.LAYOUT]
        interaction_requirements = [req for req in requirements if req.type == RequirementType.INTERACTION]
        
        try:
            # 使用模块配置指定的模型
            module_config = self.config.get_module_config("requirement_analyzer")
            model_config_name = module_config.model_config if module_config else self.config.get_app_setting("default_model")
            model = self.model_factory.get_model(model_config_name)
            
            # Analyze layout requirements
            for requirement in layout_requirements:
                prompt = self.prompts['layout_analysis'].format(
                    language_instruction=self._get_language_instruction(),
                    requirement_description=requirement.description,
                    original_text=original_text
                )
                
                response = model.generate(prompt)
                # 解析详细需求分析结果并更新需求对象
                analysis_result = self._parse_detailed_analysis(response)
                
                if analysis_result:
                    self._update_requirement_with_analysis(requirement, analysis_result)
            
            # Analyze interaction requirements
            for requirement in interaction_requirements:
                prompt = self.prompts['interaction_analysis'].format(
                    language_instruction=self._get_language_instruction(),
                    requirement_description=requirement.description,
                    original_text=original_text
                )
                
                response = model.generate(prompt)
                # 解析详细需求分析结果并更新需求对象
                analysis_result = self._parse_detailed_analysis(response)
                
                if analysis_result:
                    self._update_requirement_with_analysis(requirement, analysis_result)
                    
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
            # 清理响应文本
            cleaned_response = self._clean_json_response(response)
            
            if cleaned_response.startswith('{'):
                data = json.loads(cleaned_response)
                return LayoutSpec(
                    type=data.get('type', 'flow'),
                    sections=data.get('sections', []),
                    responsive=data.get('responsive', True),
                    breakpoints=data.get('breakpoints'),
                    spacing=data.get('spacing'),
                    alignment=data.get('alignment')
                )
            else:
                # 尝试从文本中提取JSON
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return LayoutSpec(
                        type=data.get('type', 'flow'),
                        sections=data.get('sections', []),
                        responsive=data.get('responsive', True),
                        breakpoints=data.get('breakpoints'),
                        spacing=data.get('spacing'),
                        alignment=data.get('alignment')
                    )
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            # 记录错误但不抛出异常
            print(f"Layout parsing error: {e}, response: {response[:200]}...")
        
        return None

    def _parse_interaction_specs(self, response: str) -> List[InteractionSpec]:
        """Parse interaction specifications from AI response"""
        specs = []
        
        try:
            # 清理响应文本
            cleaned_response = self._clean_json_response(response)
            
            data = None
            
            if cleaned_response.startswith('['):
                data = json.loads(cleaned_response)
            elif cleaned_response.startswith('{'):
                parsed_obj = json.loads(cleaned_response)
                if 'interactions' in parsed_obj:
                    data = parsed_obj['interactions']
                elif isinstance(parsed_obj, dict) and any(key in parsed_obj for key in ['trigger', 'action', 'target']):
                    # 单个交互对象
                    data = [parsed_obj]
            else:
                # 尝试从文本中提取JSON数组
                json_match = re.search(r'\[.*\]', cleaned_response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    # 尝试提取JSON对象
                    json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                    if json_match:
                        parsed_obj = json.loads(json_match.group())
                        if isinstance(parsed_obj, dict) and any(key in parsed_obj for key in ['trigger', 'action', 'target']):
                            data = [parsed_obj]
            
            if data and isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        spec = InteractionSpec(
                            trigger=item.get('trigger', ''),
                            action=item.get('action', ''),
                            target=item.get('target', ''),
                            conditions=item.get('conditions', []),
                            feedback=item.get('feedback'),
                            validation=item.get('validation')
                        )
                        specs.append(spec)
                
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            # 记录错误但不抛出异常
            print(f"Interaction parsing error: {e}, response: {response[:200]}...")
        
        return specs

    def _clean_json_response(self, response: str) -> str:
        """清理AI响应文本，移除markdown代码块标记和其他干扰内容"""
        if not response:
            return ""
        
        # 移除开头和结尾的空白
        cleaned = response.strip()
        
        # 移除markdown代码块标记
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        # 移除其他可能的前缀/后缀
        prefixes_to_remove = [
            '分析结果：', '分析结果:', 'Result:', 'result:', 
            '布局分析：', '布局分析:', 'Layout:', 'layout:',
            '交互分析：', '交互分析:', 'Interaction:', 'interaction:',
            'JSON:', 'json:', 'JSON格式：', 'JSON格式:'
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break
        
        # 清理结尾的说明文字
        suffixes_to_remove = [
            '以上是分析结果', '分析完成', 'Analysis complete', 'analysis complete'
        ]
        
        for suffix in suffixes_to_remove:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()
                break
        
        # 修复中文引号问题 - 智能处理嵌套引号
        cleaned = self._fix_chinese_quotes(cleaned)
        
        # 尝试提取纯JSON部分
        cleaned = self._extract_json_part(cleaned)
        
        return cleaned.strip()
    
    def _extract_json_part(self, text: str) -> str:
        """从文本中提取JSON部分"""
        import re
        
        # 如果已经是纯JSON，直接返回
        if (text.startswith('{') and text.endswith('}')) or (text.startswith('[') and text.endswith(']')):
            return text
        
        # 尝试提取JSON对象
        json_obj_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_obj_match:
            return json_obj_match.group().strip()
        
        # 尝试提取JSON数组
        json_arr_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_arr_match:
            return json_arr_match.group().strip()
        
        return text
    
    def _fix_chinese_quotes(self, text: str) -> str:
        """智能修复中文引号问题"""
        import re
        
        # 先统一转换所有中文引号为英文引号
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # 处理JSON中的控制字符
        # 移除或替换不合法的控制字符
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        # 规范化多个空格为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        # 专门修复常见的嵌套引号问题
        # 直接字符串替换方式修复已知问题
        text = text.replace(
            '"在输入框下方显示红色提示"任务内容不能为空""',
            '"在输入框下方显示红色提示\\"任务内容不能为空\\""'
        )
        
        return text
    
    def _identify_gaps(self, requirements: List[Requirement], original_text: str) -> List[str]:
        """Identify missing information in requirements"""
        gaps = []
        
        # Check for common missing elements
        has_ui_components = any(req.type == RequirementType.UI_COMPONENT for req in requirements)
        has_layout = any(req.type == RequirementType.LAYOUT for req in requirements)
        has_styling = any(req.type == RequirementType.STYLING for req in requirements)
        has_interactions = any(req.type == RequirementType.INTERACTION for req in requirements)
        
        language = self.config.get_app_setting("language", "zh_CN")
        
        if not has_ui_components:
            gaps.append(tr("gap_no_ui_components"))
        if not has_layout:
            gaps.append(tr("gap_no_layout"))
        if not has_styling:
            gaps.append(tr("gap_no_styling"))
        if not has_interactions:
            gaps.append(tr("gap_no_interactions"))
        
        # Check for incomplete requirements
        for req in requirements:
            if not req.description.strip():
                gaps.append(tr("gap_missing_description").format(title=req.title))
            if not req.acceptance_criteria:
                gaps.append(tr("gap_missing_acceptance_criteria").format(title=req.title))
        
        return gaps
    
    def _identify_ambiguities(self, requirements: List[Requirement]) -> List[str]:
        """Identify ambiguous or unclear requirements"""
        ambiguities = []
        language = self.config.get_app_setting("language", "zh_CN")
        
        # Look for vague language
        vague_words_en = ['somehow', 'maybe', 'probably', 'might', 'could', 'should probably']
        vague_words_zh = ['可能', '也许', '大概', '或许', '应该可能', '某种程度上']
        
        for req in requirements:
            text = (req.title + ' ' + req.description).lower()
            
            # Check English vague words
            for word in vague_words_en:
                if word in text:
                    ambiguities.append(tr("ambiguity_vague_language").format(title=req.title, word=word))
                    req.status = RequirementStatus.AMBIGUOUS
                    break
            
            # Check Chinese vague words
            for word in vague_words_zh:
                if word in text:
                    ambiguities.append(tr("ambiguity_vague_language").format(title=req.title, word=word))
                    req.status = RequirementStatus.AMBIGUOUS
                    break
            
            # Check for contradictory requirements
            if ('simple' in text and 'complex' in text) or ('简单' in text and '复杂' in text):
                ambiguities.append(tr("ambiguity_contradictory").format(title=req.title))
        
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
        language = self.config.get_app_setting("language", "zh_CN")
        
        if gaps:
            recommendations.append(tr("recommendation_address_gaps"))
        
        if ambiguities:
            recommendations.append(tr("recommendation_clarify_ambiguities"))
        
        # Check requirement balance
        critical_count = len([req for req in requirements if req.priority == RequirementPriority.CRITICAL])
        total_count = len(requirements)
        
        if critical_count > total_count * 0.5:
            recommendations.append(tr("recommendation_reduce_critical"))
        
        if critical_count == 0:
            recommendations.append(tr("recommendation_identify_critical"))
        
        return recommendations
    
    def _get_language_instruction(self) -> str:
        """Get language instruction for AI prompts based on user's language setting"""
        language = self.config.get_app_setting("language", "zh_CN")
        
        if language == "zh_CN":
            return "请用中文回答。"
        elif language == "en_US":
            return "Please respond in English."
        else:
            return "Please respond in English."
    
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
        {language_instruction}
        
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
        {language_instruction}
        
        对UI组件需求进行详细的需求分析: "{requirement_title}"
        需求描述: {requirement_description}
        
        基于原始需求文档: {original_text}
        
        请从需求分析的角度深入分析这个UI组件需求，输出详细的需求规格说明。请返回JSON格式：
        
        {{
            "requirement_details": {{
                "detailed_description": "对该组件需求的详细描述，包括功能目的、使用场景、预期效果",
                "user_stories": [
                    "作为用户，我希望能够...",
                    "当我使用这个组件时，我期望..."
                ],
                "business_value": "这个组件为业务带来的价值和意义",
                "functional_requirements": [
                    "必须支持的具体功能点1",
                    "必须支持的具体功能点2"
                ],
                "non_functional_requirements": [
                    "性能要求：响应时间<300ms",
                    "可用性要求：支持键盘导航",
                    "兼容性要求：支持IE11+"
                ],
                "acceptance_criteria": [
                    "验收标准1：当用户点击按钮时，应该...",
                    "验收标准2：当输入无效数据时，应该显示...",
                    "验收标准3：在移动端访问时，组件应该..."
                ],
                "constraints": [
                    "设计约束：必须符合现有设计规范",
                    "技术约束：需要兼容现有框架",
                    "业务约束：不能超过预算限制"
                ],
                "assumptions": [
                    "假设用户已经登录系统",
                    "假设网络连接稳定"
                ],
                "dependencies": [
                    "依赖于用户认证模块",
                    "依赖于数据API接口"
                ],
                "risks": [
                    "风险1：复杂交互可能影响性能",
                    "风险2：浏览器兼容性问题"
                ]
            }},
            "layout_considerations": {{
                "description": "该组件在页面布局中的考虑因素",
                "placement": "组件在页面中的位置和作用",
                "responsive_needs": "响应式设计需求说明",
                "spacing_requirements": "与其他元素的间距要求"
            }},
            "ux_considerations": {{
                "usability": "易用性要求和考虑",
                "accessibility": "无障碍访问要求",
                "user_feedback": "用户反馈和状态提示需求",
                "error_handling": "错误处理和用户引导"
            }}
        }}
        
        注意：
        1. 专注于需求分析，不要涉及具体的技术实现细节
        2. 验收标准要具体、可测试、可衡量
        3. 考虑用户体验和业务价值
        4. 识别潜在的风险和依赖关系
        """
    
    def _get_layout_analysis_prompt(self) -> str:
        return """
        {language_instruction}
        
        对布局需求进行详细的需求分析: {requirement_description}
        
        基于原始需求文档: {original_text}
        
        请从需求分析的角度深入分析这个布局需求，输出详细的需求规格说明。请返回JSON格式：
        
        {{
            "requirement_details": {{
                "detailed_description": "对该布局需求的详细描述，包括布局目的、信息架构、用户流程",
                "user_stories": [
                    "作为用户，我希望页面布局能够...",
                    "当我浏览页面时，我期望信息组织..."
                ],
                "business_value": "这个布局设计为业务带来的价值",
                "functional_requirements": [
                    "必须清晰展示主要功能区域",
                    "必须支持快速导航和信息查找",
                    "必须适配不同设备屏幕"
                ],
                "acceptance_criteria": [
                    "验收标准1：在桌面端，主要内容区域应占据...",
                    "验收标准2：在移动端，导航菜单应该...",
                    "验收标准3：页面加载后，用户应该能够在3秒内找到..."
                ],
                "constraints": [
                    "设计约束：必须遵循既定的设计规范",
                    "内容约束：需要容纳特定数量的信息模块",
                    "技术约束：需要支持多种浏览器"
                ]
            }},
            "information_architecture": {{
                "content_hierarchy": "内容层级和重要性划分",
                "navigation_flow": "用户导航流程和路径",
                "content_grouping": "内容分组和关联关系"
            }},
            "responsive_requirements": {{
                "breakpoint_behavior": "不同断点下的布局行为需求",
                "content_priority": "内容在不同屏幕尺寸下的优先级",
                "interaction_adaptation": "交互方式在不同设备上的适配需求"
            }},
            "ux_requirements": {{
                "visual_hierarchy": "视觉层次和引导需求",
                "scan_patterns": "用户浏览模式和视觉流",
                "accessibility": "无障碍访问的布局要求"
            }}
        }}
        
        注意：
        1. 专注于布局的功能性和用户体验需求
        2. 不要涉及具体的CSS实现细节
        3. 考虑信息架构和用户认知
        4. 验收标准要基于用户行为和业务目标
        """
    
    def _get_styling_analysis_prompt(self) -> str:
        return """
        {language_instruction}
        
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
        {language_instruction}
        
        对交互需求进行详细的需求分析: {requirement_description}
        
        基于原始需求文档: {original_text}
        
        请从需求分析的角度深入分析这个交互需求，输出详细的需求规格说明。请返回JSON格式：
        
        {{
            "requirement_details": {{
                "detailed_description": "对该交互需求的详细描述，包括交互目的、使用场景、预期效果",
                "user_stories": [
                    "作为用户，当我执行某个操作时，我希望...",
                    "在特定情况下，系统应该提供..."
                ],
                "business_value": "这个交互设计为业务和用户带来的价值",
                "functional_requirements": [
                    "必须支持的交互功能点1",
                    "必须提供的用户反馈2"
                ],
                "acceptance_criteria": [
                    "验收标准1：当用户点击时，在200ms内应该显示...",
                    "验收标准2：当操作失败时，应该明确提示...",
                    "验收标准3：支持键盘操作，Tab键顺序应该..."
                ],
                "error_scenarios": [
                    "错误场景1：网络中断时的处理",
                    "错误场景2：无效输入的反馈"
                ]
            }},
            "interaction_flows": {{
                "primary_flow": "主要交互流程的详细步骤",
                "alternative_flows": "备选交互路径和分支",
                "edge_cases": "边界情况和异常处理"
            }},
            "feedback_requirements": {{
                "visual_feedback": "视觉反馈的需求说明",
                "audio_feedback": "音频反馈需求（如适用）",
                "haptic_feedback": "触觉反馈需求（如适用）",
                "timing_requirements": "反馈时机和持续时间要求"
            }},
            "accessibility_requirements": {{
                "keyboard_navigation": "键盘导航支持需求",
                "screen_reader": "屏幕阅读器支持需求",
                "motor_accessibility": "运动障碍用户的交互需求"
            }}
        }}
        
        注意：
        1. 专注于交互的功能需求和用户体验
        2. 不要涉及具体的JavaScript实现
        3. 考虑所有可能的用户操作路径
        4. 包含完整的错误处理需求
        """
    
    def _get_validation_prompt(self) -> str:
        return """
        {language_instruction}
        
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
    
    def _get_requirement_list_prompt(self) -> str:
        return """
        {language_instruction}
        
        分析以下需求文本，提取出完整的需求列表。这是第一阶段分析，专注于识别和分类所有需求项目，确保完整性。
        
        需求文本:
        {requirements_text}
        
        附加上下文:
        {context}
        
        目标平台: {platform}
        
        请返回一个JSON数组，包含所有识别出的需求项目。每个需求项目应该包含基本信息：
        [
            {{
                "id": "REQ-001",
                "title": "简明的需求标题",
                "description": "需求的详细描述",
                "type": "functional|ui_component|layout|styling|interaction|data|performance|accessibility|business",
                "priority": "critical|high|medium|low",
                "category": "核心功能|界面设计|数据处理|性能优化|其他",
                "brief_rationale": "为什么需要这个需求的简要说明"
            }}
        ]
        
        请确保：
        1. 提取出所有明确或隐含的需求
        2. 正确分类每个需求的类型
        3. 合理设置优先级
        4. 用简洁明确的语言描述每个需求
        5. 不要遗漏任何重要的功能或特性需求
        
        重点关注：
        - 功能需求（用户可以做什么）
        - UI组件需求（需要什么界面元素）
        - 布局需求（界面如何组织）
        - 交互需求（用户如何操作）
        - 数据需求（需要处理什么数据）
        - 性能需求（速度、响应时间等）
        - 业务需求（业务逻辑和规则）
        """

    def _parse_detailed_analysis(self, response: str) -> Optional[Dict[str, Any]]:
        """解析详细需求分析的JSON响应"""
        try:
            # 清理响应，移除markdown代码块标记
            cleaned_response = response.strip()
            
            # 移除 ```json 和 ``` 标记
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            
            cleaned_response = cleaned_response.strip()
            
            # 解析JSON
            if cleaned_response.startswith('{'):
                data = json.loads(cleaned_response)
                return data
            else:
                # 如果不是JSON格式，尝试从文本中提取信息
                return self._extract_analysis_from_text(response)
                
        except json.JSONDecodeError as e:
            # JSON解析失败，尝试文本解析
            return self._extract_analysis_from_text(response)
        except Exception as e:
            self.error_occurred.emit(f"Error parsing detailed analysis: {str(e)}")
            return None
    
    def _extract_analysis_from_text(self, text: str) -> Dict[str, Any]:
        """从文本中提取分析信息的回退方法"""
        # 简单的文本解析，提取关键信息
        result = {
            "requirement_details": {
                "detailed_description": "",
                "user_stories": [],
                "business_value": "",
                "functional_requirements": [],
                "acceptance_criteria": [],
                "constraints": [],
                "assumptions": [],
                "dependencies": [],
                "risks": []
            }
        }
        
        # 尝试提取描述信息
        lines = text.split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 识别不同的段落
            if "详细描述" in line or "描述" in line:
                current_section = "description"
            elif "用户故事" in line or "用户需求" in line:
                current_section = "user_stories"
            elif "验收标准" in line or "验收条件" in line:
                current_section = "acceptance_criteria"
            elif "业务价值" in line:
                current_section = "business_value"
            elif "功能需求" in line:
                current_section = "functional_requirements"
            elif "约束" in line:
                current_section = "constraints"
            elif "依赖" in line:
                current_section = "dependencies"
            elif "风险" in line:
                current_section = "risks"
            else:
                # 内容行
                if current_section == "description" and result["requirement_details"]["detailed_description"] == "":
                    result["requirement_details"]["detailed_description"] = line
                elif current_section in ["user_stories", "acceptance_criteria", "functional_requirements", "constraints", "dependencies", "risks"]:
                    if line.startswith(('- ', '• ', '1. ', '2. ', '3. ')):
                        result["requirement_details"][current_section].append(line[2:].strip())
                    elif line:
                        result["requirement_details"][current_section].append(line)
                elif current_section == "business_value" and result["requirement_details"]["business_value"] == "":
                    result["requirement_details"]["business_value"] = line
        
        return result
    
    def _update_requirement_with_analysis(self, requirement: Requirement, analysis_result: Dict[str, Any]):
        """使用详细分析结果更新需求对象"""
        try:
            req_details = analysis_result.get("requirement_details", {})
            
            # 更新详细描述
            if req_details.get("detailed_description"):
                requirement.description = req_details["detailed_description"]
            
            # 更新业务理由
            if req_details.get("business_value"):
                requirement.rationale = req_details["business_value"]
            
            # 更新验收标准
            if req_details.get("acceptance_criteria"):
                requirement.acceptance_criteria = req_details["acceptance_criteria"]
            
            # 更新依赖关系（转换为字符串列表）
            if req_details.get("dependencies"):
                # 这里暂时存储为描述性文本，实际项目中可能需要解析为具体的需求ID
                requirement.dependencies = [str(dep) for dep in req_details["dependencies"]]
            
            # 在source字段中记录用户故事
            if req_details.get("user_stories"):
                user_stories_text = "\n".join([f"- {story}" for story in req_details["user_stories"]])
                requirement.source = f"用户故事:\n{user_stories_text}"
            
            # 在tags中添加风险和约束信息
            if req_details.get("risks"):
                for risk in req_details["risks"]:
                    requirement.tags.append(f"风险: {risk}")
            
            if req_details.get("constraints"):
                for constraint in req_details["constraints"]:
                    requirement.tags.append(f"约束: {constraint}")
            
            # 如果有布局考虑，创建布局规格对象
            if "layout_considerations" in analysis_result:
                layout_info = analysis_result["layout_considerations"]
                requirement.layout_spec = LayoutSpec(
                    type="custom",
                    sections=[],
                    responsive=True,
                    breakpoints={},
                    spacing={},
                    alignment={}
                )
            
            # 如果有UX考虑，可以记录在其他字段中
            if "ux_considerations" in analysis_result:
                ux_info = analysis_result["ux_considerations"]
                # 将UX考虑作为非功能性需求添加到验收标准中
                if ux_info.get("usability"):
                    requirement.acceptance_criteria.append(f"易用性要求: {ux_info['usability']}")
                if ux_info.get("accessibility"):
                    requirement.acceptance_criteria.append(f"无障碍要求: {ux_info['accessibility']}")
            
            # 更新时间戳
            requirement.updated_at = datetime.now()
            
        except Exception as e:
            self.error_occurred.emit(f"Error updating requirement with analysis: {str(e)}")