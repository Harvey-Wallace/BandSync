import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('bandsync-theme');
    return saved ? saved === 'dark' : false;
  });

  const [orgThemeColor, setOrgThemeColor] = useState('#007bff');

  useEffect(() => {
    // Update CSS custom properties for theme
    const root = document.documentElement;
    
    // Set Bootstrap theme
    root.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');
    
    // Set Bootstrap CSS properties for theming
    root.style.setProperty('--bs-primary', orgThemeColor);
    root.style.setProperty('--bs-primary-rgb', hexToRgb(orgThemeColor));
    
    // Set custom theme CSS properties for our components
    root.style.setProperty('--theme-primary', orgThemeColor);
    
    // Create darker variant for hover states
    const darkerColor = adjustColor(orgThemeColor, -20);
    root.style.setProperty('--bs-primary-dark', darkerColor);
    root.style.setProperty('--theme-primary-dark', darkerColor);
    
    // Create lighter variant for backgrounds
    const lighterColor = adjustColor(orgThemeColor, 40);
    root.style.setProperty('--bs-primary-light', lighterColor);
    root.style.setProperty('--theme-primary-light', lighterColor);
    
    localStorage.setItem('bandsync-theme', isDark ? 'dark' : 'light');
  }, [isDark, orgThemeColor]);  useEffect(() => {
    // Load organization theme color from localStorage or API
    const loadOrgTheme = async () => {
      // First try localStorage
      const savedColor = localStorage.getItem('bandsync-org-color');
      if (savedColor && savedColor !== orgThemeColor) {
        console.log('Loading saved theme color:', savedColor);
        setOrgThemeColor(savedColor);
        return;
      }
      
      // If we have a token, try to load from API (all users can see the theme)
      const token = localStorage.getItem('token');
      if (token) {
        try {
          console.log('Loading theme from API...');
          
          // Try organization current endpoint first
          let response = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/organizations/current`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          
          // If organization endpoint fails, try admin endpoint (for backwards compatibility)
          if (!response.ok) {
            console.log('Public org endpoint failed for theme, trying admin endpoint...');
            response = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/admin/organization`, {
              headers: { Authorization: `Bearer ${token}` }
            });
          }
          
          if (response.ok) {
            const orgData = await response.json();
            const organization = orgData.organization || orgData;
            const themeColor = organization.theme_color || 
                             (orgData.organization && orgData.organization.theme_color);
            if (themeColor && themeColor !== orgThemeColor) {
              console.log('Setting theme color from API:', themeColor);
              setOrgThemeColor(themeColor);
              localStorage.setItem('bandsync-org-color', themeColor);
            }
          } else {
            console.error('Failed to load theme from API:', response.status);
          }
        } catch (error) {
          console.error('Error loading organization theme:', error);
        }
      }
    };

    loadOrgTheme();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  const updateOrgThemeColor = (color) => {
    setOrgThemeColor(color);
    localStorage.setItem('bandsync-org-color', color);
  };

  // Helper functions
  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? 
      `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` 
      : '0, 123, 255'; // fallback to bootstrap primary
  };

  const adjustColor = (hex, amount) => {
    const usePound = hex[0] === '#';
    const col = usePound ? hex.slice(1) : hex;
    const num = parseInt(col, 16);
    let r = (num >> 16) + amount;
    let b = ((num >> 8) & 0x00FF) + amount;
    let g = (num & 0x0000FF) + amount;
    r = r > 255 ? 255 : r < 0 ? 0 : r;
    b = b > 255 ? 255 : b < 0 ? 0 : b;
    g = g > 255 ? 255 : g < 0 ? 0 : g;
    return (usePound ? '#' : '') + (g | (b << 8) | (r << 16)).toString(16).padStart(6, '0');
  };

  return (
    <ThemeContext.Provider value={{ 
      isDark, 
      toggleTheme, 
      orgThemeColor, 
      updateOrgThemeColor 
    }}>
      {children}
    </ThemeContext.Provider>
  );
};
