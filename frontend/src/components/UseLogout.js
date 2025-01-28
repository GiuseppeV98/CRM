import { useNavigate } from 'react-router-dom';
import axios from './AxiosConfig';

const useLogout = () => {
  const navigate = useNavigate();

  const logout = async () => {
    try {
      const response = await axios.post('/auth/logout/');
      if (response.data.status === 'success') {
        // Redireziona alla pagina di login
        navigate('/login');
      } else {
        console.error('Logout failed:', response.data.message);
      }
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  return logout;
};

export default useLogout;
