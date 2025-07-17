"""
Frontend Integration Example - How to use Requirements Analyzer in UI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QLabel, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from src.core.requirement_analyzer import RequirementAnalyzer, RequirementType, RequirementPriority

class RequirementAnalysisWorker(QThread):
    """Worker thread for requirement analysis to avoid blocking UI"""
    
    progress_updated = pyqtSignal(int, str)
    analysis_completed = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, requirements_text, platform='web'):
        super().__init__()
        self.requirements_text = requirements_text
        self.platform = platform
        
    def run(self):
        try:
            self.progress_updated.emit(10, "初始化分析器...")
            analyzer = RequirementAnalyzer()
            
            # Connect analyzer signals to worker signals
            analyzer.progress_updated.connect(self.progress_updated.emit)
            analyzer.status_updated.connect(lambda msg: self.progress_updated.emit(-1, msg))
            
            self.progress_updated.emit(20, "开始分析需求...")
            
            result = analyzer.process({
                'text': self.requirements_text,
                'context': '现代化Web应用',
                'platform': self.platform
            })
            
            self.progress_updated.emit(100, "分析完成")
            self.analysis_completed.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class RequirementAnalyzerUI(QMainWindow):
    """示例UI界面，展示如何集成需求分析器"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("需求分析器 - 前端集成示例")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Input area
        layout.addWidget(QLabel("请输入项目需求:"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("""
示例需求：
我需要创建一个在线任务管理系统，功能包括：
1. 用户登录注册
2. 任务创建和编辑
3. 任务列表显示和筛选
4. 任务状态管理
5. 团队协作功能
6. 响应式设计支持
7. 数据导出功能

界面要求：
- 现代化设计风格
- 主色调为蓝色
- 左侧导航，右侧主内容
- 支持拖拽排序
        """)
        self.input_text.setMaximumHeight(200)
        layout.addWidget(self.input_text)
        
        # Analyze button
        self.analyze_button = QPushButton("开始分析需求")
        self.analyze_button.clicked.connect(self.start_analysis)
        layout.addWidget(self.analyze_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)
        
        # Results area
        layout.addWidget(QLabel("分析结果:"))
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)
        
        # Worker thread
        self.worker = None
        
    def start_analysis(self):
        """开始需求分析"""
        requirements_text = self.input_text.toPlainText().strip()
        if not requirements_text:
            self.status_label.setText("请输入需求内容")
            return
        
        # Disable button and show progress
        self.analyze_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_text.clear()
        
        # Start worker thread
        self.worker = RequirementAnalysisWorker(requirements_text)
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.analysis_completed.connect(self.on_analysis_completed)
        self.worker.error_occurred.connect(self.on_error_occurred)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()
        
    def on_progress_updated(self, percentage, message):
        """更新进度"""
        if percentage >= 0:
            self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        
    def on_analysis_completed(self, result):
        """处理分析完成"""
        # Format results for display
        output = self.format_analysis_result(result)
        self.results_text.setHtml(output)
        self.status_label.setText(f"分析完成 - 发现 {len(result.requirements)} 个需求")
        
    def on_error_occurred(self, error):
        """处理错误"""
        self.results_text.setPlainText(f"分析失败: {error}")
        self.status_label.setText("分析失败")
        
    def on_worker_finished(self):
        """清理工作线程"""
        self.analyze_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
    
    def format_analysis_result(self, result):
        """格式化分析结果为HTML显示"""
        html = f"""
        <h2>📊 项目概览</h2>
        <p><strong>项目描述:</strong> {result.project_overview or '未识别'}</p>
        <p><strong>目标用户:</strong> {result.target_audience or '未识别'}</p>
        <p><strong>目标平台:</strong> {result.platform}</p>
        
        <h2>📈 质量评分</h2>
        <p><strong>完整性:</strong> {result.completeness_score:.1%}</p>
        <p><strong>清晰度:</strong> {result.clarity_score:.1%}</p>
        <p><strong>可行性:</strong> {result.feasibility_score:.1%}</p>
        
        <h2>🎯 需求列表 ({len(result.requirements)} 个)</h2>
        """
        
        # Group requirements by type
        req_by_type = {}
        for req in result.requirements:
            req_type = req.type.value
            if req_type not in req_by_type:
                req_by_type[req_type] = []
            req_by_type[req_type].append(req)
        
        # Display requirements by type
        type_icons = {
            'functional': '⚙️',
            'ui_component': '🎨',
            'layout': '📐',
            'styling': '🎭',
            'interaction': '🖱️',
            'data': '📊',
            'performance': '⚡',
            'accessibility': '♿',
            'business': '💼'
        }
        
        priority_colors = {
            'critical': '#ff4757',
            'high': '#ff6b7a',
            'medium': '#ffa502',
            'low': '#2ed573'
        }
        
        for req_type, reqs in req_by_type.items():
            icon = type_icons.get(req_type, '📝')
            html += f"<h3>{icon} {req_type.title()} ({len(reqs)})</h3>"
            
            for req in reqs:
                priority_color = priority_colors.get(req.priority.value, '#333')
                html += f"""
                <div style="margin: 10px 0; padding: 10px; border-left: 4px solid {priority_color}; background: #f8f9fa;">
                    <strong>{req.title}</strong> 
                    <span style="color: {priority_color}; font-size: 0.9em;">({req.priority.value})</span>
                    <br>
                    <em>{req.description}</em>
                """
                
                if req.acceptance_criteria:
                    html += "<br><strong>验收条件:</strong><ul>"
                    for criteria in req.acceptance_criteria:
                        html += f"<li>{criteria}</li>"
                    html += "</ul>"
                
                if req.component_spec:
                    html += f"<br><strong>组件:</strong> {req.component_spec.name} ({req.component_spec.type})"
                
                html += "</div>"
        
        # Framework recommendations
        if result.framework_recommendations:
            html += f"""
            <h2>🛠️ 推荐技术栈</h2>
            <ul>
            """
            for framework in result.framework_recommendations:
                html += f"<li>{framework}</li>"
            html += "</ul>"
        
        # Development estimate
        if result.total_estimated_effort:
            html += f"""
            <h2>⏱️ 开发估算</h2>
            <p><strong>总体工作量:</strong> {result.total_estimated_effort}</p>
            """
            
            if result.development_phases:
                html += "<h3>开发阶段:</h3><ul>"
                for phase in result.development_phases:
                    html += f"""
                    <li><strong>{phase['name']}:</strong> {phase['description']} 
                    <em>({phase['estimated_duration']})</em></li>
                    """
                html += "</ul>"
        
        # Gaps and recommendations
        if result.gaps:
            html += f"""
            <h2>⚠️ 缺失项目 ({len(result.gaps)})</h2>
            <ul>
            """
            for gap in result.gaps:
                html += f"<li style='color: #e74c3c;'>{gap}</li>"
            html += "</ul>"
        
        if result.recommendations:
            html += f"""
            <h2>💡 改进建议 ({len(result.recommendations)})</h2>
            <ul>
            """
            for rec in result.recommendations:
                html += f"<li style='color: #3498db;'>{rec}</li>"
            html += "</ul>"
        
        return html

def main():
    """运行示例应用"""
    app = QApplication(sys.argv)
    app.setApplicationName("需求分析器 - 前端集成示例")
    
    window = RequirementAnalyzerUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()