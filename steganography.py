"""
Core steganography module for encoding and decoding hidden messages in images.
Uses LSB (Least Significant Bit) technique for secure message hiding with AES encryption.
"""

import os
from PIL import Image
from cryptography.fernet import Fernet, InvalidToken
import base64
import hashlib
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('steganography.log'),
        logging.StreamHandler()
    ]
)


class SteganographyCore:
    """Core steganography operations using LSB technique."""
    
    @staticmethod
    def _derive_key(password: str) -> bytes:
        """Derive a Fernet-compatible key from password."""
        hash_obj = hashlib.sha256(password.encode())
        key = base64.urlsafe_b64encode(hash_obj.digest())
        return key
    
    @staticmethod
    def _encrypt_message(message: str, password: str) -> bytes:
        """Encrypt message using Fernet with password-derived key."""
        try:
            key = SteganographyCore._derive_key(password)
            cipher = Fernet(key)
            encrypted = cipher.encrypt(message.encode())
            return encrypted
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise Exception(f"Encryption error: {str(e)}")
    
    @staticmethod
    def _decrypt_message(encrypted_data: bytes, password: str) -> str:
        """Decrypt message using Fernet with password-derived key."""
        try:
            key = SteganographyCore._derive_key(password)
            cipher = Fernet(key)
            decrypted = cipher.decrypt(encrypted_data)
            return decrypted.decode()
        except InvalidToken:
            logger.error("Invalid password or corrupted data")
            raise Exception("Decryption failed: Invalid password or corrupted message")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise Exception(f"Decryption error: {str(e)}")
    
    @staticmethod
    def _set_lsb(pixel_value: int, bit: int) -> int:
        """Set the least significant bit of a pixel channel."""
        return (pixel_value & 0xFE) | (bit & 1)
    
    @staticmethod
    def _get_lsb(pixel_value: int) -> int:
        """Get the least significant bit of a pixel channel."""
        return pixel_value & 1
    
    @staticmethod
    def validate_image(image_path: str) -> tuple:
        """
        Validate image format and return image object.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (PIL Image object, error message or None)
        """
        if not os.path.exists(image_path):
            return None, "Image file not found."
        
        # Check file extension
        valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
        if not image_path.lower().endswith(valid_extensions):
            return None, f"Unsupported format. Supported: {', '.join(valid_extensions)}"
        
        try:
            img = Image.open(image_path)
            img.load()  # Verify image can be loaded
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            return img, None
        except Exception as e:
            return None, f"Failed to load image: {str(e)}"
    
    @staticmethod
    def get_max_capacity(image: Image.Image) -> int:
        """
        Calculate maximum bytes that can be stored in image.
        Uses LSB technique: 3 bits per pixel (RGB channels)
        Stores message length in first 32 bits.
        
        Args:
            image: PIL Image object
            
        Returns:
            Maximum bytes that can be stored
        """
        total_pixels = image.width * image.height
        # 3 bits per pixel (LSB in each channel)
        total_bits = total_pixels * 3
        # Reserve 32 bits for message length
        total_bytes = (total_bits - 32) // 8
        return max(0, total_bytes)
    
    @staticmethod
    def encode(image_path: str, message: str, password: str, output_path: str) -> tuple:
        """
        Encode secret message into image using LSB steganography.
        
        Args:
            image_path: Path to input image
            message: Secret message to hide
            password: Password for encryption
            output_path: Path to save encoded image
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate inputs
            if not message.strip():
                return False, "Error: Message cannot be empty."
            
            if not password.strip():
                return False, "Error: Password cannot be empty."
            
            # Load and validate image
            img, error = SteganographyCore.validate_image(image_path)
            if error:
                return False, error
            
            # Encrypt message
            try:
                encrypted_msg = SteganographyCore._encrypt_message(message, password)
            except Exception as e:
                return False, str(e)
            
            # Check capacity
            max_capacity = SteganographyCore.get_max_capacity(img)
            if len(encrypted_msg) > max_capacity:
                return False, f"Error: Message too large. Max: {max_capacity} bytes, Got: {len(encrypted_msg)} bytes"
            
            # Create working copy
            img = img.convert('RGB')
            pixels = img.load()
            
            # Convert message length to 4 bytes (32-bit integer)
            msg_length = len(encrypted_msg)
            length_bytes = msg_length.to_bytes(4, byteorder='big')
            
            # Combine length bytes + encrypted message
            full_data = length_bytes + encrypted_msg
            
            # Convert to bits
            data_bits = ''.join(format(byte, '08b') for byte in full_data)
            
            # Encode bits into LSB of pixels
            bit_index = 0
            for y in range(img.height):
                for x in range(img.width):
                    if bit_index >= len(data_bits):
                        break
                    
                    r, g, b = pixels[x, y][:3]  # Get RGB
                    
                    # Set LSB of each channel
                    r = SteganographyCore._set_lsb(r, int(data_bits[bit_index]))
                    bit_index += 1
                    
                    if bit_index < len(data_bits):
                        g = SteganographyCore._set_lsb(g, int(data_bits[bit_index]))
                        bit_index += 1
                    
                    if bit_index < len(data_bits):
                        b = SteganographyCore._set_lsb(b, int(data_bits[bit_index]))
                        bit_index += 1
                    
                    pixels[x, y] = (r, g, b)
                
                if bit_index >= len(data_bits):
                    break
            
            # Save as PNG (no compression loss)
            if not output_path.lower().endswith('.png'):
                output_path = output_path.rsplit('.', 1)[0] + '.png'
            
            img.save(output_path, 'PNG')
            logger.info(f"Message encoded and saved to {output_path}")
            
            return True, f"Message successfully encoded and saved as:\n{os.path.basename(output_path)}"
        
        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            return False, f"Encoding error: {str(e)}"
    
    @staticmethod
    def decode(image_path: str, password: str) -> tuple:
        """
        Decode secret message from image using LSB steganography.
        
        Args:
            image_path: Path to encoded image
            password: Password for decryption
            
        Returns:
            Tuple of (success: bool, message or error: str)
        """
        try:
            # Load and validate image
            img, error = SteganographyCore.validate_image(image_path)
            if error:
                return False, error
            
            img = img.convert('RGB')
            pixels = img.load()
            
            # Extract bits from LSB
            bits = ''
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b = pixels[x, y][:3]
                    bits += str(SteganographyCore._get_lsb(r))
                    bits += str(SteganographyCore._get_lsb(g))
                    bits += str(SteganographyCore._get_lsb(b))
            
            # Extract message length (first 32 bits)
            if len(bits) < 32:
                return False, "Error: Not enough data in image."
            
            length_bits = bits[:32]
            msg_length = int(length_bits, 2)
            
            # Extract encrypted message
            data_bits = bits[32:]
            
            if len(data_bits) < msg_length * 8:
                return False, "Error: Not enough data in image."
            
            # Convert bits back to bytes
            encrypted_msg_bits = data_bits[:msg_length * 8]
            encrypted_msg = bytes(
                int(encrypted_msg_bits[i:i+8], 2)
                for i in range(0, len(encrypted_msg_bits), 8)
            )
            
            # Decrypt message
            try:
                message = SteganographyCore._decrypt_message(encrypted_msg, password)
            except Exception as e:
                return False, str(e)
            
            logger.info("Message successfully decoded")
            return True, message
        
        except Exception as e:
            logger.error(f"Decoding failed: {e}")
            return False, f"Decoding error: {str(e)}"
