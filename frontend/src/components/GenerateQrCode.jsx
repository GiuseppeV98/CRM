import React, { useState, useEffect } from 'react';
import axios from './AxiosConfig';
import { Container, Row, Col, Alert, Button } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import styles from './styles/QR_Code.module.css';

const GenerateQrCode =  ( {onNextStep} ) => {
  const [qrImage, setQrImage] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchQrCode = async () => {
      try {
        const response = await axios.get('/auth/generate_qr/');
        if (response.data.qr_image_base64) {
          setQrImage(response.data.qr_image_base64);
        } else {
          onNextStep('verify_otp');
        }
      } catch (error) {
        setError('An unexpected error occurred while fetching the QR code.');
        console.error('Error fetching QR code:', error);
      }
    };

    fetchQrCode();
  }, [onNextStep]);

  return (
<div className={` col-4 ${(styles.lato_form)}`}>  
    <div className={`p-4 border rounded ${(styles.containerloginform)}`}>
        <div className={`p-4 border rounded ${(styles.containerTesto)}`}>
          <h4>Scansiona il QR Code</h4>
          <p>utilizza l'app Authenticator sul tuo dispositivo mobile</p>
        </div>    
          <div className={styles.messaggioErrore}>
            {error && <Alert variant="danger">{error}</Alert>}
          </div>
          <div className={styles.login_form}>
          {qrImage ? (
            <>
              <img src={`data:image/png;base64,${qrImage}`} alt="QR Code" style={{ maxWidth: '60%', height: 'auto' }} />
              <Button variant="primary" className="mt-3" onClick={() => onNextStep('complete_config')}>Procedi alla verifica OTP</Button>
            </>
          ) : (
            <p>Loading QR code...</p>
          )}
            </div>
          </div>

</div>
  );
};

export default GenerateQrCode;




