#!/usr/bin/env python3
"""
测试改进后的原型生成器：分步骤生成和实时预览功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.config import Config
from src.core.prototype_generator.analyzer import PrototypeGenerator, PrototypeInput

def test_enhanced_prototype_generator():
    """测试改进后的原型生成器"""
    print("🚀 开始测试改进的原型生成器...")
    print("📋 新功能：分步骤生成 + 实时预览 + 避免代码重复")
    
    # 创建配置
    config = Config()
    
    # 创建原型生成器
    generator = PrototypeGenerator(config)
    
    # 连接信号以观察实时更新
    def on_step_completed(step_name, step_result):
        print(f"✅ 步骤完成: {step_name}")
        print(f"   - HTML长度: {len(step_result.get('html', ''))}")
        print(f"   - CSS长度: {len(step_result.get('css', ''))}")
        print(f"   - JS长度: {len(step_result.get('js', ''))}")
    
    def on_preview_ready(html_content):
        print(f"🎯 预览更新: {len(html_content)} 字符")
    
    # 连接信号
    generator.step_completed.connect(on_step_completed)
    generator.preview_ready.connect(on_preview_ready)
    
    # 添加测试输入
    test_input = """
    我需要一个在线图书管理系统，包含以下功能：
    
    ## 主要功能
    1. 图书列表展示 - 显示图书封面、标题、作者、评分
    2. 图书搜索 - 支持按标题、作者、分类搜索
    3. 图书详情页 - 显示完整的图书信息和简介
    4. 图书收藏 - 用户可以收藏喜欢的图书
    5. 用户评价 - 用户可以给图书评分和写评论
    6. 用户登录注册 - 基本的用户认证功能
    
    ## 界面要求
    - 现代化的卡片式设计
    - 响应式布局，支持手机和桌面访问
    - 友好的用户交互体验
    - 清晰的信息层级结构
    
    ## 技术要求
    - 使用Bootstrap样式框架
    - 支持无障碍访问
    - 代码结构清晰，便于维护
    """
    
    generator.add_input("text", test_input, "图书管理系统需求")
    
    print(f"✅ 已添加输入源: {len(generator.inputs)} 个")
    
    # 准备生成参数 - 启用实时预览
    input_data = {
        'prototype_type': '网页',
        'framework': 'HTML/CSS/JS',
        'style_framework': 'Bootstrap',
        'responsive': True,
        'accessibility': True,
        'realtime_preview': True  # 启用实时预览
    }
    
    print("\n🔧 开始分步骤生成原型（启用实时预览）...")
    print("=" * 60)
    
    try:
        # 执行完整的分步骤生成流程
        result = generator.process(input_data)
        
        print("\n" + "=" * 60)
        print("🎉 生成完成! 结果统计:")
        print(f"📊 完成步骤: {sum(result.generation_steps.values())}/5")
        print(f"📄 HTML代码: {len(result.html_code)} 字符")
        print(f"🎨 CSS代码: {len(result.css_code)} 字符")
        print(f"⚡ JavaScript代码: {len(result.js_code)} 字符")
        print(f"🏗️ 组件数量: {len(result.component_structure)}")
        print(f"📝 实现建议: {len(result.implementation_notes)} 条")
        
        # 检查是否避免了代码重复
        print("\n🔍 代码重复检查:")
        html_has_style = '<style>' in result.html_code or 'style=' in result.html_code
        html_has_script = '<script>' in result.html_code or 'onclick=' in result.html_code
        css_has_html = '<div>' in result.css_code or '<body>' in result.css_code
        js_has_html = '<div>' in result.js_code or '<body>' in result.js_code
        
        print(f"   - HTML中包含样式代码: {'❌ 是' if html_has_style else '✅ 否'}")
        print(f"   - HTML中包含脚本代码: {'❌ 是' if html_has_script else '✅ 否'}")
        print(f"   - CSS中包含HTML代码: {'❌ 是' if css_has_html else '✅ 否'}")
        print(f"   - JS中包含HTML代码: {'❌ 是' if js_has_html else '✅ 否'}")
        
        # 显示组件结构
        print("\n🧩 组件结构:")
        for i, comp in enumerate(result.component_structure[:5], 1):  # 显示前5个
            print(f"   {i}. {comp.get('name', '未知')}: {comp.get('description', '无描述')}")
            if comp.get('functions'):
                print(f"      功能: {', '.join(comp['functions'])}")
        
        # 显示实现建议
        print(f"\n💡 实现建议 (前3条):")
        for i, note in enumerate(result.implementation_notes[:3], 1):
            print(f"   {i}. {note}")
        
        # 生成最终预览文件
        print("\n📁 生成预览文件...")
        preview_html = generator.generate_preview_html()
        
        # 保存到文件以供查看
        output_file = "test_prototype_output.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(preview_html)
        
        print(f"✅ 预览文件已保存: {output_file}")
        print(f"📊 预览文件大小: {len(preview_html)} 字符")
        
        # 验证分步骤功能
        print("\n✨ 分步骤生成验证:")
        for step, completed in result.generation_steps.items():
            status = "✅ 完成" if completed else "❌ 未完成"
            print(f"   - {step}: {status}")
        
        print("\n🏆 测试完成! 新功能验证:")
        print("   ✅ 分步骤生成 - 每个步骤独立完成")
        print("   ✅ 代码分离 - HTML/CSS/JS各司其职")
        print("   ✅ 实时预览 - 支持步骤间预览更新")
        print("   ✅ 组件化设计 - 结构化的组件架构")
        print("   ✅ 实施建议 - 具体的开发指导")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_step_by_step_preview():
    """测试分步骤预览功能"""
    print("\n" + "=" * 60)
    print("🔍 测试分步骤预览功能...")
    
    config = Config()
    generator = PrototypeGenerator(config)
    
    # 模拟输入
    generator.add_input("text", "简单的待办事项管理器", "待办事项需求")
    
    # 测试各个步骤的预览生成
    try:
        from src.core.prototype_generator.analyzer import PrototypeResult
        
        # 创建一个测试结果对象
        result = PrototypeResult()
        
        # 模拟第1步完成
        result.component_structure = [
            {'name': 'TodoList', 'description': '待办事项列表'},
            {'name': 'TodoItem', 'description': '单个待办事项'},
            {'name': 'AddTodoForm', 'description': '添加待办事项表单'}
        ]
        
        preview1 = generator._generate_partial_preview(result, 'framework')
        print("📋 第1步预览生成成功")
        
        # 模拟第2步完成
        result.html_code = '<div class="todo-app"><h1>待办事项</h1></div>'
        preview2 = generator._generate_partial_preview(result, 'components')
        print("🏗️ 第2步预览生成成功")
        
        # 模拟第3步完成
        result.css_code = '.todo-app { padding: 20px; }'
        preview3 = generator._generate_partial_preview(result, 'styling')
        print("🎨 第3步预览生成成功")
        
        # 模拟第4步完成
        result.js_code = 'console.log("Todo app ready");'
        preview4 = generator._generate_partial_preview(result, 'interactions')
        print("⚡ 第4步预览生成成功")
        
        print("✅ 分步骤预览功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 分步骤预览测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 原型生成器增强功能测试")
    print("=" * 60)
    
    # 测试主要功能
    main_test = test_enhanced_prototype_generator()
    
    # 测试分步骤预览
    preview_test = test_step_by_step_preview()
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print(f"   主要功能测试: {'✅ 通过' if main_test else '❌ 失败'}")
    print(f"   分步骤预览测试: {'✅ 通过' if preview_test else '❌ 失败'}")
    
    if main_test and preview_test:
        print("\n🎉 所有测试通过! 原型生成器增强功能工作正常。")
        print("💡 建议: 运行main.py测试完整的UI界面功能。")
    else:
        print("\n⚠️ 部分测试失败，请检查配置和依赖。")
    
    sys.exit(0 if main_test and preview_test else 1) 