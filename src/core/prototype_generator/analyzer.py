"""
Prototype Generator for creating interactive prototypes from various inputs
"""

import json
from typing import Dict, Any, Optional, List
from PyQt5.QtCore import QObject, pyqtSignal

from core.base_module import BaseModule
from models.model_factory import ModelFactory


class PrototypeInput:
    """Represents an input source for prototype generation"""
    
    def __init__(self, input_type: str, content: str, name: str = ""):
        self.input_type = input_type  # 'text', 'image_analysis', 'requirement_analysis'
        self.content = content
        self.name = name or f"{input_type}_input"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_type": self.input_type,
            "content": self.content,
            "name": self.name
        }


class PrototypeResult:
    """Results from prototype generation"""
    
    def __init__(self):
        self.html_code = ""
        self.css_code = ""
        self.js_code = ""
        self.component_structure = []
        self.design_rationale = ""
        self.implementation_notes = []
        self.preview_available = False
        self.metadata = {}
        # 新增分步骤生成状态
        self.generation_steps = {
            'framework': False,
            'components': False,
            'styling': False,
            'interactions': False,
            'finalization': False
        }
        self.step_results = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "html_code": self.html_code,
            "css_code": self.css_code,
            "js_code": self.js_code,
            "component_structure": self.component_structure,
            "design_rationale": self.design_rationale,
            "implementation_notes": self.implementation_notes,
            "preview_available": self.preview_available,
            "metadata": self.metadata,
            "generation_steps": self.generation_steps,
            "step_results": self.step_results
        }


