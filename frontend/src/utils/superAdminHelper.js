// Super Admin Helper Utility
// This utility can be used to set or check super admin status for debugging

export const setSuperAdminStatus = (isSuper = true) => {
  localStorage.setItem('super_admin', isSuper ? 'true' : 'false');
  console.log('Super admin status set to:', isSuper);
  // Trigger a page refresh to update the navbar
  window.location.reload();
};

export const checkSuperAdminStatus = () => {
  const isSuperAdmin = localStorage.getItem('super_admin') === 'true';
  const role = localStorage.getItem('role');
  const username = localStorage.getItem('username');
  
  console.log('=== Super Admin Status Check ===');
  console.log('Username:', username);
  console.log('Role:', role);
  console.log('Super Admin localStorage value:', localStorage.getItem('super_admin'));
  console.log('Is Super Admin:', isSuperAdmin);
  console.log('===============================');
  
  return isSuperAdmin;
};

export const enableSuperAdminForTesting = () => {
  console.log('Enabling Super Admin for testing...');
  setSuperAdminStatus(true);
};

// Add to window for easy access in browser console
if (typeof window !== 'undefined') {
  window.enableSuperAdmin = enableSuperAdminForTesting;
  window.checkSuperAdmin = checkSuperAdminStatus;
}
