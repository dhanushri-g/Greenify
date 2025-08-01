# Smart Waste Sorter Backend

A comprehensive Python backend API for the Smart Waste Sorter application, built with FastAPI and featuring AI-powered waste detection, user management, and eco-analytics.

## 🚀 Features

### 🤖 AI-Powered Waste Detection
- **TensorFlow Integration**: Advanced image classification for waste categorization
- **Real-time Analysis**: Instant waste type identification with confidence scores
- **Quality Assessment**: Image quality analysis with improvement recommendations
- **9 Waste Categories**: Plastic, Paper, Glass, Metal, Organic, Electronic, Hazardous, Textile, Other

### 👤 User Management
- **JWT Authentication**: Secure token-based authentication
- **User Profiles**: Comprehensive profile management with avatars
- **Eco Points System**: Gamified point system for environmental actions
- **Level Progression**: User advancement from Eco Beginner to Eco Master

### 💳 Smart Card System
- **Digital Cards**: Virtual eco-cards with QR codes and barcodes
- **Card Customization**: Personalized colors and information
- **Status Tracking**: Dynamic status based on eco activity
- **Validation API**: Public endpoint for card verification

### 🛒 Eco Shop
- **Sustainable Products**: Curated eco-friendly product catalog
- **Eco Points Payment**: Alternative payment using earned points
- **Product Categories**: Personal care, drinkware, bags, electronics, kitchen
- **Order Management**: Complete order tracking and history

### 📊 Analytics & Insights
- **Environmental Impact**: Track CO2 reduction, water saved, trees saved
- **Waste Trends**: Time-series analysis of waste detection patterns
- **Leaderboards**: Community rankings and achievements
- **Personal Stats**: Detailed user analytics and progress tracking

### 🔨 DIY Projects
- **Upcycling Ideas**: Creative waste reuse projects
- **Step-by-step Guides**: Detailed instructions with images
- **Community Sharing**: User-generated content platform
- **Difficulty Levels**: Projects for all skill levels

## 🛠️ Technology Stack

- **Framework**: FastAPI (Python 3.8+)
- **Database**: SQLAlchemy with SQLite/PostgreSQL support
- **AI/ML**: TensorFlow, OpenCV, Pillow
- **Authentication**: JWT with bcrypt password hashing
- **File Storage**: Local file system with async file handling
- **API Documentation**: Automatic OpenAPI/Swagger documentation

## 📦 Installation

### Quick Start

1. **Clone and Navigate**
   ```bash
   cd backend
   ```

2. **Run Setup Script**
   ```bash
   python start.py
   ```
   This will automatically:
   - Check Python version compatibility
   - Install all dependencies
   - Create necessary directories
   - Set up environment variables
   - Create a sample AI model
   - Start the development server

### Manual Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Create Directories**
   ```bash
   mkdir -p uploads/{waste_images,user_avatars,diy_images}
   mkdir -p static models logs
   ```

4. **Start Server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Security
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./smart_waste_sorter.db

# CORS
ALLOWED_HOSTS=http://localhost:3000,http://localhost:3001

# AI Model
MODEL_PATH=./models/waste_classifier.h5
CONFIDENCE_THRESHOLD=0.7

# File Upload
MAX_IMAGE_SIZE=5242880  # 5MB
MAX_FILE_SIZE=10485760  # 10MB

# External APIs (optional)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Database Configuration

**SQLite (Default)**
```env
DATABASE_URL=sqlite:///./smart_waste_sorter.db
```

**PostgreSQL**
```env
DATABASE_URL=postgresql://username:password@localhost/smart_waste_sorter
```

**MySQL**
```env
DATABASE_URL=mysql://username:password@localhost/smart_waste_sorter
```

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/me` - Current user info

### Waste Detection
- `POST /api/detection/scan` - Scan waste image
- `GET /api/detection/history` - Scan history
- `POST /api/detection/feedback` - Submit feedback
- `GET /api/detection/categories` - Waste categories
- `GET /api/detection/stats` - Detection statistics

### User Profile
- `GET /api/profile/` - Get profile
- `PUT /api/profile/` - Update profile
- `POST /api/profile/avatar` - Upload avatar
- `POST /api/profile/change-password` - Change password

### Smart Card
- `POST /api/smart-card/create` - Create card
- `GET /api/smart-card/` - Get user's card
- `PUT /api/smart-card/` - Update card
- `POST /api/smart-card/renew` - Renew card

### Shop
- `GET /api/shop/products` - List products
- `GET /api/shop/categories` - Product categories
- `POST /api/shop/orders` - Create order
- `GET /api/shop/orders` - Order history

### Analytics
- `GET /api/analytics/overview` - Analytics overview
- `GET /api/analytics/environmental-impact` - Environmental metrics
- `GET /api/analytics/leaderboard` - User rankings
- `GET /api/analytics/trends` - Waste trends

### DIY Projects
- `GET /api/diy/` - List projects
- `POST /api/diy/` - Create project
- `POST /api/diy/{id}/images` - Upload images
- `POST /api/diy/{id}/like` - Like project

## 🤖 AI Model

The backend includes a TensorFlow-based waste classification model:

### Model Architecture
- **Input**: 224x224x3 RGB images
- **Architecture**: CNN with Global Average Pooling
- **Output**: 9 waste categories with confidence scores
- **Format**: Keras H5 model file

### Training Your Own Model
1. Prepare dataset with labeled waste images
2. Use the provided model architecture
3. Train with your data
4. Save as `models/waste_classifier.h5`

### Model Performance
- **Confidence Threshold**: 70% (configurable)
- **Supported Formats**: JPEG, PNG
- **Max Image Size**: 5MB
- **Processing Time**: <2 seconds per image

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt with salt
- **CORS Protection**: Configurable allowed origins
- **File Validation**: Type and size restrictions
- **Input Sanitization**: SQL injection prevention
- **Rate Limiting**: API endpoint protection

## 📈 Performance

- **Response Time**: <100ms for most endpoints
- **Concurrent Users**: 100+ (with proper deployment)
- **Database**: Optimized queries with indexing
- **File Storage**: Async file operations
- **Caching**: Redis support for session management

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Use PostgreSQL for production database
- Set up Redis for caching and sessions
- Configure proper CORS origins
- Use environment-specific secrets
- Set up SSL/TLS certificates
- Configure reverse proxy (nginx)
- Set up monitoring and logging

## 🧪 Testing

Run the test suite:
```bash
pytest
```

Test coverage:
```bash
pytest --cov=app
```

## 📝 Development

### Code Style
- **Formatter**: Black
- **Linting**: Flake8
- **Import Sorting**: isort

Format code:
```bash
black .
isort .
flake8 .
```

### Database Migrations
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation
- Review the error logs
- Open an issue on GitHub
- Contact the development team

## 🔄 Updates

The backend is actively maintained with regular updates for:
- Security patches
- Performance improvements
- New features
- Bug fixes
- AI model improvements
