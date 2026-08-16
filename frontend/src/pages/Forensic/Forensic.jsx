import { useState, useRef, useEffect } from 'react';
import { Card, Message, StatusBadge } from '../../components/common/UI';
import { forensic } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { API_ORIGIN } from '../../config';

function ForensicPage() {
  const { user } = useAuth();
  const [recording, setRecording] = useState(false);
  const [recordings, setRecordings] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [docName, setDocName] = useState('');

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);

  const loadRecordings = async () => {
    try {
      const res = await forensic.recordings();
      setRecordings(res.recordings || []);
    } catch (err) {
      setError(err.message || 'Failed to load recordings');
    }
  };

  useEffect(() => {
    loadRecordings();
  }, []);

  const startRecording = async () => {
    setError('');
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false });
      streamRef.current = stream;
      chunksRef.current = [];

      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      mediaRecorder.onstop = handleStop;

      stream.getVideoTracks()[0].onended = () => stopRecording();

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      setError(err.message || 'Screen recording permission was denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
    }
    setRecording(false);
  };

  const handleStop = async () => {
    const blob = new Blob(chunksRef.current, { type: 'video/webm' });
    setUploading(true);
    setError('');
    try {
      await forensic.uploadRecording(blob, user?.email || 'current-user', docName || 'Live Session');
      await loadRecordings();
    } catch (err) {
      setError(err.message || 'Failed to upload the recording');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-slate-950 min-h-screen p-4 sm:p-6 lg:p-8">
      <h1 className="font-display text-white text-2xl md:text-3xl font-semibold mb-2">
        Forensic — Session Recording
      </h1>
      <p className="text-gray-400 mb-6">
        Record user screen sessions and play them back for forensic investigation and compliance.
      </p>

      {error && <Message type="error">{error}</Message>}

      <Card title="Session Recorder" subtitle="Capture screen activity for the current session" className="mb-6">
        <div className="flex flex-col sm:flex-row gap-3 sm:items-center mb-4">
          <input
            type="text"
            placeholder="Document / context name (optional)"
            value={docName}
            onChange={(e) => setDocName(e.target.value)}
            disabled={recording}
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 disabled:opacity-50"
          />
          {!recording ? (
            <button onClick={startRecording}
              className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition-colors whitespace-nowrap">
              ● Start Recording
            </button>
          ) : (
            <button onClick={stopRecording}
              className="bg-red-600 hover:bg-red-500 text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition-colors whitespace-nowrap">
              ■ Stop &amp; Save
            </button>
          )}
        </div>

        {recording && (
          <div className="flex items-center gap-2 text-red-400 text-sm">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            Recording in progress — the browser will ask which screen/tab/window to share.
          </div>
        )}
        {uploading && <p className="text-slate-400 text-sm mt-2">Saving recording to the server...</p>}
      </Card>

      <Card title="Recorded Sessions" subtitle={`${recordings.length} recording(s)`}>
        {recordings.length === 0 ? (
          <p className="text-slate-500 text-sm">No sessions recorded yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recordings.map((rec) => (
              <div key={rec.filename} className="bg-slate-900/70 border border-slate-800 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white text-sm font-medium truncate">{rec.document}</span>
                  <StatusBadge status="recorded" />
                </div>
                <p className="text-slate-500 text-xs mb-3">
                  {rec.user} · {new Date(rec.recorded_at).toLocaleString()}
                </p>
                <video src={rec.url.startsWith('http') ? rec.url : `${API_ORIGIN}${rec.url}`} controls className="w-full rounded-lg bg-black" />
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

export default ForensicPage;