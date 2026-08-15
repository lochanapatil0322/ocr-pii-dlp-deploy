import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { DocumentAnalysisProvider } from "./context/DocumentAnalysisContext";

import Sidebar from "./components/layout/Sidebar";
import Navbar from "./components/layout/Navbar";

import Login from "./pages/Login/Login";
import Dashboard from "./pages/dashboard/Dashboard";
import Upload from "./pages/upload/Upload";
import OCR from "./pages/ocr/OCR";
import Detection from "./pages/Detection/Detection";
import Risk from "./pages/risk/Risk";
import Audit from "./pages/audit/Audit";
import Reports from "./pages/reports/Reports";
import DLPControls from "./pages/DLPControls/DLPControls";
import AIBehavior from "./pages/AIBehavior/AIBehavior";
import Forensic from "./pages/Forensic/Forensic";
import ForgotPassword from "./pages/ForgotPassword/ForgotPassword";
import Unlock from "./pages/Unlock/unlock";

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <Sidebar />
      <div className="min-h-screen ml-64">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/ocr" element={<OCR />} />
            <Route path="/detection" element={<Detection />} />
            <Route path="/risk" element={<Risk />} />
            <Route path="/audit" element={<Audit />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/dlp-controls" element={<DLPControls />} />
            <Route path="/ai-behavior" element={<AIBehavior />} />
            <Route path="/forensic-sessions" element={<Forensic />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <DocumentAnalysisProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/unlock" element={<Unlock />} />
            <Route path="/*" element={<ProtectedRoute><AppLayout /></ProtectedRoute>} />
          </Routes>
        </BrowserRouter>
      </DocumentAnalysisProvider>
    </AuthProvider>
  );
}

export default App;