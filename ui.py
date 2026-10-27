"""
Modern GUI for Image Steganography using CustomTkinter.
Provides intuitive interface for encoding and decoding hidden messages.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import re
from threading import Thread
from steganography import SteganographyCore
import logging

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


class SteganographyGUI:
    """Main GUI Application for Image Steganography."""
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Image Steganography - Hide Messages Securely")
        self.root.geometry("1000x750")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.image_path = None
        self.photo_image = None
        self.operation_in_progress = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="🔐 Image Steganography Tool",
            font=("Arial", 28, "bold"),
            text_color="#00A8E8"
        )
        title.pack(pady=(0, 20))
        
        # Create notebook-like layout with tabs
        tab_frame = ctk.CTkFrame(main_frame)
        tab_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.tab_var = tk.StringVar(value="encode")
        
        # Tab buttons
        button_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=0, pady=(0, 10))
        
        encode_btn = ctk.CTkButton(
            button_frame,
            text="📝 ENCODE",
            font=("Arial", 14, "bold"),
            command=lambda: self.switch_tab("encode"),
            fg_color="#00A8E8",
            hover_color="#0088C0"
        )
        encode_btn.pack(side="left", padx=5)
        
        decode_btn = ctk.CTkButton(
            button_frame,
            text="🔍 DECODE",
            font=("Arial", 14, "bold"),
            command=lambda: self.switch_tab("decode"),
            fg_color="#00A8E8",
            hover_color="#0088C0"
        )
        decode_btn.pack(side="left", padx=5)
        
        # Content frame
        self.content_frame = ctk.CTkFrame(tab_frame)
        self.content_frame.pack(fill="both", expand=True)
        
        # Initialize tabs
        self.setup_encode_tab()
        self.setup_decode_tab()
        
        self.switch_tab("encode")
    
    def setup_encode_tab(self):
        """Setup the encoding tab."""
        self.encode_frame = ctk.CTkFrame(self.content_frame)
        
        # Left side: Image preview and controls
        left_frame = ctk.CTkFrame(self.encode_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Image label
        ctk.CTkLabel(left_frame, text="Image Preview", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Image display frame
        self.encode_image_frame = ctk.CTkFrame(left_frame, fg_color="#1a1a1a")
        self.encode_image_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.encode_image_label = ctk.CTkLabel(
            self.encode_image_frame,
            text="No image selected\nClick 'Select Image' to begin",
            font=("Arial", 12),
            text_color="#666666"
        )
        self.encode_image_label.pack(fill="both", expand=True)
        
        # Image info label
        self.encode_info_label = ctk.CTkLabel(
            left_frame,
            text="",
            font=("Arial", 10),
            text_color="#888888",
            justify="left"
        )
        self.encode_info_label.pack(anchor="w", pady=5)
        
        # Select image button
        ctk.CTkButton(
            left_frame,
            text="📂 Select Image",
            command=self.select_image_encode,
            font=("Arial", 12, "bold"),
            height=40
        ).pack(fill="x", pady=(0, 10))
        
        # Right side: Input fields
        right_frame = ctk.CTkFrame(self.encode_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Message input
        ctk.CTkLabel(right_frame, text="Secret Message", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.message_text = ctk.CTkTextbox(
            right_frame,
            font=("Arial", 11),
            height=120,
            corner_radius=8
        )
        self.message_text.pack(fill="both", expand=True, pady=(0, 15))
        
        # Password input
        ctk.CTkLabel(right_frame, text="Password", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.password_encode = ctk.CTkEntry(
            right_frame,
            placeholder_text="Enter a strong password",
            show="•",
            font=("Arial", 11),
            height=40
        )
        self.password_encode.pack(fill="x", pady=(0, 8))
        
        # Password criteria info
        criteria_text = PasswordValidator.get_criteria_text()
        ctk.CTkLabel(
            right_frame, 
            text=criteria_text,
            font=("Arial", 9),
            text_color="#999999",
            justify="left"
        ).pack(anchor="w", pady=(0, 15))
        
        # Confirm password
        ctk.CTkLabel(right_frame, text="Confirm Password", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.password_confirm = ctk.CTkEntry(
            right_frame,
            placeholder_text="Re-enter password",
            show="•",
            font=("Arial", 11),
            height=40
        )
        self.password_confirm.pack(fill="x", pady=(0, 15))
        
        # Encode button
        ctk.CTkButton(
            right_frame,
            text="🔒 Encode Message",
            command=self.encode_message,
            font=("Arial", 13, "bold"),
            height=45,
            fg_color="#00A8E8",
            hover_color="#0088C0"
        ).pack(fill="x", pady=(0, 10))
        
        # Status label
        self.encode_status = ctk.CTkLabel(
            right_frame,
            text="",
            font=("Arial", 10),
            text_color="#00A8E8",
            wraplength=300,
            justify="left"
        )
        self.encode_status.pack(anchor="w", pady=5)
    
    def setup_decode_tab(self):
        """Setup the decoding tab."""
        self.decode_frame = ctk.CTkFrame(self.content_frame)
        
        # Left side: Image preview
        left_frame = ctk.CTkFrame(self.decode_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(left_frame, text="Encoded Image", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.decode_image_frame = ctk.CTkFrame(left_frame, fg_color="#1a1a1a")
        self.decode_image_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.decode_image_label = ctk.CTkLabel(
            self.decode_image_frame,
            text="No image selected\nClick 'Select Image' to begin",
            font=("Arial", 12),
            text_color="#666666"
        )
        self.decode_image_label.pack(fill="both", expand=True)
        
        self.decode_info_label = ctk.CTkLabel(
            left_frame,
            text="",
            font=("Arial", 10),
            text_color="#888888",
            justify="left"
        )
        self.decode_info_label.pack(anchor="w", pady=5)
        
        ctk.CTkButton(
            left_frame,
            text="📂 Select Image",
            command=self.select_image_decode,
            font=("Arial", 12, "bold"),
            height=40
        ).pack(fill="x", pady=(0, 10))
        
        # Right side: Input and output
        right_frame = ctk.CTkFrame(self.decode_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Password input
        ctk.CTkLabel(right_frame, text="Password", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.password_decode = ctk.CTkEntry(
            right_frame,
            placeholder_text="Enter password",
            show="•",
            font=("Arial", 11),
            height=40
        )
        self.password_decode.pack(fill="x", pady=(0, 8))
        
        # Password criteria info
        criteria_text = PasswordValidator.get_criteria_text()
        ctk.CTkLabel(
            right_frame, 
            text=criteria_text,
            font=("Arial", 9),
            text_color="#999999",
            justify="left"
        ).pack(anchor="w", pady=(0, 15))
        
        # Decode button
        ctk.CTkButton(
            right_frame,
            text="🔓 Decode Message",
            command=self.decode_message,
            font=("Arial", 13, "bold"),
            height=45,
            fg_color="#00A8E8",
            hover_color="#0088C0"
        ).pack(fill="x", pady=(0, 15))
        
        # Decoded message output
        ctk.CTkLabel(right_frame, text="Decoded Message", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.decoded_text = ctk.CTkTextbox(
            right_frame,
            font=("Arial", 11),
            height=120,
            corner_radius=8,
            state="disabled"
        )
        self.decoded_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Copy button
        ctk.CTkButton(
            right_frame,
            text="📋 Copy Message",
            command=self.copy_decoded_message,
            font=("Arial", 11, "bold"),
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(fill="x", pady=(0, 10))
        
        # Status label
        self.decode_status = ctk.CTkLabel(
            right_frame,
            text="",
            font=("Arial", 10),
            text_color="#00A8E8",
            wraplength=300,
            justify="left"
        )
        self.decode_status.pack(anchor="w", pady=5)
    
    def switch_tab(self, tab_name):
        """Switch between encode and decode tabs."""
        self.tab_var.set(tab_name)
        
        # Clear previous widgets
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()
        
        if tab_name == "encode":
            if not hasattr(self, 'encode_frame'):
                self.setup_encode_tab()
            self.encode_frame.pack(fill="both", expand=True)
        else:
            if not hasattr(self, 'decode_frame'):
                self.setup_decode_tab()
            self.decode_frame.pack(fill="both", expand=True)
    
    def select_image_encode(self):
        """Select image for encoding."""
        file_path = filedialog.askopenfilename(
            title="Select Image for Encoding",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.image_path = file_path
            self.display_image_preview(file_path, "encode")
    
    def select_image_decode(self):
        """Select image for decoding."""
        file_path = filedialog.askopenfilename(
            title="Select Image for Decoding",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.image_path = file_path
            self.display_image_preview(file_path, "decode")
    
    def display_image_preview(self, image_path, tab):
        """Display image preview in the specified tab."""
        try:
            img, error = SteganographyCore.validate_image(image_path)
            if error:
                messagebox.showerror("Error", error)
                return
            
            # Resize image for display
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            if tab == "encode":
                self.encode_image_label.configure(image=photo, text="")
                self.encode_image_label.image = photo
                
                # Show image info
                original_img = Image.open(image_path)
                max_capacity = SteganographyCore.get_max_capacity(original_img)
                info_text = f"File: {os.path.basename(image_path)}\nSize: {original_img.width}x{original_img.height}\nMax Capacity: {max_capacity} bytes"
                self.encode_info_label.configure(text=info_text)
            else:
                self.decode_image_label.configure(image=photo, text="")
                self.decode_image_label.image = photo
                
                original_img = Image.open(image_path)
                info_text = f"File: {os.path.basename(image_path)}\nSize: {original_img.width}x{original_img.height}"
                self.decode_info_label.configure(text=info_text)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")
    
    def encode_message(self):
        """Encode message into image."""
        if self.operation_in_progress:
            messagebox.showwarning("Busy", "Operation in progress. Please wait.")
            return
        
        # Validate inputs
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first.")
            return
        
        message = self.message_text.get("1.0", "end-1c").strip()
        password = self.password_encode.get().strip()
        confirm_password = self.password_confirm.get().strip()
        
        if not message:
            messagebox.showerror("Error", "Please enter a message.")
            return
        
        if not password:
            messagebox.showerror("Error", "Please enter a password.")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        
        # Validate password meets security criteria
        is_valid, error_msg = PasswordValidator.validate(password)
        if not is_valid:
            criteria = PasswordValidator.get_criteria_text()
            messagebox.showerror("Weak Password", f"{error_msg}\n\n{criteria}")
            return
        
        # Perform encoding in a separate thread
        self.operation_in_progress = True
        self.encode_status.configure(text="⏳ Encoding... Please wait", text_color="#FFA500")
        
        thread = Thread(target=self._encode_worker, args=(message, password))
        thread.daemon = True
        thread.start()
    
    def _encode_worker(self, message, password):
        """Worker thread for encoding."""
        try:
            output_path = filedialog.asksaveasfilename(
                title="Save Encoded Image",
                defaultextension=".png",
                filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
            )
            
            if not output_path:
                self.encode_status.configure(text="Encoding cancelled", text_color="#FF6B6B")
                self.operation_in_progress = False
                return
            
            success, result = SteganographyCore.encode(self.image_path, message, password, output_path)
            
            if success:
                self.encode_status.configure(text=f"✅ {result}", text_color="#4CAF50")
                self.message_text.delete("1.0", "end")
                self.password_encode.delete(0, "end")
                self.password_confirm.delete(0, "end")
            else:
                self.encode_status.configure(text=f"❌ {result}", text_color="#FF6B6B")
        
        except Exception as e:
            self.encode_status.configure(text=f"❌ Error: {str(e)}", text_color="#FF6B6B")
        
        finally:
            self.operation_in_progress = False
    
    def decode_message(self):
        """Decode message from image."""
        if self.operation_in_progress:
            messagebox.showwarning("Busy", "Operation in progress. Please wait.")
            return
        
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first.")
            return
        
        password = self.password_decode.get().strip()
        
        if not password:
            messagebox.showerror("Error", "Please enter a password.")
            return
        
        # Validate password meets security criteria
        is_valid, error_msg = PasswordValidator.validate(password)
        if not is_valid:
            criteria = PasswordValidator.get_criteria_text()
            messagebox.showerror("Invalid Password", f"{error_msg}\n\n{criteria}")
            return
        
        # Perform decoding in a separate thread
        self.operation_in_progress = True
        self.decode_status.configure(text="⏳ Decoding... Please wait", text_color="#FFA500")
        
        thread = Thread(target=self._decode_worker, args=(password,))
        thread.daemon = True
        thread.start()
    
    def _decode_worker(self, password):
        """Worker thread for decoding."""
        try:
            success, result = SteganographyCore.decode(self.image_path, password)
            
            if success:
                self.decode_status.configure(text="✅ Message decoded successfully", text_color="#4CAF50")
                
                # Display decoded message
                self.decoded_text.configure(state="normal")
                self.decoded_text.delete("1.0", "end")
                self.decoded_text.insert("1.0", result)
                self.decoded_text.configure(state="disabled")
            else:
                self.decode_status.configure(text=f"❌ {result}", text_color="#FF6B6B")
                self.decoded_text.configure(state="normal")
                self.decoded_text.delete("1.0", "end")
                self.decoded_text.configure(state="disabled")
        
        except Exception as e:
            self.decode_status.configure(text=f"❌ Error: {str(e)}", text_color="#FF6B6B")
        
        finally:
            self.operation_in_progress = False
    
    def copy_decoded_message(self):
        """Copy decoded message to clipboard."""
        try:
            message = self.decoded_text.get("1.0", "end-1c")
            if message.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(message)
                messagebox.showinfo("Success", "Message copied to clipboard!")
            else:
                messagebox.showwarning("Empty", "No message to copy.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {str(e)}")


def run_gui():
    """Run the GUI application."""
    root = ctk.CTk()
    app = SteganographyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
