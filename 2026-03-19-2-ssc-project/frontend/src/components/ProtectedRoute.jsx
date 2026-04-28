import { Navigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';

export function ProtectedRoute({ children }) {
  const token = useAppStore((s) => s.token);
  if (!token) return <Navigate to="/login" replace />;
  return children;
}
