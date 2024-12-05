from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel,
    QPushButton, QComboBox, QLineEdit, QToolButton, QMessageBox, QWidget, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QTextEdit
import os
import json
from threads.pdf_processing import PDFProcessingThread

class PDFProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = "English"
        self.translations = self.load_translations()
        self.setWindowTitle(self.translations[self.language]["app_title"])
        self.setGeometry(300, 300, 600, 500)
        self.input_pdf = None  # 当前选中的 PDF 文件路径
        self.is_processing = False  # 表示是否正在处理
        self.timer = QTimer(self)  # 初始化计时器
        self.timer.timeout.connect(self.update_timer)  # 连接计时器更新函数
        self.elapsed_time = 0  # 记录经过的时间（以秒为单位）
        self.initUI()

        # 确保窗口接受拖拽事件
        self.setAcceptDrops(True)


    def load_translations(self):
        with open("translations/en.json") as en_file, open("translations/zh.json") as zh_file:
            return {
                "English": json.load(en_file),
                "中文": json.load(zh_file)
            }

    def initUI(self):
        main_layout = QHBoxLayout()

        # 左侧布局
        left_layout = QVBoxLayout()
        file_group = QGroupBox(self.translations[self.language]["file_selection"])
        file_layout = QVBoxLayout()

        # 初始化 SVG 图标
        self.svg_widget = QSvgWidget(self)
        if self.input_pdf:
            self.svg_widget.load("assets/pdf_icon.svg")  # 如果已有 PDF，展示 PDF 图标
        else:
            self.svg_widget.load("assets/none.svg")  # 否则展示空图标
        self.svg_widget.setFixedSize(100, 100)
        file_layout.addWidget(self.svg_widget, alignment=Qt.AlignCenter)

        # 文件选择区域
        self.file_label = QLabel(
            self.translations[self.language]["no_file_selected"] if not self.input_pdf else
            self.translations[self.language]["selected_file"].format(os.path.basename(self.input_pdf))
        )
        self.file_label.setWordWrap(True)  # 启用自动换行
        file_layout.addWidget(self.file_label)
        self.file_button = QPushButton(self.translations[self.language]["select_file"])
        self.file_button.clicked.connect(self.select_pdf)
        file_layout.addWidget(self.file_button)
        file_group.setLayout(file_layout)
        left_layout.addWidget(file_group)

        self.progress_bar = QProgressBar(self)
        left_layout.addWidget(self.progress_bar)

        
        main_layout.addLayout(left_layout)

        # 右侧布局
        right_layout = QVBoxLayout()
        lang_button = QPushButton(self.translations[self.language]["switch_language"])
        lang_button.clicked.connect(self.toggle_language)
        right_layout.addWidget(lang_button, alignment=Qt.AlignTop | Qt.AlignRight)

        settings_group = QGroupBox(self.translations[self.language]["settings"])
        settings_layout = QVBoxLayout()

        self.mode_label = QLabel(self.translations[self.language]["processing_mode"])
        settings_layout.addWidget(self.mode_label)

        self.comboBox = QComboBox(self)
        self.update_mode_options()
        settings_layout.addWidget(self.comboBox)

        dpi_container_layout = QHBoxLayout()
        self.dpi_label = QLabel("DPI:")
        self.dpi_input = QLineEdit(self)
        self.dpi_input.setPlaceholderText(self.translations[self.language]["dpi_placeholder"])
        dpi_help_button = QToolButton(self)
        dpi_help_button.setText("?")
        dpi_help_button.clicked.connect(self.show_dpi_help)
        dpi_container_layout.addWidget(dpi_help_button)
        dpi_container_layout.addWidget(self.dpi_label)
        dpi_container_layout.addWidget(self.dpi_input)
        settings_layout.addLayout(dpi_container_layout)

        settings_group.setLayout(settings_layout)
        right_layout.addWidget(settings_group)

        self.process_button = QPushButton(self.translations[self.language]["process_pdf"])
        self.process_button.clicked.connect(self.process_pdf)
        right_layout.addWidget(self.process_button)

        # 添加日志框
        self.log_box = QTextEdit(self)
        self.log_box.setReadOnly(True)  # 设置为只读模式
        self.log_box.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-family: monospace;")
        right_layout.addWidget(self.log_box)

        self.timer_label = QLabel(self.translations[self.language]["processing_timer"].format(0))
        right_layout.addWidget(self.timer_label, alignment=Qt.AlignCenter)
        main_layout.addLayout(right_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    def log_action(self, message):
        """记录日志"""
        self.log_box.append(f"[{self.elapsed_time}s] {message}")
    def update_timer(self):
        self.elapsed_time += 1
        self.timer_label.setText(self.translations[self.language]["processing_timer"].format(self.elapsed_time))

    def handle_result(self, result_message):
        self.timer.stop()  # 停止计时器
        self.is_processing = False
        self.process_button.setEnabled(True)  # 启用按钮
        self.file_label.setText(result_message)  # 显示结果

    def show_dpi_help(self):
        QMessageBox.information(
            self,
            self.translations[self.language]["dpi_info_title"],
            self.translations[self.language]["dpi_info"]
        )

    def toggle_language(self):
        self.language = "中文" if self.language == "English" else "English"
        self.initUI()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith(".pdf") for url in urls):
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.lower().endswith(".pdf"):
                self.input_pdf = file_path
                self.file_label.setText(
                    self.translations[self.language]["selected_file"].format(os.path.basename(file_path))
                )
                self.svg_widget.load("assets/pdf_icon.svg")  # 更新图标为 PDF 图标
                break

    def complete_processing(self):
        self.timer.stop()  # 停止计时器
        self.is_processing = False
        self.process_button.setEnabled(True)  # 启用按钮
        self.file_label.setText(self.translations[self.language]["processing_complete"])
        self.progress_bar.setValue(100)

    def update_mode_options(self):
        self.comboBox.clear()
        self.comboBox.addItems(self.translations[self.language]["modes"])

    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.translations[self.language]["select_pdf"], "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.input_pdf = file_path
            self.file_label.setText(
                self.translations[self.language]["selected_file"].format(os.path.basename(file_path))
            )
            self.svg_widget.load("assets/pdf_icon.svg")  # 更新图标为 PDF 图标
            self.log_action(f"PDF selected: {file_path}")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def process_pdf(self):
        if not self.input_pdf:
            self.file_label.setText(self.translations[self.language]["no_pdf_error"])
            return
        dpi_text = self.dpi_input.text()
        if not dpi_text.isdigit():
            self.file_label.setText(self.translations[self.language]["invalid_dpi_error"])
            return
        dpi = int(dpi_text)
        mode = self.comboBox.currentText()
        if mode == self.translations[self.language]["modes"][0]:
            self.file_label.setText(self.translations[self.language]["select_mode_error"])
            return

        self.process_button.setEnabled(False)  # 禁用按钮
        self.is_processing = True
        self.elapsed_time = 0
        self.timer.start(1000)  # 开始计时，每秒更新

        # 设定输出 PDF 路径，加入模式和 DPI 后缀
        base_name, ext = os.path.splitext(self.input_pdf)
        mode_suffix = mode.replace(" ", "_").replace("（", "_").replace("）", "_")
        output_pdf = f"{base_name}_{mode_suffix}_{dpi}dpi{ext}"
        
        self.log_action(f"Processing started: Mode={mode}, DPI={dpi}")

        # 创建线程
        self.thread = PDFProcessingThread(self.input_pdf, output_pdf, mode, dpi, self.language)
        self.thread.progress.connect(self.update_progress)  # 更新进度条
        self.thread.result.connect(self.handle_result)  # 处理结果
        self.thread.start()

    def handle_result(self, result_message):
        self.timer.stop()  # 停止计时器
        self.is_processing = False
        self.process_button.setEnabled(True)  # 启用按钮
        self.file_label.setText(result_message)  # 显示结果
        self.log_action(f"Processing completed: {result_message}")

