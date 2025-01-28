import React, { useState } from 'react';
import styles from './styles/otpInput.module.css';

const OtpInput = ({ length = 6,  onOtpChange}) => {
    const [otp, setOtp] = useState(Array(length).fill(''));

    const handlePaste = (e, index) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text').replace(/\D/g, ''); // Filtra solo i numeri
        if (pastedData) {
            const newOtp = [...otp];
            for (let i = 0; i < pastedData.length && index + i < length; i++) {
                newOtp[index + i] = pastedData[i];
            }
            setOtp(newOtp);
            onOtpChange(newOtp.join(''));
        }
    };

    const handleChange = (e, index) => {
        const { value } = e.target;
        const inputs = document.querySelectorAll(`.${styles.otpInput}`);
        if (/^[0-9]{1,2}$/.test(value)) {
            const newOtp = [...otp];
            newOtp[index] = value.slice(-1); // Prendi solo l'ultimo valore
            setOtp(newOtp);
            onOtpChange(newOtp.join(''));

            // Sposta il focus solo se l'input non è vuoto
            if (value && index < length - 1) {
                const nextInput = inputs[index + 1];
                if (nextInput) {
                    nextInput.focus();
                    setTimeout(() => nextInput.setSelectionRange(nextInput.value.length, nextInput.value.length), 0);
                }
            }
        } else if (value === '') {
            const newOtp = [...otp];
            newOtp[index] = '';
            setOtp(newOtp);
            onOtpChange(newOtp.join('')); 
        }
    };
    const handleKeyDown = (e, index) => {
        const inputs = document.querySelectorAll(`.${styles.otpInput}`);
        if (e.key === 'Backspace' && otp[index] === '' && index > 0) {
            const prevInput = inputs[index - 1];
            if (prevInput) {
                prevInput.focus();
                setTimeout(() => prevInput.setSelectionRange(prevInput.value.length, prevInput.value.length), 0);
            }
        } else if (e.key === 'ArrowLeft' && index > 0) {
            const prevInput = inputs[index - 1];
            if (prevInput) {
                prevInput.focus();
                setTimeout(() => prevInput.setSelectionRange(prevInput.value.length, prevInput.value.length), 0);
            }
        } else if (e.key === 'ArrowRight' && index < inputs.length - 1) {
            const nextInput = inputs[index + 1];
            if (nextInput) {
                nextInput.focus();
                setTimeout(() => nextInput.setSelectionRange(nextInput.value.length, nextInput.value.length), 0);
            }
        }
    };

    return (
        <div className={styles.otpContainer}>
            <div className={styles.otpinputs}>
            {[...Array(length)].map((_, index) => (
                <input
                    key={index}
                    id={`otp-input-${index + 1}`}
                    type="text"
                    className={styles.otpInput}
                    maxLength="2"
                    value={otp[index]}
                    required
                    onChange={(e) => handleChange(e, index)}
                    onKeyDown={(e) => handleKeyDown(e, index)}
                    onPaste={(e) => handlePaste(e, index)}
                />
            ))}
        </div>
        </div>
    );
};

export default OtpInput;
