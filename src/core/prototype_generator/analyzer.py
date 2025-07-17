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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "html_code": self.html_code,
            "css_code": self.css_code,
            "js_code": self.js_code,
            "component_structure": self.component_structure,
            "design_rationale": self.design_rationale,
            "implementation_notes": self.implementation_notes,
            "preview_available": self.preview_available,
            "metadata": self.metadata
        }


class PrototypeGenerator(BaseModule):
    """Generator for interactive prototypes from multiple input sources"""
    
    # Signals
    prototype_generated = pyqtSignal(dict)
    preview_ready = pyqtSignal(str)  # HTML content for preview
    
    def __init__(self, config):
        super().__init__("prototype_generator", config)
        self.inputs = []  # List of PrototypeInput objects
        self.current_result = None
        self.model_factory = ModelFactory(config)
    
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
        Process inputs and generate prototype using multi-step approach
        
        Args:
            input_data: Dictionary containing:
                - inputs: List of input objects (optional, uses self.inputs if not provided)
                - prototype_type: 'web', 'mobile', 'desktop'
                - framework: 'html_css_js', 'react', 'vue', 'angular'
                - style_framework: 'bootstrap', 'tailwind', 'custom'
                - responsive: boolean
                - accessibility: boolean
        """
        try:
            self.progress_updated.emit(5)
            self.status_updated.emit("开始生成原型...")
            
            # Use provided inputs or current inputs
            inputs_to_process = input_data.get('inputs', self.inputs)
            if not inputs_to_process:
                raise ValueError("没有可用的输入源")
            
            prototype_type = input_data.get('prototype_type', 'web')
            framework = input_data.get('framework', 'html_css_js')
            style_framework = input_data.get('style_framework', 'bootstrap')
            responsive = input_data.get('responsive', True)
            accessibility = input_data.get('accessibility', True)
            
            result = PrototypeResult()
            
            # Step 1: Generate design rationale and planning
            self.progress_updated.emit(15)
            self.status_updated.emit("生成设计理念...")
            result.design_rationale = self._generate_design_rationale(
                inputs_to_process, prototype_type, framework, style_framework, responsive, accessibility
            )
            
            # Step 2: Generate component structure
            self.progress_updated.emit(30)
            self.status_updated.emit("分析组件结构...")
            result.component_structure = self._generate_component_structure(
                inputs_to_process, prototype_type, framework
            )
            
            # Step 3: Generate HTML code
            self.progress_updated.emit(45)
            self.status_updated.emit("生成HTML代码...")
            result.html_code = self._generate_html_code(
                inputs_to_process, result.component_structure, prototype_type, framework
            )
            
            # Step 4: Generate CSS code
            self.progress_updated.emit(60)
            self.status_updated.emit("生成CSS样式...")
            result.css_code = self._generate_css_code(
                inputs_to_process, result.component_structure, style_framework, responsive, accessibility
            )
            
            # Step 5: Generate JavaScript code
            self.progress_updated.emit(75)
            self.status_updated.emit("生成JavaScript代码...")
            result.js_code = self._generate_js_code(
                inputs_to_process, result.component_structure, framework
            )
            
            # Step 6: Generate implementation notes
            self.progress_updated.emit(90)
            self.status_updated.emit("生成实现要点...")
            result.implementation_notes = self._generate_implementation_notes(
                result, prototype_type, framework
            )
            
            # Finalize result
            result.preview_available = bool(result.html_code.strip())
            result.metadata = {
                'generated_at': self._get_timestamp(),
                'input_count': len(inputs_to_process),
                'prototype_type': prototype_type,
                'framework': framework,
                'style_framework': style_framework
            }
            
            self.progress_updated.emit(100)
            self.status_updated.emit("原型生成完成")
            
            self.current_result = result
            return result
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            raise
    
    def _generate_design_rationale(self, inputs: List[PrototypeInput], 
                                  prototype_type: str, framework: str,
                                  style_framework: str, responsive: bool, 
                                  accessibility: bool) -> str:
        """Generate design rationale and planning"""
        
        prompt = f"""你是一个专业的UI/UX设计师。请基于以下输入内容，生成设计理念和决策说明。

## 输入内容分析

"""
        
        # Add each input to the prompt
        for i, inp in enumerate(inputs, 1):
            prompt += f"""
### 输入 {i}: {inp.name} ({inp.input_type})
{inp.content}

"""
        
        prompt += f"""
## 设计要求

- **原型类型**: {prototype_type}
- **技术框架**: {framework}
- **样式框架**: {style_framework}
- **响应式设计**: {'是' if responsive else '否'}
- **无障碍支持**: {'是' if accessibility else '否'}

## 请生成内容

请详细说明：
1. 设计理念和核心思路
2. 用户体验考虑
3. 视觉设计风格选择
4. 布局结构决策
5. 交互模式设计
6. 技术选型理由

请用中文回答，内容要详细且专业。
"""
        
        return self._call_ai_model(prompt)
    
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
    
    def _generate_component_structure(self, inputs: List[PrototypeInput], 
                                     prototype_type: str, framework: str) -> List[Dict[str, Any]]:
        """Generate component structure analysis"""
        
        prompt = f"""你是一个专业的前端架构师。请基于以下输入内容，分析并设计组件结构。

## 输入内容分析

"""
        
        # Add each input to the prompt
        for i, inp in enumerate(inputs, 1):
            prompt += f"""
