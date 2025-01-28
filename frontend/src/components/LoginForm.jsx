import React, { useState, useEffect } from 'react';
import axios from './AxiosConfig';
import Cookies from 'js-cookie';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import { Helmet } from 'react-helmet';
import styles from './styles/loginForm.module.css';

const LoginForm = ({ onNextStep }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken');
  }, []);

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
};

  const handleLogin = async () => {
    try {
      const response = await axios.post('/auth/login/', { username, password });

      if (response.data.redirect) {
        if (response.data.redirect === 'generate_qr') {
          onNextStep('generate_qr'); // Cambia lo step nel componente principale
        } else if (response.data.redirect === 'verify_otp') {
          onNextStep('verify_otp'); // Cambia lo step
        }
      }
    } catch (error) {
      console.error('Error during login:', error);
      setError('Login failed');
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    handleLogin();
  };

  return (

<div className={` col-4 ${(styles.lato_form)}`}>  
    <div className={`p-4 border rounded ${(styles.containerloginform)}`}>
        <div className={`p-4 border rounded ${(styles.containerTesto)}`}>
            <h2 className="mb-4">Accedi</h2>
        </div>    
          <div className={styles.messaggioErrore}>
            {error && <div className="alert alert-danger">{error}</div>}
          </div>
          <div className={styles.login_form}>
            <form onSubmit={(e) => handleSubmit(e, username, password)}>
              <div className="form-group mb-3">
                <label htmlFor="username">Username:</label>
                <input
                  type="text"
                  className="form-control"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="form-group mb-3">
                <label htmlFor="password">Password:</label>
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="form-control"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />   
                <div className={styles.lookpassword}>
             <i class="bi bi-eye-fill" onClick={togglePasswordVisibility} ></i>
             </div>
              </div>

              <button type="submit" className="btn btn-primary btn-block">
                Avanti
              </button>
            </form>
            </div>
          </div>

</div>

  );      
};

export default LoginForm;
