from PyQt5.QtCore import QThread, pyqtSignal
from pdf2image import convert_from_path
from PIL import Image
from utils.image_processing import (
    invert_colors_rgb, convert_to_grayscale, enhance_contrast, crop_white_borders, clean_gray_dots
)

Image.MAX_IMAGE_PIXELS = None  # 解除 PIL 限制，支持大文件

class PDFProcessingThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str)

    def __init__(self, input_pdf, output_pdf, mode, dpi, language):
        super().__init__()
        self.input_pdf = input_pdf
        self.output_pdf = output_pdf
        self.mode = mode
        self.dpi = dpi
        self.language = language

    def run(self):
        try:
            images = convert_from_path(self.input_pdf, dpi=self.dpi)
            processed_images = []
            for i, img in enumerate(images):
                if self.mode in ["Invert Colors", "反转颜色"]:
                    processed_img = invert_colors_rgb(img)
                elif self.mode in ["Grayscale", "灰度化"]:
                    processed_img = convert_to_grayscale(img)
                elif self.mode in ["Enhance Contrast", "增强对比度（黑白增强）"]:
                    processed_img = enhance_contrast(img)
                elif self.mode in ["Crop White Borders", "剪裁无内容白边"]:
                    processed_img = crop_white_borders(img)
                elif self.mode in ["Clean Gray Dots", "清除灰色"]:
                    processed_img = clean_gray_dots(img)
                else:
                    raise ValueError("Unknown processing mode selected.")
                processed_images.append(processed_img)
                self.progress.emit(int((i + 1) / len(images) * 100))

            processed_images[0].save(self.output_pdf, save_all=True, append_images=processed_images[1:])
            self.result.emit(f"Saved: {self.output_pdf}" if self.language == "English" else f"已保存: {self.output_pdf}")
        except Exception as e:
            self.result.emit(f"Error: {e}" if self.language == "English" else f"错误: {e}")