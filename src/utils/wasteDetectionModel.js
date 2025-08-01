import * as tf from '@tensorflow/tfjs';

// Waste classification classes
export const WASTE_CLASSES = {
  0: { name: 'Wet Waste', color: '#ef4444', description: 'Organic waste, food scraps' },
  1: { name: 'Dry Waste', color: '#f59e0b', description: 'Non-recyclable dry waste' },
  2: { name: 'Recyclable', color: '#10b981', description: 'Plastic, paper, metal, glass' }
};

// Pre-trained model URLs (in a real app, these would be your trained models)
const MODEL_URLS = {
  mobilenet: 'https://tfhub.dev/google/tfjs-model/imagenet/mobilenet_v3_small_100_224/feature_vector/5/default/1',
  waste_classifier: '/models/waste-classifier/model.json' // Your custom model
};

// Load and initialize the waste detection model
export class WasteDetectionModel {
  constructor() {
    this.model = null;
    this.isLoaded = false;
    this.inputSize = 224;
  }

  async loadModel() {
    try {
      console.log('Loading TensorFlow.js...');
      await tf.ready();
      
      // For demo purposes, create a simple model
      // In production, you would load a pre-trained model
      this.model = await this.createDemoModel();
      
      this.isLoaded = true;
      console.log('Waste detection model loaded successfully!');
      return true;
    } catch (error) {
      console.error('Error loading model:', error);
      throw error;
    }
  }

  async createDemoModel() {
    // Create a simple CNN for demonstration
    const model = tf.sequential({
      layers: [
        tf.layers.conv2d({
          inputShape: [this.inputSize, this.inputSize, 3],
          filters: 32,
          kernelSize: 3,
          activation: 'relu',
          padding: 'same'
        }),
        tf.layers.maxPooling2d({ poolSize: 2 }),
        tf.layers.conv2d({ 
          filters: 64, 
          kernelSize: 3, 
          activation: 'relu',
          padding: 'same'
        }),
        tf.layers.maxPooling2d({ poolSize: 2 }),
        tf.layers.conv2d({ 
          filters: 128, 
          kernelSize: 3, 
          activation: 'relu',
          padding: 'same'
        }),
        tf.layers.globalAveragePooling2d(),
        tf.layers.dense({ units: 128, activation: 'relu' }),
        tf.layers.dropout({ rate: 0.5 }),
        tf.layers.dense({ units: 3, activation: 'softmax' })
      ]
    });

    // Compile the model
    model.compile({
      optimizer: tf.train.adam(0.001),
      loss: 'categoricalCrossentropy',
      metrics: ['accuracy']
    });

    // Initialize with random weights (in production, load pre-trained weights)
    const dummyInput = tf.randomNormal([1, this.inputSize, this.inputSize, 3]);
    model.predict(dummyInput).dispose();
    dummyInput.dispose();

    return model;
  }

  preprocessImage(imageElement) {
    return tf.tidy(() => {
      // Convert image to tensor
      let tensor = tf.browser.fromPixels(imageElement);
      
      // Resize to model input size
      tensor = tf.image.resizeBilinear(tensor, [this.inputSize, this.inputSize]);
      
      // Normalize pixel values to [0, 1]
      tensor = tensor.div(255.0);
      
      // Add batch dimension
      tensor = tensor.expandDims(0);
      
      return tensor;
    });
  }

  async predict(imageElement, confidenceThreshold = 0.5) {
    if (!this.isLoaded || !this.model) {
      throw new Error('Model not loaded');
    }

    try {
      // Preprocess the image
      const preprocessed = this.preprocessImage(imageElement);
      
      // Make prediction
      const predictions = await this.model.predict(preprocessed).data();
      
      // Clean up tensors
      preprocessed.dispose();
      
      // Process predictions
      const results = [];
      for (let i = 0; i < predictions.length; i++) {
        if (predictions[i] > confidenceThreshold) {
          results.push({
            classId: i,
            className: WASTE_CLASSES[i].name,
            confidence: predictions[i],
            color: WASTE_CLASSES[i].color,
            description: WASTE_CLASSES[i].description
          });
        }
      }
      
      // Sort by confidence
      results.sort((a, b) => b.confidence - a.confidence);
      
      return {
        predictions: results,
        topPrediction: results[0] || null,
        processingTime: Date.now()
      };
      
    } catch (error) {
      console.error('Prediction error:', error);
      throw error;
    }
  }

