import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Restaurants from './pages/Restaurants';
import RestaurantDetail from './pages/RestaurantDetail';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Apply from './pages/Apply';
import ApplicationStatus from './pages/ApplicationStatus';
import OwnerDashboard from './pages/OwnerDashboard';
import OwnerRestaurantEdit from './pages/OwnerRestaurantEdit';
import OwnerRestaurantPhotos from './pages/OwnerRestaurantPhotos';
import AdminApplications from './pages/admin/AdminApplications';
import AdminApplicationDetail from './pages/admin/AdminApplicationDetail';
import SuperAdminUsers from './pages/superadmin/SuperAdminUsers';
import SuperAdminUserDetail from './pages/superadmin/SuperAdminUserDetail';
import SuperAdminCreateUser from './pages/superadmin/SuperAdminCreateUser';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout><Restaurants /></Layout>} />
          <Route path="/restaurants/:id" element={<Layout><RestaurantDetail /></Layout>} />
          <Route path="/dashboard" element={<Layout><Home /></Layout>} />
          <Route path="/login" element={<Layout><Login /></Layout>} />
          <Route path="/register" element={<Layout><Register /></Layout>} />
          <Route
            path="/apply"
            element={
              <ProtectedRoute allowedRoles={['USER']}>
                <Layout><Apply /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/application-status"
            element={
              <ProtectedRoute allowedRoles={['USER']}>
                <Layout><ApplicationStatus /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/owner-dashboard"
            element={
              <ProtectedRoute allowedRoles={['OWNER']}>
                <Layout><OwnerDashboard /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/owner-dashboard/edit"
            element={
              <ProtectedRoute allowedRoles={['OWNER']}>
                <Layout><OwnerRestaurantEdit /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/owner-dashboard/photos"
            element={
              <ProtectedRoute allowedRoles={['OWNER']}>
                <Layout><OwnerRestaurantPhotos /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/applications"
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'SUPER_ADMIN']}>
                <Layout><AdminApplications /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/applications/:id"
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'SUPER_ADMIN']}>
                <Layout><AdminApplicationDetail /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/superadmin/users"
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN']}>
                <Layout><SuperAdminUsers /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/superadmin/users/create"
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN']}>
                <Layout><SuperAdminCreateUser /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/superadmin/users/:id"
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN']}>
                <Layout><SuperAdminUserDetail /></Layout>
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
