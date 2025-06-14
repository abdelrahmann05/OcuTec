from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import logging
import os
import json
from morse_main import EyeTracker  # استيراد فئة EyeTracker من morse_main
import base64
import numpy as np
import cv2
from auth import router as auth_router  # Import the auth router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log'
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = BASE_DIR

app = FastAPI()

app.mount("/images", StaticFiles(directory="images"), name="images")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # للتطوير فقط، في الإنتاج يجب تحديد النطاقات المسموح بها
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the auth router
app.include_router(auth_router, prefix="/api")

# API Models
class MorseSignal(BaseModel):
    signal: str

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        logger.info("WebSocket connection established")
        
        eye_tracker = EyeTracker()
        
        while True:
            try:
                data = await websocket.receive_json()
                if 'image' in data:
                    # Decode base64 image
                    img_bytes = base64.b64decode(data['image'])
                    img_np = np.frombuffer(img_bytes, np.uint8)
                    frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
                    
                    # Process frame using EyeTracker
                    debug_frame, ear, eye_status, morse, word = eye_tracker.process_frame(frame)
                    
                    # Convert debug frame to base64
                    _, buffer = cv2.imencode('.jpg', debug_frame)
                    debug_frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Send results back to client
                    await websocket.send_json({
                        "debug_frame": debug_frame_base64,
                        "eye_status": eye_status,
                        "ear": float(ear),
                        "morse": morse,
                        "word": word
                    })
                    
            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                await websocket.send_json({"error": "Invalid JSON format"})
            except Exception as e:
                logger.error(f"Error processing data: {str(e)}")
                await websocket.send_json({"error": "Internal server error"})
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.close()
        except:
            pass

# Static files configuration should come after API routes
app.mount("/images", StaticFiles(directory=os.path.join(STATIC_DIR, "images"), html=True), name="images")
app.mount("/login", StaticFiles(directory=os.path.join(STATIC_DIR, "login")), name="login")
app.mount("/signup", StaticFiles(directory=os.path.join(STATIC_DIR, "signup")), name="signup")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

# Morse code dictionary and conversion function
MORSE_DICT = {
    '.-': 'A', '-...': 'B', 
    '-.-.': 'C', '-..': 'D', 
    '.': 'E', '..-.': 'F', 
    '--.': 'G', '....': 'H', 
    '..': 'I', '.---': 'J', 
    '-.-': 'K', '.-..': 'L', 
    '--': 'M', '-.': 'N', 
    '---': 'O', '.--.': 'P', 
    '--.-': 'Q', '.-.': 'R', 
    '...': 'S', '-': 'T', 
    '..-': 'U', '...-': 'V', 
    '.--': 'W', '-..-': 'X', 
    '-.--': 'Y','--..': 'Z', 
    '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4', 
    '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9'
}

def convert_to_morse(text: str) -> str:
    return ' '.join(MORSE_DICT.get(char.lower(), '') for char in text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
