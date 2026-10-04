import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Repositories from "./pages/Repositories";
import Documents from "./pages/Documents";
import DocumentDetail from "./pages/DocumentDetail";
import Search from "./pages/Search";
import Chat from "./pages/Chat";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

function Protected({ children }) {
  return (
    <ProtectedRoute>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<Protected><Dashboard /></Protected>} />
      <Route path="/repositories" element={<Protected><Repositories /></Protected>} />
      <Route path="/documents" element={<Protected><Documents /></Protected>} />
      <Route path="/documents/:id" element={<Protected><DocumentDetail /></Protected>} />
      <Route path="/search" element={<Protected><Search /></Protected>} />
      <Route path="/chat/:documentId" element={<Protected><Chat /></Protected>} />
    </Routes>
  );
}

export default App;