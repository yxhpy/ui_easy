#!/usr/bin/env python3
"""
测试原型生成器的分步生成功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.config import Config
from src.core.prototype_generator.analyzer import PrototypeGenerator, PrototypeInput

def test_prototype_generator():
    """测试原型生成器的分步功能"""
    print("🚀 开始测试原型生成器...")
    
    # 创建配置
    config = Config()
    
    # 创建原型生成器
    generator = PrototypeGenerator(config)
    
    # 添加测试输入
    test_input = """
    我需要一个简单的任务管理系统，包含以下功能：
    1. 任务列表显示
    2. 添加新任务
    3. 标记任务完成
    4. 删除任务
    5. 任务搜索功能
    
    界面要求：
    - 简洁现代的设计
    - 响应式布局
    - 用户友好的交互
    """
    
    generator.add_input("text", test_input, "任务管理系统需求")
    
    print(f"✅ 已添加输入源: {len(generator.inputs)} 个")
    
    # 准备生成参数
    input_data = {
        'prototype_type': '网页',
        'framework': 'HTML/CSS/JS',
        'style_framework': 'Bootstrap',
        'responsive': True,
        'accessibility': True
    }
    
    print("🔧 开始分步生成原型...")
    
    try:
        # 测试各个生成步骤
        
        # 1. 测试设计理念生成
        print("\n📝 测试设计理念生成...")
        rationale = generator._generate_design_rationale(
            generator.inputs, 
            input_data['prototype_type'],
            input_data['framework'],
            input_data['style_framework'],
            input_data['responsive'],
            input_data['accessibility']
        )
        print(f"✅ 设计理念生成成功 ({len(rationale)} 字符)")
        print(f"预览: {rationale[:100]}...")
        
        # 2. 测试组件结构生成
        print("\n🧩 测试组件结构生成...")
        components = generator._generate_component_structure(
            generator.inputs,
            input_data['prototype_type'],
            input_data['framework']
        )
        print(f"✅ 组件结构生成成功 ({len(components)} 个组件)")
        for comp in components[:3]:  # 显示前3个组件
            print(f"  - {comp['name']}: {comp['description']}")
        
        # 3. 测试HTML代码生成
        print("\n🏗️ 测试HTML代码生成...")
        html_code = generator._generate_html_code(
            generator.inputs,
            components,
            input_data['prototype_type'],
            input_data['framework']
        )
        print(f"✅ HTML代码生成成功 ({len(html_code)} 字符)")
        print(f"预览: {html_code[:100]}...")
        
        # 4. 测试CSS代码生成
        print("\n🎨 测试CSS代码生成...")
        css_code = generator._generate_css_code(
            generator.inputs,
            components,
            input_data['style_framework'],
            input_data['responsive'],
            input_data['accessibility']
        )
        print(f"✅ CSS代码生成成功 ({len(css_code)} 字符)")
        print(f"预览: {css_code[:100]}...")
        
        # 5. 测试JavaScript代码生成
        print("\n⚡ 测试JavaScript代码生成...")
        js_code = generator._generate_js_code(
            generator.inputs,
            components,
            input_data['framework']
        )
        print(f"✅ JavaScript代码生成成功 ({len(js_code)} 字符)")
        print(f"预览: {js_code[:100]}...")
        
        print("\n🎉 所有分步测试都成功完成！")
        print("✨ 新的分步生成方式避免了JSON解析错误，更加稳定可靠。")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_prototype_generator()
    sys.exit(0 if success else 1) 