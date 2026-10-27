"""
Modern multi-page PyQt5 GUI for Image Steganography.
Features: Home page, Encode page, Decode page with smooth navigation.
Uses Qt signals for thread-safe UI updates.
"""

import sys
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QLineEdit, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, pyqtSignal, pyqtProperty, QThread
from PyQt5.QtWidgets import QWidget
from PIL import Image as PILImage
import logging
from steganography import SteganographyCore

logger = logging.getLogger(__name__)


class PasswordValidator:
    """Validate passwords against security criteria."""
    
    MIN_LENGTH = 8
    
    @staticmethod
    def validate(password):
        """
        Validate password meets all criteria:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        
        Returns: (is_valid, error_message)
        """
        if not password:
            return False, "Password cannot be empty."
        
        if len(password) < PasswordValidator.MIN_LENGTH:
            return False, f"Password must be at least {PasswordValidator.MIN_LENGTH} characters long."
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter (A-Z)."
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter (a-z)."
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit (0-9)."
        
        return True, "Password is valid."
    
    @staticmethod
    def get_criteria_text():
        """Return formatted password criteria text for display."""
        return (
            f"Password requirements:\n"
            f"• Minimum {PasswordValidator.MIN_LENGTH} characters\n"
            f"• Uppercase letter (A-Z)\n"
            f"• Lowercase letter (a-z)\n"
            f"• Digit (0-9)"
        )


