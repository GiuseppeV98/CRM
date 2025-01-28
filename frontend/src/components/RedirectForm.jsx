import React, { useEffect } from 'react';

const RedirectForm = ({ url, session_token, user, password }) => {
  useEffect(() => {
    console.log("Eseguo il reindirizzamento con i seguenti dati:", { url, session_token, user, password });

    // Crea un modulo e invialo per reindirizzare con dati POST
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;

    const tokenInput = document.createElement('input');
    tokenInput.type = 'hidden';
    tokenInput.name = 'session_token';
    tokenInput.value = session_token;
    form.appendChild(tokenInput);

    const userInput = document.createElement('input');
    userInput.type = 'hidden';
    userInput.name = 'user';
    userInput.value = user;
    form.appendChild(userInput);

    const ppwInput = document.createElement('input');
    ppwInput.type = 'hidden';
    ppwInput.name = 'password';
    ppwInput.value = password;
    form.appendChild(ppwInput);
    document.body.appendChild(form);
    form.submit();
  }, [url, session_token, user, password]);

  return null;
};

export default RedirectForm;
