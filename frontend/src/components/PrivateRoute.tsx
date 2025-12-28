import { Navigate } from 'react-router-dom'

interface PrivateRouteProps {
  isAuthenticated: boolean
  children: React.ReactNode
}

function PrivateRoute({ isAuthenticated, children }: PrivateRouteProps) {
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

export default PrivateRoute
