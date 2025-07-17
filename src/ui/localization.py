"""
Localization system for UI Easy application
"""

import json
import os
from typing import Dict, Any

class Localization:
    """Manages localization for the application"""
    
    def __init__(self, language: str = "zh_CN"):
        self.language = language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.current_translations: Dict[str, str] = {}
        self.load_translations()
    
    def load_translations(self):
        """Load translation dictionaries"""
        # Define translations inline for now
        self.translations = {
            "zh_CN": {
                # Window title
                "window_title": "UI Easy - AI驱动的设计工具",
                "main_title": "UI Easy - 专业设计分析工具",
                
                # Tabs
                "tab_image_analyzer": "图像分析器",
                "tab_requirement_analyzer": "需求分析器", 
                "tab_prototype_generator": "原型生成器",
                "tab_settings": "设置",
                
                # Image Analyzer
                "image_selection": "图像选择",
                "select_image": "选择设计图像",
                "no_image_selected": "未选择图像",
                "analysis_options": "分析选项",
                "analysis_type": "分析类型:",
                "full_analysis": "完整分析",
                "layout_only": "仅布局",
                "colors_only": "仅颜色",
                "components_only": "仅组件",
                "analyze_design": "分析设计",
                "progress": "进度",
                "ready": "就绪",
                "analysis_results": "分析结果",
                "analysis_placeholder": "分析结果将在此处显示...",
                "export_json": "导出 JSON",
                "export_txt": "导出文本",
                
                # Requirement Analyzer
                "requirements_input": "需求输入",
                "requirements_text": "需求文本:",
                "requirements_placeholder": "在此输入您的需求...\n\n示例:\n我需要一个任务管理系统，包含：\n1. 用户登录功能\n2. 创建和编辑任务\n3. 任务列表显示\n4. 任务状态管理",
                "additional_context": "附加上下文 (可选):",
                "context_placeholder": "提供关于您项目的附加上下文...",
                "target_platform": "目标平台:",
                "analyze_requirements": "分析需求",
                "analysis_progress": "分析进度",
                "overview": "概览",
                "requirements": "需求",
                "components": "组件",
                "quality_recommendations": "质量与建议",
                "filter_by_type": "按类型过滤:",
                "priority": "优先级:",
                "export_report": "导出报告",
                
                # Settings
                "app_settings": "应用设置",
                "model_config": "模型配置 (Model Configuration)",
                "model_config_desc": "配置不同的 AI 模型以用于图像分析和需求分析。至少需要配置一个模型。",
                "select_model": "选择模型:",
                "add_model": "添加模型",
                "delete_model": "删除模型",
                "model_details": "模型详细配置",
                "model_name": "模型名称:",
                "provider": "提供商:",
                "api_key": "API 密钥:",
                "base_url": "基础 URL:",
                "model_id": "模型 ID:",
                "max_tokens": "最大令牌数:",
                "temperature": "温度:",
                "timeout": "超时 (秒):",
                "update_model": "更新模型配置",
                "module_config": "模块配置 (Module Configuration)",
                "module_config_desc": "为每个分析模块配置相关设置，选择使用的模型和自定义提示。",
                "select_module": "选择模块:",
                "enable_module": "启用模块:",
                "use_model": "使用模型:",
                "custom_prompts": "自定义提示 (可选):",
                "prompt_placeholder": "输入自定义提示词...",
                "update_module": "更新模块配置",
                "app_settings_title": "应用设置 (Application Settings)",
                "ui_language": "界面语言:",
                "default_analysis_type": "默认分析类型:",
                "auto_save_results": "自动保存结果:",
                "default_export_format": "默认导出格式:",
                "test_config": "测试配置",
                "save_settings": "保存设置",
                "reload_settings": "重新加载设置",
                
                # Messages
                "success": "成功",
                "error": "错误",
                "warning": "警告",
                "settings_saved": "设置已保存！",
                "settings_loaded": "设置已重新加载！",
                "model_updated": "模型配置已更新！",
                "module_updated": "模块配置已更新！",
                "config_error": "配置错误",
                "api_key_required": "请在设置中配置 API 密钥后再分析",
                "select_image_first": "请先选择图像",
                "enter_requirements": "请先输入需求文本",
                "model_name_required": "模型名称不能为空！",
                "api_key_empty": "API 密钥不能为空！",
                "model_exists": "模型名称已存在！",
                "confirm_delete": "确认删除",
                "confirm_delete_model": "确定要删除模型配置吗？",
                "enter_model_name": "输入模型名称:",
                "add_model_title": "添加模型",
                "analysis_failed": "分析失败",
                "analysis_completed": "分析完成",
                "export_success": "导出成功",
                "export_failed": "导出失败",
                
                # Status messages
                "analyzing_image": "正在分析图像，请稍候...",
                "analyzing_requirements": "正在分析需求，请稍候...",
                "analysis_complete": "分析完成",
                "analysis_type_label": "分析类型",
                "timestamp": "时间戳",
                "model_used": "使用模型",
                "confidence": "置信度",
                
                # Filters
                "all": "全部",
                "functional": "功能性",
                "ui_component": "UI 组件",
                "layout": "布局",
                "styling": "样式",
                "interaction": "交互",
                "data": "数据",
                "performance": "性能",
                "accessibility": "可访问性",
                "business": "业务",
                "critical": "关键",
                "high": "高",
                "medium": "中",
                "low": "低",
                
                # Platforms
                "web": "网页",
                "mobile": "移动端",
                "desktop": "桌面端",
                
                # Export formats
                "json": "JSON",
                "txt": "文本",
                "both": "两者",
                
                # Prototype generator
                "prototype_coming_soon": "原型生成器 - 即将推出",
                
                # Additional UI elements that need localization
                "image_files": "图像文件 (*.png *.jpg *.jpeg *.gif *.bmp)",
                "select_design_image": "选择设计图像",
                "configuration_test_results": "配置测试结果",
                "test_results": "测试结果",
                "successful_models": "成功配置的模型",
                "configuration_issues": "配置问题",
                "module_status": "模块状态",
                "enabled_using_model": "已启用，使用模型",
                "enabled_invalid_model": "已启用但模型配置无效",
                "disabled": "已禁用",
                "missing_api_key": "缺少 API 密钥",
                "openai_needs_model_id": "OpenAI 模型需要指定 model_id",
                "deepseek_needs_base_url": "DeepSeek 模型需要指定 base_url",
                "config_test_error": "测试配置时出错",
                "failed_load_initial_settings": "加载初始设置失败",
                "failed_save_settings": "保存设置失败",
                "failed_update_ui_language": "更新UI语言失败",
                "auto_save_failed": "自动保存失败",
                "display_error": "显示错误",
                "failed_display_results": "显示结果失败",
                "export_requirements_as_json": "导出需求分析为 JSON",
                "export_requirements_report": "导出需求报告",
                "requirements_analysis": "需求分析",
                "requirements_report": "需求报告",
                "export_analysis_as_json": "导出分析为 JSON",
                "export_analysis_as_text": "导出分析为文本",
                "analysis_result": "分析结果",
                "warning": "警告",
                "confirm": "确认",
                "cancel": "取消",
                "yes": "是",
                "no": "否",
                "ok": "确定",
                "failed_to_load_image": "加载图像失败",
                "failed_to_export": "导出失败",
                "export_error": "导出错误",
                "analysis_error": "分析错误",
                "failed_load_settings": "加载设置失败",
                "analysis_overview": "分析概述",
                "requirements_list": "需求列表",
                "items": "项",
                "component_specifications": "组件规格",
                "no_ui_components": "需求中未识别到UI组件",
                "component": "组件",
                "description": "描述",
                "type": "类型",
                "name": "名称",
                "properties": "属性",
                "events": "事件",
                "validation": "验证",
                "accessibility": "可访问性",
                "quality_analysis": "质量分析",
                "analysis_scores": "分析得分",
                "completeness_score": "完整性得分",
                "clarity_score": "清晰度得分",
                "feasibility_score": "可行性得分",
                "identified_gaps": "识别的差距",
                "ambiguities_clarify": "需要澄清的模糊点",
                "recommendations": "建议",
                "development_phases": "开发阶段",
                "duration": "持续时间",
                "title": "标题",
                "status": "状态",
                "acceptance_criteria": "验收标准",
                "estimated_effort": "预估工作量",
                "rationale": "基础原理",
                "project_overview": "项目概述",
                "target_audience": "目标用户",
                "quality_scores": "质量评分",
                "completeness": "完整性",
                "clarity": "清晰度",
                "feasibility": "可行性",
                "development_estimation": "开发预估",
                "recommended_frameworks": "推荐框架",
                "analysis_summary": "分析结果摘要",
                "analyzing_image_please_wait": "正在分析图像，请稍候...",
                "analyzing_requirements_please_wait": "正在分析需求，请稍候...",
                "analysis_completed_meta": "分析完成",
                "analysis_type_meta": "分析类型",
                "timestamp_meta": "时间戳",
                "model_used_meta": "使用模型",
                "confidence_meta": "置信度",
                "unknown": "未知",
                "na": "不适用",
            },
            "en_US": {
                # Window title
                "window_title": "UI Easy - AI-Powered Design Tool",
                "main_title": "UI Easy - Professional Design Analysis Tool",
                
                # Tabs
                "tab_image_analyzer": "Image Analyzer",
                "tab_requirement_analyzer": "Requirement Analyzer",
                "tab_prototype_generator": "Prototype Generator",
                "tab_settings": "Settings",
                
                # Image Analyzer
                "image_selection": "Image Selection",
                "select_image": "Select Design Image",
                "no_image_selected": "No image selected",
                "analysis_options": "Analysis Options",
                "analysis_type": "Analysis Type:",
                "full_analysis": "Full Analysis",
                "layout_only": "Layout Only",
                "colors_only": "Colors Only",
                "components_only": "Components Only",
                "analyze_design": "Analyze Design",
                "progress": "Progress",
                "ready": "Ready",
                "analysis_results": "Analysis Results",
                "analysis_placeholder": "Analysis results will appear here...",
                "export_json": "Export JSON",
                "export_txt": "Export Text",
                
                # Requirement Analyzer
                "requirements_input": "Requirements Input",
                "requirements_text": "Requirements Text:",
                "requirements_placeholder": "Enter your requirements here...\n\nExample:\nI need a task management system with:\n1. User login functionality\n2. Create and edit tasks\n3. Task list display\n4. Task status management",
                "additional_context": "Additional Context (Optional):",
                "context_placeholder": "Provide additional context about your project...",
                "target_platform": "Target Platform:",
                "analyze_requirements": "Analyze Requirements",
                "analysis_progress": "Analysis Progress",
                "overview": "Overview",
                "requirements": "Requirements",
                "components": "Components",
                "quality_recommendations": "Quality & Recommendations",
                "filter_by_type": "Filter by Type:",
                "priority": "Priority:",
                "export_report": "Export Report",
                
                # Settings
                "app_settings": "Application Settings",
                "model_config": "Model Configuration",
                "model_config_desc": "Configure different AI models for image analysis and requirement analysis. At least one model must be configured.",
                "select_model": "Select Model:",
                "add_model": "Add Model",
                "delete_model": "Delete Model",
                "model_details": "Model Detail Configuration",
                "model_name": "Model Name:",
                "provider": "Provider:",
                "api_key": "API Key:",
                "base_url": "Base URL:",
                "model_id": "Model ID:",
                "max_tokens": "Max Tokens:",
                "temperature": "Temperature:",
                "timeout": "Timeout (seconds):",
                "update_model": "Update Model Configuration",
                "module_config": "Module Configuration",
                "module_config_desc": "Configure settings for each analysis module, select models to use and custom prompts.",
                "select_module": "Select Module:",
                "enable_module": "Enable Module:",
                "use_model": "Use Model:",
                "custom_prompts": "Custom Prompts (Optional):",
                "prompt_placeholder": "Enter custom prompts...",
                "update_module": "Update Module Configuration",
                "app_settings_title": "Application Settings",
                "ui_language": "UI Language:",
                "default_analysis_type": "Default Analysis Type:",
                "auto_save_results": "Auto-save Results:",
                "default_export_format": "Default Export Format:",
                "test_config": "Test Configuration",
                "save_settings": "Save Settings",
                "reload_settings": "Reload Settings",
                
                # Messages
                "success": "Success",
                "error": "Error",
                "warning": "Warning",
                "settings_saved": "Settings saved!",
                "settings_loaded": "Settings reloaded!",
                "model_updated": "Model configuration updated!",
                "module_updated": "Module configuration updated!",
                "config_error": "Configuration Error",
                "api_key_required": "Please configure API key in settings before analyzing",
                "select_image_first": "Please select an image first",
                "enter_requirements": "Please enter requirements text first",
                "model_name_required": "Model name cannot be empty!",
                "api_key_empty": "API key cannot be empty!",
                "model_exists": "Model name already exists!",
                "confirm_delete": "Confirm Delete",
                "confirm_delete_model": "Are you sure you want to delete this model configuration?",
                "enter_model_name": "Enter model name:",
                "add_model_title": "Add Model",
                "analysis_failed": "Analysis failed",
                "analysis_completed": "Analysis completed",
                "export_success": "Export successful",
                "export_failed": "Export failed",
                
                # Status messages
                "analyzing_image": "Analyzing image, please wait...",
                "analyzing_requirements": "Analyzing requirements, please wait...",
                "analysis_complete": "Analysis complete",
                "analysis_type_label": "Analysis Type",
                "timestamp": "Timestamp",
                "model_used": "Model Used",
                "confidence": "Confidence",
                
                # Filters
                "all": "All",
                "functional": "Functional",
                "ui_component": "UI Component",
                "layout": "Layout",
                "styling": "Styling",
                "interaction": "Interaction",
                "data": "Data",
                "performance": "Performance",
                "accessibility": "Accessibility",
                "business": "Business",
                "critical": "Critical",
                "high": "High",
                "medium": "Medium",
                "low": "Low",
                
                # Platforms
                "web": "Web",
                "mobile": "Mobile",
                "desktop": "Desktop",
                
                # Export formats
                "json": "JSON",
                "txt": "Text",
                "both": "Both",
                
                # Prototype generator
                "prototype_coming_soon": "Prototype Generator - Coming Soon",
                
                # Additional UI elements that need localization
                "image_files": "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)",
                "select_design_image": "Select Design Image",
                "configuration_test_results": "Configuration Test Results",
                "test_results": "Test Results",
                "successful_models": "Successfully Configured Models",
                "configuration_issues": "Configuration Issues",
                "module_status": "Module Status",
                "enabled_using_model": "Enabled, using model",
                "enabled_invalid_model": "Enabled but invalid model configuration",
                "disabled": "Disabled",
                "missing_api_key": "Missing API key",
                "openai_needs_model_id": "OpenAI models require model_id",
                "deepseek_needs_base_url": "DeepSeek models require base_url",
                "config_test_error": "Error testing configuration",
                "failed_load_initial_settings": "Failed to load initial settings",
                "failed_save_settings": "Failed to save settings",
                "failed_update_ui_language": "Failed to update UI language",
                "auto_save_failed": "Auto-save failed",
                "display_error": "Display Error",
                "failed_display_results": "Failed to display results",
                "export_requirements_as_json": "Export Requirements Analysis as JSON",
                "export_requirements_report": "Export Requirements Report",
                "requirements_analysis": "Requirements Analysis",
                "requirements_report": "Requirements Report",
                "export_analysis_as_json": "Export Analysis as JSON",
                "export_analysis_as_text": "Export Analysis as Text",
                "analysis_result": "Analysis Result",
                "warning": "Warning",
                "confirm": "Confirm",
                "cancel": "Cancel",
                "yes": "Yes",
                "no": "No",
                "ok": "OK",
                "failed_to_load_image": "Failed to load image",
                "failed_to_export": "Failed to export",
                "export_error": "Export Error",
                "analysis_error": "Analysis Error",
                "failed_load_settings": "Failed to load settings",
                "analysis_overview": "Analysis Overview",
                "requirements_list": "Requirements List",
                "items": "items",
                "component_specifications": "Component Specifications",
                "no_ui_components": "No UI components identified in the requirements",
                "component": "Component",
                "description": "Description",
                "type": "Type",
                "name": "Name",
                "properties": "Properties",
                "events": "Events",
                "validation": "Validation",
                "accessibility": "Accessibility",
                "quality_analysis": "Quality Analysis",
                "analysis_scores": "Analysis Scores",
                "completeness_score": "Completeness Score",
                "clarity_score": "Clarity Score",
                "feasibility_score": "Feasibility Score",
                "identified_gaps": "Identified Gaps",
                "ambiguities_clarify": "Ambiguities to Clarify",
                "recommendations": "Recommendations",
                "development_phases": "Development Phases",
                "duration": "Duration",
                "title": "Title",
                "status": "Status",
                "acceptance_criteria": "Acceptance Criteria",
                "estimated_effort": "Estimated Effort",
                "rationale": "Rationale",
                "project_overview": "Project Overview",
                "target_audience": "Target Audience",
                "quality_scores": "Quality Scores",
                "completeness": "Completeness",
                "clarity": "Clarity",
                "feasibility": "Feasibility",
                "development_estimation": "Development Estimation",
                "recommended_frameworks": "Recommended Frameworks",
                "analysis_summary": "Analysis Summary",
                "analyzing_image_please_wait": "Analyzing image, please wait...",
                "analyzing_requirements_please_wait": "Analyzing requirements, please wait...",
                "analysis_completed_meta": "Analysis completed",
                "analysis_type_meta": "Analysis Type",
                "timestamp_meta": "Timestamp",
                "model_used_meta": "Model Used",
                "confidence_meta": "Confidence",
                "unknown": "Unknown",
                "na": "N/A",
            }
        }
        
        # Set current translations
        self.set_language(self.language)
    
    def set_language(self, language: str):
        """Set the current language"""
        self.language = language
        self.current_translations = self.translations.get(language, self.translations.get("zh_CN", {}))
    
    def tr(self, key: str, default: str = None) -> str:
        """Translate a key to the current language"""
        if default is None:
            default = key
        return self.current_translations.get(key, default)
    
    def get_languages(self) -> list:
        """Get available languages"""
        return list(self.translations.keys())

# Global localization instance
_localization = Localization()

def tr(key: str, default: str = None) -> str:
    """Global translation function"""
    return _localization.tr(key, default)

def set_language(language: str):
    """Set global language"""
    _localization.set_language(language)

def get_languages() -> list:
    """Get available languages"""
    return _localization.get_languages()