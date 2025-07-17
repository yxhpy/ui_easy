"""
Image Analyzer Module - Analyzes design images and generates design documentation
"""

import base64
import io
from typing import Dict, Any, Optional, List
from PIL import Image
from ..base_module import BaseModule
from ..config import Config
from ...models.model_factory import ModelFactory

class ImageAnalyzer(BaseModule):
    """Analyzes design images using powerful AI models"""
    
    def __init__(self, config: Optional[Config] = None):
        super().__init__("Image Analyzer", config)
        self.config_manager = config or Config()
        self.model_factory = ModelFactory(self.config_manager)
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process design image and generate documentation
        
        Args:
            input_data: Dict containing:
                - image_path: str - Path to the image file
                - analysis_type: str - Type of analysis (full, layout, colors, etc.)
                - custom_prompt: str - Optional custom prompt
        
        Returns:
            Dict containing analysis results
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data")
        
        image_path = input_data.get('image_path')
        analysis_type = input_data.get('analysis_type', 'full')
        custom_prompt = input_data.get('custom_prompt')
        
        self.update_progress(10, "Loading image...")
        
        # Load and process image
        image_data = self._load_image(image_path)
        
        self.update_progress(30, "Preparing analysis...")
        
        # Get analysis prompt
        prompt = self._get_analysis_prompt(analysis_type, custom_prompt)
        
        self.update_progress(50, "Analyzing design...")
        
        # Get model for analysis
        module_config = self.config_manager.get_module_config("image_analyzer")
        model_config_name = module_config.model_config if module_config else "powerful_model"
        model = self.model_factory.get_model(model_config_name)
        
        # Perform analysis with streaming
        analysis_result = ""
        try:
            for chunk in model.analyze_image_stream(image_data, prompt):
                analysis_result += chunk
                # Emit streaming text signal
                self.streaming_text_updated.emit(chunk)
        except AttributeError:
            # Fallback to non-streaming if not supported
            analysis_result = model.analyze_image(image_data, prompt)
        
        self.update_progress(80, "Processing results...")
        
        # Structure the results
        result = self._structure_analysis_result(analysis_result, analysis_type)
        
        self.update_progress(100, "Analysis complete")
        
        return result
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data"""
        if not isinstance(input_data, dict):
            return False
        
        image_path = input_data.get('image_path')
        if not image_path:
            return False
        
        # Check if file exists and is an image
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def _load_image(self, image_path: str) -> str:
        """Load image and convert to base64"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large (max 1024x1024 for most APIs)
                max_size = 1024
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return image_data
                
        except Exception as e:
            raise ValueError(f"Failed to load image: {str(e)}")
    
    def _get_analysis_prompt(self, analysis_type: str, custom_prompt: Optional[str] = None) -> str:
        """Get analysis prompt based on type"""
        if custom_prompt:
            return custom_prompt
        
        module_config = self.config_manager.get_module_config("image_analyzer")
        base_prompt = module_config.custom_prompts.get("analyze_design", "") if module_config else ""
        
        prompts = {
            "full": f"""{base_prompt}

作为一名专业的UI/UX设计师和前端工程师，请对这个设计图进行详细分析，提供可直接用于前端开发的具体规范：

## 1. 布局与结构 (Layout & Structure)
- 整体布局类型：网格布局/弹性布局/固定布局
- 页面宽度：具体像素值或百分比
- 主要区域划分：头部、导航、内容区、侧边栏、底部等具体尺寸
- 网格系统：列数、间距、断点设置
- 响应式设计：不同屏幕尺寸下的布局变化

## 2. 精确尺寸规范 (Exact Dimensions)
- 容器宽度：最大宽度、最小宽度
- 内边距(padding)：上下左右具体数值
- 外边距(margin)：组件间距具体数值
- 边框宽度：具体像素值
- 圆角半径：具体数值(border-radius)

## 3. 色彩规范 (Color Specifications)
- 主色调：精确的HEX/RGB颜色值
- 辅助色：精确的颜色值及使用场景
- 文字颜色：标题、正文、链接、禁用状态的具体色值
- 背景色：页面背景、卡片背景、悬停状态等色值
- 边框颜色：默认、选中、错误状态的具体色值
- 透明度：具体的opacity或rgba值

## 4. 字体设计规范 (Typography Specifications)
- 字体族：具体字体名称（如：PingFang SC, Helvetica Neue等）
- 字体大小：各级标题和正文的具体px/rem值
- 字重：font-weight具体数值(100-900)
- 行高：line-height具体数值或倍数
- 字间距：letter-spacing具体数值
- 段落间距：具体的margin-bottom值

## 5. UI组件详细规范 (Detailed Component Specs)
对每个组件提供：
- 按钮：尺寸、内边距、圆角、颜色、悬停效果、禁用状态
- 输入框：高度、内边距、边框样式、聚焦状态、错误状态
- 卡片：阴影效果(box-shadow)、圆角、内边距
- 导航：菜单项间距、激活状态样式、下拉菜单规范
- 图标：大小、颜色、间距、对齐方式

## 6. 状态设计 (State Design)
- 默认状态(default)：基础样式
- 悬停状态(hover)：鼠标悬停时的变化
- 激活状态(active)：点击或选中时的样式
- 禁用状态(disabled)：不可交互时的样式
- 加载状态(loading)：数据加载时的显示

## 7. 动画与交互 (Animation & Interaction)
- 过渡效果：transition具体参数(duration, timing-function)
- 动画效果：animation具体实现方式
- 微交互：按钮点击、表单验证等反馈效果
- 页面切换：路由跳转的过渡动画

## 8. 前端实现建议 (Frontend Implementation)
- CSS框架建议：Bootstrap、Tailwind CSS等
- 组件库推荐：Ant Design、Element UI等
- 响应式断点：具体的媒体查询断点
- CSS变量定义：主要颜色、字体、间距的CSS变量
- 浏览器兼容性要求

请确保每个数值都尽可能精确，避免使用"较大"、"适中"等模糊描述。
所有测量数值应该基于常见的8px或4px网格系统。
提供的规范应该足够详细，让前端工程师可以直接按照规范进行开发，不需要再次猜测。""",

            "layout": """详细分析这个设计的布局结构，提供具体的前端实现参数：

## 布局分析要求：
1. 整体布局模式：Flexbox/Grid/Float布局
2. 页面最大宽度：具体像素值
3. 各区域尺寸：头部高度、侧边栏宽度、内容区宽度等
4. 网格系统：列数、gutters间距、容器padding
5. 组件对齐：左对齐/居中/右对齐的具体实现方式
6. 垂直节奏：各部分的垂直间距规律(如：8px的倍数)
7. 响应式断点：mobile(<768px), tablet(768-1024px), desktop(>1024px)的具体布局变化

请提供具体的CSS Grid或Flexbox参数。""",

            "colors": """分析这个设计的色彩使用，提供精确的颜色规范：

## 颜色分析要求：
1. 主色调：精确的HEX值(如：#1890ff)
2. 辅助色系：2-3个辅助色的HEX值及使用场景
3. 中性色：灰色系的完整色阶(如：#000000, #333333, #666666, #999999, #cccccc, #f0f0f0, #ffffff)
4. 功能色：成功(success)、警告(warning)、错误(error)、信息(info)的具体色值
5. 文字颜色：主文字、次要文字、禁用文字的具体色值
6. 背景色：页面背景、卡片背景、悬停背景等
7. 边框颜色：默认边框、聚焦边框、错误边框的色值
8. 色彩对比度：确保符合WCAG无障碍标准

请为每种颜色提供使用场景和CSS变量命名建议。""",

            "components": """识别并详细分析所有UI组件，提供具体的开发规范：

## 组件分析要求：
1. 按钮组件：
   - 尺寸：高度、最小宽度、内边距
   - 圆角：border-radius具体数值
   - 字体：大小、字重、颜色
   - 状态：默认、hover、active、disabled的具体样式

2. 输入框组件：
   - 尺寸：高度、内边距
   - 边框：宽度、颜色、圆角
   - 状态：聚焦、错误、禁用的样式变化

3. 导航组件：
   - 菜单项间距、高度
   - 激活状态的视觉表现
   - 下拉菜单的具体实现

4. 卡片组件：
   - 阴影效果：box-shadow参数
   - 圆角、内边距、外边距
   - 悬停效果变化

5. 图标规范：
   - 标准尺寸(16px, 20px, 24px等)
   - 颜色使用规则
   - 与文字的对齐方式

请为每个组件提供完整的CSS类定义示例。"""
        }
        
        return prompts.get(analysis_type, prompts["full"])
    
    def _structure_analysis_result(self, raw_result: str, analysis_type: str) -> Dict[str, Any]:
        """Structure the analysis result into organized format"""
        structured_data = self._parse_analysis_sections(raw_result)
        
        return {
            "analysis_type": analysis_type,
            "raw_analysis": raw_result,
            "timestamp": self._get_timestamp(),
            "structured_data": structured_data,
            "frontend_specs": self._extract_frontend_specs(structured_data),
            "implementation_guide": self._generate_implementation_guide(structured_data),
            "metadata": {
                "model_used": self._get_model_name(),
                "confidence_score": self._estimate_confidence(raw_result),
                "specs_completeness": self._assess_specs_completeness(structured_data)
            }
        }
    
    def _parse_analysis_sections(self, text: str) -> Dict[str, str]:
        """Parse analysis text into sections"""
        sections = {}
        current_section = "overview"
        current_content = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a section header
            if any(keyword in line.lower() for keyword in ['layout', 'color', 'typography', 'component', 'ux', 'recommendation']):
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.lower().replace(':', '').replace('#', '').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_model_name(self) -> str:
        """Get the name of the model used"""
        module_config = self.config_manager.get_module_config("image_analyzer")
        if module_config:
            model_config = self.config_manager.get_model_config(module_config.model_config)
            return model_config.name if model_config else "Unknown"
        return "Unknown"
    
    def _estimate_confidence(self, text: str) -> float:
        """Estimate confidence score based on analysis quality"""
        # Simple heuristic based on content length and structure
        if len(text) < 100:
            return 0.3
        elif len(text) < 500:
            return 0.6
        elif len(text) > 1000:
            return 0.9
        else:
            return 0.7
    
    def _extract_frontend_specs(self, structured_data: Dict[str, str]) -> Dict[str, Any]:
        """Extract specific frontend development specifications"""
        specs = {
            "colors": self._extract_color_specs(structured_data),
            "typography": self._extract_typography_specs(structured_data),
            "layout": self._extract_layout_specs(structured_data),
            "components": self._extract_component_specs(structured_data),
            "spacing": self._extract_spacing_specs(structured_data)
        }
        return specs
    
    def _extract_color_specs(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Extract color specifications from analysis"""
        import re
        color_data = {}
        
        # Look for color-related sections
        color_sections = [section for key, section in data.items() 
                         if any(keyword in key.lower() for keyword in ['color', '色彩', '颜色'])]
        
        for section in color_sections:
            # Extract HEX colors
            hex_colors = re.findall(r'#[0-9A-Fa-f]{6}', section)
            if hex_colors:
                color_data['hex_colors'] = list(set(hex_colors))
            
            # Extract RGB colors
            rgb_colors = re.findall(r'rgb\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)', section)
            if rgb_colors:
                color_data['rgb_colors'] = list(set(rgb_colors))
        
        return color_data
    
    def _extract_typography_specs(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Extract typography specifications"""
        import re
        typography_data = {}
        
        # Look for typography-related sections
        typography_sections = [section for key, section in data.items() 
                              if any(keyword in key.lower() for keyword in ['typography', 'font', '字体', '文字'])]
        
        for section in typography_sections:
            # Extract font sizes
            font_sizes = re.findall(r'(\d+)px', section)
            if font_sizes:
                typography_data['font_sizes'] = [int(size) for size in set(font_sizes)]
            
            # Extract font weights
            font_weights = re.findall(r'font-weight:\s*(\d+)', section)
            if font_weights:
                typography_data['font_weights'] = [int(weight) for weight in set(font_weights)]
        
        return typography_data
    
    def _extract_layout_specs(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Extract layout specifications"""
        import re
        layout_data = {}
        
        # Look for layout-related sections
        layout_sections = [section for key, section in data.items() 
                          if any(keyword in key.lower() for keyword in ['layout', 'structure', '布局', '结构'])]
        
        for section in layout_sections:
            # Extract pixel values for dimensions
            dimensions = re.findall(r'(\d+)px', section)
            if dimensions:
                layout_data['dimensions'] = [int(dim) for dim in set(dimensions)]
            
            # Extract percentage values
            percentages = re.findall(r'(\d+)%', section)
            if percentages:
                layout_data['percentages'] = [int(pct) for pct in set(percentages)]
        
        return layout_data
    
    def _extract_component_specs(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Extract component specifications"""
        import re
        component_data = {}
        
        # Look for component-related sections
        component_sections = [section for key, section in data.items() 
                             if any(keyword in key.lower() for keyword in ['component', 'button', 'input', '组件', '按钮'])]
        
        for section in component_sections:
            # Extract border-radius values
            border_radius = re.findall(r'border-radius:\s*(\d+)px', section)
            if border_radius:
                component_data['border_radius'] = [int(radius) for radius in set(border_radius)]
            
            # Extract padding values
            padding = re.findall(r'padding:\s*(\d+)px', section)
            if padding:
                component_data['padding'] = [int(pad) for pad in set(padding)]
        
        return component_data
    
    def _extract_spacing_specs(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Extract spacing specifications"""
        import re
        spacing_data = {}
        
        # Look for spacing-related information across all sections
        all_text = ' '.join(data.values())
        
        # Extract margin values
        margins = re.findall(r'margin[^:]*:\s*(\d+)px', all_text)
        if margins:
            spacing_data['margins'] = [int(margin) for margin in set(margins)]
        
        # Extract padding values
        paddings = re.findall(r'padding[^:]*:\s*(\d+)px', all_text)
        if paddings:
            spacing_data['paddings'] = [int(padding) for padding in set(paddings)]
        
        # Extract gap values
        gaps = re.findall(r'gap:\s*(\d+)px', all_text)
        if gaps:
            spacing_data['gaps'] = [int(gap) for gap in set(gaps)]
        
        return spacing_data
    
    def _generate_implementation_guide(self, structured_data: Dict[str, str]) -> Dict[str, Any]:
        """Generate practical implementation guide for frontend developers"""
        guide = {
            "css_variables": self._generate_css_variables(structured_data),
            "responsive_breakpoints": self._extract_breakpoints(structured_data),
            "component_classes": self._suggest_component_classes(structured_data),
            "development_checklist": self._create_development_checklist()
        }
        return guide
    
    def _generate_css_variables(self, data: Dict[str, str]) -> Dict[str, str]:
        """Generate CSS custom properties based on analysis"""
        import re
        variables = {}
        
        # Extract colors and create CSS variables
        all_text = ' '.join(data.values())
        hex_colors = re.findall(r'#[0-9A-Fa-f]{6}', all_text)
        
        for i, color in enumerate(set(hex_colors)):
            variables[f'--color-{i+1}'] = color
        
        # Extract common pixel values for spacing
        pixel_values = re.findall(r'(\d+)px', all_text)
        common_values = [int(val) for val in pixel_values if int(val) % 4 == 0]  # 4px grid system
        
        for i, value in enumerate(sorted(set(common_values))[:10]):  # Top 10 common values
            variables[f'--spacing-{i+1}'] = f'{value}px'
        
        return variables
    
    def _extract_breakpoints(self, data: Dict[str, str]) -> Dict[str, str]:
        """Extract responsive breakpoints"""
        import re
        breakpoints = {}
        
        all_text = ' '.join(data.values()).lower()
        
        # Look for common breakpoint patterns
        if 'mobile' in all_text or '768px' in all_text:
            breakpoints['mobile'] = 'max-width: 767px'
        if 'tablet' in all_text or '1024px' in all_text:
            breakpoints['tablet'] = 'min-width: 768px and max-width: 1023px'
        if 'desktop' in all_text:
            breakpoints['desktop'] = 'min-width: 1024px'
        
        return breakpoints
    
    def _suggest_component_classes(self, data: Dict[str, str]) -> List[str]:
        """Suggest CSS class names for components"""
        classes = []
        
        # Based on common component types mentioned
        all_text = ' '.join(data.values()).lower()
        
        if any(word in all_text for word in ['button', '按钮']):
            classes.extend(['.btn', '.btn-primary', '.btn-secondary', '.btn-disabled'])
        
        if any(word in all_text for word in ['input', '输入', 'form']):
            classes.extend(['.form-input', '.form-group', '.form-error'])
        
        if any(word in all_text for word in ['card', '卡片']):
            classes.extend(['.card', '.card-header', '.card-body', '.card-footer'])
        
        if any(word in all_text for word in ['nav', '导航']):
            classes.extend(['.nav', '.nav-item', '.nav-link', '.nav-active'])
        
        return classes
    
    def _create_development_checklist(self) -> List[str]:
        """Create a development checklist for frontend implementation"""
        return [
            "设置CSS变量和设计token",
            "创建响应式网格系统",
            "实现基础组件样式",
            "添加交互状态（hover, active, disabled）",
            "确保无障碍访问性（WCAG标准）",
            "测试不同屏幕尺寸的显示效果",
            "优化加载性能和动画效果",
            "进行跨浏览器兼容性测试"
        ]
    
    def _assess_specs_completeness(self, structured_data: Dict[str, str]) -> float:
        """Assess how complete the specifications are for frontend development"""
        required_elements = [
            'color', 'font', 'layout', 'component', 'spacing', 
            '颜色', '字体', '布局', '组件', '间距'
        ]
        
        all_text = ' '.join(structured_data.values()).lower()
        found_elements = sum(1 for element in required_elements if element in all_text)
        
        # Also check for specific technical details
        technical_details = ['px', 'rem', 'hex', 'rgb', 'margin', 'padding', 'border-radius']
        found_details = sum(1 for detail in technical_details if detail in all_text)
        
        # Calculate completeness score
        element_score = found_elements / len(required_elements)
        detail_score = min(found_details / len(technical_details), 1.0)
        
        return (element_score + detail_score) / 2