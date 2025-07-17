"""
Main window for UI Easy application
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTextEdit, QFileDialog, 
                            QTabWidget, QProgressBar, QMessageBox, QGroupBox,
                            QComboBox, QSplitter, QScrollArea, QLineEdit,
                            QSpinBox, QDoubleSpinBox, QCheckBox, QGridLayout,
                            QFormLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QIcon

from core.config import Config
from core.image_analyzer import ImageAnalyzer
from core.requirement_analyzer.analyzer import RequirementAnalyzer
from ui.localization import tr, set_language

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
        
        # Initialize settings UI components
        self.model_combo = None
        self.model_name_edit = None
        self.model_provider_combo = None
        self.model_api_key_edit = None
        self.model_base_url_edit = None
        self.model_id_edit = None
        self.model_max_tokens_spin = None
        self.model_temperature_spin = None
        self.model_timeout_spin = None
        self.module_combo = None
        self.module_enabled_check = None
        self.module_model_combo = None
        self.module_prompts_text = None
        self.language_combo = None
        self.default_analysis_combo = None
        self.auto_save_check = None
        self.export_format_combo = None
        
        # Set initial language from config
        initial_language = self.config.get_app_setting("language", "zh_CN")
        set_language(initial_language)
        self._current_language = initial_language
        
        self.setWindowTitle(tr("window_title"))
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        self.setup_connections()
        
        # Load initial settings
        self.load_initial_settings()
    
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel(tr("main_title"))
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
        self.statusBar().showMessage(tr("ready"))
    
    def setup_image_analyzer_tab(self):
        """Setup image analyzer tab"""
        tab = QWidget()
        self.tab_widget.addTab(tab, tr("tab_image_analyzer"))
        
        layout = QHBoxLayout(tab)
        
        # Left panel - Controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Image selection
        image_group = QGroupBox(tr("image_selection"))
        image_layout = QVBoxLayout(image_group)
        
        self.select_image_btn = QPushButton(tr("select_image"))
        self.select_image_btn.clicked.connect(self.select_image)
        image_layout.addWidget(self.select_image_btn)
        
        self.image_preview = QLabel()
        self.image_preview.setMinimumHeight(200)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("border: 2px dashed #ccc; background-color: #f9f9f9;")
        self.image_preview.setText(tr("no_image_selected"))
        image_layout.addWidget(self.image_preview)
        
        left_layout.addWidget(image_group)
        
        # Analysis options
        options_group = QGroupBox(tr("analysis_options"))
        options_layout = QVBoxLayout(options_group)
        
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems([tr("full_analysis"), tr("layout_only"), tr("colors_only"), tr("components_only")])
        options_layout.addWidget(QLabel(tr("analysis_type")))
        options_layout.addWidget(self.analysis_type_combo)
        
        self.analyze_btn = QPushButton(tr("analyze_design"))
        self.analyze_btn.clicked.connect(self.analyze_image)
        self.analyze_btn.setEnabled(False)
        options_layout.addWidget(self.analyze_btn)
        
        left_layout.addWidget(options_group)
        
        # Progress
        progress_group = QGroupBox(tr("progress"))
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel(tr("ready"))
        progress_layout.addWidget(self.status_label)
        
        left_layout.addWidget(progress_group)
        
        left_layout.addStretch()
        
        # Right panel - Results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        results_group = QGroupBox(tr("analysis_results"))
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText(tr("analysis_placeholder"))
        results_layout.addWidget(self.results_text)
        
        # Export buttons
        export_layout = QHBoxLayout()
        self.export_json_btn = QPushButton(tr("export_json"))
        self.export_json_btn.clicked.connect(self.export_json)
        self.export_json_btn.setEnabled(False)
        
        self.export_txt_btn = QPushButton(tr("export_txt"))
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
        self.tab_widget.addTab(tab, tr("tab_requirement_analyzer"))
        
        layout = QHBoxLayout(tab)
        
        # Left panel - Input and Controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Requirements Input
        input_group = QGroupBox(tr("requirements_input"))
        input_layout = QVBoxLayout(input_group)
        
        # Text input area
        input_layout.addWidget(QLabel(tr("requirements_text")))
        self.requirements_text = QTextEdit()
        self.requirements_text.setPlaceholderText(tr("requirements_placeholder"))
        self.requirements_text.setMinimumHeight(200)
        input_layout.addWidget(self.requirements_text)
        
        # Context input
        input_layout.addWidget(QLabel(tr("additional_context")))
        self.context_text = QTextEdit()
        self.context_text.setPlaceholderText(tr("context_placeholder"))
        self.context_text.setMaximumHeight(80)
        input_layout.addWidget(self.context_text)
        
        left_layout.addWidget(input_group)
        
        # Analysis Options
        options_group = QGroupBox(tr("analysis_options"))
        options_layout = QVBoxLayout(options_group)
        
        # Platform selection
        self.platform_combo = QComboBox()
        self.platform_combo.addItems([tr("web"), tr("mobile"), tr("desktop")])
        options_layout.addWidget(QLabel(tr("target_platform")))
        options_layout.addWidget(self.platform_combo)
        
        # Analyze button
        self.analyze_requirements_btn = QPushButton(tr("analyze_requirements"))
        self.analyze_requirements_btn.clicked.connect(self.analyze_requirements)
        self.analyze_requirements_btn.setEnabled(True)
        options_layout.addWidget(self.analyze_requirements_btn)
        
        left_layout.addWidget(options_group)
        
        # Progress section
        progress_group = QGroupBox(tr("analysis_progress"))
        progress_layout = QVBoxLayout(progress_group)
        
        self.req_progress_bar = QProgressBar()
        progress_layout.addWidget(self.req_progress_bar)
        
        self.req_status_label = QLabel(tr("ready"))
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
        self.overview_text.setPlaceholderText(tr("analysis_placeholder"))
        overview_layout.addWidget(self.overview_text)
        
        self.results_tab_widget.addTab(overview_tab, tr("overview"))
        
        # Requirements List Tab
        requirements_tab = QWidget()
        req_layout = QVBoxLayout(requirements_tab)
        
        # Requirements filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel(tr("filter_by_type")))
        self.req_type_filter = QComboBox()
        self.req_type_filter.addItems([tr("all"), tr("functional"), tr("ui_component"), tr("layout"), tr("styling"), tr("interaction"), tr("data"), tr("performance"), tr("accessibility"), tr("business")])
        self.req_type_filter.currentTextChanged.connect(self.filter_requirements)
        filter_layout.addWidget(self.req_type_filter)
        
        filter_layout.addWidget(QLabel(tr("priority")))
        self.req_priority_filter = QComboBox()
        self.req_priority_filter.addItems([tr("all"), tr("critical"), tr("high"), tr("medium"), tr("low")])
        self.req_priority_filter.currentTextChanged.connect(self.filter_requirements)
        filter_layout.addWidget(self.req_priority_filter)
        
        filter_layout.addStretch()
        req_layout.addLayout(filter_layout)
        
        # Requirements list
        self.requirements_list = QTextEdit()
        self.requirements_list.setReadOnly(True)
        self.requirements_list.setPlaceholderText(tr("analysis_placeholder"))
        req_layout.addWidget(self.requirements_list)
        
        self.results_tab_widget.addTab(requirements_tab, tr("requirements"))
        
        # Components Tab
        components_tab = QWidget()
        comp_layout = QVBoxLayout(components_tab)
        
        self.components_text = QTextEdit()
        self.components_text.setReadOnly(True)
        self.components_text.setPlaceholderText(tr("analysis_placeholder"))
        comp_layout.addWidget(self.components_text)
        
        self.results_tab_widget.addTab(components_tab, tr("components"))
        
        # Analysis Quality Tab
        quality_tab = QWidget()
        quality_layout = QVBoxLayout(quality_tab)
        
        self.quality_text = QTextEdit()
        self.quality_text.setReadOnly(True)
        self.quality_text.setPlaceholderText(tr("analysis_placeholder"))
        quality_layout.addWidget(self.quality_text)
        
        self.results_tab_widget.addTab(quality_tab, tr("quality_recommendations"))
        
        right_layout.addWidget(self.results_tab_widget)
        
        # Export buttons
        export_layout = QHBoxLayout()
        self.export_req_json_btn = QPushButton(tr("export_json"))
        self.export_req_json_btn.clicked.connect(self.export_requirements_json)
        self.export_req_json_btn.setEnabled(False)
        
        self.export_req_txt_btn = QPushButton(tr("export_report"))
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
        self.tab_widget.addTab(tab, tr("tab_prototype_generator"))
        
        layout = QVBoxLayout(tab)
        placeholder = QLabel(tr("prototype_coming_soon"))
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
    
    def setup_settings_tab(self):
        """Setup settings tab"""
        tab = QWidget()
        self.tab_widget.addTab(tab, tr("tab_settings"))
        
        # Main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        
        layout = QVBoxLayout(tab)
        layout.addWidget(scroll_area)
        
        # Main layout for settings content
        main_layout = QVBoxLayout(scroll_widget)
        
        # Settings title
        title_label = QLabel(tr("app_settings"))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Model Configuration Section
        self.setup_model_config_section(main_layout)
        
        # Module Configuration Section
        self.setup_module_config_section(main_layout)
        
        # Application Settings Section
        self.setup_app_settings_section(main_layout)
        
        # Buttons section
        buttons_layout = QHBoxLayout()
        
        self.test_config_btn = QPushButton(tr("test_config"))
        self.test_config_btn.clicked.connect(self.test_configuration)
        
        self.save_config_btn = QPushButton(tr("save_settings"))
        self.save_config_btn.clicked.connect(self.save_settings)
        
        self.load_config_btn = QPushButton(tr("reload_settings"))
        self.load_config_btn.clicked.connect(self.load_settings)
        
        buttons_layout.addWidget(self.test_config_btn)
        buttons_layout.addWidget(self.save_config_btn)
        buttons_layout.addWidget(self.load_config_btn)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def select_image(self):
        """Select an image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            tr("select_design_image"), 
            "", 
            tr("image_files")
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
            QMessageBox.warning(self, tr("error"), f"{tr('failed_to_load_image')}: {str(e)}")
    
    def analyze_image(self):
        """Start image analysis"""
        if not self.current_image_path:
            QMessageBox.warning(self, tr("warning"), tr("select_image_first"))
            return
        
        # Check if API key is configured
        config = self.config.get_module_config("image_analyzer")
        if config:
            model_config = self.config.get_model_config(config.model_config)
            if not model_config or not model_config.api_key:
                QMessageBox.warning(
                    self, 
                    tr("config_error"), 
                    tr("api_key_required")
                )
                return
        
        # Disable analyze button
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # Show analysis header in results
        analysis_type_text = self.analysis_type_combo.currentText()
        header_text = f"=== {analysis_type_text} ===\n{tr('analyzing_image_please_wait')}\n\n"
        self.results_text.setPlainText(header_text)
        
        # Prepare input data
        analysis_type_map = {
            tr("full_analysis"): "full",
            tr("layout_only"): "layout", 
            tr("colors_only"): "colors",
            tr("components_only"): "components"
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
        self.status_label.setText(tr("analysis_completed"))
    
    def on_analysis_error(self, error_msg):
        """Handle analysis error"""
        QMessageBox.critical(self, tr("analysis_error"), f"{tr('analysis_failed')}: {error_msg}")
        self.analyze_btn.setEnabled(True)
        self.status_label.setText(tr("analysis_failed"))
    
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
        
        metadata_text = f"\n\n=== {tr('analysis_completed_meta')} ===\n"
        metadata_text += f"{tr('analysis_type_meta')}: {result.get('analysis_type', tr('unknown'))}\n"
        metadata_text += f"{tr('timestamp_meta')}: {result.get('timestamp', tr('unknown'))}\n"
        metadata_text += f"{tr('model_used_meta')}: {result.get('metadata', {}).get('model_used', tr('unknown'))}\n"
        metadata_text += f"{tr('confidence_meta')}: {result.get('metadata', {}).get('confidence_score', 0):.2f}\n"
        
        cursor.insertText(metadata_text)
        self.results_text.setTextCursor(cursor)
        self.results_text.ensureCursorVisible()
    
    def export_json(self):
        """Export results as JSON"""
        if not self.current_analysis_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            tr("export_analysis_as_json"), 
            "analysis_result.json", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_analysis_result, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, tr("success"), f"Analysis exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, tr("export_error"), f"{tr('failed_to_export')}: {str(e)}")
    
    def export_text(self):
        """Export results as text"""
        if not self.current_analysis_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            tr("export_analysis_as_text"), 
            "analysis_result.txt", 
            "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.toPlainText())
                QMessageBox.information(self, tr("success"), f"Analysis exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, tr("export_error"), f"{tr('failed_to_export')}: {str(e)}")
    
    def analyze_requirements(self):
        """Start requirements analysis"""
        requirements_text = self.requirements_text.toPlainText().strip()
        if not requirements_text:
            QMessageBox.warning(self, tr("warning"), tr("enter_requirements"))
            return
        
        # Check if API key is configured
        config = self.config.get_module_config("requirement_analyzer")
        if config:
            model_config = self.config.get_model_config(config.model_config)
            if not model_config or not model_config.api_key:
                QMessageBox.warning(
                    self, 
                    tr("config_error"), 
                    tr("api_key_required")
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
                        comp_text += f"• {tr('type')}: {component_spec.type}\n"
                        comp_text += f"• {tr('name')}: {component_spec.name}\n"
                        
                        if component_spec.properties:
                            comp_text += f"• {tr('properties')}:\n"
                            for key, value in component_spec.properties.items():
                                comp_text += f"  - {key}: {value}\n"
                        
                        if component_spec.events:
                            comp_text += f"• {tr('events')}: {', '.join(component_spec.events)}\n"
                        
                        if component_spec.validation:
                            comp_text += f"• {tr('validation')}: {component_spec.validation}\n"
                        
                        if component_spec.accessibility:
                            comp_text += f"• {tr('accessibility')}: {component_spec.accessibility}\n"
                
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
            tr("export_requirements_as_json"), 
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
                QMessageBox.information(self, tr("success"), f"Requirements analysis exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, tr("export_error"), f"{tr('failed_to_export')}: {str(e)}")
    
    def export_requirements_report(self):
        """Export requirements analysis as text report"""
        if not self.current_requirements_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            tr("export_requirements_report"), 
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
                
                QMessageBox.information(self, tr("success"), f"Requirements report exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, tr("export_error"), f"{tr('failed_to_export')}: {str(e)}")
    
    def setup_model_config_section(self, parent_layout):
        """Setup model configuration section"""
        model_group = QGroupBox(tr("model_config"))
        model_layout = QVBoxLayout(model_group)
        
        # Instructions
        instructions = QLabel(tr("model_config_desc"))
        instructions.setWordWrap(True)
        model_layout.addWidget(instructions)
        
        # Model list and controls
        model_controls_layout = QHBoxLayout()
        
        # Model selection
        model_select_layout = QVBoxLayout()
        model_select_layout.addWidget(QLabel(tr("select_model")))
        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self.load_model_config)
        model_select_layout.addWidget(self.model_combo)
        
        # Model control buttons
        model_btn_layout = QHBoxLayout()
        self.add_model_btn = QPushButton(tr("add_model"))
        self.add_model_btn.clicked.connect(self.add_model_config)
        self.delete_model_btn = QPushButton(tr("delete_model"))
        self.delete_model_btn.clicked.connect(self.delete_model_config)
        
        model_btn_layout.addWidget(self.add_model_btn)
        model_btn_layout.addWidget(self.delete_model_btn)
        model_btn_layout.addStretch()
        
        model_select_layout.addLayout(model_btn_layout)
        model_controls_layout.addLayout(model_select_layout)
        
        model_layout.addLayout(model_controls_layout)
        
        # Model configuration form
        model_form_group = QGroupBox(tr("model_details"))
        model_form_layout = QFormLayout(model_form_group)
        
        self.model_name_edit = QLineEdit()
        self.model_provider_combo = QComboBox()
        self.model_provider_combo.addItems(["openai", "deepseek", "anthropic"])
        self.model_api_key_edit = QLineEdit()
        self.model_api_key_edit.setEchoMode(QLineEdit.Password)
        self.model_base_url_edit = QLineEdit()
        self.model_id_edit = QLineEdit()
        self.model_max_tokens_spin = QSpinBox()
        self.model_max_tokens_spin.setRange(100, 10000)
        self.model_max_tokens_spin.setValue(4000)
        self.model_temperature_spin = QDoubleSpinBox()
        self.model_temperature_spin.setRange(0.0, 2.0)
        self.model_temperature_spin.setSingleStep(0.1)
        self.model_temperature_spin.setValue(0.7)
        self.model_timeout_spin = QSpinBox()
        self.model_timeout_spin.setRange(10, 300)
        self.model_timeout_spin.setValue(30)
        
        model_form_layout.addRow(tr("model_name"), self.model_name_edit)
        model_form_layout.addRow(tr("provider"), self.model_provider_combo)
        model_form_layout.addRow(tr("api_key"), self.model_api_key_edit)
        model_form_layout.addRow(tr("base_url"), self.model_base_url_edit)
        model_form_layout.addRow(tr("model_id"), self.model_id_edit)
        model_form_layout.addRow(tr("max_tokens"), self.model_max_tokens_spin)
        model_form_layout.addRow(tr("temperature"), self.model_temperature_spin)
        model_form_layout.addRow(tr("timeout"), self.model_timeout_spin)
        
        # Update model button
        self.update_model_btn = QPushButton(tr("update_model"))
        self.update_model_btn.clicked.connect(self.update_model_config)
        model_form_layout.addRow(self.update_model_btn)
        
        model_layout.addWidget(model_form_group)
        parent_layout.addWidget(model_group)
    
    def setup_module_config_section(self, parent_layout):
        """Setup module configuration section"""
        module_group = QGroupBox(tr("module_config"))
        module_layout = QVBoxLayout(module_group)
        
        # Instructions
        instructions = QLabel(tr("module_config_desc"))
        instructions.setWordWrap(True)
        module_layout.addWidget(instructions)
        
        # Module selection
        module_select_layout = QHBoxLayout()
        module_select_layout.addWidget(QLabel(tr("select_module")))
        self.module_combo = QComboBox()
        self.module_combo.addItems(["image_analyzer", "requirement_analyzer"])
        self.module_combo.currentTextChanged.connect(self.load_module_config)
        module_select_layout.addWidget(self.module_combo)
        module_select_layout.addStretch()
        
        module_layout.addLayout(module_select_layout)
        
        # Module configuration form
        module_form_layout = QFormLayout()
        
        self.module_enabled_check = QCheckBox()
        self.module_enabled_check.setChecked(True)
        self.module_model_combo = QComboBox()
        
        module_form_layout.addRow(tr("enable_module"), self.module_enabled_check)
        module_form_layout.addRow(tr("use_model"), self.module_model_combo)
        
        # Custom prompts
        prompts_label = QLabel(tr("custom_prompts"))
        module_form_layout.addRow(prompts_label)
        
        self.module_prompts_text = QTextEdit()
        self.module_prompts_text.setMaximumHeight(100)
        self.module_prompts_text.setPlaceholderText(tr("prompt_placeholder"))
        module_form_layout.addRow(tr("custom_prompts"), self.module_prompts_text)
        
        # Update module button
        self.update_module_btn = QPushButton(tr("update_module"))
        self.update_module_btn.clicked.connect(self.update_module_config)
        module_form_layout.addRow(self.update_module_btn)
        
        module_layout.addLayout(module_form_layout)
        parent_layout.addWidget(module_group)
    
    def setup_app_settings_section(self, parent_layout):
        """Setup application settings section"""
        app_group = QGroupBox(tr("app_settings_title"))
        app_layout = QFormLayout(app_group)
        
        # UI Language
        self.language_combo = QComboBox()
        self.language_combo.addItems(["zh_CN", "en_US"])
        self.language_combo.currentTextChanged.connect(self.auto_save_app_settings)
        app_layout.addRow(tr("ui_language"), self.language_combo)
        
        # Default analysis type
        self.default_analysis_combo = QComboBox()
        self.default_analysis_combo.addItems([tr("full_analysis"), tr("layout_only"), tr("colors_only"), tr("components_only")])
        self.default_analysis_combo.currentTextChanged.connect(self.auto_save_app_settings)
        app_layout.addRow(tr("default_analysis_type"), self.default_analysis_combo)
        
        # Auto-save results
        self.auto_save_check = QCheckBox()
        self.auto_save_check.toggled.connect(self.auto_save_app_settings)
        app_layout.addRow(tr("auto_save_results"), self.auto_save_check)
        
        # Export format preference
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems([tr("json"), tr("txt"), tr("both")])
        self.export_format_combo.currentTextChanged.connect(self.auto_save_app_settings)
        app_layout.addRow(tr("default_export_format"), self.export_format_combo)
        
        parent_layout.addWidget(app_group)
    
    def load_model_config(self):
        """Load selected model configuration into form"""
        model_name = self.model_combo.currentText()
        if not model_name:
            return
        
        model_config = self.config.get_model_config(model_name)
        if model_config:
            self.model_name_edit.setText(model_config.name)
            self.model_provider_combo.setCurrentText(model_config.provider)
            self.model_api_key_edit.setText(model_config.api_key)
            self.model_base_url_edit.setText(model_config.base_url or "")
            self.model_id_edit.setText(model_config.model_id)
            self.model_max_tokens_spin.setValue(model_config.max_tokens)
            self.model_temperature_spin.setValue(model_config.temperature)
            self.model_timeout_spin.setValue(model_config.timeout)
        else:
            # Clear form
            self.model_name_edit.clear()
            self.model_api_key_edit.clear()
            self.model_base_url_edit.clear()
            self.model_id_edit.clear()
    
    def load_module_config(self):
        """Load selected module configuration into form"""
        module_name = self.module_combo.currentText()
        if not module_name:
            return
        
        module_config = self.config.get_module_config(module_name)
        if module_config:
            self.module_enabled_check.setChecked(module_config.enabled)
            
            # Update model combo and select current model
            self.refresh_module_model_combo()
            index = self.module_model_combo.findText(module_config.model_config)
            if index >= 0:
                self.module_model_combo.setCurrentIndex(index)
            
            # Load custom prompts
            prompts_text = ""
            if module_config.custom_prompts:
                for key, value in module_config.custom_prompts.items():
                    prompts_text += f"{key}: {value}\n"
            self.module_prompts_text.setPlainText(prompts_text)
        else:
            # Set defaults
            self.module_enabled_check.setChecked(True)
            self.refresh_module_model_combo()
            self.module_prompts_text.clear()
    
    def refresh_module_model_combo(self):
        """Refresh the model combo box for modules"""
        self.module_model_combo.clear()
        model_names = list(self.config.models.keys())
        if model_names:
            self.module_model_combo.addItems(model_names)
        else:
            self.module_model_combo.addItem("default")
    
    def add_model_config(self):
        """Add a new model configuration"""
        from PyQt5.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, tr("add_model_title"), tr("enter_model_name"))
        if ok and name.strip():
            if name in self.config.models:
                QMessageBox.warning(self, tr("warning"), tr("model_exists"))
                return
            
            # Create new model config with defaults
            from core.config import ModelConfig
            new_config = ModelConfig(
                name=name,
                provider="openai",
                api_key="",
                model_id="gpt-4",
                max_tokens=4000,
                temperature=0.7,
                timeout=30
            )
            
            self.config.set_model_config(name, new_config)
            self.config.save()  # Auto-save when adding model
            self.refresh_model_combo()
            self.model_combo.setCurrentText(name)
    
    def delete_model_config(self):
        """Delete selected model configuration"""
        model_name = self.model_combo.currentText()
        if not model_name:
            return
        
        reply = QMessageBox.question(
            self, 
            tr("confirm_delete"), 
            f"{tr('confirm_delete_model')} '{model_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if model_name in self.config.models:
                del self.config.models[model_name]
                self.config.save()  # Auto-save when deleting model
                self.refresh_model_combo()
    
    def update_model_config(self):
        """Update the current model configuration"""
        model_name = self.model_combo.currentText()
        if not model_name:
            return
        
        # Validate inputs
        if not self.model_name_edit.text().strip():
            QMessageBox.warning(self, tr("warning"), tr("model_name_required"))
            return
        
        if not self.model_api_key_edit.text().strip():
            QMessageBox.warning(self, tr("warning"), tr("api_key_empty"))
            return
        
        # Create or update model config
        from core.config import ModelConfig
        config = ModelConfig(
            name=self.model_name_edit.text().strip(),
            provider=self.model_provider_combo.currentText(),
            api_key=self.model_api_key_edit.text().strip(),
            base_url=self.model_base_url_edit.text().strip() or None,
            model_id=self.model_id_edit.text().strip(),
            max_tokens=self.model_max_tokens_spin.value(),
            temperature=self.model_temperature_spin.value(),
            timeout=self.model_timeout_spin.value()
        )
        
        self.config.set_model_config(model_name, config)
        self.refresh_model_combo()
        self.refresh_module_model_combo()
        
        # Auto-save configuration
        self.config.save()
        
        QMessageBox.information(self, tr("success"), tr("model_updated"))
    
    def update_module_config(self):
        """Update the current module configuration"""
        module_name = self.module_combo.currentText()
        if not module_name:
            return
        
        # Parse custom prompts
        custom_prompts = {}
        prompts_text = self.module_prompts_text.toPlainText().strip()
        if prompts_text:
            for line in prompts_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    custom_prompts[key.strip()] = value.strip()
        
        # Create or update module config
        from core.config import ModuleConfig
        config = ModuleConfig(
            enabled=self.module_enabled_check.isChecked(),
            model_config=self.module_model_combo.currentText(),
            custom_prompts=custom_prompts
        )
        
        self.config.set_module_config(module_name, config)
        
        # Auto-save configuration
        self.config.save()
        
        QMessageBox.information(self, tr("success"), tr("module_updated"))
    
    def refresh_model_combo(self):
        """Refresh the model combo box"""
        current_text = self.model_combo.currentText()
        self.model_combo.clear()
        
        model_names = list(self.config.models.keys())
        if model_names:
            self.model_combo.addItems(model_names)
            
            # Try to restore selection
            index = self.model_combo.findText(current_text)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
            else:
                self.model_combo.setCurrentIndex(0)
    
    def load_settings(self):
        """Load settings from configuration"""
        try:
            # Reload config from file
            self.config.load()
            
            # Refresh model combo
            self.refresh_model_combo()
            
            # Load model config if available
            if self.model_combo.count() > 0:
                self.load_model_config()
            
            # Load module config
            self.load_module_config()
            
            # Load app settings
            self.language_combo.setCurrentText(
                self.config.get_app_setting("language", "zh_CN")
            )
            self.default_analysis_combo.setCurrentText(
                self.config.get_app_setting("default_analysis_type", "Full Analysis")
            )
            self.auto_save_check.setChecked(
                self.config.get_app_setting("auto_save", False)
            )
            self.export_format_combo.setCurrentText(
                self.config.get_app_setting("export_format", "JSON")
            )
            
            QMessageBox.information(self, tr("success"), tr("settings_loaded"))
            
        except Exception as e:
            QMessageBox.critical(self, tr("error"), f"加载设置失败：{str(e)}")
    
    def auto_save_app_settings(self):
        """Auto-save app settings when they change"""
        try:
            # Only save if all UI components exist and are initialized
            if (self.language_combo is not None and 
                self.default_analysis_combo is not None and 
                self.auto_save_check is not None and 
                self.export_format_combo is not None):
                
                # Check if language changed and update UI
                new_language = self.language_combo.currentText()
                if hasattr(self, '_current_language') and self._current_language != new_language:
                    set_language(new_language)
                    self._current_language = new_language
                    self.update_ui_language()
                
                # Save app settings
                self.config.set_app_setting("language", self.language_combo.currentText())
                self.config.set_app_setting("default_analysis_type", self.default_analysis_combo.currentText())
                self.config.set_app_setting("auto_save", self.auto_save_check.isChecked())
                self.config.set_app_setting("export_format", self.export_format_combo.currentText())
                
                # Save to file
                self.config.save()
                
        except Exception as e:
            print(f"Auto-save failed: {e}")
    
    def save_settings(self):
        """Save current settings to configuration"""
        try:
            # Save app settings
            self.config.set_app_setting("language", self.language_combo.currentText())
            self.config.set_app_setting("default_analysis_type", self.default_analysis_combo.currentText())
            self.config.set_app_setting("auto_save", self.auto_save_check.isChecked())
            self.config.set_app_setting("export_format", self.export_format_combo.currentText())
            
            # Save to file
            self.config.save()
            
            QMessageBox.information(self, tr("success"), tr("settings_saved"))
            
        except Exception as e:
            QMessageBox.critical(self, tr("error"), f"保存设置失败：{str(e)}")
    
    def test_configuration(self):
        """Test the current configuration"""
        try:
            # Test each configured model
            tested_models = []
            failed_models = []
            
            for model_name, model_config in self.config.models.items():
                if not model_config.api_key:
                    failed_models.append(f"{model_name}: 缺少 API 密钥")
                    continue
                
                # Basic validation
                if model_config.provider == "openai" and not model_config.model_id:
                    failed_models.append(f"{model_name}: OpenAI 模型需要指定 model_id")
                    continue
                    
                if model_config.provider == "deepseek" and not model_config.base_url:
                    failed_models.append(f"{model_name}: DeepSeek 模型需要指定 base_url")
                    continue
                
                tested_models.append(model_name)
            
            # Show results
            result_text = "配置测试结果：\n\n"
            
            if tested_models:
                result_text += f"成功配置的模型 ({len(tested_models)})：\n"
                for model in tested_models:
                    result_text += f"✓ {model}\n"
                result_text += "\n"
            
            if failed_models:
                result_text += f"配置问题 ({len(failed_models)})：\n"
                for error in failed_models:
                    result_text += f"✗ {error}\n"
                result_text += "\n"
            
            # Check modules
            result_text += "模块状态：\n"
            for module_name in ["image_analyzer", "requirement_analyzer"]:
                module_config = self.config.get_module_config(module_name)
                if module_config and module_config.enabled:
                    model_config = self.config.get_model_config(module_config.model_config)
                    if model_config and model_config.api_key:
                        result_text += f"✓ {module_name}: 已启用，使用模型 {module_config.model_config}\n"
                    else:
                        result_text += f"✗ {module_name}: 已启用但模型配置无效\n"
                else:
                    result_text += f"- {module_name}: 已禁用\n"
            
            QMessageBox.information(self, "配置测试结果", result_text)
             
        except Exception as e:
            QMessageBox.critical(self, "错误", f"测试配置时出错：{str(e)}")
    
    def load_initial_settings(self):
        """Load initial settings when the app starts"""
        try:
            # Only load if components are created
            if self.model_combo is not None:
                self.refresh_model_combo()
                if self.model_combo.count() > 0:
                    self.load_model_config()
            
            if self.module_combo is not None:
                self.load_module_config()
            
            # Load app settings
            if self.language_combo is not None:
                self.language_combo.setCurrentText(
                    self.config.get_app_setting("language", "zh_CN")
                )
            if self.default_analysis_combo is not None:
                self.default_analysis_combo.setCurrentText(
                    self.config.get_app_setting("default_analysis_type", "Full Analysis")
                )
            if self.auto_save_check is not None:
                self.auto_save_check.setChecked(
                    self.config.get_app_setting("auto_save", False)
                )
            if self.export_format_combo is not None:
                self.export_format_combo.setCurrentText(
                    self.config.get_app_setting("export_format", "JSON")
                )
                
        except Exception as e:
            print(f"Warning: Failed to load initial settings: {e}")
            # Don't show error dialog on startup
    
    def update_ui_language(self):
        """Update UI language for all components"""
        try:
            # Update window title
            self.setWindowTitle(tr("window_title"))
            
            # Update tab titles
            self.tab_widget.setTabText(0, tr("tab_image_analyzer"))
            self.tab_widget.setTabText(1, tr("tab_requirement_analyzer"))
            self.tab_widget.setTabText(2, tr("tab_prototype_generator"))
            self.tab_widget.setTabText(3, tr("tab_settings"))
            
            # Update status bar
            self.statusBar().showMessage(tr("ready"))
            
            # Update combo box items that use translations
            if self.default_analysis_combo:
                current_index = self.default_analysis_combo.currentIndex()
                self.default_analysis_combo.clear()
                self.default_analysis_combo.addItems([tr("full_analysis"), tr("layout_only"), tr("colors_only"), tr("components_only")])
                self.default_analysis_combo.setCurrentIndex(current_index)
            
            if self.export_format_combo:
                current_index = self.export_format_combo.currentIndex()
                self.export_format_combo.clear()
                self.export_format_combo.addItems([tr("json"), tr("txt"), tr("both")])
                self.export_format_combo.setCurrentIndex(current_index)
            
            # Update button texts
            if self.test_config_btn:
                self.test_config_btn.setText(tr("test_config"))
            if self.save_config_btn:
                self.save_config_btn.setText(tr("save_settings"))
            if self.load_config_btn:
                self.load_config_btn.setText(tr("reload_settings"))
            
            # Update other UI elements that are visible
            # This is a basic implementation - in a full application,
            # you'd want to update all visible text elements
            
        except Exception as e:
            print(f"Failed to update UI language: {e}")