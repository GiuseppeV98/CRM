import React, { useState, useEffect } from 'react';
import axios from './AxiosConfig';
import Cookies from 'js-cookie';
import styles from './styles/completeConfig.module.css';
import Timer from './Timer';
import OtpInput from './OtpInput';

const CompleteConfig = ({ onNextStep }) => {
    const [otp, setOtp] = useState(''); // Ora otp è una stringa concatenata
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');

    useEffect(() => {
        const csrfToken = Cookies.get('csrftoken');
        if (csrfToken) {
            console.log('CSRF Token trovato nei cookie');
            axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
        } else {
            console.error('CSRF Token non trovato nei cookie');
        }
    }, []);

    const handleSubmit = async (event) => {
        event.preventDefault();

        if (otp.length < 6) {
            setError('Inserisci un codice OTP completo.');
            return;
        }

        try {
            const response = await axios.post(
                'http://172.23.149.57:8000/auth/complete_config/',
                { otp },
                {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            );

            if (response.data.status === 'success') {
                onNextStep('verify_otp');
            } else {
                setError('Codice OTP non valido.');
            }
        } catch (error) {
            console.error("Errore durante la verifica dell'OTP:", error);
            setError('Errore durante la verifica dell\'OTP.');
        }
    };

    const handleOtpChange = (value) => {
        console.log('Codice OTP concatenato:', value);
        setOtp(value);
    };

    return (
        <div className={`col-4 ${styles.lato_form}`}>
            <div className={`p-4 border rounded ${styles.containerloginform}`}>
                <div className={`p-4 border rounded ${styles.containerTesto}`}>
                    <h3>Verifica Backup</h3>
                </div>
                <div className={styles.messaggioErrore}>
                    {error && <div className="alert alert-danger">{error}</div>}
                    {message && <div className="alert alert-success">{message}</div>}
                </div>
                <div className={styles.login_form}>
                    <form onSubmit={handleSubmit}>
                        <label htmlFor="otpCode">Inserisci l'OTP ricevuto tramite email:</label>
                        {/* Componente figlio con prop per gestire il cambio OTP */}
                        <OtpInput length={6} onOtpChange={handleOtpChange} />
                        <button type="submit" className={styles.btnVerify}>
                            Verifica
                        </button>
                    </form>
                    <div className={styles.backup_Option}>
                        <p>Non hai scansionato il QR code? Torna indietro</p>
                        <button
                            onClick={() => onNextStep('generate_qr')}
                            className={`btn btn-link ${styles.btnLink}`}
                        >
                            Torna al QR
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CompleteConfig;
