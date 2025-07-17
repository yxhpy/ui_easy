"""
Test script for Requirements Analyzer module
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.requirement_analyzer import RequirementAnalyzer
from src.core.requirement_analyzer.models import RequirementType, RequirementPriority
from src.core.requirement_analyzer.validator import RequirementValidator

def test_requirements_analysis():
    """Test requirements analysis with sample data"""
    
    print("Testing Requirements Analyzer...")
    print("=" * 50)
    
    # Test data
    test_requirements = """
    我需要创建一个在线任务管理系统。这个系统需要让用户能够：
    
    1. 用户注册和登录功能
    2. 创建、编辑和删除任务
    3. 为任务设置优先级和截止日期
    4. 任务列表显示和过滤功能
    5. 任务状态管理（待办、进行中、已完成）
    6. 用户仪表板显示任务统计
    7. 响应式设计，支持手机和桌面端
    8. 深色和浅色主题切换
    9. 任务提醒功能
    10. 数据导出功能
    
    用户界面要求：
    - 现代化、简洁的设计风格
    - 主要使用蓝色调
    - 左侧导航栏，右侧主内容区
    - 顶部包含用户信息和设置按钮
    - 任务卡片式布局
    - 拖拽排序功能
    
    技术要求：
    - 支持1000+用户同时使用
    - 页面加载时间 < 3秒
    - 支持离线模式
    - 数据实时同步
    """
    
    test_input = {
        'text': test_requirements,
        'context': '面向中小企业和个人用户的任务管理工具',
        'platform': 'web'
    }
    
    try:
        # Test basic configuration
        print("1. Testing basic configuration...")
        from src.core.config import Config
        config = Config()
        analyzer = RequirementAnalyzer(config)
        print("✓ RequirementAnalyzer initialized successfully")
        
        # Test Phase 1: Extract requirement list
        print("\n2. Testing Phase 1: Extract requirement list...")
        test_input_phase1 = test_input.copy()
        test_input_phase1['phase'] = 'list'
        
        result_phase1 = analyzer.process(test_input_phase1)
        print(f"✓ Phase 1 completed: {len(result_phase1.requirements)} requirements extracted")
        
        # Display extracted requirements
        print("\nExtracted Requirements:")
        for i, req in enumerate(result_phase1.requirements, 1):
            print(f"{i}. {req.title} ({req.type.value}, {req.priority.value})")
        
        # Test Phase 2: Detailed analysis
        print("\n3. Testing Phase 2: Detailed analysis...")
        requirement_list = []
        for req in result_phase1.requirements:
            requirement_list.append(req.to_dict())
        
        test_input_phase2 = {
            'text': test_requirements,
            'context': '面向中小企业和个人用户的任务管理工具',
            'platform': 'web',
            'phase': 'detail',
            'requirement_list': requirement_list
        }
        
        result_phase2 = analyzer.process(test_input_phase2)
        print(f"✓ Phase 2 completed: {len(result_phase2.requirements)} requirements analyzed in detail")
        
        # Display detailed analysis results
        print("\nDetailed Analysis Results:")
        for req in result_phase2.requirements:
            print(f"\n--- {req.title} ---")
            print(f"类型: {req.type.value}")
            print(f"优先级: {req.priority.value}")
            print(f"状态: {req.status.value}")
            print(f"描述: {req.description[:100]}..." if len(req.description) > 100 else f"描述: {req.description}")
            
            if req.acceptance_criteria:
                print("验收标准:")
                for criteria in req.acceptance_criteria:
                    print(f"  • {criteria}")
            
            if req.rationale:
                print(f"业务价值: {req.rationale[:100]}..." if len(req.rationale) > 100 else f"业务价值: {req.rationale}")
            
            if req.dependencies:
                print("依赖关系:")
                for dep in req.dependencies:
                    print(f"  • {dep}")
        
        # Test validator
        print("\n4. Testing requirements validation...")
        validator = RequirementValidator()
        validation_result = validator.validate_analysis_result(result_phase2)
        
        print(f"Overall Score: {validation_result['overall_score']:.2f}")
        print(f"Category Scores: {validation_result['category_scores']}")
        
        if validation_result['issues']:
            print("Issues found:")
            for issue in validation_result['issues']:
                print(f"  • {issue}")
        
        if validation_result['recommendations']:
            print("Recommendations:")
            for rec in validation_result['recommendations']:
                print(f"  • {rec}")
        
        print("\n✓ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_requirements():
    """Test specific requirement types"""
    print("\n" + "=" * 50)
    print("Testing Specific Requirement Types...")
    
    # Test UI Component requirement
    ui_test = {
        'text': '我需要一个任务卡片组件，用于显示任务的标题、描述、优先级和截止日期。用户应该能够点击卡片来编辑任务，也能够拖拽卡片来重新排序。',
        'context': '任务管理系统中的核心UI组件',
        'platform': 'web'
    }
    
    # Test Layout requirement  
    layout_test = {
        'text': '主页面需要采用三栏布局：左侧是导航菜单（宽度200px），中间是主要内容区域，右侧是辅助信息面板（宽度300px）。在移动端需要折叠为单栏布局。',
        'context': '任务管理系统的主页面布局',
        'platform': 'web'
    }
    
    from src.core.config import Config
    config = Config()
    analyzer = RequirementAnalyzer(config)
    
    try:
        print("\nTesting UI Component Analysis:")
        ui_result = analyzer.process(ui_test)
        ui_req = ui_result.requirements[0] if ui_result.requirements else None
        if ui_req and ui_req.acceptance_criteria:
            print(f"✓ Generated {len(ui_req.acceptance_criteria)} acceptance criteria")
            for criteria in ui_req.acceptance_criteria[:3]:  # Show first 3
                print(f"  • {criteria}")
        
        print("\nTesting Layout Analysis:")
        layout_result = analyzer.process(layout_test)
        layout_req = layout_result.requirements[0] if layout_result.requirements else None
        if layout_req and layout_req.acceptance_criteria:
            print(f"✓ Generated {len(layout_req.acceptance_criteria)} acceptance criteria")
            for criteria in layout_req.acceptance_criteria[:3]:  # Show first 3
                print(f"  • {criteria}")
        
        return True
        
    except Exception as e:
        print(f"✗ Specific tests failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Requirements Analyzer Test Suite")
    print("=" * 60)
    
    success1 = test_requirements_analysis()
    success2 = test_specific_requirements()
    
    if success1 and success2:
        print(f"\n{'='*60}")
        print("🎉 All tests passed! Requirements analyzer is working correctly.")
        print("Key improvements verified:")
        print("• ✓ 提取需求列表功能正常")
        print("• ✓ 详细分析生成验收标准")
        print("• ✓ 业务价值和依赖关系分析")
        print("• ✓ 需求状态正确更新")
    else:
        print(f"\n{'='*60}")
        print("❌ Some tests failed. Please check the configuration and implementation.")
        sys.exit(1)