import React, { useState, useRef } from 'react';

const AudioRecorder = ({ onSend }) => {
    const [recording, setRecording] = useState(false);
    // const [audioURL, setAudioURL] = useState('');
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const startRecording = async () => {
        try {
            console.log('startRecording');
            if (audioChunksRef.current.length > 0) {
                console.log('Clearing audio chunks');
                audioChunksRef.current = [];
            }
            console.log('audio chunks at begginning: ', audioChunksRef);
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            let options = {};

            // Check if 'audio/webm' is supported
            if (MediaRecorder.isTypeSupported('audio/webm')) {
                options = { mimeType: 'audio/webm' };
            }

            mediaRecorderRef.current = new MediaRecorder(stream, options);
            mediaRecorderRef.current.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };
            mediaRecorderRef.current.start(1000);
            setRecording(true);
            console.log('MediaRecorder started, state:', mediaRecorderRef.current.state);
            console.log('MediaRecorder Mime type', mediaRecorderRef.current.mimeType);
            console.log('Audio chunks', audioChunksRef.current);
        } catch (error) {
            console.error('Error in starting audio recording', error);
            alert('Error in starting audio recording');
            setRecording(false); // Reset recording state on error
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            setRecording(false);
            console.log('MediaRecorder stopped, state:', mediaRecorderRef.current.state);
            console.log('MediaRecorder Mime type', mediaRecorderRef.current.mimeType);
            console.log('Audio chunks', audioChunksRef.current);
            handleSend(); // Automatically send after stopping the recording
        }
    };

    const handleSend = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mediaRecorderRef.current ? mediaRecorderRef.current.mimeType : 'audio/webm' });
        // const url = URL.createObjectURL(audioBlob);
        // setAudioURL(url);
        console.log('audioBlob', audioBlob);
        onSend(audioBlob);
        // Reset all values
        audioChunksRef.current = [];
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop()); // Stop the tracks
            mediaRecorderRef.current = null; // Clear the MediaRecorder
        }
        console.log('audio chunks at end of send: ', audioChunksRef);
        console.log('Audio chunks after clearing', audioChunksRef.current);
    };

    return (
        <div>
            {recording
                ? <button className="btn btn-outline-danger" onClick={stopRecording}>Stop talking to me</button>
                : <button className="btn btn-outline-success" onClick={startRecording}>Talk to me</button>}
                {/* {audioURL && <a href={audioURL} download="recording.webm">Download</a>} */}
        </div>
    );
};

export default AudioRecorder;
