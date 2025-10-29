let room;
let microphoneTrack;

// Get LiveKit client
function getLiveKitClient() {
    // The library exports as "LivekitClient" (note the lowercase 'k')
    if (window.LivekitClient) return window.LivekitClient;
    if (window.LiveKitClient) return window.LiveKitClient;
    if (window.livekit) return window.livekit;
    
    throw new Error('LiveKit library not found');
}

// Update status display
function setStatus(message, isError = false) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    statusEl.style.color = isError ? 'red' : '';
}

// Get token from server
async function getTokenData() {
    const response = await fetch('/token');
    if (!response.ok) throw new Error('Failed to get token');
    return await response.json();
}

// Connect to room
async function connectToRoom() {
    try {
        setStatus('Connecting...');
        document.getElementById('connectBtn').disabled = true;
        
        const data = await getTokenData(); 
        console.log('Connecting to:', data.url); 
        
        const lk = getLiveKitClient();
        room = new lk.Room();
        
        room.on(lk.RoomEvent.Connected, async () => {
            setStatus('Connected - Enabling microphone...');
            document.getElementById('disconnectBtn').disabled = false;
            await publishMicrophone();
        });

        room.on(lk.RoomEvent.Disconnected, () => {
            setStatus('Disconnected');
            document.getElementById('connectBtn').disabled = false;
            document.getElementById('disconnectBtn').disabled = true;
            room = null;
        });

        // CRITICAL FIX: Listen for agent audio tracks and play them
        room.on(lk.RoomEvent.TrackSubscribed, (track, publication, participant) => {
            console.log('Track subscribed:', track.kind, 'from', participant.identity);
            if (track.kind === 'audio') {
                const audioElement = track.attach();
                document.body.appendChild(audioElement);
                audioElement.play().catch(e => console.error('Error playing audio:', e));
                console.log('Agent audio track attached and playing');
            }
        });
        
        await room.connect(data.url, data.token);
        
    } catch (error) {
        console.error('Connection error:', error);
        setStatus('Error: ' + error.message, true);
        document.getElementById('connectBtn').disabled = false;
    }
}

// Publish microphone
async function publishMicrophone() {
    try {
        const lk = getLiveKitClient();
        const tracks = await lk.createLocalTracks({ audio: true, video: false });
        
        for (const track of tracks) {
            if (track.kind === 'audio') {
                microphoneTrack = track;
                await room.localParticipant.publishTrack(track);
                setStatus('Connected - Microphone active');
                break;
            }
        }
    } catch (error) {
        console.error('Microphone error:', error);
        setStatus('Error: Could not access microphone', true);
    }
}

// Disconnect
async function disconnect() {
    if (microphoneTrack) {
        microphoneTrack.stop();
        microphoneTrack = null;
    }
    if (room) {
        await room.disconnect();
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    try {
        getLiveKitClient();
        console.log('LiveKit library loaded successfully');
        
        document.getElementById('connectBtn').onclick = connectToRoom;
        document.getElementById('disconnectBtn').onclick = disconnect;
        
    } catch (error) {
        console.error('Failed to load LiveKit:', error);
        setStatus('Error: LiveKit library not loaded', true);
        document.getElementById('connectBtn').disabled = true;
    }
});