  // Simulate real-time detection with color/texture analysis
  async detectRealTime(videoElement, confidenceThreshold = 0.5) {
    if (!videoElement || videoElement.videoWidth === 0) {
      return null;
    }

    try {
      // Create canvas for frame capture
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = videoElement.videoWidth;
      canvas.height = videoElement.videoHeight;
      
      // Draw current frame
      ctx.drawImage(videoElement, 0, 0);
      
      // Analyze frame (simplified approach for demo)
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const analysis = this.analyzeImageData(imageData);
      
      // Generate prediction based on analysis
      const prediction = this.generatePredictionFromAnalysis(analysis, confidenceThreshold);
      
      return prediction;
      
    } catch (error) {
      console.error('Real-time detection error:', error);
      return null;
    }
  }

  analyzeImageData(imageData) {
    const data = imageData.data;
    let totalR = 0, totalG = 0, totalB = 0;
    let pixelCount = 0;
    
    // Sample every 10th pixel for performance
    for (let i = 0; i < data.length; i += 40) {
      totalR += data[i];
      totalG += data[i + 1];
      totalB += data[i + 2];
      pixelCount++;
    }
    
    const avgR = totalR / pixelCount;
    const avgG = totalG / pixelCount;
    const avgB = totalB / pixelCount;
    
    return {
      averageColor: { r: avgR, g: avgG, b: avgB },
      brightness: (avgR + avgG + avgB) / 3,
      dominantChannel: avgR > avgG && avgR > avgB ? 'red' : 
                      avgG > avgB ? 'green' : 'blue'
    };
  }

  generatePredictionFromAnalysis(analysis, confidenceThreshold) {
    const { averageColor, brightness, dominantChannel } = analysis;
    
    // Simple heuristic-based classification (for demo)
    let predictions = [0, 0, 0];
    
    // Green/brown tones suggest organic waste
    if (dominantChannel === 'green' || (averageColor.r > 100 && averageColor.g > 80)) {
      predictions[0] = Math.random() * 0.4 + 0.6; // Wet waste
    }
    
    // Gray/white tones suggest dry waste
    if (brightness > 150 && Math.abs(averageColor.r - averageColor.g) < 30) {
      predictions[1] = Math.random() * 0.4 + 0.5; // Dry waste
    }
    
    // Bright colors suggest recyclables
    if (brightness > 120 && (dominantChannel === 'blue' || averageColor.b > 120)) {
      predictions[2] = Math.random() * 0.4 + 0.7; // Recyclable
    }
    
    // Normalize predictions
    const sum = predictions.reduce((a, b) => a + b, 0);
    if (sum > 0) {
      predictions = predictions.map(p => p / sum);
    }
    
    // Find top prediction
    const maxIndex = predictions.indexOf(Math.max(...predictions));
    const maxConfidence = predictions[maxIndex];
    
    if (maxConfidence > confidenceThreshold) {
      return {
        classId: maxIndex,
        className: WASTE_CLASSES[maxIndex].name,
        confidence: maxConfidence,
        color: WASTE_CLASSES[maxIndex].color,
        description: WASTE_CLASSES[maxIndex].description,
        timestamp: Date.now()
      };
    }
    
    return null;
  }

  dispose() {
    if (this.model) {
      this.model.dispose();
      this.model = null;
      this.isLoaded = false;
    }
  }
}

// Singleton instance
export const wasteDetectionModel = new WasteDetectionModel();
