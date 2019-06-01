import sys
import os
import logging

sys.path.append(os.path.join(os.getcwd(), "src"))

logging.basicConfig(filename=None, level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

from app import app
