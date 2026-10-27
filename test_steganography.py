"""
Test suite for Image Steganography application.
Validates core functionality without requiring GUI.
"""

import os
import sys
from pathlib import Path
from PIL import Image

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from steganography import SteganographyCore


def test_create_test_image():
    """Create a test image for testing."""
    print("\n📝 Creating test image...")
    img = Image.new('RGB', (512, 512), color='blue')
    test_image_path = os.path.join(os.path.dirname(__file__), 'test_image.png')
    img.save(test_image_path)
    print(f"✅ Test image created: {test_image_path}")
    return test_image_path


def test_image_validation():
    """Test image validation."""
    print("\n🔍 Testing image validation...")
    
    # Test with non-existent file
    result, error = SteganographyCore.validate_image("nonexistent.png")
    assert result is None, "Should fail for non-existent file"
    assert "not found" in error, "Should show appropriate error"
    print("✅ Non-existent file validation works")
    
    # Test with valid image
    test_img = test_create_test_image()
    result, error = SteganographyCore.validate_image(test_img)
    assert result is not None, "Should load valid image"
    assert error is None, "Should not show error for valid image"
    print("✅ Valid image validation works")
    
    return test_img


def test_capacity_calculation():
    """Test capacity calculation."""
    print("\n📊 Testing capacity calculation...")
    
    test_img = test_image_validation()
    img = Image.open(test_img)
    capacity = SteganographyCore.get_max_capacity(img)
    
    print(f"✅ Image: {img.width}x{img.height}")
    print(f"✅ Max capacity: {capacity} bytes")
    
    # For 512x512: (512*512*3 - 32)/8 = 98,295 bytes
    expected = (512 * 512 * 3 - 32) // 8
    assert capacity == expected, f"Capacity mismatch: {capacity} vs {expected}"
    print(f"✅ Capacity calculation correct")
    
    return test_img


def test_encoding_decoding():
    """Test encoding and decoding."""
    print("\n🔐 Testing encode/decode cycle...")
    
    test_img = test_capacity_calculation()
    
    # Test parameters
    message = "Hello, this is a secret message! 🔒"
    password = "TestPassword123!@#"
    output_path = os.path.join(os.path.dirname(__file__), 'test_encoded.png')
    
    # Test encoding
    print(f"\n📝 Encoding message: '{message}'")
    print(f"🔑 Password: {password}")
    
    success, result = SteganographyCore.encode(test_img, message, password, output_path)
    
    if not success:
        print(f"❌ Encoding failed: {result}")
        return False
    
    print(f"✅ Encoding successful: {result}")
    assert os.path.exists(output_path), "Encoded image not created"
    print(f"✅ Encoded image exists: {output_path}")
    
    # Test decoding with correct password
    print(f"\n🔓 Decoding with correct password...")
    success, decoded_msg = SteganographyCore.decode(output_path, password)
    
    if not success:
        print(f"❌ Decoding failed: {decoded_msg}")
        return False
    
    print(f"✅ Decoded message: '{decoded_msg}'")
    assert decoded_msg == message, f"Message mismatch: '{decoded_msg}' vs '{message}'"
    print(f"✅ Message verification passed!")
    
    # Test decoding with wrong password
    print(f"\n🚨 Testing wrong password protection...")
    success, error_msg = SteganographyCore.decode(output_path, "WrongPassword123")
    
    if success:
        print(f"❌ Security flaw: Wrong password was accepted!")
        return False
    
    assert not success, "Wrong password should fail"
    print(f"✅ Wrong password correctly rejected: {error_msg}")
    
    return True


def test_message_limits():
    """Test message size validation."""
    print("\n📏 Testing message limits...")
    
    test_img = test_capacity_calculation()
    
    # Get capacity
    img = Image.open(test_img)
    capacity = SteganographyCore.get_max_capacity(img)
    
    # Create message that's too large
    large_message = "A" * (capacity + 1000)
    
    print(f"✅ Capacity: {capacity} bytes")
    print(f"📝 Attempting to encode {len(large_message)} byte message...")
    
    success, error = SteganographyCore.encode(
        test_img,
        large_message,
        "password",
        "test_large.png"
    )
    
    if success:
        print(f"❌ Should have rejected message that's too large!")
        return False
    
    assert not success, "Should reject message too large"
    assert "too large" in error.lower(), "Should mention size issue"
    print(f"✅ Large message correctly rejected: {error}")
    
    return True


def test_empty_message():
    """Test empty message validation."""
    print("\n⚠️ Testing empty message validation...")
    
    test_img = test_capacity_calculation()
    
    success, error = SteganographyCore.encode(
        test_img,
        "",  # Empty message
        "password",
        "test_empty.png"
    )
    
    if success:
        print(f"❌ Should have rejected empty message!")
        return False
    
    assert not success, "Should reject empty message"
    print(f"✅ Empty message correctly rejected: {error}")
    
    return True


def cleanup_test_files():
    """Clean up test files."""
    print("\n🧹 Cleaning up test files...")
    
    test_files = [
        'test_image.png',
        'test_encoded.png',
        'test_large.png',
        'test_empty.png'
    ]
    
    for filename in test_files:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"✅ Removed: {filename}")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Image Steganography - Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        test_image_validation()
        test_capacity_calculation()
        test_message_limits()
        test_empty_message()
        result = test_encoding_decoding()
        
        if result:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED!")
            print("=" * 60)
            print("\n🎉 The application is ready to use!")
            print("💡 Tip: Run 'python main.py' to start the GUI")
            print("=" * 60)
            
            # Cleanup
            cleanup_test_files()
            return 0
        else:
            print("\n" + "=" * 60)
            print("❌ TESTS FAILED")
            print("=" * 60)
            cleanup_test_files()
            return 1
    
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        cleanup_test_files()
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
