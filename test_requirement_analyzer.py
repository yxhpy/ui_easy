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
        # Initialize analyzer
        analyzer = RequirementAnalyzer()
        
        # Process requirements
        print("Processing requirements...")
        result = analyzer.process(test_input)
        
        print(f"\n✓ Analysis completed successfully!")
        print(f"Found {len(result.requirements)} requirements")
        print(f"Project: {result.project_overview}")
        print(f"Target audience: {result.target_audience}")
        print(f"Platform: {result.platform}")
        
        # Display requirements by type
        print(f"\nRequirements by type:")
        for req_type in RequirementType:
            type_reqs = result.get_requirements_by_type(req_type)
            if type_reqs:
                print(f"  {req_type.value}: {len(type_reqs)} requirements")
        
        # Display critical requirements
        critical_reqs = result.get_critical_requirements()
        print(f"\nCritical requirements: {len(critical_reqs)}")
        for req in critical_reqs:
            print(f"  - {req.title}")
        
        # Display framework recommendations
        if result.framework_recommendations:
            print(f"\nFramework recommendations:")
            for framework in result.framework_recommendations:
                print(f"  - {framework}")
        
        # Display gaps and recommendations
        if result.gaps:
            print(f"\nIdentified gaps:")
            for gap in result.gaps:
                print(f"  - {gap}")
        
        if result.recommendations:
            print(f"\nRecommendations:")
            for rec in result.recommendations:
                print(f"  - {rec}")
        
        # Test validator
        print(f"\n" + "="*50)
        print("Testing Requirement Validator...")
        
        validator = RequirementValidator()
        validation_result = validator.validate_analysis_result(result)
        
        print(f"\nValidation Results:")
        print(f"Overall Score: {validation_result['overall_score']:.2f}")
        
        print(f"\nCategory Scores:")
        for category, score in validation_result['category_scores'].items():
            print(f"  {category}: {score:.2f}")
        
        if validation_result['issues']:
            print(f"\nIssues found:")
            for issue in validation_result['issues'][:5]:  # Show first 5
                print(f"  - {issue}")
            if len(validation_result['issues']) > 5:
                print(f"  ... and {len(validation_result['issues']) - 5} more")
        
        if validation_result['warnings']:
            print(f"\nWarnings:")
            for warning in validation_result['warnings'][:3]:  # Show first 3
                print(f"  - {warning}")
            if len(validation_result['warnings']) > 3:
                print(f"  ... and {len(validation_result['warnings']) - 3} more")
        
        # Test JSON serialization
        print(f"\n" + "="*50)
        print("Testing JSON serialization...")
        
        analysis_dict = result.to_dict()
        print(f"✓ Analysis serialized successfully ({len(str(analysis_dict))} characters)")
        
        # Show sample requirement details
        if result.requirements:
            sample_req = result.requirements[0]
            print(f"\nSample requirement details:")
            print(f"Title: {sample_req.title}")
            print(f"Type: {sample_req.type.value}")
            print(f"Priority: {sample_req.priority.value}")
            print(f"Status: {sample_req.status.value}")
            if sample_req.acceptance_criteria:
                print(f"Acceptance criteria: {len(sample_req.acceptance_criteria)} items")
            if sample_req.component_spec:
                print(f"Component spec: {sample_req.component_spec.type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases and error handling"""
    
    print(f"\n" + "="*50)
    print("Testing edge cases...")
    
    analyzer = RequirementAnalyzer()
    
    # Test empty input
    try:
        result = analyzer.process({'text': '', 'platform': 'web'})
        print("❌ Should have failed with empty input")
        return False
    except ValueError:
        print("✓ Empty input handled correctly")
    
    # Test minimal input
    try:
        result = analyzer.process({
            'text': 'Create a simple login page',
            'platform': 'web'
        })
        print(f"✓ Minimal input processed ({len(result.requirements)} requirements found)")
    except Exception as e:
        print(f"❌ Minimal input failed: {str(e)}")
        return False
    
    # Test complex input
    complex_text = """
    Build a comprehensive e-commerce platform with the following features:
    
    Frontend Requirements:
    - Modern responsive design using React/Vue.js
    - Product catalog with search and filtering
    - Shopping cart with real-time updates
    - User authentication and profiles
    - Order tracking and history
    - Payment integration (Stripe/PayPal)
    - Admin dashboard for inventory management
    
    Backend Requirements:
    - RESTful API with authentication
    - Database design for products, users, orders
    - File upload for product images
    - Email notifications
    - Inventory management system
    - Analytics and reporting
    
    Performance Requirements:
    - Support 10,000 concurrent users
    - Page load time < 2 seconds
    - 99.9% uptime
    - Mobile-first responsive design
    
    Security Requirements:
    - HTTPS encryption
    - Input validation and sanitization
    - Rate limiting
    - Data backup and recovery
    """
    
    try:
        result = analyzer.process({
            'text': complex_text,
            'context': 'Enterprise e-commerce solution',
            'platform': 'web'
        })
        print(f"✓ Complex input processed ({len(result.requirements)} requirements found)")
        
        # Check that we have diverse requirement types
        types_found = set(req.type for req in result.requirements)
        if len(types_found) >= 3:
            print(f"✓ Diverse requirement types identified: {len(types_found)}")
        else:
            print(f"⚠ Limited requirement type diversity: {len(types_found)}")
        
    except Exception as e:
        print(f"❌ Complex input failed: {str(e)}")
        return False
    
    return True

def test_validator_standalone():
    """Test validator with manually created requirements"""
    
    print(f"\n" + "="*50)
    print("Testing validator with sample requirements...")
    
    from src.core.requirement_analyzer.models import (
        Requirement, AnalysisResult, ComponentSpec, RequirementStatus
    )
    
    # Create sample requirements
    requirements = [
        Requirement(
            title="User Login",
            description="Users must be able to log in with email and password",
            type=RequirementType.FUNCTIONAL,
            priority=RequirementPriority.CRITICAL,
            acceptance_criteria=[
                "User enters valid email and password",
                "System authenticates user",
                "User is redirected to dashboard"
            ]
        ),
        Requirement(
            title="Login Button",
            description="A blue login button",
            type=RequirementType.UI_COMPONENT,
            priority=RequirementPriority.HIGH,
            component_spec=ComponentSpec(
                name="LoginButton",
                type="button",
                properties={"color": "blue", "size": "medium"},
                events=["click"]
            )
        ),
        Requirement(
            title="Fast Performance",
            description="The app should be fast",
            type=RequirementType.PERFORMANCE,
            priority=RequirementPriority.MEDIUM,
            status=RequirementStatus.AMBIGUOUS
        )
    ]
    
    analysis = AnalysisResult(
        requirements=requirements,
        project_overview="A sample application",
        target_audience="General users",
        platform="web"
    )
    
    validator = RequirementValidator()
    validation_result = validator.validate_analysis_result(analysis)
    
    print(f"Validation score: {validation_result['overall_score']:.2f}")
    print(f"Requirements validated: {len(requirements)}")
    
    if validation_result['issues']:
        print(f"Issues found: {len(validation_result['issues'])}")
        for issue in validation_result['issues']:
            print(f"  - {issue}")
    
    if validation_result['warnings']:
        print(f"Warnings: {len(validation_result['warnings'])}")
        for warning in validation_result['warnings']:
            print(f"  - {warning}")
    
    return True

if __name__ == "__main__":
    print("Requirements Analyzer Test Suite")
    print("="*50)
    
    success = True
    
    # Run main test
    if not test_requirements_analysis():
        success = False
    
    # Run edge case tests
    if not test_edge_cases():
        success = False
    
    # Run validator tests
    if not test_validator_standalone():
        success = False
    
    print(f"\n" + "="*50)
    if success:
        print("✅ All tests passed!")
        print("\nRequirements Analyzer is ready for frontend development!")
        print("\nKey features available:")
        print("- Comprehensive requirement extraction and categorization")
        print("- Component, layout, and interaction specification")
        print("- Validation and quality scoring")
        print("- Gap analysis and recommendations")
        print("- Framework recommendations")
        print("- Development effort estimation")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    exit(0 if success else 1)