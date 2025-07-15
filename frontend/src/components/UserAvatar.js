import React, { useState } from 'react';
import { getApiUrl } from '../utils/apiUrl';

function UserAvatar({ 
  user, 
  size = 32, 
  showUpload = false, 
  onAvatarUpdate = null,
  className = '',
  isAdmin = false 
}) {
  const [isUploading, setIsUploading] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const API_BASE_URL = getApiUrl();

  // Generate initials from name or username
  const getInitials = (user) => {
    const name = user?.name || user?.username || user?.display_name || 'U';
    return name
      .split(' ')
      .map(word => word.charAt(0).toUpperCase())
      .join('')
      .substring(0, 2);
  };

  // Handle file selection
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        alert('Please select a valid image file (PNG, JPG, JPEG, GIF, or WebP)');
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        return;
      }

      setSelectedFile(file);
      
      // Create preview URL
      const reader = new FileReader();
      reader.onload = (e) => setPreviewUrl(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  // Upload avatar
  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(`${API_BASE_URL}/admin/users/${user.id}/avatar/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        if (onAvatarUpdate) {
          onAvatarUpdate(user.id, data.avatar_url);
        }
        setShowUploadModal(false);
        setSelectedFile(null);
        setPreviewUrl(null);
      } else {
        const errorData = await response.json();
        alert(errorData.error || 'Failed to upload avatar');
      }
    } catch (error) {
      console.error('Error uploading avatar:', error);
      alert('Failed to upload avatar');
    }
    setIsUploading(false);
  };

  // Avatar image component
  const AvatarImage = () => {
    if (user?.avatar_url) {
      return (
        <img
          src={user.avatar_url}
          alt={`${user.display_name || user.name || user.username} avatar`}
          className={`rounded-circle ${className}`}
          style={{ 
            width: size, 
            height: size, 
            objectFit: 'cover',
            border: '2px solid #dee2e6'
          }}
          onError={(e) => {
            // If image fails to load, show initials
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'flex';
          }}
        />
      );
    }

    // Fallback initials avatar
    return (
      <div
        className={`rounded-circle d-flex align-items-center justify-content-center bg-primary text-white fw-bold ${className}`}
        style={{ 
          width: size, 
          height: size, 
          fontSize: size * 0.4,
          border: '2px solid #dee2e6'
        }}
      >
        {getInitials(user)}
      </div>
    );
  };

  return (
    <>
      <div className="position-relative d-inline-block">
        <AvatarImage />
        
        {/* Upload button overlay */}
        {showUpload && isAdmin && (
          <button
            className="btn btn-sm btn-primary position-absolute bottom-0 end-0 rounded-circle p-1"
            style={{ 
              width: '24px', 
              height: '24px',
              transform: 'translate(25%, 25%)'
            }}
            onClick={() => setShowUploadModal(true)}
            title="Upload avatar"
          >
            <i className="bi bi-camera" style={{ fontSize: '10px' }}></i>
          </button>
        )}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <>
          <div className="modal-backdrop fade show" onClick={() => setShowUploadModal(false)}></div>
          <div className="modal fade show" style={{ display: 'block' }} tabIndex="-1">
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">
                    Upload Avatar for {user.display_name || user.name || user.username}
                  </h5>
                  <button 
                    type="button" 
                    className="btn-close" 
                    onClick={() => setShowUploadModal(false)}
                  ></button>
                </div>
                <div className="modal-body">
                  <div className="text-center mb-3">
                    {/* Current avatar */}
                    <div className="mb-3">
                      <label className="form-label">Current Avatar:</label>
                      <div className="d-flex justify-content-center">
                        <AvatarImage />
                      </div>
                    </div>

                    {/* File input */}
                    <div className="mb-3">
                      <label className="form-label">Choose New Avatar:</label>
                      <input
                        type="file"
                        className="form-control"
                        accept="image/*"
                        onChange={handleFileSelect}
                      />
                      <div className="form-text">
                        Max file size: 5MB. Supported formats: PNG, JPG, JPEG, GIF, WebP
                      </div>
                    </div>

                    {/* Preview */}
                    {previewUrl && (
                      <div className="mb-3">
                        <label className="form-label">Preview:</label>
                        <div className="d-flex justify-content-center">
                          <img
                            src={previewUrl}
                            alt="Preview"
                            className="rounded-circle"
                            style={{ 
                              width: 100, 
                              height: 100, 
                              objectFit: 'cover',
                              border: '2px solid #dee2e6'
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowUploadModal(false)}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleUpload}
                    disabled={!selectedFile || isUploading}
                  >
                    {isUploading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Uploading...
                      </>
                    ) : (
                      'Upload Avatar'
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}

export default UserAvatar;
