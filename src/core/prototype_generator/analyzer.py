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
        self.complete_html = ""  # 包含HTML+CSS+JS的完整文档
        self.component_structure = []
        self.design_rationale = ""
        self.implementation_notes = []
        self.preview_available = False
        self.metadata = {}
        # 生成方式记录
        self.generation_mode = "integrated"  # integrated为一次性生成
        self.generation_steps = {
            'analysis': False,      # 需求分析
            'design': False,        # 设计规划  
            'implementation': False,# 代码实现
            'optimization': False   # 优化完善
        }
        self.step_results = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "html_code": self.html_code,
            "css_code": self.css_code,
            "js_code": self.js_code,
            "complete_html": self.complete_html,
            "component_structure": self.component_structure,
            "design_rationale": self.design_rationale,
            "implementation_notes": self.implementation_notes,
            "preview_available": self.preview_available,
            "metadata": self.metadata,
            "generation_mode": self.generation_mode,
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
        self.generation_context = {}
    
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
        Process inputs and generate complete prototype in integrated mode
        
        Args:
            input_data: Dictionary containing:
                - inputs: List of input objects (optional, uses self.inputs if not provided)
                - prototype_type: 'web', 'mobile', 'desktop'
                - framework: 'html_css_js', 'react', 'vue', 'angular'
                - style_framework: 'bootstrap', 'tailwind', 'custom'
                - responsive: boolean
                - accessibility: boolean
                - generation_mode: 'integrated' (一次性生成) or 'separate' (分开生成其他内容)
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
            generation_mode = input_data.get('generation_mode', 'integrated')
            
            result = PrototypeResult()
            result.generation_mode = generation_mode
            
            # 保存生成上下文
            self.generation_context = {
                'inputs': inputs_to_process,
                'prototype_type': prototype_type,
                'framework': framework,
                'style_framework': style_framework,
                'responsive': responsive,
                'accessibility': accessibility,
                'generation_mode': generation_mode
            }
            
            if generation_mode == 'integrated':
                # 一次性生成HTML+CSS+JS
                result = self._generate_integrated_prototype(inputs_to_process, result)
            else:
                # 其他内容分开生成（如文档、测试等）
                result = self._generate_separate_components(inputs_to_process, result)
            
            # Finalize result
            result.preview_available = bool(result.complete_html.strip())
            result.metadata = {
                'generated_at': self._get_timestamp(),
                'input_count': len(inputs_to_process),
                'prototype_type': prototype_type,
                'framework': framework,
                'style_framework': style_framework,
                'generation_mode': generation_mode,
                'steps_completed': len([s for s in result.generation_steps.values() if s])
            }
            
            self.progress_updated.emit(100)
            self.status_updated.emit("✅ 原型生成完成")
            
            self.current_result = result
            
            # 发送预览
            self.preview_ready.emit(result.complete_html)
            
            return result
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            raise
    
    def _generate_integrated_prototype(self, inputs: List[PrototypeInput], result: PrototypeResult) -> PrototypeResult:
        """一次性生成完整的HTML+CSS+JS原型"""
        
        # Step 1: 需求分析 (5-20%)
        self.progress_updated.emit(10)
        self.status_updated.emit("📋 分析需求...")
        analysis_result = self._analyze_requirements(inputs)
        result.design_rationale = analysis_result['design_rationale']
        result.component_structure = analysis_result['components']
        result.generation_steps['analysis'] = True
        result.step_results['analysis'] = analysis_result
        
        # Step 2: 设计规划 (20-35%)
        self.progress_updated.emit(25)
        self.status_updated.emit("🎨 设计规划...")
        design_result = self._plan_design_system(result.component_structure)
        result.generation_steps['design'] = True
        result.step_results['design'] = design_result
        
        # Step 3: 一次性生成完整代码 (35-85%)
        self.progress_updated.emit(40)
        self.status_updated.emit("🚀 生成完整原型代码...")
        implementation_result = self._generate_complete_prototype_code(
            inputs, result.component_structure, design_result
        )
        
        # 提取分离的代码
        result.html_code = implementation_result.get('html_code', '')
        result.css_code = implementation_result.get('css_code', '')
        result.js_code = implementation_result.get('js_code', '')
        result.complete_html = implementation_result.get('complete_html', '')
        
        result.generation_steps['implementation'] = True
        result.step_results['implementation'] = implementation_result
        
        # Step 4: 优化完善 (85-100%)
        self.progress_updated.emit(85)
        self.status_updated.emit("✨ 优化完善...")
        optimization_result = self._optimize_prototype(result)
        result.implementation_notes = optimization_result.get('implementation_notes', [])
        result.generation_steps['optimization'] = True
        result.step_results['optimization'] = optimization_result
        
        return result
    
    def _generate_separate_components(self, inputs: List[PrototypeInput], result: PrototypeResult) -> PrototypeResult:
        """分开生成其他组件（文档、测试、配置等）"""
        
        # Step 1: 分析需求
        self.progress_updated.emit(20)
        self.status_updated.emit("📋 分析组件需求...")
        analysis_result = self._analyze_requirements(inputs)
        result.design_rationale = analysis_result['design_rationale']
        result.component_structure = analysis_result['components']
        result.generation_steps['analysis'] = True
        
        # Step 2: 生成文档
        self.progress_updated.emit(40)
        self.status_updated.emit("📚 生成项目文档...")
        doc_result = self._generate_documentation(result.component_structure)
        result.generation_steps['design'] = True
        result.step_results['documentation'] = doc_result
        
        # Step 3: 生成配置文件
        self.progress_updated.emit(60)
        self.status_updated.emit("⚙️ 生成配置文件...")
        config_result = self._generate_configuration_files(result.component_structure)
        result.generation_steps['implementation'] = True
        result.step_results['configuration'] = config_result
        
        # Step 4: 生成测试文件
        self.progress_updated.emit(80)
        self.status_updated.emit("🧪 生成测试用例...")
        test_result = self._generate_test_files(result.component_structure)
        result.generation_steps['optimization'] = True
        result.step_results['testing'] = test_result
        
        # 生成简单的HTML预览
        result.complete_html = self._generate_simple_preview(result.component_structure)
        
        return result
    
    def _analyze_requirements(self, inputs: List[PrototypeInput]) -> Dict[str, Any]:
        """分析需求，提取核心功能和组件"""
        
        prompt = f"""你是一个专业的产品分析师。请分析以下需求，提取核心功能和所需组件。

## 需求输入

"""
        
        for i, inp in enumerate(inputs, 1):
            prompt += f"""
### 需求 {i}: {inp.name} ({inp.input_type})
{inp.content}

"""
        
        prompt += f"""
## 技术约束

在分析过程中，请考虑以下技术约束：
- **样式系统**: 将使用Tailwind CSS框架
- **图标系统**: 将使用Font Awesome 5图标
- **图片资源**: 将使用Unsplash.com免费图片（Picsum Photos占位符）
- **前端框架**: 可选择Vue 2来减少代码量和提升交互体验
- **响应式设计**: 需要适配移动端和桌面端

## 分析任务

请完成以下分析：

### 1. 核心功能分析
分析用户的核心需求和期望功能，总结设计理念和产品定位。考虑如何利用Tailwind CSS和Vue 2实现现代化的视觉设计和流畅的交互体验。

### 2. 组件架构设计
基于功能需求，设计所需组件列表。每个组件都要考虑Tailwind CSS的设计能力、Font Awesome图标的使用，以及是否需要Vue 2的响应式特性。

每个组件格式：
组件名称|组件类型|主要功能|设计要点|交互特性

例如：
导航栏|Navigation|页面导航、用户入口|使用Tailwind flex布局、固定顶部、响应式折叠|汉堡菜单图标(fas fa-bars)、Vue 2数据绑定控制菜单状态
产品卡片|Card|产品展示、信息预览|Tailwind卡片样式、阴影效果、图片占位符|Vue 2点击事件、数据绑定、状态变化动画
搜索框|Search|内容搜索、过滤功能|Tailwind输入框样式、搜索图标|Vue 2双向绑定v-model、实时搜索、结果过滤

### 3. 技术实现策略
分析各功能的复杂度，制定技术选型策略：
- **静态展示类**：仅使用HTML + Tailwind CSS
- **简单交互类**：使用少量原生JavaScript
- **复杂交互类**：使用Vue 2的数据绑定和指令系统
- **动态内容类**：使用Vue 2的响应式数据和计算属性

### 4. Vue 2适用场景
评估以下功能是否适合使用Vue 2：
- 表单输入和验证（v-model、数据绑定）
- 列表渲染和过滤（v-for、computed属性）
- 条件显示和状态切换（v-if、v-show）
- 用户交互反馈（事件处理、状态管理）
- 动态内容更新（响应式数据、watch监听）

请从技术可行性和用户体验两个维度进行综合分析。
"""
        
        response = self._call_ai_model(prompt)
        
        # 解析响应
        sections = response.split("### 2. 组件架构设计")
        design_rationale = sections[0].replace("### 1. 核心功能分析", "").strip()
        
        components = []
        if len(sections) > 1:
            # 查找组件部分和视觉风格部分
            content = sections[1]
            if "### 3. 视觉风格建议" in content:
                component_content = content.split("### 3. 视觉风格建议")[0]
            else:
                component_content = content
            
            component_lines = component_content.strip().split('\n')
            for line in component_lines:
                line = line.strip()
                if '|' in line and not line.startswith('#') and not line.startswith('例如') and not line.startswith('格式'):
                    parts_line = line.split('|')
                    if len(parts_line) >= 5:
                        component = {
                            'name': parts_line[0].strip(),
                            'type': parts_line[1].strip(),
                            'functions': [f.strip() for f in parts_line[2].split(',')],
                            'design_points': parts_line[3].strip(),
                            'interactions': parts_line[4].strip()
                        }
                        components.append(component)
        
        return {
            'design_rationale': design_rationale,
            'components': components
        }
    
    def _plan_design_system(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """规划统一的设计系统"""
        
        prompt = f"""你是一个UI/UX设计师。请为以下组件设计一套基于Tailwind CSS的统一设计系统。

## 组件列表

"""
        for comp in components:
            prompt += f"- {comp['name']}: {comp.get('design_points', '')}\n"
        
        prompt += f"""

## 技术约束

- **样式框架**: 必须使用Tailwind CSS
- **图标系统**: 必须使用Font Awesome 5
- **图片来源**: 必须使用Unsplash.com图片

## 设计系统要求

请设计一套完整的基于Tailwind CSS的设计系统，包括：

### 色彩系统（基于Tailwind调色板）
- 主色调：选择Tailwind颜色（如blue-600, indigo-600等）
- 辅助色：选择Tailwind颜色（如gray-600, slate-600等）
- 功能色：
  - Success: green-500
  - Warning: yellow-500  
  - Error: red-500
  - Info: blue-500
- 中性色：使用Tailwind的gray系列

### 字体系统（基于Tailwind Typography）
- 字体族：使用Tailwind默认字体栈
- 字号层次：使用Tailwind文字大小类（text-xs到text-6xl）
- 字重：使用Tailwind字重类（font-thin到font-black）

### 间距系统（基于Tailwind Spacing）
- 基础单位：使用Tailwind间距系统（4px基础单位）
- 内边距：p-1, p-2, p-4, p-6, p-8, p-12等
- 外边距：m-1, m-2, m-4, m-6, m-8, m-12等

### 组件样式规范
- 圆角：使用rounded-none, rounded-sm, rounded, rounded-lg, rounded-xl等
- 阴影：使用shadow-sm, shadow, shadow-md, shadow-lg, shadow-xl等
- 边框：使用border, border-2, border-4等配合颜色类

### Font Awesome图标规范
- 图标大小：配合Tailwind文字大小类（text-sm fa图标，text-lg fa图标等）
- 图标颜色：使用Tailwind颜色类（text-blue-600等）
- 常用图标推荐：
  - 导航：fas fa-bars, fas fa-home, fas fa-user
  - 操作：fas fa-edit, fas fa-trash, fas fa-save
  - 状态：fas fa-check, fas fa-times, fas fa-exclamation

### Unsplash图片规范
- 横幅图片：1200x400或1920x600
- 卡片图片：300x200或400x300
- 头像图片：150x150或200x200
- 背景图片：1920x1080
- 使用Picsum Photos占位符：https://picsum.photos/[宽度]/[高度]
- 带随机参数：https://picsum.photos/[宽度]/[高度]?random=[数字]
- 示例：https://picsum.photos/1200/400（横幅）、https://picsum.photos/300/200（卡片）

### 响应式设计规范
- 移动端优先：默认样式针对移动端
- 断点使用：sm:, md:, lg:, xl:, 2xl:
- 网格布局：使用grid和flex布局类
- 隐藏显示：使用hidden, block, sm:hidden, md:block等

请输出具体的Tailwind CSS类名组合和设计参数，用于后续代码生成。
"""
        
        response = self._call_ai_model(prompt)
        
        return {
            'design_system': response,
            'color_palette': self._extract_colors(response),
            'typography': self._extract_typography(response),
            'spacing': self._extract_spacing(response)
        }
    
    def _generate_complete_prototype_code(self, inputs: List[PrototypeInput], 
                                         components: List[Dict[str, Any]], 
                                         design_result: Dict[str, Any]) -> Dict[str, Any]:
        """一次性生成完整的HTML+CSS+JS代码"""
        
        context = self.generation_context
        design_system = design_result.get('design_system', '')
        
        prompt = f"""你是一个全栈前端工程师。请根据需求和设计系统，一次性生成完整的HTML+CSS+JS代码。

## 项目需求

"""
        for i, inp in enumerate(inputs, 1):
            prompt += f"""
### 需求 {i}: {inp.name}
{inp.content}

"""
        
        prompt += f"""
## 设计系统

{design_system}

## 组件规范

"""
        for comp in components:
            prompt += f"""
### {comp['name']}
- 类型: {comp['type']}
- 功能: {', '.join(comp.get('functions', []))}
- 设计要点: {comp.get('design_points', '')}
- 交互特性: {comp.get('interactions', '')}

"""
        
        prompt += f"""
## 技术要求

- **原型类型**: {context.get('prototype_type', 'web')}
- **技术框架**: {context.get('framework', 'html_css_js')}
- **样式框架**: Tailwind CSS（必须使用）
- **图片素材**: 使用 Unsplash.com 图片（通过官方API或占位符）
- **图标系统**: Font Awesome 5（通过CDN引入）
- **前端框架**: Vue 2（可选，用于减少代码量和提升交互性）
- **响应式设计**: {'必须支持' if context.get('responsive', True) else '桌面优先'}
- **无障碍支持**: {'必须支持' if context.get('accessibility', True) else '基础支持'}

## 资源引用规范

### Tailwind CSS v4
使用最新CDN引入：
<script src="https://cdn.tailwindcss.com"></script>
或者使用 jsDelivr CDN：
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>

### Font Awesome 5
使用CDN引入：
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">

### Vue 2（推荐使用以减少代码量）
使用CDN引入最新稳定版：
<script src="https://cdn.jsdelivr.net/npm/vue@2.7.16/dist/vue.min.js"></script>

### Unsplash 图片
**推荐方式**：使用占位符服务
- Picsum Photos: https://picsum.photos/[宽度]/[高度]
- Lorem Picsum: https://picsum.photos/[宽度]/[高度]?category=[类别]

**示例**：
- 横幅图片：https://picsum.photos/1200/400
- 卡片图片：https://picsum.photos/300/200
- 头像图片：https://picsum.photos/150/150
- 带类别：https://picsum.photos/400/300?random=1

**备选方式**：使用Unsplash占位符（如果需要特定主题）
- 格式：https://images.unsplash.com/photo-[图片ID]?w=[宽度]&h=[高度]&fit=crop
- 通用占位符：https://via.placeholder.com/[宽度]x[高度]/[背景色]/[文字色]?text=[文字内容]

## 生成要求

请生成一个完整、可运行的原型，根据复杂程度选择合适的技术栈：

### 方案选择原则
- **简单静态展示**：仅使用HTML + Tailwind CSS + 少量原生JavaScript
- **中等交互需求**：使用HTML + Tailwind CSS + Vue 2（推荐）
- **复杂交互逻辑**：使用Vue 2 + 组件化架构

### 1. 完整HTML文档（Vue 2推荐版本）
使用以下结构：
- HTML文档头部引入Tailwind CSS、Font Awesome和Vue 2
- body中包含Vue应用的挂载点
- script标签中定义Vue应用实例

### 2. 分离的代码文件

同时提供分离的HTML、CSS、JS代码：

**HTML部分** (Vue 2模板，仅body内容):
包含Vue应用的根元素和模板结构

**CSS部分** (自定义样式代码，补充Tailwind不足):
包含Vue相关样式和自定义CSS

**JavaScript部分** (Vue 2应用代码):
包含Vue实例的完整配置

## Vue 2使用优势

1. **代码量减少60-80%**：
   - 数据绑定替代手动DOM操作
   - 指令系统简化常见交互
   - 响应式更新自动处理

2. **开发效率提升**：
   - 声明式编程，更直观
   - 双向数据绑定
   - 组件化思维

3. **维护性更好**：
   - 状态管理集中化
   - 模板语法清晰
   - 逻辑与视图分离

## 关键要求

1. **Tailwind CSS优先**: 所有样式优先使用Tailwind CSS类名，只在必要时添加自定义CSS
2. **Font Awesome图标**: 所有图标使用Font Awesome 5的class格式，如 <i class="fas fa-home"></i>
3. **图片使用**: 优先使用Picsum Photos占位符，确保图片能正常加载
4. **Vue 2集成**: 合理使用Vue 2的数据绑定、指令和生命周期，大幅减少JavaScript代码
5. **设计系统一致性**: 严格按照设计系统规范，确保视觉统一
6. **代码质量**: 语义化HTML、模块化CSS、简洁的Vue代码
7. **用户体验**: 流畅的交互、合理的反馈、直观的操作
8. **响应式设计**: 使用Tailwind的响应式类名实现移动端和桌面端适配
9. **性能优化**: 高效的代码结构、CDN资源加载、Vue的响应式优化
10. **可维护性**: 清晰的代码结构、合理的命名规范、Vue的组件化思维

## Vue 2常用指令和功能
- **v-model**: 双向数据绑定，用于表单控件
- **v-if/v-show**: 条件渲染，控制元素显示隐藏
- **v-for**: 列表渲染，循环展示数据
- **v-on (@)**: 事件监听，处理用户交互
- **v-bind (:)**: 属性绑定，动态设置HTML属性
- **computed**: 计算属性，基于响应式数据的衍生值
- **methods**: 方法定义，处理用户交互和业务逻辑
- **watch**: 监听器，响应数据变化
- **过渡动画**: 使用transition标签实现平滑动画效果

请按照上述格式生成完整代码，优先使用Vue 2来减少代码复杂度。
"""
        
        response = self._call_ai_model(prompt)
        
        # 解析生成的代码
        complete_html = self._extract_complete_html(response)
        html_code = self._extract_html_body(response)
        css_code = self._extract_css_code(response)
        js_code = self._extract_js_code(response)
        
        # 如果没有提取到分离的代码，从完整HTML中提取
        if not html_code and complete_html:
            html_code = self._extract_body_from_complete_html(complete_html)
        if not css_code and complete_html:
            css_code = self._extract_style_from_complete_html(complete_html)
        if not js_code and complete_html:
            js_code = self._extract_script_from_complete_html(complete_html)
        
        return {
            'complete_html': complete_html,
            'html_code': html_code,
            'css_code': css_code,
            'js_code': js_code,
            'generation_notes': self._analyze_generated_code(complete_html)
        }
    
    def _optimize_prototype(self, result: PrototypeResult) -> Dict[str, Any]:
        """优化完善原型"""
        
        prompt = f"""你是一个前端架构师。请分析以下原型代码，提供优化建议。

## 代码分析

- **HTML长度**: {len(result.html_code)} 字符
- **CSS长度**: {len(result.css_code)} 字符  
- **JavaScript长度**: {len(result.js_code)} 字符
- **组件数量**: {len(result.component_structure)}

## 请提供优化建议

请分析代码质量，给出具体的改进建议：

### 1. 性能优化
- 代码效率提升
- 资源加载优化
- 渲染性能改进

### 2. 代码质量
- 代码结构优化
- 命名规范改进
- 最佳实践应用

### 3. 用户体验
- 交互体验优化
- 视觉效果改进
- 响应式优化

### 4. 维护性提升
- 代码可读性
- 扩展性考虑
- 文档完善

### 5. 部署建议
- 生产环境配置
- 浏览器兼容性
- 性能监控

请为每个方面提供3-5个具体建议，每个建议一行。
"""
        
        response = self._call_ai_model(prompt)
        
        # 解析建议
        notes = []
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                notes.append(line[2:].strip())
            elif line and not line.startswith('#') and not line.startswith('###'):
                if any(keyword in line for keyword in ['优化', '改进', '建议', '使用', '避免', '确保']):
                    notes.append(line)
        
        return {
            'implementation_notes': notes,
            'optimization_summary': response
        }
    
    def _generate_documentation(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成项目文档"""
        
        prompt = f"""为以下组件生成技术文档：

## 组件列表
"""
        for comp in components:
            prompt += f"- {comp['name']}: {', '.join(comp.get('functions', []))}\n"
        
        prompt += """

请生成：
1. README.md - 项目说明
2. API文档 - 组件接口说明  
3. 部署指南 - 环境配置和部署步骤

每个文档请用标准Markdown格式。
"""
        
        response = self._call_ai_model(prompt)
        
        return {
            'readme': self._extract_readme(response),
            'api_docs': self._extract_api_docs(response),
            'deployment_guide': self._extract_deployment_guide(response)
        }
    
    def _generate_configuration_files(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成配置文件"""
        
        prompt = f"""为项目生成配置文件：

## 组件需求
"""
        for comp in components:
            prompt += f"- {comp['name']}\n"
        
        prompt += """

请生成：
1. package.json - 依赖配置
2. webpack.config.js - 构建配置
3. .eslintrc.js - 代码规范配置
4. .gitignore - Git忽略规则

请提供完整的配置文件内容。
"""
        
        response = self._call_ai_model(prompt)
        
        return {
            'package_json': self._extract_package_json(response),
            'webpack_config': self._extract_webpack_config(response),
            'eslint_config': self._extract_eslint_config(response),
            'gitignore': self._extract_gitignore(response)
        }
    
    def _generate_test_files(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成测试文件"""
        
        prompt = f"""为以下组件生成测试用例：

## 组件列表
"""
        for comp in components:
            prompt += f"- {comp['name']}: {', '.join(comp.get('functions', []))}\n"
        
        prompt += """

请生成：
1. 单元测试 - Jest测试用例
2. 集成测试 - 组件交互测试
3. E2E测试 - Cypress端到端测试

请提供完整的测试代码。
"""
        
        response = self._call_ai_model(prompt)
        
        return {
            'unit_tests': self._extract_unit_tests(response),
            'integration_tests': self._extract_integration_tests(response),
            'e2e_tests': self._extract_e2e_tests(response)
        }
    
    def _generate_simple_preview(self, components: List[Dict[str, Any]]) -> str:
        """为分开生成模式创建简单预览"""
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>组件概览</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; background: #f8fafc; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .component-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .component-card {{ background: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        .component-name {{ font-size: 18px; font-weight: 600; color: #2d3748; margin-bottom: 12px; }}
        .component-desc {{ color: #4a5568; margin-bottom: 16px; }}
        .component-functions {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .function-tag {{ background: #e2e8f0; color: #2d3748; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📦 组件架构概览</h1>
            <p>项目组件结构和功能说明</p>
        </div>
        <div class="component-grid">
"""
        
        for comp in components:
            functions = comp.get('functions', [])
            html += f"""
            <div class="component-card">
                <div class="component-name">{comp['name']}</div>
                <div class="component-desc">{comp.get('design_points', comp.get('type', ''))}</div>
                <div class="component-functions">
                    {''.join([f'<span class="function-tag">{func}</span>' for func in functions])}
        </div>
    </div>
"""
        
        html += """
    </div>
    </div>
</body>
</html>"""
        
        return html
    
    # 代码提取辅助方法
    def _extract_complete_html(self, response: str) -> str:
        """提取完整HTML代码"""
        import re
        
        # 查找```html...```块
        html_match = re.search(r'```html\s*\n(.*?)\n```', response, re.DOTALL)
        if html_match:
            return html_match.group(1).strip()
        
        # 查找DOCTYPE开头的HTML
        doctype_match = re.search(r'<!DOCTYPE html>.*?</html>', response, re.DOTALL | re.IGNORECASE)
        if doctype_match:
            return doctype_match.group(0).strip()
        
        return ""
    
    def _extract_html_body(self, response: str) -> str:
        """提取HTML body部分"""
        import re
        
        # 查找HTML部分标记
        html_section = re.search(r'\*\*HTML部分\*\*.*?```html\s*\n(.*?)\n```', response, re.DOTALL)
        if html_section:
            return html_section.group(1).strip()
        
        return ""
    
    def _extract_css_code(self, response: str) -> str:
        """提取CSS代码"""
        import re
        
        # 查找CSS部分标记
        css_section = re.search(r'\*\*CSS部分\*\*.*?```css\s*\n(.*?)\n```', response, re.DOTALL)
        if css_section:
            return css_section.group(1).strip()
        
        return ""
    
    def _extract_js_code(self, response: str) -> str:
        """提取JavaScript代码"""
        import re
        
        # 查找JavaScript部分标记
        js_section = re.search(r'\*\*JavaScript部分\*\*.*?```javascript\s*\n(.*?)\n```', response, re.DOTALL)
        if js_section:
            return js_section.group(1).strip()
        
        return ""
    
    def _extract_body_from_complete_html(self, html: str) -> str:
        """从完整HTML中提取body内容"""
        import re
        
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
        if body_match:
            content = body_match.group(1).strip()
            # 移除script标签
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            return content.strip()
        
        return ""
    
    def _extract_style_from_complete_html(self, html: str) -> str:
        """从完整HTML中提取CSS"""
        import re
        
        style_match = re.search(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
        if style_match:
            return style_match.group(1).strip()
        
        return ""
    
    def _extract_script_from_complete_html(self, html: str) -> str:
        """从完整HTML中提取JavaScript"""
        import re
        
        script_matches = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
        if script_matches:
            return '\n\n'.join([match.strip() for match in script_matches if match.strip()])
        
        return ""
    
    def _extract_colors(self, design_system: str) -> Dict[str, str]:
        """从设计系统中提取颜色定义"""
        # 简单的颜色提取逻辑
        return {
            'primary': '#007bff',
            'secondary': '#6c757d',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545'
        }
    
    def _extract_typography(self, design_system: str) -> Dict[str, str]:
        """从设计系统中提取字体定义"""
        return {
            'font_family': '-apple-system, BlinkMacSystemFont, sans-serif',
            'base_size': '16px',
            'scale': '1.2'
        }
    
    def _extract_spacing(self, design_system: str) -> Dict[str, str]:
        """从设计系统中提取间距定义"""
        return {
            'base_unit': '8px',
            'scale': '1, 2, 3, 4, 6, 8, 12, 16, 24'
        }
    
    def _analyze_generated_code(self, html: str) -> List[str]:
        """分析生成的代码质量"""
        notes = []
        
        if len(html) > 5000:
            notes.append("代码量较大，建议考虑模块化拆分")
        
        if 'responsive' in html.lower() or 'media' in html.lower():
            notes.append("已实现响应式设计")
        
        if 'accessibility' in html.lower() or 'aria-' in html.lower():
            notes.append("包含无障碍访问支持")
        
        return notes
    
    # 文档提取方法（简化实现）
    def _extract_readme(self, response: str) -> str:
        """提取README文档"""
        import re
        readme_match = re.search(r'README\.md.*?```markdown\s*\n(.*?)\n```', response, re.DOTALL)
        return readme_match.group(1).strip() if readme_match else ""
    
    def _extract_api_docs(self, response: str) -> str:
        """提取API文档"""
        import re
        api_match = re.search(r'API文档.*?```markdown\s*\n(.*?)\n```', response, re.DOTALL)
        return api_match.group(1).strip() if api_match else ""
    
    def _extract_deployment_guide(self, response: str) -> str:
        """提取部署指南"""
        import re
        deploy_match = re.search(r'部署指南.*?```markdown\s*\n(.*?)\n```', response, re.DOTALL)
        return deploy_match.group(1).strip() if deploy_match else ""
    
    def _extract_package_json(self, response: str) -> str:
        """提取package.json"""
        import re
        package_match = re.search(r'package\.json.*?```json\s*\n(.*?)\n```', response, re.DOTALL)
        return package_match.group(1).strip() if package_match else ""
    
    def _extract_webpack_config(self, response: str) -> str:
        """提取webpack配置"""
        import re
        webpack_match = re.search(r'webpack\.config\.js.*?```javascript\s*\n(.*?)\n```', response, re.DOTALL)
        return webpack_match.group(1).strip() if webpack_match else ""
    
    def _extract_eslint_config(self, response: str) -> str:
        """提取eslint配置"""
        import re
        eslint_match = re.search(r'\.eslintrc\.js.*?```javascript\s*\n(.*?)\n```', response, re.DOTALL)
        return eslint_match.group(1).strip() if eslint_match else ""
    
    def _extract_gitignore(self, response: str) -> str:
        """提取gitignore"""
        import re
        gitignore_match = re.search(r'\.gitignore.*?```\s*\n(.*?)\n```', response, re.DOTALL)
        return gitignore_match.group(1).strip() if gitignore_match else ""
    
    def _extract_unit_tests(self, response: str) -> str:
        """提取单元测试"""
        import re
        test_match = re.search(r'单元测试.*?```javascript\s*\n(.*?)\n```', response, re.DOTALL)
        return test_match.group(1).strip() if test_match else ""
    
    def _extract_integration_tests(self, response: str) -> str:
        """提取集成测试"""
        import re
        test_match = re.search(r'集成测试.*?```javascript\s*\n(.*?)\n```', response, re.DOTALL)
        return test_match.group(1).strip() if test_match else ""
    
    def _extract_e2e_tests(self, response: str) -> str:
        """提取端到端测试"""
        import re
        test_match = re.search(r'E2E测试.*?```javascript\s*\n(.*?)\n```', response, re.DOTALL)
        return test_match.group(1).strip() if test_match else ""
    
    def _call_ai_model(self, prompt: str) -> str:
        """Call AI model to generate prototype"""
        try:
            # Get model configuration
            model_config_name = "default"
            
            # Check if config is a Config object or dictionary
            if hasattr(self.config, 'get_module_config') and callable(getattr(self.config, 'get_module_config')):
                module_config = getattr(self.config, 'get_module_config')("prototype_generator")
                if module_config and hasattr(module_config, 'model_config'):
                    model_config_name = module_config.model_config
                elif hasattr(self.config, 'get_app_setting'):
                    model_config_name = getattr(self.config, 'get_app_setting')("default_model", "default")
            elif isinstance(self.config, dict):
                # Fallback to dictionary access
                model_config_name = self.config.get("model_config", "default")
            
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
        if not self.current_result or not self.current_result.complete_html:
            return "<html><body><h1>暂无预览内容</h1></body></html>"
        
        return self.current_result.complete_html
    
    def export_prototype(self, export_path: str, format_type: str = 'html') -> bool:
        """Export prototype to file"""
        try:
            if not self.current_result:
                return False
            
            if format_type == 'html':
                content = self.current_result.complete_html or self.generate_preview_html()
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            elif format_type == 'json':
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_result.to_dict(), f, 
                             ensure_ascii=False, indent=2)
            
            elif format_type == 'separate':
                # Export HTML, CSS, JS as separate files
                base_path = export_path.rsplit('.', 1)[0]
                
                if self.current_result.html_code:
                    with open(f"{base_path}.html", 'w', encoding='utf-8') as f:
                        f.write(self.current_result.html_code)
                
                if self.current_result.css_code:
                    with open(f"{base_path}.css", 'w', encoding='utf-8') as f:
                        f.write(self.current_result.css_code)
                
                if self.current_result.js_code:
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