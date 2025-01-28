import React, { useState } from 'react';
import LoginForm from './LoginForm';
import GenerateQrCode from './GenerateQrCode';
import CompleteConfig from './CompleteConfig';
import VerifyOtpForm from './VerifyOtpForm';
import VerifyBackupForm from './VerifyBackupForm';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Helmet, HelmetProvider } from 'react-helmet-async';
const AuthFlow = () => {
  const [step, setStep] = useState('login'); // Lo stato determina quale form mostrare

  // Funzione per passare allo step successivo
  const handleNextStep = (nextStep) => {
    console.log("handleNextStep chiamato con:", nextStep);  
    setStep(nextStep);
  };

  const renderCurrentStep = () => {
    switch (step) {
      case 'login':
        return <LoginForm onNextStep={handleNextStep} />;
      case 'generate_qr':
        console.log("Passo onNextStep a GenerateQrCode");
        return <GenerateQrCode onNextStep={handleNextStep} />;
      case 'complete_config':  // Nuovo caso per la schermata di conferma
        return <CompleteConfig onNextStep={handleNextStep} />;
      case 'verify_otp':
        return<VerifyOtpForm onNextStep={handleNextStep} />;
      case 'verify_backup':
        return <VerifyBackupForm />;
      default:
        return <LoginForm onNextStep={handleNextStep} />;
    }
  };

  return (
    <HelmetProvider>
    <div className="container" id="container">
      <Helmet>
        <title>ADN Login</title>
        <meta name="description" content="Questa è la descrizione della pagina." />
        <meta name="keywords" content="react, helmet, meta tags" />
        <link rel="icon" href="/images/adn_Piccolo.png" />
      </Helmet>
      <div className="row justify-content-center" id="login">
        <div className="col-4" id="lato_logo">
          <div id="logo-container" className="text-center mb-4">
            <img src="/images/adn_Piccolo.gif" id="imglogin" alt="Cuffie" />
          </div>
        </div>
        {renderCurrentStep()}
      </div>
    </div>
  </HelmetProvider>
  );
};

export default AuthFlow;
