import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { restaurants } from '../api';
import './OwnerDashboard.css';

export default function OwnerDashboard() {
  const [restaurant, setRestaurant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    restaurants
      .me()
      .then(({ data }) => setRestaurant(data))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load restaurant'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="owner-loading">Loading dashboard...</div>;
  if (error) return <div className="owner-error">{error}</div>;
  if (!restaurant) return null;

  return (
    <div className="owner-dashboard">
      <h1>Owner dashboard</h1>
      <div className="owner-card">
        <h2>{restaurant.name}</h2>
        <p><strong>Address:</strong> {restaurant.address}, {restaurant.city}</p>
        {restaurant.phone && <p><strong>Phone:</strong> <a href={`tel:${restaurant.phone}`}>{restaurant.phone}</a></p>}
        {restaurant.operating_hours && <p><strong>Hours:</strong> {restaurant.operating_hours}</p>}
        {restaurant.google_maps_link && (
          <p>
            <a href={restaurant.google_maps_link} target="_blank" rel="noreferrer">View on Google Maps</a>
          </p>
        )}
        <p><strong>Status:</strong> <span className={`owner-status ${restaurant.status.toLowerCase()}`}>{restaurant.status}</span></p>
        <p className="owner-meta">Created: {new Date(restaurant.created_at).toLocaleDateString()}</p>
        <div className="owner-card-actions">
          <Link to="/owner-dashboard/edit" className="owner-btn owner-btn-edit">Edit restaurant</Link>
          <Link to="/owner-dashboard/photos" className="owner-btn owner-btn-photos">Manage photos</Link>
          <a href={`/restaurants/${restaurant.id}`} target="_blank" rel="noreferrer" className="owner-btn owner-btn-view">View public listing →</a>
        </div>
      </div>
      <p className="owner-intro">Your restaurant is active. More management features can be added here (menu, orders, etc.).</p>
    </div>
  );
}