class PrototypeGenerator(BaseModule):
    """Generator for interactive prototypes from multiple input sources"""
    
    # Signals
    prototype_generated = pyqtSignal(dict)
    preview_ready = pyqtSignal(str)  # HTML content for preview
    step_completed = pyqtSignal(str, dict)  # step_name, step_result
    
    def __init__(self, config):
        super().__init__("prototype_generator", config)
        self.inputs = []  # List of PrototypeInput objects
        self.current_result = None
        self.model_factory = ModelFactory(config)
        self.generation_context = {}  # 保存生成上下文，避免重复
    
    def add_input(self, input_type: str, content: str, name: str = "") -> None:
        """Add an input source for prototype generation"""
        input_obj = PrototypeInput(input_type, content, name)
        self.inputs.append(input_obj)
        self.status_updated.emit(f"已添加输入: {input_obj.name}")
    
    def remove_input(self, index: int) -> None:
        """Remove an input source by index"""
        if 0 <= index < len(self.inputs):
            removed = self.inputs.pop(index)
            self.status_updated.emit(f"已移除输入: {removed.name}")
    
    def clear_inputs(self) -> None:
        """Clear all input sources"""
        self.inputs.clear()
        self.status_updated.emit("已清除所有输入")
    
    def get_inputs_summary(self) -> List[Dict[str, str]]:
        """Get summary of all current inputs"""
        return [
            {
                "index": str(i),
                "name": inp.name,
                "type": inp.input_type,
                "content_preview": inp.content[:100] + "..." if len(inp.content) > 100 else inp.content
            }
            for i, inp in enumerate(self.inputs)
        ]
    
    def process(self, input_data: Dict[str, Any]) -> PrototypeResult:
        """
        Process inputs and generate prototype using enhanced multi-step approach
        
        Args:
            input_data: Dictionary containing:
                - inputs: List of input objects (optional, uses self.inputs if not provided)
                - prototype_type: 'web', 'mobile', 'desktop'
                - framework: 'html_css_js', 'react', 'vue', 'angular'
                - style_framework: 'bootstrap', 'tailwind', 'custom'
                - responsive: boolean
                - accessibility: boolean
                - realtime_preview: boolean (新增，是否启用实时预览)
        """
        try:
            self.progress_updated.emit(5)
            self.status_updated.emit("开始分步骤生成原型...")
            
            # Use provided inputs or current inputs
            inputs_to_process = input_data.get('inputs', self.inputs)
            if not inputs_to_process:
                raise ValueError("没有可用的输入源")
            
            prototype_type = input_data.get('prototype_type', 'web')
            framework = input_data.get('framework', 'html_css_js')
            style_framework = input_data.get('style_framework', 'bootstrap')
            responsive = input_data.get('responsive', True)
            accessibility = input_data.get('accessibility', True)
            realtime_preview = input_data.get('realtime_preview', True)
            
            result = PrototypeResult()
            
            # 保存生成上下文
            self.generation_context = {
                'inputs': inputs_to_process,
                'prototype_type': prototype_type,
                'framework': framework,
                'style_framework': style_framework,
                'responsive': responsive,
                'accessibility': accessibility,
                'realtime_preview': realtime_preview
            }
            
            # Step 1: 生成整体框架和设计理念 (10-25%)
            self.progress_updated.emit(10)
            self.status_updated.emit("📋 第1步: 生成框架设计...")
            framework_result = self._generate_framework_design(inputs_to_process, prototype_type, framework, style_framework)
            result.design_rationale = framework_result['design_rationale']
            result.component_structure = framework_result['components']
            result.generation_steps['framework'] = True
            result.step_results['framework'] = framework_result
            
            # 保存设计系统信息到生成上下文
            self.generation_context['design_system'] = framework_result.get('design_system', '')
            
            if realtime_preview:
                self._emit_step_preview(result, 'framework')
            
            # Step 2: 生成HTML结构框架 (25-40%)
            self.progress_updated.emit(25)
            self.status_updated.emit("🏗️ 第2步: 构建HTML结构...")
            html_result = self._generate_html_structure(result.component_structure, framework)
            result.html_code = html_result['html_code']
            result.generation_steps['components'] = True
            result.step_results['components'] = html_result
            
            if realtime_preview:
                self._emit_step_preview(result, 'components')
            
            # Step 3: 生成CSS样式 (40-65%)
            self.progress_updated.emit(40)
            self.status_updated.emit("🎨 第3步: 设计样式系统...")
            css_result = self._generate_css_styling(result.component_structure, style_framework, responsive, accessibility)
            result.css_code = css_result['css_code']
            result.generation_steps['styling'] = True
            result.step_results['styling'] = css_result
            
            if realtime_preview:
                self._emit_step_preview(result, 'styling')
            
            # Step 4: 生成JavaScript交互 (65-85%)
            self.progress_updated.emit(65)
            self.status_updated.emit("⚡ 第4步: 实现交互功能...")
            js_result = self._generate_javascript_interactions(result.component_structure, framework)
            result.js_code = js_result['js_code']
            result.generation_steps['interactions'] = True
            result.step_results['interactions'] = js_result
            
            if realtime_preview:
                self._emit_step_preview(result, 'interactions')
            
            # Step 5: 完善和优化 (85-100%)
            self.progress_updated.emit(85)
            self.status_updated.emit("✨ 第5步: 完善整合...")
            final_result = self._finalize_prototype(result)
            result.implementation_notes = final_result['implementation_notes']
            result.generation_steps['finalization'] = True
            result.step_results['finalization'] = final_result
            
            # Finalize result
            result.preview_available = bool(result.html_code.strip())
            result.metadata = {
                'generated_at': self._get_timestamp(),
                'input_count': len(inputs_to_process),
                'prototype_type': prototype_type,
                'framework': framework,
                'style_framework': style_framework,
                'steps_completed': len([s for s in result.generation_steps.values() if s])
            }
            
            self.progress_updated.emit(100)
            self.status_updated.emit("✅ 原型生成完成")
            
            self.current_result = result
            
            # 发送最终预览
            if realtime_preview:
                self._emit_final_preview(result)
            
            return result
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            raise
    
    def _generate_framework_design(self, inputs: List[PrototypeInput], 
                                  prototype_type: str, framework: str,
                                  style_framework: str) -> Dict[str, Any]:
        """第1步：生成整体框架设计和组件结构"""
        
        prompt = f"""你是一个专业的UI/UX架构师。请基于以下需求，设计一个完整的设计系统和组件架构。

## 需求分析

"""
        
        # Add each input to the prompt
        for i, inp in enumerate(inputs, 1):
            prompt += f"""
### 需求 {i}: {inp.name} ({inp.input_type})
{inp.content}

"""
        
        prompt += f"""
## 技术栈

- **原型类型**: {prototype_type}
- **技术框架**: {framework}
- **样式框架**: {style_framework}

## 设计要求

请设计一个完整的设计系统，确保所有组件风格统一、视觉协调。

### 1. 设计系统定义

请先定义设计系统的核心要素：

**色彩系统**：
- 主色调（Primary）：[选择一个主色]
- 辅助色（Secondary）：[选择辅助色]
- 功能色（Success/Warning/Error）：[定义功能色]
- 中性色（灰度系统）：[定义灰度层次]

**字体系统**：
- 主字体：[选择字体族]
- 字体尺寸比例：[定义尺寸层次]
- 字重定义：[定义字重使用场景]

**间距系统**：
- 基础间距单位：[如8px基础单位]
- 间距比例：[4, 8, 16, 24, 32, 48, 64px等]

**圆角系统**：
- 小圆角：[如4px]
- 中圆角：[如8px]
- 大圆角：[如16px]

**阴影系统**：
- 轻微阴影：[卡片悬浮]
- 中等阴影：[弹窗]
- 重度阴影：[模态框]

### 2. 组件架构

基于上述设计系统，列出所需组件：

格式：组件名称|组件类型|设计特点|主要功能|样式关键词

例如：
NavigationBar|导航组件|简洁现代、固定顶部|主导航、搜索、用户菜单|白色背景、主色按钮、中等阴影
ProductCard|卡片组件|卡片式设计、悬浮效果|产品展示、交互反馈|圆角卡片、渐变悬浮、主色强调

**重要**：确保所有组件都遵循同一套设计系统，视觉风格保持高度一致。

只输出设计系统定义和组件架构。
"""
        
        response = self._call_ai_model(prompt)
        
        # 解析响应
        sections = response.split("### 2. 组件架构")
        design_system = sections[0].replace("### 1. 设计系统定义", "").strip()
        
        components = []
        if len(sections) > 1:
            component_lines = sections[1].strip().split('\n')
            for line in component_lines:
                line = line.strip()
                if '|' in line and not line.startswith('#') and not line.startswith('例如') and not line.startswith('格式'):
                    parts_line = line.split('|')
                    if len(parts_line) >= 5:
                        component = {
                            'name': parts_line[0].strip(),
                            'type': parts_line[1].strip(),
                            'description': parts_line[2].strip(),
                            'functions': [f.strip() for f in parts_line[3].split(',')],
                            'style_keywords': parts_line[4].strip()  # 新增样式关键词
                        }
                        components.append(component)
        
        return {
            'design_rationale': design_system,
            'components': components,
            'design_system': design_system  # 保存设计系统用于后续步骤
        }
    
    def _generate_html_structure(self, components: List[Dict[str, Any]], framework: str) -> Dict[str, Any]:
        """第2步：生成HTML结构，基于设计系统"""
        
        # 获取设计系统信息
        design_system = self.generation_context.get('design_system', '')
        
        prompt = f"""你是一个专业的HTML结构工程师。请基于设计系统和组件设计，生成语义化的HTML结构。

## 设计系统约束

{design_system}

## 组件设计

"""
        for comp in components:
            style_keywords = comp.get('style_keywords', '')
            prompt += f"- {comp['name']}: {comp['description']}\n"
            prompt += f"  功能: {', '.join(comp.get('functions', []))}\n"
            prompt += f"  样式特点: {style_keywords}\n\n"
        
        prompt += f"""

## 技术要求

- **框架**: {framework}

## 生成规则

请生成一个结构完整、语义清晰的HTML文档：

1. **设计系统友好**：class命名要与设计系统对应，便于CSS样式应用
2. **语义化标签**：使用正确的HTML5语义化标签
3. **BEM命名规范**：使用Block__Element--Modifier命名规范
4. **数据属性**：为交互组件添加合适的data-*属性
5. **无内联代码**：绝对不要任何style属性、<style>标签或<script>标签
6. **结构层次**：清晰的DOM层次结构，便于样式和交互

请只输出完整的HTML代码，从<!DOCTYPE html>开始。确保结构支持设计系统的样式应用。
"""
        
        html_code = self._call_ai_model(prompt)
        
        return {
            'html_code': html_code.strip()
        }
    
    def _generate_css_styling(self, components: List[Dict[str, Any]], 
                             style_framework: str, responsive: bool, 
                             accessibility: bool) -> Dict[str, Any]:
        """第3步：生成CSS样式，严格按照设计系统"""
        
        # 获取设计系统信息
        design_system = self.generation_context.get('design_system', '')
        
        prompt = f"""你是一个专业的CSS设计师。请严格按照设计系统，生成统一、协调的样式代码。

## 设计系统规范

{design_system}

## 组件样式要求

"""
        for comp in components:
            style_keywords = comp.get('style_keywords', '')
            prompt += f"### {comp['name']} 样式\n"
            prompt += f"- 组件描述: {comp['description']}\n"
            prompt += f"- 样式要求: {style_keywords}\n"
            prompt += f"- 需要实现: {', '.join(comp.get('functions', []))}\n\n"
        
        prompt += f"""

## 样式框架

- **基础框架**: {style_framework}
- **响应式设计**: {'必须实现' if responsive else '固定宽度'}
- **无障碍支持**: {'必须支持' if accessibility else '标准实现'}

## 生成规则

请生成一个完整、统一的CSS样式系统：

1. **设计系统变量**：首先定义CSS变量（:root），包含颜色、字体、间距、圆角、阴影等
2. **基础样式重置**：标准化浏览器默认样式
3. **布局系统**：实现整体页面布局结构
4. **组件样式**：为每个组件实现完整样式，严格遵循设计系统
5. **交互状态**：hover、focus、active等状态，保持一致的反馈效果
6. **响应式设计**：{'实现移动端适配' if responsive else '桌面端优化'}
7. **无障碍样式**：{'包含对比度、焦点指示等' if accessibility else '标准可见性'}

**关键要求**：
- 所有颜色必须来自设计系统色彩定义
- 所有间距必须使用设计系统间距比例
- 所有圆角、阴影必须统一使用设计系统定义
- 组件之间风格必须高度一致

请只输出CSS代码，确保风格统一、视觉协调。
"""
        
        css_code = self._call_ai_model(prompt)
        
        return {
            'css_code': css_code.strip()
        }
    
    def _generate_javascript_interactions(self, components: List[Dict[str, Any]], 
                                         framework: str) -> Dict[str, Any]:
        """第4步：生成JavaScript交互，与设计系统协调"""
        
        # 筛选需要交互的组件
        interactive_components = [comp for comp in components if comp.get('functions')]
        
        if not interactive_components:
            return {'js_code': '// 当前原型无需JavaScript交互功能'}
        
        prompt = f"""你是一个专业的JavaScript开发工程师。请基于组件功能需求和设计系统，生成优雅的交互代码。

## 交互组件功能

"""
        for comp in interactive_components:
            functions = comp.get('functions', [])
            style_keywords = comp.get('style_keywords', '')
            if functions:
                prompt += f"### {comp['name']} 交互\n"
                prompt += f"- 功能需求: {', '.join(functions)}\n"
                prompt += f"- 样式特点: {style_keywords}\n"
                prompt += f"- 交互建议: 保持与设计系统一致的动画和反馈\n\n"
        
        prompt += f"""

## 技术要求

- **框架**: {framework}

## 生成规则

请生成高质量的JavaScript交互代码：

1. **设计系统一致性**：动画、过渡效果要与CSS样式协调
2. **模块化设计**：使用ES6模块和类，代码结构清晰
3. **事件处理**：统一的事件管理和错误处理
4. **用户体验**：流畅的交互反馈，loading状态等
5. **性能优化**：事件委托、防抖节流等优化技术
6. **无障碍支持**：键盘导航、ARIA属性管理
7. **状态管理**：清晰的组件状态管理

**交互风格要求**：
- 动画时长统一（如300ms过渡）
- 缓动函数一致（如ease-out）
- 反馈方式统一（如统一的加载动画）

请只输出JavaScript代码，确保交互体验与设计系统协调。
"""
        
        js_code = self._call_ai_model(prompt)
        
        return {
            'js_code': js_code.strip()
        }
    
    def _finalize_prototype(self, result: PrototypeResult) -> Dict[str, Any]:
        """第5步：完善整合，生成实施建议"""
        
        prompt = f"""你是一个技术架构师。请基于已生成的原型内容，提供实施建议和优化建议。

## 原型信息

- **组件数量**: {len(result.component_structure)}
- **是否有HTML**: {'是' if result.html_code else '否'}
- **是否有CSS**: {'是' if result.css_code else '否'}
- **是否有JavaScript**: {'是' if result.js_code else '否'}
- **技术栈**: {self.generation_context.get('framework', '未知')}

## 请提供建议

请给出具体的实施建议，每行一个建议：

1. **代码优化建议**（提升代码质量）
2. **性能优化要点**（提升运行效率）  
3. **扩展性考虑**（便于后续开发）
4. **维护性建议**（便于代码维护）
5. **部署注意事项**（生产环境部署）

每行格式：- 具体建议内容

只输出建议列表。
"""
        
        response = self._call_ai_model(prompt)
        
        # 解析实施建议
        notes = []
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith('- '):
                notes.append(line[2:].strip())
            elif line and not line.startswith('#') and not line.startswith('*'):
                notes.append(line)
        
        return {
            'implementation_notes': notes
        }
    
    def _emit_step_preview(self, result: PrototypeResult, step_name: str):
        """发送步骤预览"""
        preview_html = self._generate_partial_preview(result, step_name)
        self.preview_ready.emit(preview_html)
        self.step_completed.emit(step_name, {
            'html': result.html_code,
            'css': result.css_code, 
            'js': result.js_code,
            'preview': preview_html
        })
    
    def _emit_final_preview(self, result: PrototypeResult):
        """发送最终预览"""
        final_html = self.generate_preview_html()
        self.preview_ready.emit(final_html)
    
    def _generate_partial_preview(self, result: PrototypeResult, step_name: str) -> str:
        """生成部分预览HTML"""
        if step_name == 'framework':
            # 显示设计系统预览
            design_system = result.step_results.get('framework', {}).get('design_system', '')
            return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>设计系统预览</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; background: #f8fafc; }}
        .preview-card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }}
        .design-system {{ line-height: 1.6; }}
        .component-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }}
        .component-item {{ background: #f8f9fa; padding: 16px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .component-name {{ font-weight: 600; color: #2d3748; margin-bottom: 8px; }}
        .component-desc {{ color: #4a5568; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="preview-card">
        <h2>📋 第1步：设计系统定义完成</h2>
        <div class="design-system">
            {design_system.replace(chr(10), '<br>')}
        </div>
    </div>
    <div class="preview-card">
        <h3>🧩 组件架构预览</h3>
        <div class="component-grid">
            {''.join([f'<div class="component-item"><div class="component-name">{comp["name"]}</div><div class="component-desc">{comp["description"]}<br><small>样式：{comp.get("style_keywords", "")}</small></div></div>' for comp in result.component_structure])}
        </div>
    </div>
</body>
</html>"""
        
        elif step_name == 'components':
            return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML结构预览</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; }}
        .preview-banner {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
        .preview-content {{ padding: 20px; }}
    </style>
</head>
<body>
    <div class="preview-banner">
        <h2>🏗️ 第2步：HTML结构完成</h2>
        <p>基础结构已生成，接下来应用设计系统样式...</p>
    </div>
    <div class="preview-content">
        {result.html_code}
    </div>
</body>
</html>"""
        
        elif step_name == 'styling':
            return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>样式设计预览</title>
    <style>
        {result.css_code}
        .preview-notification {{ position: fixed; top: 20px; right: 20px; background: #10b981; color: white; padding: 16px 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4); z-index: 10000; animation: slideIn 0.3s ease-out; }}
        @keyframes slideIn {{ from {{ transform: translateX(100%); opacity: 0; }} to {{ transform: translateX(0); opacity: 1; }} }}
    </style>
</head>
<body>
    <div class="preview-notification">
        🎨 设计系统样式已应用
    </div>
    {result.html_code}
</body>
</html>"""
        
        elif step_name == 'interactions':
            return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>交互功能预览</title>
    <style>
        {result.css_code}
        .preview-notification {{ position: fixed; top: 20px; right: 20px; background: #3b82f6; color: white; padding: 16px 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); z-index: 10000; animation: slideIn 0.3s ease-out; }}
        @keyframes slideIn {{ from {{ transform: translateX(100%); opacity: 0; }} to {{ transform: translateX(0); opacity: 1; }} }}
    </style>
</head>
<body>
    <div class="preview-notification">
        ⚡ 交互功能已实现
    </div>
    {result.html_code}
    <script>
        {result.js_code}
    </script>
</body>
</html>"""
        
        return self.generate_preview_html()
    
    def _call_ai_model(self, prompt: str) -> str:
        """Call AI model to generate prototype"""
        try:
            # Get model configuration
            module_config = self.config.get_module_config("prototype_generator")
            model_config_name = module_config.model_config if module_config else self.config.get_app_setting("default_model")
            model = self.model_factory.get_model(model_config_name)
            
            if not model:
                raise ValueError("未配置可用的AI模型")
            
            # Call model with streaming support
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
            
            return response
            
        except Exception as e:
            raise Exception(f"AI模型调用失败: {str(e)}")
    
    def generate_preview_html(self) -> str:
        """Generate complete HTML preview from current result"""
        if not self.current_result or not self.current_result.html_code:
            return "<html><body><h1>暂无预览内容</h1></body></html>"
        
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>原型预览</title>
    <style>
        {self.current_result.css_code}
    </style>
</head>
<body>
    {self.current_result.html_code}
    
    <script>
        {self.current_result.js_code}
    </script>
</body>
</html>"""
        
        return html_template
    
    def export_prototype(self, export_path: str, format_type: str = 'html') -> bool:
        """Export prototype to file"""
        try:
            if not self.current_result:
                return False
            
            if format_type == 'html':
                content = self.generate_preview_html()
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            elif format_type == 'json':
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_result.to_dict(), f, 
                             ensure_ascii=False, indent=2)
            
            elif format_type == 'separate':
                # Export HTML, CSS, JS as separate files
                base_path = export_path.rsplit('.', 1)[0]
                
                with open(f"{base_path}.html", 'w', encoding='utf-8') as f:
                    f.write(self.current_result.html_code)
                
                with open(f"{base_path}.css", 'w', encoding='utf-8') as f:
                    f.write(self.current_result.css_code)
                
                with open(f"{base_path}.js", 'w', encoding='utf-8') as f:
                    f.write(self.current_result.js_code)
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"导出失败: {str(e)}")
            return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat() 