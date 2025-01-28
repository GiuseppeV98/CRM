import React, { useState, useEffect } from 'react';
import axios from './AxiosConfig';
import Cookies from 'js-cookie';
import RedirectForm from './RedirectForm';
import { useNavigate } from 'react-router-dom';
import styles from './styles/Otpform.module.css';
import Timer from './Timer';
import OtpInput from './OtpInput';

const VerifyOtpForm = ({ onNextStep }) => {
    const [otp, setOtp] = useState(''); // OTP concatenato come stringa
    const [error, setError] = useState('');
    const [redirectData, setRedirectData] = useState(null);
    const navigate = useNavigate();
    const [limit, setLimit] = useState(0);

    useEffect(() => {
        const csrfToken = Cookies.get('csrftoken');
        axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
        console.log("Token CSRF impostato:", csrfToken);
    }, []);
    const handleVerifyOtp = async () => {
        if (otp.length < 6) {
            setError("Inserisci un codice OTP completo.");
            return;
        }
        try {
            const response = await axios.post(
                'http://172.23.149.57:8000/auth/verify_otp/',
                { otp_code: otp },
                { headers: { 'Content-Type': 'application/json' } }
            );
            console.log("Risposta del server:", response);
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
                    navigate(response.data.redirect);
                }
            } else {
                console.log("Errore dal server, OTP non valido.");
                setError('OTP non valido.');
            }
        } catch (error) {
            console.error("Errore durante la verifica dell'OTP:", error);
            setError("Errore durante la verifica dell'OTP.");
        }
    };
    const handleOtpChange = (value) => {
        console.log("Codice OTP concatenato:", value);
        setOtp(value);
    };
    const handleNavigateToBackup = async () => {
        
        if (limit === 0) {
            setLimit(1);
            try {
                const response = await axios.post('http://172.23.149.57:8000/auth/get_user_email/');
                console.log("Risposta email presente:", response.data);
                if (response.data.email_presente) {
                    await axios.get('/auth/send_otp_and_redirect/');
                    onNextStep('verify_backup');
                } else {
                    setError("Non hai un'email registrata.");
                }
            } catch (error) {
                console.error("Errore durante l'invio dell'OTP:", error);
                setError("Errore durante l'invio dell'OTP.");
            }
            setLimit(0);
        }
    };
    const handleSubmit = (event) => {
        event.preventDefault();
        handleVerifyOtp();
    };
    return (
        <div className={`col-4 ${styles.lato_form}`}>
            <Timer />
            <div className={`p-4 border rounded ${styles.containerloginform}`}>
                <div className={`p-4 border rounded ${styles.containerTesto}`}>
                    <h3 className="mb-4">Verifica OTP</h3>
                </div>
                <div className={styles.messaggioErrore}>
                    {error && <div className="alert alert-danger">{error}</div>}
                </div>
                <div className={styles.login_form}>
                    <form onSubmit={handleSubmit}>
                        <label htmlFor="otpCode">Inserisci il codice OTP dall'app Authenticator:</label>
                        {/* Utilizzo del componente figlio per l'OTP */}
                        <OtpInput length={6} onOtpChange={handleOtpChange} />
                        <button type="submit" className={`btn btn-primary ${styles.btnVerify}`}>Verifica</button>
                    </form>
                </div>
                <div className={`text-center mt-3 ${styles.backup_Option}`}>
                    <h6>Non hai con te il cellulare?</h6>
                    <h6>Accedi tramite Email</h6>
                    <button onClick={handleNavigateToBackup} className={`btn btn-link ${styles.btnLink}`}>
                        Usa il Codice di Backup
                    </button>
                </div>
                {redirectData && <RedirectForm {...redirectData} />}
            </div>
        </div>
    );
};

export default VerifyOtpForm;
