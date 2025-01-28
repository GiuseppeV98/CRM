import React, { useEffect, useState } from 'react';

const Timer = () => {
    const [totalSeconds, setTotalSeconds] = useState(15); // Impostato a 10 secondi
    const [isTimerRunning, setIsTimerRunning] = useState(true);

    useEffect(() => {
        let timerInterval;

        const updateTimer = () => {
            if (isTimerRunning) {
                setTotalSeconds((prevSeconds) => {
                    if (prevSeconds <= 0) {
                        clearInterval(timerInterval);
                        window.location.href = "http://logintest.adncallcenter.net/auth/logout";
                        return prevSeconds;
                    }
                    return prevSeconds - 1;
                });
            }
        };

        if (isTimerRunning) {
            timerInterval = setInterval(updateTimer, 1000);
        }

        return () => clearInterval(timerInterval);
    }, [isTimerRunning]);

    const formattedTime = totalSeconds < 10 ? `00:0${totalSeconds}` : `00:${totalSeconds}`;

    return (
        <div id="timer" style={styles.timer}>
            {formattedTime}
        </div>
    );
};

const styles = {
    timer: {
        position: 'absolute',
        right: '20px',
        top: '20px',
        fontSize: '24px',
        padding: '10px',
        backgroundColor: '#f0f0f0',
        border: '2px solid #000',
        borderRadius: '15px',
    },
};

export default Timer;