### 输入 {i}: {inp.name} ({inp.input_type})
{inp.content}

"""
        
        prompt += f"""
## 技术要求

- **原型类型**: {prototype_type}
- **技术框架**: {framework}

## 请生成内容

分析需要的组件，每个组件一行，格式：
组件名称|组件类型|组件描述|主要属性|主要事件

示例：
Header|布局组件|页面顶部导航栏|title,logo,menuItems|onMenuClick,onLogoClick
Button|交互组件|通用按钮组件|text,type,disabled|onClick,onHover

只返回组件列表。
"""
        
        response = self._call_ai_model(prompt)
        
        # Parse component structure
        components = []
        for line in response.strip().split('\n'):
            line = line.strip()
            if '|' in line and not line.startswith('#'):
                parts = line.split('|')
                if len(parts) >= 3:
                    component = {
                        'name': parts[0].strip(),
                        'type': parts[1].strip(),
                        'description': parts[2].strip(),
                        'props': [p.strip() for p in parts[3].split(',')] if len(parts) > 3 and parts[3].strip() else [],
                        'events': [e.strip() for e in parts[4].split(',')] if len(parts) > 4 and parts[4].strip() else []
                    }
                    components.append(component)
        
        return components
    
    def _generate_html_code(self, inputs: List[PrototypeInput], 
                           components: List[Dict[str, Any]], 
                           prototype_type: str, framework: str) -> str:
        """Generate HTML code"""
        
        prompt = f"""你是一个专业的前端开发工程师。请基于以下信息生成HTML代码。

## 输入内容

"""
        
        # Add inputs
        for i, inp in enumerate(inputs, 1):
            prompt += f"""
### 输入 {i}: {inp.name}
{inp.content[:300]}...
"""
        
        # Add component structure
        prompt += f"""

## 组件结构

"""
        for comp in components:
            prompt += f"- {comp['name']}: {comp['description']}\n"
        
        prompt += f"""

## 技术要求

- **原型类型**: {prototype_type}
- **框架**: {framework}

## 请生成内容

生成完整的HTML代码：
1. 结构清晰，语义化标签
2. 包含所有必要的组件
3. 添加适当的class和id
4. 包含基本的meta标签
5. 确保代码可以直接运行

只返回HTML代码，不要代码块标记。
"""
        
        return self._call_ai_model(prompt)
    
    def _generate_css_code(self, inputs: List[PrototypeInput], 
                          components: List[Dict[str, Any]], 
                          style_framework: str, responsive: bool, 
                          accessibility: bool) -> str:
        """Generate CSS code"""
        
        prompt = f"""你是一个专业的UI设计师和CSS专家。请基于以下信息生成CSS样式代码。

## 组件结构

"""
        for comp in components:
            prompt += f"- {comp['name']}: {comp['description']}\n"
        
        prompt += f"""

## 样式要求

- **样式框架**: {style_framework}
- **响应式设计**: {'是' if responsive else '否'}
- **无障碍支持**: {'是' if accessibility else '否'}

## 请生成内容

生成完整的CSS样式代码：
1. 现代化的视觉设计
2. 清晰的组件样式定义
3. {'包含响应式媒体查询' if responsive else '固定宽度设计'}
4. {'包含无障碍支持样式' if accessibility else '标准样式'}
5. 使用{style_framework}的设计理念
6. 包含hover、focus等交互状态

只返回CSS代码，不要代码块标记。
"""
        
        return self._call_ai_model(prompt)
    
    def _generate_js_code(self, inputs: List[PrototypeInput], 
                         components: List[Dict[str, Any]], 
                         framework: str) -> str:
        """Generate JavaScript code"""
        
        prompt = f"""你是一个专业的前端开发工程师。请基于以下信息生成JavaScript交互代码。

## 组件结构和事件

"""
        for comp in components:
            if comp.get('events'):
                prompt += f"- {comp['name']}: {', '.join(comp['events'])}\n"
        
        prompt += f"""

## 技术要求

- **框架**: {framework}

## 请生成内容

生成JavaScript交互代码：
1. 实现组件的交互功能
2. 添加必要的事件监听器
3. 包含表单验证（如果有表单）
4. 添加适当的用户反馈
5. 确保代码兼容现代浏览器
6. 使用{framework}的开发模式

只返回JavaScript代码，不要代码块标记。
"""
        
        return self._call_ai_model(prompt)
    
    def _generate_implementation_notes(self, result: PrototypeResult, 
                                     prototype_type: str, framework: str) -> List[str]:
        """Generate implementation notes"""
        
        prompt = f"""你是一个技术架构师。请基于以下原型信息，生成实现要点和建议。

## 原型信息

- **类型**: {prototype_type}
- **框架**: {framework}
- **组件数量**: {len(result.component_structure)}
- **是否有HTML**: {'是' if result.html_code else '否'}
- **是否有CSS**: {'是' if result.css_code else '否'}
- **是否有JS**: {'是' if result.js_code else '否'}

## 请生成内容

提供实现要点和建议，每行一个要点：
- 要点1
- 要点2
- 要点3

包含以下方面：
1. 技术实施建议
2. 性能优化要点
3. 维护性考虑
4. 扩展性建议
5. 部署注意事项

只返回要点列表。
"""
        
        response = self._call_ai_model(prompt)
        
        # Parse implementation notes
        notes = []
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('• '):
                notes.append(line[2:].strip())
            elif line and not line.startswith('#'):
                notes.append(line)
        
        return notes
    
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