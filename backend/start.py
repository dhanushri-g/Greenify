#!/usr/bin/env python3
"""
Smart Waste Sorter Backend Startup Script
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def setup_environment():
    """Setup environment variables"""
    if not os.path.exists(".env"):
        print("📝 Creating .env file from template...")
        try:
            with open(".env.example", "r") as example:
                content = example.read()
            with open(".env", "w") as env_file:
                env_file.write(content)
            print("✅ .env file created. Please update it with your configuration.")
        except FileNotFoundError:
            print("⚠️  .env.example not found. Creating basic .env file...")
            with open(".env", "w") as env_file:
                env_file.write("SECRET_KEY=change-this-secret-key\n")
                env_file.write("DATABASE_URL=sqlite:///./smart_waste_sorter.db\n")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = [
        "uploads",
        "uploads/waste_images",
        "uploads/user_avatars", 
        "uploads/diy_images",
        "static",
        "models",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directories created")

def download_sample_model():
    """Download or create a sample AI model"""
    model_path = "models/waste_classifier.h5"
    if not os.path.exists(model_path):
        print("🤖 Creating sample AI model...")
        try:
            import tensorflow as tf
            
            # Create a simple model for demonstration
            model = tf.keras.Sequential([
                tf.keras.layers.Input(shape=(224, 224, 3)),
                tf.keras.layers.GlobalAveragePooling2D(),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dropout(0.5),
                tf.keras.layers.Dense(9, activation='softmax')  # 9 waste categories
            ])
            
            model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
            model.save(model_path)
            print("✅ Sample AI model created")
        except ImportError:
            print("⚠️  TensorFlow not available. AI model will be created at runtime.")
        except Exception as e:
            print(f"⚠️  Could not create sample model: {e}")

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Smart Waste Sorter Backend...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/api/docs")
    print("🔄 Interactive API: http://localhost:8000/api/redoc")
    print("\n" + "="*50)
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "uvicorn[standard]"])
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )

def main():
    """Main startup function"""
    print("🌱 Smart Waste Sorter Backend Setup")
    print("="*40)
    
    # Check system requirements
    check_python_version()
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Setup AI model
    download_sample_model()
    
    print("\n✅ Setup complete!")
    print("🎯 Ready to start the backend server")
    
    # Ask user if they want to start the server
    start_now = input("\nStart the server now? (y/n): ").lower().strip()
    if start_now in ['y', 'yes', '']:
        start_server()
    else:
        print("\n📝 To start the server later, run:")
        print("   python start.py --server-only")
        print("   or")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--server-only":
        start_server()
    else:
        main()
