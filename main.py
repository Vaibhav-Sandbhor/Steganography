"""
Main entry point for Image Steganography application.
Launches the GUI interface.
"""

import logging
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('steganography.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    try:
        logger.info("Starting Image Steganography Application...")
        
        from ui import run_gui
        run_gui()
    
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        print(f"\n❌ Error: Missing required libraries!")
        print("\nPlease install dependencies using:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
