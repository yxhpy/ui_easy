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

class AnalysisWorker(QThread):
    """Worker thread for image analysis"""
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
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.image_analyzer = ImageAnalyzer(self.config)
        self.current_image_path = None
        self.analysis_worker = None
        
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
        
        layout = QVBoxLayout(tab)
        placeholder = QLabel("Requirement Analyzer - Coming Soon")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
    
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