class EncodingWorker(QThread):
    """Worker thread for encoding operations."""
    
    finished = pyqtSignal(bool, str)  # success, result_message
    
    def __init__(self, image_path, message, password, output_path):
        super().__init__()
        self.image_path = image_path
        self.message = message
        self.password = password
        self.output_path = output_path
    
    def run(self):
        """Run encoding in worker thread."""
        try:
            success, result = SteganographyCore.encode(
                self.image_path, self.message, self.password, self.output_path
            )
            self.finished.emit(success, result)
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class DecodingWorker(QThread):
    """Worker thread for decoding operations."""
    
    finished = pyqtSignal(bool, str)  # success, message_or_error
    
    def __init__(self, image_path, password):
        super().__init__()
        self.image_path = image_path
        self.password = password
    
    def run(self):
        """Run decoding in worker thread."""
        try:
            success, result = SteganographyCore.decode(self.image_path, self.password)
            self.finished.emit(success, result)
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class SteganographyApp(QMainWindow):
    """Main application window managing multiple pages."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Steganography Tool")
        self.setGeometry(100, 100, 900, 700)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Create stacked widget for page navigation
        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)
        
        # Create pages
        self.home_page = HomePage(self)
        self.encode_page = EncodePage(self)
        self.decode_page = DecodePage(self)
        
        # Add pages to stack
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.encode_page)
        self.pages.addWidget(self.decode_page)
        
        # Connect navigation signals
        self.home_page.encode_clicked.connect(self.go_to_encode)
        self.home_page.decode_clicked.connect(self.go_to_decode)
        
        self.encode_page.back_clicked.connect(self.go_home)
        self.decode_page.back_clicked.connect(self.go_home)
        
        # Show home page
        self.pages.setCurrentWidget(self.home_page)
    
    def apply_dark_theme(self):
        """Apply dark theme to application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QFrame {
                background-color: #1e1e2e;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #00b4d8;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0096c7;
            }
            QPushButton:pressed {
                background-color: #006e9a;
            }
            QPushButton#backBtn {
                background-color: #444444;
                color: #e0e0e0;
            }
            QPushButton#backBtn:hover {
                background-color: #555555;
            }
            QTextEdit {
                background-color: #2d2d44;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
            }
            QLineEdit {
                background-color: #2d2d44;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
            }
            QMessageBox {
                background-color: #1e1e2e;
            }
            QMessageBox QLabel {
                color: #e0e0e0;
            }
            QMessageBox QPushButton {
                min-width: 60px;
            }
        """)
    
    def go_home(self):
        """Navigate to home page."""
        self.pages.setCurrentWidget(self.home_page)
    
    def go_to_encode(self):
        """Navigate to encode page."""
        self.encode_page.reset()
        self.pages.setCurrentWidget(self.encode_page)
    
    def go_to_decode(self):
        """Navigate to decode page."""
        self.decode_page.reset()
        self.pages.setCurrentWidget(self.decode_page)


class HomePage(QFrame):
    """Home page with navigation buttons."""
    
    from PyQt5.QtCore import pyqtSignal
    encode_clicked = pyqtSignal()
    decode_clicked = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize home page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 100, 50, 100)
        layout.setSpacing(30)
        
        # Title
        title = QLabel("🔐 Image Steganography Tool")
        title.setFont(QFont("Arial", 36, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Hide and extract secret messages in images securely")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Spacer
        layout.addSpacing(50)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(30)
        
        # Encode button
        encode_btn = QPushButton("📝 Encode Message")
        encode_btn.setFont(QFont("Arial", 16, QFont.Bold))
        encode_btn.setMinimumHeight(120)
        encode_btn.clicked.connect(self.encode_clicked.emit)
        buttons_layout.addWidget(encode_btn)
        
        # Decode button
        decode_btn = QPushButton("🔍 Decode Message")
        decode_btn.setFont(QFont("Arial", 16, QFont.Bold))
        decode_btn.setMinimumHeight(120)
        decode_btn.clicked.connect(self.decode_clicked.emit)
        buttons_layout.addWidget(decode_btn)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        # Footer
        footer = QLabel("© 2026 Image Steganography | Secure Message Hiding")
        footer.setFont(QFont("Arial", 10))
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)


class EncodePage(QFrame):
    """Encode page for hiding messages in images."""
    
    from PyQt5.QtCore import pyqtSignal
    back_clicked = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)
        self.image_path = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize encode page UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        
        # Header with back button
        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Back to Home")
        back_btn.setObjectName("backBtn")
        back_btn.setMaximumWidth(150)
        back_btn.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Title
        title = QLabel("Encode Message in Image")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        main_layout.addWidget(title)
        
        # Content layout (2 columns)
        content_layout = QHBoxLayout()
        
        # Left column: Image preview
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        
        left_layout.addWidget(QLabel("Image Preview:"))
        self.image_preview = QLabel("No image selected")
        self.image_preview.setStyleSheet("""
            background-color: #2d2d44;
            border: 2px dashed #00b4d8;
            border-radius: 4px;
            min-height: 300px;
            color: #888888;
        """)
        self.image_preview.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.image_preview)
        
        select_btn = QPushButton("📂 Select Image")
        select_btn.clicked.connect(self.select_image)
        left_layout.addWidget(select_btn)
        
        content_layout.addLayout(left_layout, 1)
        
        # Right column: Input fields
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        
        # Message input
        right_layout.addWidget(QLabel("Secret Message:"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter your secret message here...")
        self.message_input.setMinimumHeight(100)
        right_layout.addWidget(self.message_input)
        
        # Password input
        right_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        right_layout.addWidget(self.password_input)
        
        # Password criteria info
        criteria_label = QLabel(PasswordValidator.get_criteria_text())
        criteria_label.setStyleSheet("color: #aaa; font-size: 10px; background-color: #1a1a2e; padding: 8px; border-radius: 4px;")
        criteria_label.setWordWrap(True)
        right_layout.addWidget(criteria_label)
        
        # Confirm password
        right_layout.addWidget(QLabel("Confirm Password:"))
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        right_layout.addWidget(self.confirm_input)
        
        # Encode button
        encode_btn = QPushButton("🔒 Encode & Save Image")
        encode_btn.setMinimumHeight(50)
        encode_btn.setFont(QFont("Arial", 12, QFont.Bold))
        encode_btn.clicked.connect(self.encode_message)
        right_layout.addWidget(encode_btn)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #00b4d8; font-weight: bold;")
        right_layout.addWidget(self.status_label)
        
        right_layout.addStretch()
        content_layout.addLayout(right_layout, 1)
        
        main_layout.addLayout(content_layout)
    
    def select_image(self):
        """Select image file."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if file_path:
            self.image_path = file_path
            self.display_preview()
    
    def display_preview(self):
        """Display image preview."""
        try:
            pixmap = QPixmap(self.image_path)
            scaled_pixmap = pixmap.scaledToHeight(300, Qt.SmoothTransformation)
            self.image_preview.setPixmap(scaled_pixmap)
            self.image_preview.setText("")
            
            # Show file info
            img = PILImage.open(self.image_path)
            capacity = SteganographyCore.get_max_capacity(img)
            info = f"{img.width}×{img.height} | Max: {capacity} bytes"
            self.status_label.setText(f"ℹ️ {info}")
        except Exception as e:
            self.status_label.setText(f"❌ Error loading image: {str(e)}")
    
    def encode_message(self):
        """Encode message in image."""
        if not self.image_path:
            QMessageBox.warning(self, "Error", "Please select an image first.")
            return
        
        message = self.message_input.toPlainText().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not message:
            QMessageBox.warning(self, "Error", "Please enter a message.")
            return
        
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a password.")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        
        # Validate password meets security criteria
        is_valid, error_msg = PasswordValidator.validate(password)
        if not is_valid:
            criteria = PasswordValidator.get_criteria_text()
            QMessageBox.warning(
                self, 
                "Weak Password", 
                f"{error_msg}\n\n{criteria}"
            )
            return
        
        # Ask user where to save
        file_dialog = QFileDialog()
        output_path, _ = file_dialog.getSaveFileName(
            self,
            "Save Encoded Image",
            "encoded.png",
            "PNG Files (*.png);;All Files (*)"
        )
        
        if not output_path:
            return
        
        # Show loading state
        self.status_label.setText("⏳ Encoding... Please wait")
        self.status_label.setStyleSheet("color: #ffa500; font-weight: bold;")
        QApplication.processEvents()
        
        # Create and start worker thread
        self.encoding_worker = EncodingWorker(self.image_path, message, password, output_path)
        self.encoding_worker.finished.connect(self.on_encoding_complete)
        self.encoding_worker.start()
    
    def on_encoding_complete(self, success, result_message):
        """Handle encoding completion (from worker thread signal)."""
        if success:
            # Trigger vanishing effect
            self.image_preview.setPixmap(QPixmap())
            self.image_preview.setText("✅ Image secured and hidden successfully")
            self.image_preview.setStyleSheet("""
                background-color: #2d2d44;
                border: 2px dashed #00b4d8;
                border-radius: 4px;
                min-height: 300px;
                color: #00aa00;
                font-weight: bold;
                font-size: 14px;
            """)
            
            self.status_label.setText(f"✅ {result_message}")
            self.status_label.setStyleSheet("color: #00aa00; font-weight: bold;")
            
            # Clear inputs after 2 seconds
            QTimer.singleShot(2000, self.clear_after_success)
            
            # Show success dialog
            output_name = os.path.basename(self.encoding_worker.output_path)
            QMessageBox.information(
                self, 
                "Success", 
                f"Message encoded successfully!\nSaved to: {output_name}"
            )
        else:
            self.status_label.setText(f"❌ {result_message}")
            self.status_label.setStyleSheet("color: #ff4444; font-weight: bold;")
            QMessageBox.critical(self, "Error", result_message)
    
    def clear_after_success(self):
        """Clear inputs after successful encoding."""
        self.message_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
    
    def reset(self):
        """Reset page when returning to it."""
        self.image_path = None
        self.image_preview.setPixmap(QPixmap())
        self.image_preview.setText("No image selected")
        self.image_preview.setStyleSheet("""
            background-color: #2d2d44;
            border: 2px dashed #00b4d8;
            border-radius: 4px;
            min-height: 300px;
            color: #888888;
        """)
        self.message_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
        self.status_label.setText("")


