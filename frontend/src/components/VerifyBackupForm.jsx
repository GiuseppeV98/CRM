import React, { useState, useEffect } from 'react';
import axios from './AxiosConfig';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import "./styles/login.css";
import 'bootstrap/dist/css/bootstrap.min.css';
import RedirectForm from './RedirectForm';
import styles from './styles/otpbackup.module.css';
import Timer from './Timer';
import OtpInput from './OtpInput';

const VerifyBackupForm = () => {
    const [otp, setOtp] = useState(''); // Gestito come stringa concatenata
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');
    const [redirectData, setRedirectData] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const csrfToken = Cookies.get('csrftoken');
        if (csrfToken) {
            axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
            console.log("CSRF Token impostato:", csrfToken);
        } else {
            console.error("CSRF Token non trovato nei cookie");
        }
    }, []);

    const handleRequestNewOtp = async () => {
        try {
            console.log("Richiesta per un nuovo OTP inviata.");
            const response = await axios.get('/auth/send_otp_and_redirect/');
            if (response.data.status === 'success') {
                setMessage('Un nuovo codice OTP è stato inviato alla tua email.');
            } else {
                setError('Errore durante l\'invio del nuovo codice OTP.');
            }
        } catch (error) {
            console.error("Errore durante la richiesta del nuovo OTP:", error);
            setError('Errore durante l\'invio del nuovo codice OTP.');
        }
    };

    const handleVerifyOtp = async (event) => {
        event.preventDefault();
        if (otp.length < 6) {
            setError('Inserisci un codice OTP completo.');
            return;
        }
        console.log("OTP da inviare:", otp);

        try {
            const response = await axios.post('http://172.23.149.57:8000/auth/verify_backup_otp/', { otp });
            console.log("Risposta dal server:", response.data);
            if (response.data.status === 'success') {
                const url_asp = 'https://crm.adncallcenter.net/training/defaultnew.asp';
                if (response.data.redirect === url_asp) {
                    setRedirectData({
                        url: response.data.redirect,
                        session_token: response.data.session_token,
                        user: response.data.user,
                        password: response.data.password,
                    });
                } else {
                    navigate('/dashboard');
                }
            } else {
                setError('OTP non valido o scaduto.');
            }
        } catch (error) {
            console.error("Errore durante la verifica dell'OTP:", error);
            setError('Errore durante la verifica dell\'OTP.');
        }
    };

    const handleOtpChange = (value) => {
        
        console.log("Codice OTP concatenato:", value);
        setOtp(value); // Salva il valore concatenato
    };

    return (
        <div className={`col-4 ${styles.lato_form}`}>
        <Timer/>
            <div className={`p-4 border rounded ${styles.containerloginform}`}>
                <div className={`p-4 border rounded ${styles.containerTesto}`}>
                    <h3>Verifica Backup</h3>
                </div>
                <div className={styles.messaggioErrore}>
                    {error && <div className="alert alert-danger">{error}</div>}
                    {message && <div className="alert alert-success">{message}</div>}
                </div>
                <div className={styles.login_form}>
                    <form onSubmit={handleVerifyOtp}>
                        <label htmlFor="otpCode">Inserisci l'OTP ricevuto tramite email:</label>
                        <OtpInput length={6} onOtpChange={handleOtpChange} />
                        <button type="submit" className={`btn btn-primary ${styles.btnVerify}`}>Verifica</button>
                    </form>
                </div>
                <div className={`text-center mt-3 ${styles.backup_Option}`}>
                    <p>Il tuo codice OTP è scaduto o hai problemi a riceverlo?</p>
                    <button onClick={handleRequestNewOtp} className={`btn btn-link ${styles.btnLink}`}>
                        Invia un nuovo codice OTP
                    </button>
                </div>
                {redirectData && <RedirectForm {...redirectData} />}
            </div>
        </div>
    );
};

export default VerifyBackupForm;
