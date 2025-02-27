from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastrtc import Stream, AsyncStreamHandler, AdditionalOutputs
from pydantic import BaseModel
import json

app = FastAPI()


class AudioStreamHandler(AsyncStreamHandler):
    """Stream handler for audio data"""
    async def process_frame(self, frame):
        return frame
    
    async def on_additional_input(self, input_data):
        """Handle additional input data"""
        if isinstance(input_data, str):
            try:
                message = json.loads(input_data)
                if message.get("type") == "code_update":
                    # Here we would handle code updates
                    # For example, broadcast to other participants
                    return AdditionalOutputs(input_data)
            except:
                pass
        return None
    
    async def copy(self):
        """Return a copy of this handler"""
        return AudioStreamHandler()
        
    async def emit(self, frame):
        """Emit a frame (required abstract method)"""
        return frame
        
    async def receive(self, frame):
        """Receive a frame (required abstract method)"""
        return await self.process_frame(frame)

stream = Stream(
    handler=AudioStreamHandler(),
    modality="audio",
    mode="send-receive",
    concurrency_limit=10
)

stream.mount(app)
stream.ui.launch()


class WebRTCOffer(BaseModel):
    """Model for WebRTC offer data"""
    sdp: str
    type: str
    webrtc_id: str


class InputData(BaseModel):
    webrtc_id: str
    message: str  # For text messages between collaborators


@app.post("/webrtc/offer")
async def handle_offer(offer: WebRTCOffer):
    """Handle WebRTC offers from clients"""
    try:
        response = await stream.handle_offer(offer.model_dump())
        return response
    except Exception as e:
        return {
            "status": "failed",
            "meta": {
                "error": str(e)
            }
        }


@app.post("/input_hook")
async def input_hook(data: InputData):
    """Process text messages from collaborators"""
    print(f"Received message from {data.webrtc_id}: {data.message}")
    stream.set_input(data.webrtc_id, data.message)
    return {"status": "success"}


@app.get("/updates")
async def stream_updates(webrtc_id: str):
    """Stream output updates to clients"""
    async def output_stream():
        async for output in stream.output_stream(webrtc_id):
            yield f"data: {json.dumps({'type': 'update', 'data': output.args[0]})}\n\n"

    return StreamingResponse(
        output_stream(),
        media_type="text/event-stream"
    )

@app.get("/")
def read_root():
    return {"message": "Codesync RTC Server Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
