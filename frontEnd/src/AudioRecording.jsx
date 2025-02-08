import React, { useState, useEffect, useRef } from 'react';

const AudioRecording = ({ onStopRecording }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    if (isRecording) {
      // Start recording
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then((stream) => {
          mediaRecorderRef.current = new MediaRecorder(stream);
          mediaRecorderRef.current.ondataavailable = (event) => {
            audioChunksRef.current.push(event.data);
          };

          mediaRecorderRef.current.onstop = () => {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
            setAudioBlob(audioBlob);
            onStopRecording(audioBlob); // Automatically send the audio after stopping the recording
          };

          mediaRecorderRef.current.start();
        })
        .catch((error) => console.error('Error accessing microphone:', error));
    } else {
      // Stop recording
      mediaRecorderRef.current?.stop();
    }

    // Cleanup function to stop the recording if the component is unmounted
    return () => {
      mediaRecorderRef.current?.stop();
    };
  }, [isRecording, onStopRecording]);

  const handleStartStopRecording = () => {
    setIsRecording((prevIsRecording) => !prevIsRecording);
  };

  return (
    <div>
      <button onClick={handleStartStopRecording} style={{ all: 'unset', fontSize: '2rem', cursor: 'pointer' }}>
        {isRecording ? '🛑' : '🎤'}
       </button>

    </div>
  );
};

export default AudioRecording;
