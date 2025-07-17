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
from core.prototype_generator import PrototypeGenerator
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
        self.prototype_generator = PrototypeGenerator(self.config)
        self.current_image_path = None
        self.analysis_worker = None
        self.current_requirements_result = None
        self.current_prototype_result = None
        
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
        
        # Two-phase analysis buttons
        self.extract_list_btn = QPushButton("📋 " + tr("extract_requirement_list"))
        self.extract_list_btn.clicked.connect(self.extract_requirement_list)
        self.extract_list_btn.setEnabled(True)
        options_layout.addWidget(self.extract_list_btn)
        
        self.detailed_analysis_btn = QPushButton("🔍 " + tr("detailed_analysis"))
        self.detailed_analysis_btn.clicked.connect(self.detailed_analysis)
        self.detailed_analysis_btn.setEnabled(False)
        options_layout.addWidget(self.detailed_analysis_btn)
        
        # Original analyze button (for backward compatibility)
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
        
        layout = QHBoxLayout(tab)
        
        # Left panel - Input Management and Settings
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Input Management Section
        input_group = QGroupBox(tr("input_management"))
        input_layout = QVBoxLayout(input_group)
        
        # Add input buttons
        input_buttons_layout = QHBoxLayout()
        self.add_text_input_btn = QPushButton("📝 " + tr("add_text_input"))
        self.add_text_input_btn.clicked.connect(self.add_text_input)
        
        self.add_image_analysis_btn = QPushButton("🖼️ " + tr("add_image_analysis"))
        self.add_image_analysis_btn.clicked.connect(self.add_image_analysis_input)
        
        self.add_req_analysis_btn = QPushButton("📋 " + tr("add_requirement_analysis"))
        self.add_req_analysis_btn.clicked.connect(self.add_requirement_analysis_input)
        
        input_buttons_layout.addWidget(self.add_text_input_btn)
        input_buttons_layout.addWidget(self.add_image_analysis_btn)
        input_buttons_layout.addWidget(self.add_req_analysis_btn)
        input_layout.addLayout(input_buttons_layout)
        
        # Input list display
        self.input_list_widget = QTextEdit()
        self.input_list_widget.setReadOnly(True)
        self.input_list_widget.setMaximumHeight(150)
        self.input_list_widget.setPlaceholderText(tr("no_inputs"))
        input_layout.addWidget(QLabel(tr("prototype_inputs")))
        input_layout.addWidget(self.input_list_widget)
        
        # Clear inputs button
        self.clear_inputs_btn = QPushButton(tr("clear_all_inputs"))
        self.clear_inputs_btn.clicked.connect(self.clear_prototype_inputs)
        input_layout.addWidget(self.clear_inputs_btn)
        
        left_layout.addWidget(input_group)
        
        # Prototype Settings Section
        settings_group = QGroupBox(tr("prototype_settings"))
        settings_layout = QFormLayout(settings_group)
        
        # Prototype type
        self.prototype_type_combo = QComboBox()
        self.prototype_type_combo.addItems([tr("web"), tr("mobile"), tr("desktop")])
        settings_layout.addRow(tr("prototype_type"), self.prototype_type_combo)
        
        # Framework
        self.framework_combo = QComboBox()
        self.framework_combo.addItems([tr("html_css_js"), tr("react"), tr("vue"), tr("angular")])
        settings_layout.addRow(tr("framework"), self.framework_combo)
        
        # Style framework
        self.style_framework_combo = QComboBox()
        self.style_framework_combo.addItems([tr("bootstrap"), tr("tailwind"), tr("custom")])
        settings_layout.addRow(tr("style_framework"), self.style_framework_combo)
        
        # Responsive design
        self.responsive_check = QCheckBox()
        self.responsive_check.setChecked(True)
        settings_layout.addRow(tr("responsive_design"), self.responsive_check)
        
        # Accessibility support
        self.accessibility_check = QCheckBox()
        self.accessibility_check.setChecked(True)
        settings_layout.addRow(tr("accessibility_support"), self.accessibility_check)
        
        left_layout.addWidget(settings_group)
        
        # Generate button
        self.generate_prototype_btn = QPushButton("🚀 " + tr("generate_prototype"))
        self.generate_prototype_btn.clicked.connect(self.generate_prototype)
        self.generate_prototype_btn.setEnabled(False)
        left_layout.addWidget(self.generate_prototype_btn)
        
        # Progress section
        progress_group = QGroupBox(tr("prototype_generation"))
        progress_layout = QVBoxLayout(progress_group)
        
        self.prototype_progress_bar = QProgressBar()
        progress_layout.addWidget(self.prototype_progress_bar)
        
        self.prototype_status_label = QLabel(tr("ready"))
        progress_layout.addWidget(self.prototype_status_label)
        
        left_layout.addWidget(progress_group)
        left_layout.addStretch()
        
        # Right panel - Results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Results tabs
        self.prototype_results_tab_widget = QTabWidget()
        
        # Code Preview Tab
        code_tab = QWidget()
        code_layout = QVBoxLayout(code_tab)
        
        # Code type selector
        code_type_layout = QHBoxLayout()
        code_type_layout.addWidget(QLabel(tr("code_preview")))
        self.code_type_combo = QComboBox()
        self.code_type_combo.addItems([tr("html_code"), tr("css_code"), tr("js_code")])
        self.code_type_combo.currentTextChanged.connect(self.switch_code_view)
        code_type_layout.addWidget(self.code_type_combo)
        code_type_layout.addStretch()
        code_layout.addLayout(code_type_layout)
        
        self.code_display = QTextEdit()
        self.code_display.setReadOnly(True)
        self.code_display.setPlaceholderText(tr("no_prototype_result"))
        code_layout.addWidget(self.code_display)
        
        self.prototype_results_tab_widget.addTab(code_tab, tr("code_preview"))
        
        # Component Structure Tab
        structure_tab = QWidget()
        structure_layout = QVBoxLayout(structure_tab)
        
        self.structure_display = QTextEdit()
        self.structure_display.setReadOnly(True)
        self.structure_display.setPlaceholderText(tr("no_prototype_result"))
        structure_layout.addWidget(self.structure_display)
        
        self.prototype_results_tab_widget.addTab(structure_tab, tr("component_structure"))
        
        # Design Rationale Tab
        rationale_tab = QWidget()
        rationale_layout = QVBoxLayout(rationale_tab)
        
        self.rationale_display = QTextEdit()
        self.rationale_display.setReadOnly(True)
        self.rationale_display.setPlaceholderText(tr("no_prototype_result"))
        rationale_layout.addWidget(self.rationale_display)
        
        self.prototype_results_tab_widget.addTab(rationale_tab, tr("design_rationale"))
        
        # Implementation Notes Tab
        notes_tab = QWidget()
        notes_layout = QVBoxLayout(notes_tab)
        
        self.notes_display = QTextEdit()
        self.notes_display.setReadOnly(True)
        self.notes_display.setPlaceholderText(tr("no_prototype_result"))
        notes_layout.addWidget(self.notes_display)
        
        self.prototype_results_tab_widget.addTab(notes_tab, tr("implementation_notes"))
        
        # Preview Tab
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)
        
        # Preview will be implemented later with QWebEngineView
        self.preview_placeholder = QLabel(tr("preview") + " - " + tr("prototype_coming_soon"))
        self.preview_placeholder.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.preview_placeholder)
        
        self.prototype_results_tab_widget.addTab(preview_tab, tr("preview"))
        
        right_layout.addWidget(self.prototype_results_tab_widget)
        
        # Export buttons
        export_layout = QHBoxLayout()
        self.export_prototype_html_btn = QPushButton(tr("export_html"))
        self.export_prototype_html_btn.clicked.connect(self.export_prototype_html)
        self.export_prototype_html_btn.setEnabled(False)
        
        self.export_prototype_json_btn = QPushButton(tr("export_json"))
        self.export_prototype_json_btn.clicked.connect(self.export_prototype_json)
        self.export_prototype_json_btn.setEnabled(False)
        
        self.export_prototype_separate_btn = QPushButton(tr("export_separate"))
        self.export_prototype_separate_btn.clicked.connect(self.export_prototype_separate)
        self.export_prototype_separate_btn.setEnabled(False)
        
        export_layout.addWidget(self.export_prototype_html_btn)
        export_layout.addWidget(self.export_prototype_json_btn)
        export_layout.addWidget(self.export_prototype_separate_btn)
        export_layout.addStretch()
        
        right_layout.addLayout(export_layout)
        
        # Add panels to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
    
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
        header_text = f"=== {tr('requirements_analysis')} ===\n{tr('analyzing_requirements_please_wait')}\n\n"
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
    
    def extract_requirement_list(self):
        """Extract requirement list (Phase 1)"""
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
        
        # Disable buttons
        self.extract_list_btn.setEnabled(False)
        self.detailed_analysis_btn.setEnabled(False)
        self.analyze_requirements_btn.setEnabled(False)
        self.req_progress_bar.setValue(0)
        
        # Clear previous results
        self.overview_text.clear()
        self.requirements_list.clear()
        self.components_text.clear()
        self.quality_text.clear()
        
        # Show analysis header
        header_text = f"=== {tr('extracting_requirements_list')} ===\n{tr('analyzing_requirements_please_wait')}\n\n"
        self.overview_text.setPlainText(header_text)
        
        # Prepare input data for Phase 1
        input_data = {
            "text": requirements_text,
            "context": self.context_text.toPlainText().strip(),
            "platform": self.platform_combo.currentText(),
            "phase": "list"
        }
        
        # Start analysis in worker thread
        self.analysis_worker = AnalysisWorker(self.requirement_analyzer, input_data)
        self.analysis_worker.finished.connect(self.on_requirement_list_finished)
        self.analysis_worker.error.connect(self.on_requirements_analysis_error)
        self.analysis_worker.progress.connect(self.on_requirements_progress_update)
        self.analysis_worker.status.connect(self.on_requirements_status_update)
        self.analysis_worker.streaming_text.connect(self.on_requirements_streaming_text_update)
        self.analysis_worker.start()
    
    def detailed_analysis(self):
        """Detailed analysis (Phase 2)"""
        if not self.current_requirements_result:
            QMessageBox.warning(self, tr("warning"), tr("extract_requirement_list_first"))
            return
        
        # Disable buttons
        self.extract_list_btn.setEnabled(False)
        self.detailed_analysis_btn.setEnabled(False)
        self.analyze_requirements_btn.setEnabled(False)
        self.req_progress_bar.setValue(0)
        
        # Show analysis header
        header_text = f"=== {tr('detailed_analysis')} ===\n{tr('analyzing_requirements_please_wait')}\n\n"
        self.overview_text.setPlainText(header_text)
        
        # Prepare input data for Phase 2
        # Handle both Requirement objects and dict objects
        requirement_list = []
        for req in self.current_requirements_result.requirements:
            if hasattr(req, 'to_dict'):
                # It's a Requirement object
                requirement_list.append(req.to_dict())
            elif isinstance(req, dict):
                # It's already a dictionary
                requirement_list.append(req)
            else:
                # Unknown type, log error and skip
                print(f"Warning: Unknown requirement type: {type(req)}")
                continue
        
        input_data = {
            "text": self.requirements_text.toPlainText().strip(),
            "context": self.context_text.toPlainText().strip(),
            "platform": self.platform_combo.currentText(),
            "phase": "detail",
            "requirement_list": requirement_list
        }
        
        # Start analysis in worker thread
        self.analysis_worker = AnalysisWorker(self.requirement_analyzer, input_data)
        self.analysis_worker.finished.connect(self.on_requirements_analysis_finished)
        self.analysis_worker.error.connect(self.on_requirements_analysis_error)
        self.analysis_worker.progress.connect(self.on_requirements_progress_update)
        self.analysis_worker.status.connect(self.on_requirements_status_update)
        self.analysis_worker.streaming_text.connect(self.on_requirements_streaming_text_update)
        self.analysis_worker.start()
    
    def on_requirement_list_finished(self, result):
        """Handle completion of requirement list extraction"""
        from core.requirement_analyzer.models import AnalysisResult
        
        # Convert dict back to AnalysisResult if needed
        if isinstance(result, dict):
            self.current_requirements_result = AnalysisResult.from_dict(result)
        else:
            self.current_requirements_result = result
        
        # Enable buttons
        self.extract_list_btn.setEnabled(True)
        self.detailed_analysis_btn.setEnabled(True)
        self.analyze_requirements_btn.setEnabled(True)
        
        # Display results
        self.display_requirements_result(self.current_requirements_result)
        
        # Show completion message
        self.req_status_label.setText(tr("requirements_list_extraction_completed"))
        self.req_progress_bar.setValue(100)
    
    def on_requirements_analysis_finished(self, result):
        """Handle requirements analysis completion"""
        from core.requirement_analyzer.models import AnalysisResult
        
        # Convert dict back to AnalysisResult if needed
        if isinstance(result, dict):
            self.current_requirements_result = AnalysisResult.from_dict(result)
        else:
            self.current_requirements_result = result
            
        self.display_requirements_result(self.current_requirements_result)
        self.analyze_requirements_btn.setEnabled(True)
        self.extract_list_btn.setEnabled(True)
        self.detailed_analysis_btn.setEnabled(True)
        self.export_req_json_btn.setEnabled(True)
        self.export_req_txt_btn.setEnabled(True)
        self.req_status_label.setText(tr('analysis_completed'))
    
    def on_requirements_analysis_error(self, error_msg):
        """Handle requirements analysis error"""
        QMessageBox.critical(self, tr('analysis_error'), f"{tr('requirements_analysis')} {tr('analysis_failed')}: {error_msg}")
        self.analyze_requirements_btn.setEnabled(True)
        self.extract_list_btn.setEnabled(True)
        self.detailed_analysis_btn.setEnabled(True)
        self.req_status_label.setText(tr('analysis_failed'))
    
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
            overview_text += f"=== {tr('analysis_summary')} ===\n\n"
            overview_text += f"{tr('project_overview')}:\n{result.project_overview or tr('na')}\n\n"
            overview_text += f"{tr('target_audience')}:\n{result.target_audience or tr('na')}\n\n"
            overview_text += f"{tr('target_platform')}: {result.platform or tr('na')}\n\n"
            
            overview_text += f"{tr('quality_scores')}:\n"
            overview_text += f"• {tr('completeness')}: {result.completeness_score:.2f}\n"
            overview_text += f"• {tr('clarity')}: {result.clarity_score:.2f}\n"
            overview_text += f"• {tr('feasibility')}: {result.feasibility_score:.2f}\n\n"
            
            overview_text += f"{tr('development_estimation')}: {result.total_estimated_effort or tr('na')}\n\n"
            
            framework_recommendations = result.framework_recommendations
            if framework_recommendations:
                overview_text += f"{tr('recommended_frameworks')}:\n"
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
            QMessageBox.critical(self, tr('display_error'), f"{tr('failed_display_results')}: {str(e)}")
    
    def filter_requirements(self):
        """Filter and display requirements based on selected filters"""
        if not self.current_requirements_result:
            return
        
        type_filter = self.req_type_filter.currentText()
        priority_filter = self.req_priority_filter.currentText()
        
        filtered_reqs = []
        
        requirements = self.current_requirements_result.requirements
        for req in requirements:
            # Type filter
            if type_filter != tr('all'):
                type_map = {
                    tr('functional'): "functional",
                    tr('ui_component'): "ui_component", 
                    tr('layout'): "layout",
                    tr('styling'): "styling",
                    tr('interaction'): "interaction",
                    tr('data'): "data",
                    tr('performance'): "performance",
                    tr('accessibility'): "accessibility",
                    tr('business'): "business"
                }
                req_type = req.get('type') if isinstance(req, dict) else req.type.value
                if req_type != type_map.get(type_filter, ""):
                    continue
            
            # Priority filter
            if priority_filter != tr('all'):
                req_priority = req.get('priority') if isinstance(req, dict) else req.priority.value
                if req_priority != priority_filter.lower():
                    continue
            
            filtered_reqs.append(req)
        
        # Display filtered requirements
        req_text = f"=== {tr('requirements_list')} ({len(filtered_reqs)} {tr('items')}) ===\n\n"
        
        for i, req in enumerate(filtered_reqs, 1):
            if isinstance(req, dict):
                title = req.get('title', tr('na'))
                req_type = req.get('type', 'unknown').replace('_', ' ').title()
                priority = req.get('priority', 'unknown').title()
                status = req.get('status', 'unknown').title()
                description = req.get('description', tr('na'))
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
            req_text += f"   {tr('type')}: {req_type}\n"
            req_text += f"   {tr('priority')}: {priority}\n"
            req_text += f"   {tr('status')}: {status}\n"
            req_text += f"   {tr('description')}: {description}\n"
            
            if acceptance_criteria:
                req_text += f"   {tr('acceptance_criteria')}:\n"
                for criteria in acceptance_criteria:
                    req_text += f"     • {criteria}\n"
            
            if estimated_effort:
                req_text += f"   {tr('estimated_effort')}: {estimated_effort}\n"
            
            if rationale:
                req_text += f"   {tr('rationale')}: {rationale}\n"
            
            req_text += "\n"
        
        self.requirements_list.setPlainText(req_text)
    
    def display_components(self, result):
        """Display component specifications"""
        comp_text = f"=== {tr('component_specifications')} ===\n\n"
        
        # Get UI component requirements
        requirements = result.requirements
        ui_reqs = []
        for req in requirements:
            if isinstance(req, dict):
                if req.get('type') == 'ui_component':
                    ui_reqs.append(req)
            else:
                if req.type.value == 'ui_component':
                    ui_reqs.append(req)
        
        if not ui_reqs:
            comp_text += f"{tr('no_ui_components')}\n"
        else:
            for req in ui_reqs:
                if isinstance(req, dict):
                    title = req.get('title', tr('na'))
                    description = req.get('description', tr('na'))
                    component_spec = req.get('component_spec')
                else:
                    title = req.title
                    description = req.description
                    component_spec = req.component_spec
                
                comp_text += f"{tr('component')}: {title}\n"
                comp_text += f"{tr('description')}: {description}\n"
                
                if component_spec:
                    if isinstance(component_spec, dict):
                        comp_text += f"• {tr('type')}: {component_spec.get('type', tr('na'))}\n"
                        comp_text += f"• {tr('name')}: {component_spec.get('name', tr('na'))}\n"
                        
                        properties = component_spec.get('properties', {})
                        if properties:
                            comp_text += f"• {tr('properties')}:\n"
                            for key, value in properties.items():
                                comp_text += f"  - {key}: {value}\n"
                        
                        events = component_spec.get('events', [])
                        if events:
                            comp_text += f"• {tr('events')}: {', '.join(events)}\n"
                        
                        validation = component_spec.get('validation')
                        if validation:
                            comp_text += f"• {tr('validation')}: {validation}\n"
                        
                        accessibility = component_spec.get('accessibility')
                        if accessibility:
                            comp_text += f"• {tr('accessibility')}: {accessibility}\n"
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
        quality_text = f"=== {tr('quality_analysis')} ===\n\n"
        
        quality_text += f"{tr('analysis_scores')}:\n"
        quality_text += f"• {tr('completeness_score')}: {result.completeness_score:.2f} / 1.0\n"
        quality_text += f"• {tr('clarity_score')}: {result.clarity_score:.2f} / 1.0\n"
        quality_text += f"• {tr('feasibility_score')}: {result.feasibility_score:.2f} / 1.0\n\n"
        
        gaps = result.gaps
        if gaps:
            quality_text += f"{tr('identified_gaps')}:\n"
            for gap in gaps:
                quality_text += f"• {gap}\n"
            quality_text += "\n"
        
        ambiguities = result.ambiguities
        if ambiguities:
            quality_text += f"{tr('ambiguities_clarify')}:\n"
            for ambiguity in ambiguities:
                quality_text += f"• {ambiguity}\n"
            quality_text += "\n"
        
        recommendations = result.recommendations
        if recommendations:
            quality_text += f"{tr('recommendations')}:\n"
            for rec in recommendations:
                quality_text += f"• {rec}\n"
            quality_text += "\n"
        
        development_phases = result.development_phases
        if development_phases:
            quality_text += f"{tr('development_phases')}:\n"
            for phase in development_phases:
                if isinstance(phase, dict):
                    name = phase.get('name', tr('na'))
                    description = phase.get('description', tr('na'))
                    duration = phase.get('estimated_duration', tr('na'))
                    quality_text += f"• {name}: {description}\n"
                    quality_text += f"  {tr('duration')}: {duration}\n"
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
        self.module_combo.addItems(["image_analyzer", "requirement_analyzer", "prototype_generator"])
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
            QMessageBox.critical(self, tr("error"), f"{tr('failed_load_settings')}：{str(e)}")
    
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
            QMessageBox.critical(self, tr("error"), f"{tr('failed_save_settings')}：{str(e)}")
    
    def test_configuration(self):
        """Test the current configuration"""
        try:
            # Test each configured model
            tested_models = []
            failed_models = []
            
            for model_name, model_config in self.config.models.items():
                if not model_config.api_key:
                    failed_models.append(f"{model_name}: {tr('missing_api_key')}")
                    continue
                
                # Basic validation
                if model_config.provider == "openai" and not model_config.model_id:
                    failed_models.append(f"{model_name}: {tr('openai_needs_model_id')}")
                    continue
                    
                if model_config.provider == "deepseek" and not model_config.base_url:
                    failed_models.append(f"{model_name}: {tr('deepseek_needs_base_url')}")
                    continue
                
                tested_models.append(model_name)
            
            # Show results
            result_text = f"{tr('configuration_test_results')}:\n\n"
            
            if tested_models:
                result_text += f"{tr('successful_models')} ({len(tested_models)}):\n"
                for model in tested_models:
                    result_text += f"✓ {model}\n"
                result_text += "\n"
            
            if failed_models:
                result_text += f"{tr('configuration_issues')} ({len(failed_models)}):\n"
                for error in failed_models:
                    result_text += f"✗ {error}\n"
                result_text += "\n"
            
            # Check modules
            result_text += f"{tr('module_status')}:\n"
            for module_name in ["image_analyzer", "requirement_analyzer", "prototype_generator"]:
                module_config = self.config.get_module_config(module_name)
                if module_config and module_config.enabled:
                    model_config = self.config.get_model_config(module_config.model_config)
                    if model_config and model_config.api_key:
                        result_text += f"✓ {module_name}: {tr('enabled_using_model')} {module_config.model_config}\n"
                    else:
                        result_text += f"✗ {module_name}: {tr('enabled_invalid_model')}\n"
                else:
                    result_text += f"- {module_name}: {tr('disabled')}\n"
            
            QMessageBox.information(self, tr('configuration_test_results'), result_text)
             
        except Exception as e:
            QMessageBox.critical(self, tr('error'), f"{tr('config_test_error')}：{str(e)}")
    
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
    
    # Prototype Generator Methods
    def add_text_input(self):
        """Add a text input to prototype generator"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("add_text_input"))
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Input name
        layout.addWidget(QLabel(tr("input_name")))
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("例如: 用户界面需求")
        layout.addWidget(name_edit)
        
        # Input content
        layout.addWidget(QLabel(tr("input_content")))
        content_edit = QTextEdit()
        content_edit.setPlaceholderText("输入详细的文本内容...")
        layout.addWidget(content_edit)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text().strip() or tr("text_input")
            content = content_edit.toPlainText().strip()
            
            if content:
                self.prototype_generator.add_input("text", content, name)
                self.update_input_list_display()
                self.update_generate_button_state()
    
    def add_image_analysis_input(self):
        """Add current image analysis result as input"""
        if not self.current_analysis_result:
            QMessageBox.warning(self, tr("warning"), "请先完成图像分析")
            return
        
        # Convert result to string format
        if isinstance(self.current_analysis_result, dict):
            import json
            content = json.dumps(self.current_analysis_result, ensure_ascii=False, indent=2)
        else:
            content = str(self.current_analysis_result)
        
        name = tr("image_analysis_result")
        self.prototype_generator.add_input("image_analysis", content, name)
        self.update_input_list_display()
        self.update_generate_button_state()
    
    def add_requirement_analysis_input(self):
        """Add current requirement analysis result as input"""
        if not self.current_requirements_result:
            QMessageBox.warning(self, tr("warning"), "请先完成需求分析")
            return
        
        # Convert result to string format
        if hasattr(self.current_requirements_result, 'to_dict'):
            import json
            content = json.dumps(self.current_requirements_result.to_dict(), ensure_ascii=False, indent=2)
        elif isinstance(self.current_requirements_result, dict):
            import json
            content = json.dumps(self.current_requirements_result, ensure_ascii=False, indent=2)
        else:
            content = str(self.current_requirements_result)
        
        name = tr("requirement_analysis_result")
        self.prototype_generator.add_input("requirement_analysis", content, name)
        self.update_input_list_display()
        self.update_generate_button_state()
    
    def clear_prototype_inputs(self):
        """Clear all prototype inputs"""
        self.prototype_generator.clear_inputs()
        self.update_input_list_display()
        self.update_generate_button_state()
    
    def update_input_list_display(self):
        """Update the input list display"""
        inputs_summary = self.prototype_generator.get_inputs_summary()
        
        if not inputs_summary:
            self.input_list_widget.setPlainText(tr("no_inputs"))
            return
        
        display_text = f"=== {tr('prototype_inputs')} ({len(inputs_summary)} {tr('items')}) ===\n\n"
        
        for inp in inputs_summary:
            display_text += f"🔹 {inp['name']} ({inp['type']})\n"
            display_text += f"   {tr('input_preview')}: {inp['content_preview']}\n\n"
        
        self.input_list_widget.setPlainText(display_text)
    
    def update_generate_button_state(self):
        """Update the generate button enabled state"""
        has_inputs = len(self.prototype_generator.inputs) > 0
        self.generate_prototype_btn.setEnabled(has_inputs)
    
    def generate_prototype(self):
        """Generate prototype from current inputs"""
        if not self.prototype_generator.inputs:
            QMessageBox.warning(self, tr("warning"), "请先添加输入源")
            return
        
        # Check if API key is configured
        config = self.config.get_module_config("prototype_generator")
        if not config:
            # Use the same model config as requirement analyzer
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
        
        # Disable generate button
        self.generate_prototype_btn.setEnabled(False)
        self.prototype_progress_bar.setValue(0)
        
        # Clear previous results
        self.clear_prototype_results_display()
        
        # Show generation header
        header_text = f"=== {tr('prototype_generation')} ===\n{tr('generating_prototype')}\n\n"
        self.rationale_display.setPlainText(header_text)
        
        # Prepare input data
        input_data = {
            "prototype_type": self.prototype_type_combo.currentText(),
            "framework": self.framework_combo.currentText(),
            "style_framework": self.style_framework_combo.currentText(),
            "responsive": self.responsive_check.isChecked(),
            "accessibility": self.accessibility_check.isChecked()
        }
        
        # Start generation in worker thread
        self.analysis_worker = AnalysisWorker(self.prototype_generator, input_data)
        self.analysis_worker.finished.connect(self.on_prototype_generation_finished)
        self.analysis_worker.error.connect(self.on_prototype_generation_error)
        self.analysis_worker.progress.connect(self.on_prototype_progress_update)
        self.analysis_worker.status.connect(self.on_prototype_status_update)
        self.analysis_worker.streaming_text.connect(self.on_prototype_streaming_text_update)
        self.analysis_worker.start()
    
    def on_prototype_generation_finished(self, result):
        """Handle prototype generation completion"""
        from core.prototype_generator.analyzer import PrototypeResult
        
        # Convert dict back to PrototypeResult if needed
        if isinstance(result, dict):
            prototype_result = PrototypeResult()
            prototype_result.html_code = result.get('html_code', '')
            prototype_result.css_code = result.get('css_code', '')
            prototype_result.js_code = result.get('js_code', '')
            prototype_result.component_structure = result.get('component_structure', [])
            prototype_result.design_rationale = result.get('design_rationale', '')
            prototype_result.implementation_notes = result.get('implementation_notes', [])
            prototype_result.preview_available = result.get('preview_available', False)
            prototype_result.metadata = result.get('metadata', {})
            self.current_prototype_result = prototype_result
        else:
            self.current_prototype_result = result
        
        self.display_prototype_result(self.current_prototype_result)
        self.generate_prototype_btn.setEnabled(True)
        self.export_prototype_html_btn.setEnabled(True)
        self.export_prototype_json_btn.setEnabled(True)
        self.export_prototype_separate_btn.setEnabled(True)
        self.prototype_status_label.setText(tr("prototype_generated"))
    
    def on_prototype_generation_error(self, error_msg):
        """Handle prototype generation error"""
        QMessageBox.critical(self, tr("error"), f"{tr('prototype_generation_failed')}: {error_msg}")
        self.generate_prototype_btn.setEnabled(True)
        self.prototype_status_label.setText(tr("prototype_generation_failed"))
    
    def on_prototype_progress_update(self, value):
        """Update prototype progress bar"""
        self.prototype_progress_bar.setValue(value)
    
    def on_prototype_status_update(self, status):
        """Update prototype status label"""
        self.prototype_status_label.setText(status)
    
    def on_prototype_streaming_text_update(self, text_chunk):
        """Handle streaming text updates for prototype generation"""
        # Append text chunk to rationale display area
        cursor = self.rationale_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text_chunk)
        self.rationale_display.setTextCursor(cursor)
        # Auto-scroll to bottom
        self.rationale_display.ensureCursorVisible()
    
    def display_prototype_result(self, result):
        """Display prototype generation results"""
        try:
            # Add completion metadata to rationale
            rationale_text = f"\n\n{'='*60}\n"
            rationale_text += f"=== {tr('prototype_generated')} ===\n\n"
            rationale_text += f"{tr('design_rationale')}:\n{result.design_rationale or tr('na')}\n\n"
            
            # Append to existing streaming content
            cursor = self.rationale_display.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertText(rationale_text)
            self.rationale_display.setTextCursor(cursor)
            self.rationale_display.ensureCursorVisible()
            
            # Update code displays
            self.switch_code_view()
            
            # Display component structure
            self.display_component_structure(result)
            
            # Display implementation notes
            self.display_implementation_notes(result)
            
        except Exception as e:
            QMessageBox.critical(self, tr('display_error'), f"{tr('failed_display_results')}: {str(e)}")
    
    def clear_prototype_results_display(self):
        """Clear all prototype result displays"""
        self.code_display.clear()
        self.structure_display.clear()
        self.rationale_display.clear()
        self.notes_display.clear()
    
    def switch_code_view(self):
        """Switch code display based on selected type"""
        if not self.current_prototype_result:
            return
        
        code_type = self.code_type_combo.currentText()
        
        if code_type == tr("html_code"):
            self.code_display.setPlainText(self.current_prototype_result.html_code)
        elif code_type == tr("css_code"):
            self.code_display.setPlainText(self.current_prototype_result.css_code)
        elif code_type == tr("js_code"):
            self.code_display.setPlainText(self.current_prototype_result.js_code)
    
    def display_component_structure(self, result):
        """Display component structure"""
        structure_text = f"=== {tr('component_structure')} ===\n\n"
        
        if not result.component_structure:
            structure_text += f"{tr('no_prototype_result')}\n"
        else:
            for i, component in enumerate(result.component_structure, 1):
                if isinstance(component, dict):
                    name = component.get('name', tr('na'))
                    comp_type = component.get('type', tr('na'))
                    description = component.get('description', tr('na'))
                    props = component.get('props', [])
                    events = component.get('events', [])
                    
                    structure_text += f"{i}. {name} ({comp_type})\n"
                    structure_text += f"   {tr('description')}: {description}\n"
                    
                    if props:
                        structure_text += f"   {tr('properties')}: {', '.join(props)}\n"
                    
                    if events:
                        structure_text += f"   {tr('events')}: {', '.join(events)}\n"
                    
                    structure_text += "\n"
                else:
                    structure_text += f"{i}. {str(component)}\n"
        
        self.structure_display.setPlainText(structure_text)
    
    def display_implementation_notes(self, result):
        """Display implementation notes"""
        notes_text = f"=== {tr('implementation_notes')} ===\n\n"
        
        if not result.implementation_notes:
            notes_text += f"{tr('no_prototype_result')}\n"
        else:
            for i, note in enumerate(result.implementation_notes, 1):
                notes_text += f"{i}. {note}\n"
        
        self.notes_display.setPlainText(notes_text)
    
    def export_prototype_html(self):
        """Export prototype as HTML file"""
        if not self.current_prototype_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            tr("select_export_location"), 
            "prototype.html", 
            tr("html_files")
        )
        
        if file_path:
            try:
                success = self.prototype_generator.export_prototype(file_path, 'html')
                if success:
                    QMessageBox.information(self, tr("success"), tr("prototype_export_success"))
                else:
                    QMessageBox.critical(self, tr("error"), tr("prototype_export_failed"))
            except Exception as e:
                QMessageBox.critical(self, tr("error"), f"{tr('prototype_export_failed')}: {str(e)}")
    
    def export_prototype_json(self):
        """Export prototype as JSON file"""
        if not self.current_prototype_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            tr("select_export_location"), 
            "prototype.json", 
            tr("json_files")
        )
        
        if file_path:
            try:
                success = self.prototype_generator.export_prototype(file_path, 'json')
                if success:
                    QMessageBox.information(self, tr("success"), tr("prototype_export_success"))
                else:
                    QMessageBox.critical(self, tr("error"), tr("prototype_export_failed"))
            except Exception as e:
                QMessageBox.critical(self, tr("error"), f"{tr('prototype_export_failed')}: {str(e)}")
    
    def export_prototype_separate(self):
        """Export prototype as separate HTML, CSS, JS files"""
        if not self.current_prototype_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            tr("select_export_location"), 
            "prototype.html", 
            tr("html_files")
        )
        
        if file_path:
            try:
                success = self.prototype_generator.export_prototype(file_path, 'separate')
                if success:
                    QMessageBox.information(self, tr("success"), tr("prototype_export_success"))
                else:
                    QMessageBox.critical(self, tr("error"), tr("prototype_export_failed"))
            except Exception as e:
                QMessageBox.critical(self, tr("error"), f"{tr('prototype_export_failed')}: {str(e)}")