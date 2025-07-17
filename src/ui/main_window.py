"""
Main window for UI Easy application
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTextEdit, QFileDialog, 
                            QTabWidget, QProgressBar, QMessageBox, QGroupBox,
                            QComboBox, QSplitter, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QIcon

from core.config import Config
from core.image_analyzer import ImageAnalyzer
from core.requirement_analyzer.analyzer import RequirementAnalyzer

class AnalysisWorker(QThread):
    """Worker thread for analysis (image or requirements)"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    streaming_text = pyqtSignal(str)
    
    def __init__(self, analyzer, input_data):
        super().__init__()
        self.analyzer = analyzer
        self.input_data = input_data
    
    def run(self):
        try:
            # Connect signals
            self.analyzer.progress_updated.connect(self.progress.emit)
            self.analyzer.status_updated.connect(self.status.emit)
            self.analyzer.error_occurred.connect(self.error.emit)
            self.analyzer.streaming_text_updated.connect(self.streaming_text.emit)
            
            result = self.analyzer.process(self.input_data)
            # Convert AnalysisResult to dict if needed for requirements analyzer
            if hasattr(result, 'to_dict'):
                self.finished.emit(result.to_dict())
            else:
                self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.image_analyzer = ImageAnalyzer(self.config)
        self.requirement_analyzer = RequirementAnalyzer(self.config)
        self.current_image_path = None
        self.analysis_worker = None
        self.current_requirements_result = None
        
        self.setWindowTitle("UI Easy - AI-Powered Design Tool")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("UI Easy - Professional Design Analysis Tool")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.setup_image_analyzer_tab()
        self.setup_requirement_analyzer_tab()
        self.setup_prototype_generator_tab()
        self.setup_settings_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def setup_image_analyzer_tab(self):
        """Setup image analyzer tab"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "Image Analyzer")
        
        layout = QHBoxLayout(tab)
        
        # Left panel - Controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Image selection
        image_group = QGroupBox("Image Selection")
        image_layout = QVBoxLayout(image_group)
        
        self.select_image_btn = QPushButton("Select Design Image")
        self.select_image_btn.clicked.connect(self.select_image)
        image_layout.addWidget(self.select_image_btn)
        
        self.image_preview = QLabel()
        self.image_preview.setMinimumHeight(200)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("border: 2px dashed #ccc; background-color: #f9f9f9;")
        self.image_preview.setText("No image selected")
        image_layout.addWidget(self.image_preview)
        
        left_layout.addWidget(image_group)
        
        # Analysis options
        options_group = QGroupBox("Analysis Options")
        options_layout = QVBoxLayout(options_group)
        
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["Full Analysis", "Layout Only", "Colors Only", "Components Only"])
        options_layout.addWidget(QLabel("Analysis Type:"))
        options_layout.addWidget(self.analysis_type_combo)
        
        self.analyze_btn = QPushButton("Analyze Design")
        self.analyze_btn.clicked.connect(self.analyze_image)
        self.analyze_btn.setEnabled(False)
        options_layout.addWidget(self.analyze_btn)
        
        left_layout.addWidget(options_group)
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        left_layout.addWidget(progress_group)
        
        left_layout.addStretch()
        
        # Right panel - Results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Analysis results will appear here...")
        results_layout.addWidget(self.results_text)
        
        # Export buttons
        export_layout = QHBoxLayout()
        self.export_json_btn = QPushButton("Export JSON")
        self.export_json_btn.clicked.connect(self.export_json)
        self.export_json_btn.setEnabled(False)
        
        self.export_txt_btn = QPushButton("Export Text")
        self.export_txt_btn.clicked.connect(self.export_text)
        self.export_txt_btn.setEnabled(False)
        
        export_layout.addWidget(self.export_json_btn)
        export_layout.addWidget(self.export_txt_btn)
        export_layout.addStretch()
        
        results_layout.addLayout(export_layout)
        right_layout.addWidget(results_group)
        
        # Add panels to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        # Store reference to results
        self.current_analysis_result = None
    
    def setup_requirement_analyzer_tab(self):
        """Setup requirement analyzer tab"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "Requirement Analyzer")
        
        layout = QHBoxLayout(tab)
        
        # Left panel - Input and Controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Requirements Input
        input_group = QGroupBox("Requirements Input")
        input_layout = QVBoxLayout(input_group)
        
        # Text input area
        input_layout.addWidget(QLabel("Requirements Text:"))
        self.requirements_text = QTextEdit()
        self.requirements_text.setPlaceholderText("Enter your requirements here...\n\nExample:\n我需要一个任务管理系统，包含：\n1. 用户登录功能\n2. 创建和编辑任务\n3. 任务列表显示\n4. 任务状态管理")
        self.requirements_text.setMinimumHeight(200)
        input_layout.addWidget(self.requirements_text)
        
        # Context input
        input_layout.addWidget(QLabel("Additional Context (Optional):"))
        self.context_text = QTextEdit()
        self.context_text.setPlaceholderText("Provide additional context about your project...")
        self.context_text.setMaximumHeight(80)
        input_layout.addWidget(self.context_text)
        
        left_layout.addWidget(input_group)
        
        # Analysis Options
        options_group = QGroupBox("Analysis Options")
        options_layout = QVBoxLayout(options_group)
        
        # Platform selection
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["web", "mobile", "desktop"])
        options_layout.addWidget(QLabel("Target Platform:"))
        options_layout.addWidget(self.platform_combo)
        
        # Analyze button
        self.analyze_requirements_btn = QPushButton("Analyze Requirements")
        self.analyze_requirements_btn.clicked.connect(self.analyze_requirements)
        self.analyze_requirements_btn.setEnabled(True)
        options_layout.addWidget(self.analyze_requirements_btn)
        
        left_layout.addWidget(options_group)
        
        # Progress section
        progress_group = QGroupBox("Analysis Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.req_progress_bar = QProgressBar()
        progress_layout.addWidget(self.req_progress_bar)
        
        self.req_status_label = QLabel("Ready")
        progress_layout.addWidget(self.req_status_label)
        
        left_layout.addWidget(progress_group)
        
        left_layout.addStretch()
        
        # Right panel - Results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Results tabs
        self.results_tab_widget = QTabWidget()
        
        # Analysis Overview Tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        self.overview_text.setPlaceholderText("Analysis overview will appear here...")
        overview_layout.addWidget(self.overview_text)
        
        self.results_tab_widget.addTab(overview_tab, "Overview")
        
        # Requirements List Tab
        requirements_tab = QWidget()
        req_layout = QVBoxLayout(requirements_tab)
        
        # Requirements filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Type:"))
        self.req_type_filter = QComboBox()
        self.req_type_filter.addItems(["All", "Functional", "UI Component", "Layout", "Styling", "Interaction", "Data", "Performance", "Accessibility", "Business"])
        self.req_type_filter.currentTextChanged.connect(self.filter_requirements)
        filter_layout.addWidget(self.req_type_filter)
        
        filter_layout.addWidget(QLabel("Priority:"))
        self.req_priority_filter = QComboBox()
        self.req_priority_filter.addItems(["All", "Critical", "High", "Medium", "Low"])
        self.req_priority_filter.currentTextChanged.connect(self.filter_requirements)
        filter_layout.addWidget(self.req_priority_filter)
        
        filter_layout.addStretch()
        req_layout.addLayout(filter_layout)
        
        # Requirements list
        self.requirements_list = QTextEdit()
        self.requirements_list.setReadOnly(True)
        self.requirements_list.setPlaceholderText("Detailed requirements will appear here...")
        req_layout.addWidget(self.requirements_list)
        
        self.results_tab_widget.addTab(requirements_tab, "Requirements")
        
        # Components Tab
        components_tab = QWidget()
        comp_layout = QVBoxLayout(components_tab)
        
        self.components_text = QTextEdit()
        self.components_text.setReadOnly(True)
        self.components_text.setPlaceholderText("Component specifications will appear here...")
        comp_layout.addWidget(self.components_text)
        
        self.results_tab_widget.addTab(components_tab, "Components")
        
        # Analysis Quality Tab
        quality_tab = QWidget()
        quality_layout = QVBoxLayout(quality_tab)
        
        self.quality_text = QTextEdit()
        self.quality_text.setReadOnly(True)
        self.quality_text.setPlaceholderText("Quality analysis and recommendations will appear here...")
        quality_layout.addWidget(self.quality_text)
        
        self.results_tab_widget.addTab(quality_tab, "Quality & Recommendations")
        
        right_layout.addWidget(self.results_tab_widget)
        
        # Export buttons
        export_layout = QHBoxLayout()
        self.export_req_json_btn = QPushButton("Export JSON")
        self.export_req_json_btn.clicked.connect(self.export_requirements_json)
        self.export_req_json_btn.setEnabled(False)
        
        self.export_req_txt_btn = QPushButton("Export Report")
        self.export_req_txt_btn.clicked.connect(self.export_requirements_report)
        self.export_req_txt_btn.setEnabled(False)
        
        export_layout.addWidget(self.export_req_json_btn)
        export_layout.addWidget(self.export_req_txt_btn)
        export_layout.addStretch()
        
        right_layout.addLayout(export_layout)
        
        # Add panels to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
    
    def setup_prototype_generator_tab(self):
        """Setup prototype generator tab"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "Prototype Generator")
        
        layout = QVBoxLayout(tab)
        placeholder = QLabel("Prototype Generator - Coming Soon")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
    
    def setup_settings_tab(self):
        """Setup settings tab"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "Settings")
        
        layout = QVBoxLayout(tab)
        placeholder = QLabel("Settings - Coming Soon")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def select_image(self):
        """Select an image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Design Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        
        if file_path:
            self.current_image_path = file_path
            self.load_image_preview(file_path)
            self.analyze_btn.setEnabled(True)
    
    def load_image_preview(self, file_path):
        """Load and display image preview"""
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale to fit preview
                scaled_pixmap = pixmap.scaled(
                    self.image_preview.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled_pixmap)
                self.image_preview.setText("")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load image: {str(e)}")
    
    def analyze_image(self):
        """Start image analysis"""
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please select an image first")
            return
        
        # Check if API key is configured
        config = self.config.get_module_config("image_analyzer")
        if config:
            model_config = self.config.get_model_config(config.model_config)
            if not model_config or not model_config.api_key:
                QMessageBox.warning(
                    self, 
                    "Configuration Error", 
                    "Please configure API key in settings before analyzing images"
                )
                return
        
        # Disable analyze button
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # Show analysis header in results
        analysis_type_text = self.analysis_type_combo.currentText()
        header_text = f"=== {analysis_type_text} ===\n正在分析图像，请稍候...\n\n"
        self.results_text.setPlainText(header_text)
        
        # Prepare input data
        analysis_type_map = {
            "Full Analysis": "full",
            "Layout Only": "layout", 
            "Colors Only": "colors",
            "Components Only": "components"
        }
        
        input_data = {
            "image_path": self.current_image_path,
            "analysis_type": analysis_type_map[self.analysis_type_combo.currentText()]
        }
        
        # Start analysis in worker thread
        self.analysis_worker = AnalysisWorker(self.image_analyzer, input_data)
        self.analysis_worker.finished.connect(self.on_analysis_finished)
        self.analysis_worker.error.connect(self.on_analysis_error)
        self.analysis_worker.progress.connect(self.on_progress_update)
        self.analysis_worker.status.connect(self.on_status_update)
        self.analysis_worker.streaming_text.connect(self.on_streaming_text_update)
        self.analysis_worker.start()
    
    def on_analysis_finished(self, result):
        """Handle analysis completion"""
        self.current_analysis_result = result
        self.display_analysis_result(result)
        self.analyze_btn.setEnabled(True)
        self.export_json_btn.setEnabled(True)
        self.export_txt_btn.setEnabled(True)
        self.status_label.setText("Analysis completed")
    
    def on_analysis_error(self, error_msg):
        """Handle analysis error"""
        QMessageBox.critical(self, "Analysis Error", f"Analysis failed: {error_msg}")
        self.analyze_btn.setEnabled(True)
        self.status_label.setText("Analysis failed")
    
    def on_progress_update(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def on_status_update(self, status):
        """Update status label"""
        self.status_label.setText(status)
    
    def on_streaming_text_update(self, text_chunk):
        """Handle streaming text updates"""
        # Append text chunk to results area
        cursor = self.results_text.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text_chunk)
        self.results_text.setTextCursor(cursor)
        # Auto-scroll to bottom
        self.results_text.ensureCursorVisible()
    
    def display_analysis_result(self, result):
        """Display analysis results"""
        # Add metadata at the end of the streaming content
        cursor = self.results_text.textCursor()
        cursor.movePosition(cursor.End)
        
        metadata_text = f"\n\n=== 分析完成 ===\n"
        metadata_text += f"分析类型: {result.get('analysis_type', 'Unknown')}\n"
        metadata_text += f"时间戳: {result.get('timestamp', 'Unknown')}\n"
        metadata_text += f"使用模型: {result.get('metadata', {}).get('model_used', 'Unknown')}\n"
        metadata_text += f"置信度: {result.get('metadata', {}).get('confidence_score', 0):.2f}\n"
        
        cursor.insertText(metadata_text)
        self.results_text.setTextCursor(cursor)
        self.results_text.ensureCursorVisible()
    
    def export_json(self):
        """Export results as JSON"""
        if not self.current_analysis_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Analysis as JSON", 
            "analysis_result.json", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_analysis_result, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "Success", f"Analysis exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    def export_text(self):
        """Export results as text"""
        if not self.current_analysis_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Analysis as Text", 
            "analysis_result.txt", 
            "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.toPlainText())
                QMessageBox.information(self, "Success", f"Analysis exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    def analyze_requirements(self):
        """Start requirements analysis"""
        requirements_text = self.requirements_text.toPlainText().strip()
        if not requirements_text:
            QMessageBox.warning(self, "Warning", "Please enter requirements text first")
            return
        
        # Check if API key is configured
        config = self.config.get_module_config("requirement_analyzer")
        if config:
            model_config = self.config.get_model_config(config.model_config)
            if not model_config or not model_config.api_key:
                QMessageBox.warning(
                    self, 
                    "Configuration Error", 
                    "Please configure API key in settings before analyzing requirements"
                )
                return
        
        # Disable analyze button
        self.analyze_requirements_btn.setEnabled(False)
        self.req_progress_bar.setValue(0)
        
        # Clear previous results
        self.overview_text.clear()
        self.requirements_list.clear()
        self.components_text.clear()
        self.quality_text.clear()
        
        # Show analysis header
        header_text = "=== Requirements Analysis ===\n正在分析需求，请稍候...\n\n"
        self.overview_text.setPlainText(header_text)
        
        # Prepare input data
        input_data = {
            "text": requirements_text,
            "context": self.context_text.toPlainText().strip(),
            "platform": self.platform_combo.currentText()
        }
        
        # Start analysis in worker thread
        self.analysis_worker = AnalysisWorker(self.requirement_analyzer, input_data)
        self.analysis_worker.finished.connect(self.on_requirements_analysis_finished)
        self.analysis_worker.error.connect(self.on_requirements_analysis_error)
        self.analysis_worker.progress.connect(self.on_requirements_progress_update)
        self.analysis_worker.status.connect(self.on_requirements_status_update)
        self.analysis_worker.streaming_text.connect(self.on_requirements_streaming_text_update)
        self.analysis_worker.start()
    
    def on_requirements_analysis_finished(self, result):
        """Handle requirements analysis completion"""
        self.current_requirements_result = result
        self.display_requirements_result(result)
        self.analyze_requirements_btn.setEnabled(True)
        self.export_req_json_btn.setEnabled(True)
        self.export_req_txt_btn.setEnabled(True)
        self.req_status_label.setText("Analysis completed")
    
    def on_requirements_analysis_error(self, error_msg):
        """Handle requirements analysis error"""
        QMessageBox.critical(self, "Analysis Error", f"Requirements analysis failed: {error_msg}")
        self.analyze_requirements_btn.setEnabled(True)
        self.req_status_label.setText("Analysis failed")
    
    def on_requirements_progress_update(self, value):
        """Update requirements progress bar"""
        self.req_progress_bar.setValue(value)
    
    def on_requirements_status_update(self, status):
        """Update requirements status label"""
        self.req_status_label.setText(status)
    
    def on_requirements_streaming_text_update(self, text_chunk):
        """Handle streaming text updates for requirements analysis"""
        # Append text chunk to overview results area
        cursor = self.overview_text.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text_chunk)
        self.overview_text.setTextCursor(cursor)
        # Auto-scroll to bottom
        self.overview_text.ensureCursorVisible()
    
    def display_requirements_result(self, result):
        """Display requirements analysis results"""
        try:
            # Overview tab - 在流式内容后追加摘要
            overview_text = f"\n\n{'='*60}\n"
            overview_text += f"=== 分析结果摘要 ===\n\n"
            overview_text += f"项目概述:\n{result.get('project_overview', 'N/A')}\n\n"
            overview_text += f"目标用户:\n{result.get('target_audience', 'N/A')}\n\n"
            overview_text += f"平台: {result.get('platform', 'N/A')}\n\n"
            
            overview_text += f"质量评分:\n"
            overview_text += f"• 完整性: {result.get('completeness_score', 0):.2f}\n"
            overview_text += f"• 清晰度: {result.get('clarity_score', 0):.2f}\n"
            overview_text += f"• 可行性: {result.get('feasibility_score', 0):.2f}\n\n"
            
            overview_text += f"开发预估: {result.get('total_estimated_effort', 'N/A')}\n\n"
            
            framework_recommendations = result.get('framework_recommendations', [])
            if framework_recommendations:
                overview_text += f"推荐框架:\n"
                for framework in framework_recommendations:
                    overview_text += f"• {framework}\n"
            
            # 追加到现有内容，而不是替换
            cursor = self.overview_text.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertText(overview_text)
            self.overview_text.setTextCursor(cursor)
            self.overview_text.ensureCursorVisible()
            
            # Display filtered requirements
            self.filter_requirements()
            
            # Components tab
            self.display_components(result)
            
            # Quality tab
            self.display_quality_analysis(result)
            
        except Exception as e:
            QMessageBox.critical(self, "Display Error", f"Failed to display results: {str(e)}")
    
    def filter_requirements(self):
        """Filter and display requirements based on selected filters"""
        if not self.current_requirements_result:
            return
        
        type_filter = self.req_type_filter.currentText()
        priority_filter = self.req_priority_filter.currentText()
        
        filtered_reqs = []
        
        requirements = self.current_requirements_result.get('requirements', [])
        for req in requirements:
            # Type filter
            if type_filter != "All":
                type_map = {
                    "Functional": "functional",
                    "UI Component": "ui_component", 
                    "Layout": "layout",
                    "Styling": "styling",
                    "Interaction": "interaction",
                    "Data": "data",
                    "Performance": "performance",
                    "Accessibility": "accessibility",
                    "Business": "business"
                }
                req_type = req.get('type') if isinstance(req, dict) else req.type.value
                if req_type != type_map.get(type_filter, ""):
                    continue
            
            # Priority filter
            if priority_filter != "All":
                req_priority = req.get('priority') if isinstance(req, dict) else req.priority.value
                if req_priority != priority_filter.lower():
                    continue
            
            filtered_reqs.append(req)
        
        # Display filtered requirements
        req_text = f"=== Requirements List ({len(filtered_reqs)} items) ===\n\n"
        
        for i, req in enumerate(filtered_reqs, 1):
            if isinstance(req, dict):
                title = req.get('title', 'N/A')
                req_type = req.get('type', 'unknown').replace('_', ' ').title()
                priority = req.get('priority', 'unknown').title()
                status = req.get('status', 'unknown').title()
                description = req.get('description', 'N/A')
                acceptance_criteria = req.get('acceptance_criteria', [])
                estimated_effort = req.get('estimated_effort')
                rationale = req.get('rationale')
            else:
                title = req.title
                req_type = req.type.value.replace('_', ' ').title()
                priority = req.priority.value.title()
                status = req.status.value.title()
                description = req.description
                acceptance_criteria = req.acceptance_criteria
                estimated_effort = req.estimated_effort
                rationale = req.rationale
            
            req_text += f"{i}. {title}\n"
            req_text += f"   Type: {req_type}\n"
            req_text += f"   Priority: {priority}\n"
            req_text += f"   Status: {status}\n"
            req_text += f"   Description: {description}\n"
            
            if acceptance_criteria:
                req_text += f"   Acceptance Criteria:\n"
                for criteria in acceptance_criteria:
                    req_text += f"     • {criteria}\n"
            
            if estimated_effort:
                req_text += f"   Estimated Effort: {estimated_effort}\n"
            
            if rationale:
                req_text += f"   Rationale: {rationale}\n"
            
            req_text += "\n"
        
        self.requirements_list.setPlainText(req_text)
    
    def display_components(self, result):
        """Display component specifications"""
        comp_text = "=== Component Specifications ===\n\n"
        
        # Get UI component requirements
        requirements = result.get('requirements', [])
        ui_reqs = []
        for req in requirements:
            if isinstance(req, dict):
                if req.get('type') == 'ui_component':
                    ui_reqs.append(req)
            else:
                if req.type.value == 'ui_component':
                    ui_reqs.append(req)
        
        if not ui_reqs:
            comp_text += "No UI components identified in the requirements.\n"
        else:
            for req in ui_reqs:
                if isinstance(req, dict):
                    title = req.get('title', 'N/A')
                    description = req.get('description', 'N/A')
                    component_spec = req.get('component_spec')
                else:
                    title = req.title
                    description = req.description
                    component_spec = req.component_spec
                
                comp_text += f"Component: {title}\n"
                comp_text += f"Description: {description}\n"
                
                if component_spec:
                    if isinstance(component_spec, dict):
                        comp_text += f"• Type: {component_spec.get('type', 'N/A')}\n"
                        comp_text += f"• Name: {component_spec.get('name', 'N/A')}\n"
                        
                        properties = component_spec.get('properties', {})
                        if properties:
                            comp_text += f"• Properties:\n"
                            for key, value in properties.items():
                                comp_text += f"  - {key}: {value}\n"
                        
                        events = component_spec.get('events', [])
                        if events:
                            comp_text += f"• Events: {', '.join(events)}\n"
                        
                        validation = component_spec.get('validation')
                        if validation:
                            comp_text += f"• Validation: {validation}\n"
                        
                        accessibility = component_spec.get('accessibility')
                        if accessibility:
                            comp_text += f"• Accessibility: {accessibility}\n"
                    else:
                        comp_text += f"• Type: {component_spec.type}\n"
                        comp_text += f"• Name: {component_spec.name}\n"
                        
                        if component_spec.properties:
                            comp_text += f"• Properties:\n"
                            for key, value in component_spec.properties.items():
                                comp_text += f"  - {key}: {value}\n"
                        
                        if component_spec.events:
                            comp_text += f"• Events: {', '.join(component_spec.events)}\n"
                        
                        if component_spec.validation:
                            comp_text += f"• Validation: {component_spec.validation}\n"
                        
                        if component_spec.accessibility:
                            comp_text += f"• Accessibility: {component_spec.accessibility}\n"
                
                comp_text += "\n"
        
        self.components_text.setPlainText(comp_text)
    
    def display_quality_analysis(self, result):
        """Display quality analysis and recommendations"""
        quality_text = "=== Quality Analysis ===\n\n"
        
        quality_text += f"Analysis Scores:\n"
        quality_text += f"• Completeness Score: {result.get('completeness_score', 0):.2f} / 1.0\n"
        quality_text += f"• Clarity Score: {result.get('clarity_score', 0):.2f} / 1.0\n"
        quality_text += f"• Feasibility Score: {result.get('feasibility_score', 0):.2f} / 1.0\n\n"
        
        gaps = result.get('gaps', [])
        if gaps:
            quality_text += f"Identified Gaps:\n"
            for gap in gaps:
                quality_text += f"• {gap}\n"
            quality_text += "\n"
        
        ambiguities = result.get('ambiguities', [])
        if ambiguities:
            quality_text += f"Ambiguities to Clarify:\n"
            for ambiguity in ambiguities:
                quality_text += f"• {ambiguity}\n"
            quality_text += "\n"
        
        recommendations = result.get('recommendations', [])
        if recommendations:
            quality_text += f"Recommendations:\n"
            for rec in recommendations:
                quality_text += f"• {rec}\n"
            quality_text += "\n"
        
        development_phases = result.get('development_phases', [])
        if development_phases:
            quality_text += f"Development Phases:\n"
            for phase in development_phases:
                if isinstance(phase, dict):
                    name = phase.get('name', 'N/A')
                    description = phase.get('description', 'N/A')
                    duration = phase.get('estimated_duration', 'N/A')
                    quality_text += f"• {name}: {description}\n"
                    quality_text += f"  Duration: {duration}\n"
                else:
                    quality_text += f"• {phase}\n"
            quality_text += "\n"
        
        self.quality_text.setPlainText(quality_text)
    
    def export_requirements_json(self):
        """Export requirements analysis as JSON"""
        if not self.current_requirements_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Requirements Analysis as JSON", 
            "requirements_analysis.json", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Check if it's already a dict or needs conversion
                    if hasattr(self.current_requirements_result, 'to_dict'):
                        json.dump(self.current_requirements_result.to_dict(), f, indent=2, ensure_ascii=False)
                    else:
                        json.dump(self.current_requirements_result, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "Success", f"Requirements analysis exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    def export_requirements_report(self):
        """Export requirements analysis as text report"""
        if not self.current_requirements_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Requirements Report", 
            "requirements_report.txt", 
            "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Write overview
                    f.write(self.overview_text.toPlainText())
                    f.write("\n\n" + "="*50 + "\n\n")
                    
                    # Write all requirements
                    f.write(self.requirements_list.toPlainText())
                    f.write("\n\n" + "="*50 + "\n\n")
                    
                    # Write components
                    f.write(self.components_text.toPlainText())
                    f.write("\n\n" + "="*50 + "\n\n")
                    
                    # Write quality analysis
                    f.write(self.quality_text.toPlainText())
                
                QMessageBox.information(self, "Success", f"Requirements report exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")