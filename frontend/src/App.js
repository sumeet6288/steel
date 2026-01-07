import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { DashboardLayout } from "./components/layout/DashboardLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { ProjectsPage } from "./pages/ProjectsPage";
import { ProjectDetailPage } from "./pages/ProjectDetailPage";
import { ConnectionDesignerPage } from "./pages/ConnectionDesignerPage";
import { AuditLogPage } from "./pages/AuditLogPage";

function App() {
  return (
    <div className="App">
      <Toaster position="top-right" />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          <Route element={<DashboardLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
            <Route path="/connections/:connectionId" element={<ConnectionDesignerPage />} />
            <Route path="/audit" element={<AuditLogPage />} />
            <Route path="/settings" element={<div className="p-8"><h1 className="text-2xl font-heading font-bold">Settings</h1></div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;