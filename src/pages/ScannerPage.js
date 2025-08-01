import React, { useState, useRef, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Upload, X, RotateCcw, Zap, History, Settings, Play, Square, Target } from 'lucide-react';
import { classifyImage } from '../data/wasteCategories';
import { wasteDetectionModel } from '../utils/wasteDetectionModel';

const ScannerPage = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState('');
  const [scanHistory, setScanHistory] = useState([]);
  const [flashEnabled, setFlashEnabled] = useState(false);
  const [isLoadingCamera, setIsLoadingCamera] = useState(false);
  const [facingMode, setFacingMode] = useState('user'); // 'user' for front camera, 'environment' for back

  // Real-time detection states
  const [isRealTimeMode, setIsRealTimeMode] = useState(false);
  const [detections, setDetections] = useState([]);
  const [isModelLoading, setIsModelLoading] = useState(false);
  const [model, setModel] = useState(null);
  const [confidence, setConfidence] = useState(0.5);
  const [realTimeStats, setRealTimeStats] = useState({
    totalDetections: 0,
    wetWaste: 0,
    dryWaste: 0,
    fps: 0
  });
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const detectionCanvasRef = useRef(null);
  const animationFrameRef = useRef(null);
  const navigate = useNavigate();

  // Cleanup camera stream on component unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [stream]);

  // Load TensorFlow.js model
  useEffect(() => {
    const loadModel = async () => {
      try {
        setIsModelLoading(true);
        setError('');

        // Load the waste detection model
        await wasteDetectionModel.loadModel();
        setModel(wasteDetectionModel);

        console.log('Waste classification model loaded successfully!');
      } catch (err) {
        console.error('Error loading model:', err);
        setError('Failed to load AI model. Some features may be limited.');
      } finally {
        setIsModelLoading(false);
      }
    };

    loadModel();
  }, []);

  // Real-time detection function
  const detectWasteRealTime = useCallback(async () => {
    if (!videoRef.current || !detectionCanvasRef.current || !model || !isRealTimeMode) {
      return;
    }

    const video = videoRef.current;
    const canvas = detectionCanvasRef.current;
    const ctx = canvas.getContext('2d');

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    try {
      // Use the new model's real-time detection
      const detection = await model.detectRealTime(video, confidence);

      if (detection) {
        setDetections(prev => [detection, ...prev.slice(0, 9)]); // Keep last 10 detections

        // Update stats
        setRealTimeStats(prev => ({
          ...prev,
          totalDetections: prev.totalDetections + 1,
          wetWaste: detection.classId === 0 ? prev.wetWaste + 1 : prev.wetWaste,
          dryWaste: detection.classId === 1 ? prev.dryWaste + 1 : prev.dryWaste,
          fps: Math.round(1000 / (Date.now() - (prev.lastUpdate || Date.now()))),
          lastUpdate: Date.now()
        }));

        // Draw detection overlay
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = detection.color;
        ctx.lineWidth = 4;
        ctx.font = '24px Arial';
        ctx.fillStyle = detection.color;

        // Draw bounding box (simplified - full detection would need object detection model)
        const boxWidth = canvas.width * 0.6;
        const boxHeight = canvas.height * 0.6;
        const boxX = (canvas.width - boxWidth) / 2;
        const boxY = (canvas.height - boxHeight) / 2;

        ctx.strokeRect(boxX, boxY, boxWidth, boxHeight);
        ctx.fillText(
          `${detection.className} (${(detection.confidence * 100).toFixed(1)}%)`,
          boxX,
          boxY - 10
        );
      } else {
        // Clear canvas if no detection
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }

    } catch (error) {
      console.error('Detection error:', error);
    }

    // Continue detection loop
    if (isRealTimeMode) {
      animationFrameRef.current = requestAnimationFrame(detectWasteRealTime);
    }
  }, [model, confidence, isRealTimeMode]);

  // Start real-time detection
  const startRealTimeDetection = useCallback(() => {
    if (!model) {
      setError('AI model not loaded yet. Please wait...');
      return;
    }

    setIsRealTimeMode(true);
    setDetections([]);
    setRealTimeStats({
      totalDetections: 0,
      wetWaste: 0,
      dryWaste: 0,
      fps: 0
    });

    // Start detection loop
    detectWasteRealTime();
  }, [model, detectWasteRealTime]);

  // Stop real-time detection
  const stopRealTimeDetection = useCallback(() => {
    setIsRealTimeMode(false);
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (detectionCanvasRef.current) {
      const ctx = detectionCanvasRef.current.getContext('2d');
      ctx.clearRect(0, 0, detectionCanvasRef.current.width, detectionCanvasRef.current.height);
    }
  }, []);

  // Start camera with enhanced options
  const startCamera = useCallback(async () => {
    try {
      setError('');
      setIsLoadingCamera(true);

      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera not supported on this device');
      }

      // Request camera permissions
      const constraints = {
        video: {
          width: { ideal: 1280, max: 1920 },
          height: { ideal: 720, max: 1080 },
          facingMode: facingMode // Use selected camera (front or back)
        }
      };

      console.log('Requesting camera access...');
      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      console.log('Camera access granted, setting up video...');

      if (videoRef.current) {
        // Set the video source
        videoRef.current.srcObject = mediaStream;

        // Force video to be visible and playing
        videoRef.current.style.display = 'block';
        videoRef.current.style.visibility = 'visible';

        // Set video properties
        videoRef.current.muted = true;
        videoRef.current.playsInline = true;
        videoRef.current.autoplay = true;

        // Ensure video plays immediately
        videoRef.current.onloadedmetadata = () => {
          console.log('Video metadata loaded, starting playback...');
          console.log('Video dimensions:', videoRef.current.videoWidth, 'x', videoRef.current.videoHeight);

          videoRef.current.play()
            .then(() => {
              console.log('✅ Video is now playing and should be visible!');
              setStream(mediaStream);
              setIsScanning(true);
              setIsLoadingCamera(false);
              setError(''); // Clear any previous errors
            })
            .catch((playError) => {
              console.error('❌ Error playing video:', playError);
              setError('Unable to start video playback. Please try again.');
              setIsLoadingCamera(false);
            });
        };

        // Handle video errors
        videoRef.current.onerror = (e) => {
          console.error('❌ Video error:', e);
          setError('Video playback error. Please try again.');
          setIsLoadingCamera(false);
        };

        // Additional fallback - try to play immediately
        setTimeout(() => {
          if (videoRef.current && videoRef.current.readyState >= 2) {
            videoRef.current.play().catch(console.error);
          }
        }, 100);
      }
    } catch (err) {
      console.error('Error accessing camera:', err);
      setIsLoadingCamera(false);

      let errorMessage = 'Unable to access camera. ';

      if (err.name === 'NotAllowedError') {
        errorMessage += 'Please allow camera permissions and try again.';
      } else if (err.name === 'NotFoundError') {
        errorMessage += 'No camera found on this device.';
      } else if (err.name === 'NotSupportedError') {
        errorMessage += 'Camera not supported on this browser.';
      } else {
        errorMessage += 'Please try uploading an image instead.';
      }

      setError(errorMessage);
    }
  }, [facingMode]);

  // Stop camera
  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setIsScanning(false);
    setCapturedImage(null);
  }, [stream]);

  // Capture photo with enhanced quality
  const capturePhoto = useCallback(() => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      // Ensure video is playing and has dimensions
      if (video.videoWidth === 0 || video.videoHeight === 0) {
        setError('Camera not ready. Please wait a moment and try again.');
        return;
      }

      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Clear any previous content
      context.clearRect(0, 0, canvas.width, canvas.height);

      // Apply image enhancements
      context.filter = 'contrast(1.1) brightness(1.05) saturate(1.1)';
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert to high-quality JPEG
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.9);
      setCapturedImage(imageDataUrl);

      // Stop the camera stream after capture
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        setStream(null);
      }
      setIsScanning(false);

      // Add to scan history
      const newScan = {
        id: Date.now(),
        image: imageDataUrl,
        timestamp: new Date().toLocaleString()
      };
      setScanHistory(prev => [newScan, ...prev.slice(0, 4)]); // Keep last 5 scans

      // Clear any errors
      setError('');
    } else {
      setError('Camera not available. Please try again.');
    }
  }, [stream]);

  // Handle file upload
  const handleFileUpload = useCallback((event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCapturedImage(e.target.result);
        setIsScanning(false);
        if (stream) {
          stream.getTracks().forEach(track => track.stop());
          setStream(null);
        }
        
        // Add to scan history
        const newScan = {
          id: Date.now(),
          image: e.target.result,
          timestamp: new Date().toLocaleString()
        };
        setScanHistory(prev => [newScan, ...prev.slice(0, 4)]);
      };
      reader.readAsDataURL(file);
    }
  }, [stream]);

  // Process image with AI simulation
  const processImage = useCallback(async () => {
    if (!capturedImage) return;
    
    setIsProcessing(true);
    try {
      const result = await classifyImage(capturedImage);
      navigate('/results', { 
        state: { 
          result,
          image: capturedImage 
        } 
      });
    } catch (err) {
      console.error('Error processing image:', err);
      setError('Error processing image. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  }, [capturedImage, navigate]);

  // Reset scan
  const resetScan = useCallback(() => {
    setCapturedImage(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  // Switch camera (front/back)
  const switchCamera = useCallback(async () => {
    const newFacingMode = facingMode === 'user' ? 'environment' : 'user';
    setFacingMode(newFacingMode);

    // If camera is currently active, restart it with new facing mode
    if (isScanning && stream) {
      // Stop current stream
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      setIsScanning(false);

      // Start camera with new facing mode
      setTimeout(() => {
        startCamera();
      }, 100);
    }
  }, [facingMode, isScanning, stream, startCamera]);

  // Toggle flash
  const toggleFlash = useCallback(async () => {
    try {
      if (stream) {
        const videoTrack = stream.getVideoTracks()[0];
        const capabilities = videoTrack.getCapabilities();

        if (capabilities.torch) {
          await videoTrack.applyConstraints({
            advanced: [{ torch: !flashEnabled }]
          });
          setFlashEnabled(prev => !prev);
        } else {
          setError('Flash not supported on this device.');
        }
      } else {
        setFlashEnabled(prev => !prev);
      }
    } catch (err) {
      console.error('Error toggling flash:', err);
      setError('Unable to control flash.');
    }
  }, [stream, flashEnabled]);

  return (
    <div className="scanner-page">
      <div className="container">
        <div className="scanner-header">
          <h1 className="scanner-title">
            <Zap className="title-icon" />
            Advanced Scanner
          </h1>
          <p className="scanner-description">
            Enhanced AI-powered waste identification with advanced camera features
          </p>
          {isScanning && (
            <div className="camera-status">
              <div className="status-indicator"></div>
              <span>Camera Active - {facingMode === 'user' ? 'Front Camera' : 'Back Camera'}</span>
            </div>
          )}
          {!isScanning && !capturedImage && !error && (
            <div className="scanner-instructions">
              <p>📱 <strong>Camera Tips:</strong></p>
              <ul>
                <li>Allow camera permissions when prompted</li>
                <li>Hold your device steady for best results</li>
                <li>Ensure good lighting for accurate scanning</li>
                <li>Position the waste item clearly in the frame</li>
              </ul>
              <div className="test-camera-section">
                <p><strong>🔧 Test Camera:</strong></p>
                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    console.log('Testing camera access...');
                    navigator.mediaDevices.getUserMedia({ video: true })
                      .then(stream => {
                        console.log('✅ Camera test successful!', stream);
                        alert('Camera test successful! Your camera is working.');
                        stream.getTracks().forEach(track => track.stop());
                      })
                      .catch(err => {
                        console.error('❌ Camera test failed:', err);
                        alert('Camera test failed: ' + err.message);
                      });
                  }}
                >
                  Test Camera Access
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="scanner-interface">
          {!isScanning && !capturedImage && (
            <div className="scanner-options">
              {/* AI Model Status */}
              <div className="ai-status">
                <div className="status-header">
                  <Zap size={20} />
                  <span>AI Detection System</span>
                </div>
                <div className="status-content">
                  {isModelLoading ? (
                    <div className="loading-status">
                      <div className="spinner enhanced"></div>
                      <span>Loading AI model...</span>
                    </div>
                  ) : model ? (
                    <div className="ready-status">
                      <div className="status-indicator ready"></div>
                      <span>Real-time detection ready</span>
                    </div>
                  ) : (
                    <div className="error-status">
                      <div className="status-indicator error"></div>
                      <span>Model loading failed</span>
                    </div>
                  )}
                </div>

                {/* Confidence Slider */}
                {model && (
                  <div className="confidence-control">
                    <label>Detection Confidence: {(confidence * 100).toFixed(0)}%</label>
                    <input
                      type="range"
                      min="0.1"
                      max="0.9"
                      step="0.1"
                      value={confidence}
                      onChange={(e) => setConfidence(parseFloat(e.target.value))}
                      className="confidence-slider"
                    />
                  </div>
                )}
              </div>

              <div className="main-options">
                <div className="scan-option">
                  <button
                    className="scan-btn camera-btn enhanced"
                    onClick={startCamera}
                    disabled={isLoadingCamera}
                  >
                    {isLoadingCamera ? (
                      <>
                        <div className="spinner enhanced"></div>
                        <span>Starting Camera...</span>
                        <small>Please allow permissions</small>
                      </>
                    ) : (
                      <>
                        <Camera size={40} />
                        <span>Smart Camera</span>
                        <small>Real-time AI detection</small>
                      </>
                    )}
                  </button>
                </div>
                
                <div className="scan-divider">
                  <span>or</span>
                </div>
                
                <div className="scan-option">
                  <button 
                    className="scan-btn upload-btn enhanced"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Upload size={40} />
                    <span>Upload Image</span>
                    <small>High-quality analysis</small>
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    style={{ display: 'none' }}
                  />
                </div>
              </div>

              {/* Scan History */}
              {scanHistory.length > 0 && (
                <div className="scan-history">
                  <div className="history-header">
                    <History size={20} />
                    <h3>Recent Scans</h3>
                  </div>
                  <div className="history-grid">
                    {scanHistory.map((scan) => (
                      <div 
                        key={scan.id} 
                        className="history-item"
                        onClick={() => setCapturedImage(scan.image)}
                      >
                        <img src={scan.image} alt="Previous scan" />
                        <small>{scan.timestamp}</small>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {isScanning && (
            <div className="camera-interface enhanced">
              <div className="camera-container">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="camera-video"
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    backgroundColor: '#000'
                  }}
                />

                {/* Real-time detection overlay */}
                <canvas
                  ref={detectionCanvasRef}
                  className="detection-overlay"
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    pointerEvents: 'none',
                    zIndex: 2
                  }}
                />

                <div className="camera-overlay">
                  <div className="scan-frame enhanced">
                    <div className="scan-corners"></div>
                    <div className="scan-grid"></div>
                  </div>

                  {/* Real-time detection info */}
                  {isRealTimeMode && (
                    <div className="realtime-info">
                      <div className="detection-status">
                        <Target size={16} />
                        <span>Live Detection Active</span>
                      </div>
                      <div className="detection-stats">
                        <div className="stat">
                          <span>FPS: {realTimeStats.fps}</span>
                        </div>
                        <div className="stat">
                          <span>Detections: {realTimeStats.totalDetections}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Recent detections */}
                  {detections.length > 0 && (
                    <div className="recent-detections">
                      <h4>Recent Detections:</h4>
                      {detections.slice(0, 3).map((detection, index) => (
                        <div
                          key={detection.timestamp}
                          className="detection-item"
                          style={{ borderColor: detection.color }}
                        >
                          <span className="detection-class">{detection.className}</span>
                          <span className="detection-confidence">
                            {(detection.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="camera-settings">
                  <button
                    className="setting-btn"
                    onClick={switchCamera}
                    title={`Switch to ${facingMode === 'user' ? 'back' : 'front'} camera`}
                  >
                    <Camera size={20} />
                  </button>
                  <button
                    className={`setting-btn ${flashEnabled ? 'active' : ''}`}
                    onClick={toggleFlash}
                    title="Toggle flash"
                  >
                    <Zap size={20} />
                  </button>

                  {/* Real-time detection toggle */}
                  <button
                    className={`setting-btn realtime-btn ${isRealTimeMode ? 'active' : ''}`}
                    onClick={isRealTimeMode ? stopRealTimeDetection : startRealTimeDetection}
                    title={isRealTimeMode ? 'Stop real-time detection' : 'Start real-time detection'}
                    disabled={isModelLoading}
                  >
                    {isRealTimeMode ? <Square size={20} /> : <Play size={20} />}
                  </button>
                </div>
              </div>
              
              <div className="camera-controls enhanced">
                <button 
                  className="control-btn cancel-btn"
                  onClick={stopCamera}
                >
                  <X size={24} />
                  Cancel
                </button>
                
                <button 
                  className="control-btn capture-btn enhanced"
                  onClick={capturePhoto}
                >
                  <div className="capture-circle enhanced">
                    <div className="capture-inner"></div>
                  </div>
                </button>
                
                <div className="control-spacer"></div>
              </div>
            </div>
          )}

          {capturedImage && (
            <div className="image-preview enhanced">
              <div className="preview-container">
                <img 
                  src={capturedImage} 
                  alt="Captured item" 
                  className="preview-image"
                />
                <div className="preview-overlay">
                  <div className="analysis-indicator">
                    <Zap size={16} />
                    Ready for AI Analysis
                  </div>
                </div>
              </div>
              
              <div className="preview-controls">
                <button 
                  className="control-btn retry-btn"
                  onClick={resetScan}
                  disabled={isProcessing}
                >
                  <RotateCcw size={20} />
                  Retake
                </button>
                
                <button 
                  className="control-btn process-btn enhanced"
                  onClick={processImage}
                  disabled={isProcessing}
                >
                  {isProcessing ? (
                    <>
                      <div className="spinner enhanced"></div>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Zap size={20} />
                      AI Analyze
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="error-message">
              <p>{error}</p>
            </div>
          )}

          
        </div>

        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>
    </div>
  );
};

export default ScannerPage;