class DecodePage(QFrame):
    """Decode page for extracting messages from images."""
    
    from PyQt5.QtCore import pyqtSignal
    back_clicked = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)
        self.image_path = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize decode page UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        
        # Header with back button
        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Back to Home")
        back_btn.setObjectName("backBtn")
        back_btn.setMaximumWidth(150)
        back_btn.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Title
        title = QLabel("Decode Message from Image")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        main_layout.addWidget(title)
        
        # Content layout
        content_layout = QHBoxLayout()
        
        # Left column: Image selection
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        
        left_layout.addWidget(QLabel("Select Encoded Image:"))
        self.image_preview = QLabel("No image selected")
        self.image_preview.setStyleSheet("""
            background-color: #2d2d44;
            border: 2px dashed #00b4d8;
            border-radius: 4px;
            min-height: 250px;
            color: #888888;
        """)
        self.image_preview.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.image_preview)
        
        select_btn = QPushButton("📂 Select Image")
        select_btn.clicked.connect(self.select_image)
        left_layout.addWidget(select_btn)
        
        left_layout.addStretch()
        content_layout.addLayout(left_layout, 1)
        
        # Right column: Password and output
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        
        # Password input
        right_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        right_layout.addWidget(self.password_input)
        
        # Password criteria info
        criteria_label = QLabel(PasswordValidator.get_criteria_text())
        criteria_label.setStyleSheet("color: #aaa; font-size: 10px; background-color: #1a1a2e; padding: 8px; border-radius: 4px;")
        criteria_label.setWordWrap(True)
        right_layout.addWidget(criteria_label)
        
        # Decode button
        decode_btn = QPushButton("🔓 Decode Message")
        decode_btn.setMinimumHeight(50)
        decode_btn.setFont(QFont("Arial", 12, QFont.Bold))
        decode_btn.clicked.connect(self.decode_message)
        right_layout.addWidget(decode_btn)
        
        # Output
        right_layout.addWidget(QLabel("Decoded Message:"))
        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Decoded message will appear here...")
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(150)
        right_layout.addWidget(self.output_text)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Copy Message")
        copy_btn.setMaximumWidth(150)
        copy_btn.clicked.connect(self.copy_message)
        buttons_layout.addWidget(copy_btn)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setMaximumWidth(150)
        clear_btn.clicked.connect(self.clear_output)
        buttons_layout.addWidget(clear_btn)
        
        buttons_layout.addStretch()
        right_layout.addLayout(buttons_layout)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #00b4d8;")
        right_layout.addWidget(self.status_label)
        
        content_layout.addLayout(right_layout, 1)
        main_layout.addLayout(content_layout)
    
    def select_image(self):
        """Select encoded image file."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Encoded Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if file_path:
            self.image_path = file_path
            self.display_preview()
    
    def display_preview(self):
        """Display image preview."""
        try:
            pixmap = QPixmap(self.image_path)
            scaled_pixmap = pixmap.scaledToHeight(250, Qt.SmoothTransformation)
            self.image_preview.setPixmap(scaled_pixmap)
            self.image_preview.setText("")
            self.status_label.setText(f"✅ Image loaded: {os.path.basename(self.image_path)}")
        except Exception as e:
            self.status_label.setText(f"❌ Error loading image: {str(e)}")
    
    def decode_message(self):
        """Decode message from image."""
        if not self.image_path:
            QMessageBox.warning(self, "Error", "Please select an image first.")
            return
        
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a password.")
            return
        
        # Validate password meets security criteria
        is_valid, error_msg = PasswordValidator.validate(password)
        if not is_valid:
            criteria = PasswordValidator.get_criteria_text()
            QMessageBox.warning(
                self, 
                "Invalid Password", 
                f"{error_msg}\n\n{criteria}"
            )
            return
        
        # Show loading state
        self.status_label.setText("⏳ Decoding... Please wait")
        self.status_label.setStyleSheet("color: #ffa500;")
        QApplication.processEvents()
        
        # Create and start worker thread
        self.decoding_worker = DecodingWorker(self.image_path, password)
        self.decoding_worker.finished.connect(self.on_decoding_complete)
        self.decoding_worker.start()
    
    def on_decoding_complete(self, success, result):
        """Handle decoding completion (from worker thread signal)."""
        if success:
            self.status_label.setText("✅ Message decoded successfully")
            self.status_label.setStyleSheet("color: #00aa00; font-weight: bold;")
            
            # Display decoded message
            self.output_text.setPlainText(result)
            
            QMessageBox.information(self, "Success", "Message decoded successfully!")
        else:
            self.status_label.setText(f"❌ {result}")
            self.status_label.setStyleSheet("color: #ff4444; font-weight: bold;")
            self.output_text.clear()
            QMessageBox.critical(self, "Error", result)
    
    def copy_message(self):
        """Copy decoded message to clipboard."""
        text = self.output_text.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(self, "Success", "Message copied to clipboard!")
        else:
            QMessageBox.warning(self, "Empty", "No message to copy.")
    
    def clear_output(self):
        """Clear output text."""
        self.output_text.clear()
        self.status_label.setText("")
    
    def reset(self):
        """Reset page when returning to it."""
        self.image_path = None
        self.image_preview.setPixmap(QPixmap())
        self.image_preview.setText("No image selected")
        self.password_input.clear()
        self.output_text.clear()
        self.status_label.setText("")


def main():
    """Run the application."""
    app = QApplication(sys.argv)
    window = SteganographyApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
