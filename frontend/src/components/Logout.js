import React, { useEffect } from 'react';
import useLogout from './UseLogout';

const Logout = () => {
  const logout = useLogout();

  useEffect(() => {
    // Esegui il logout automaticamente quando il componente è montato
    logout();
  }, [logout]);

  return null;  // Nessun contenuto da visualizzare durante il logout
};

export default Logout;