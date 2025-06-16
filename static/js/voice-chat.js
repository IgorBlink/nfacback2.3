class VoiceChat {
    constructor() {
        this.ws = null;
        this.mediaRecorder = null;
        this.audioStream = null;
        this.isRecording = false;
        this.isProcessing = false;
        this.isConnected = false;
        this.sessionId = null;
        
        this.initElements();
        this.connectWebSocket();
        this.setupEventListeners();
    }

    initElements() {
        this.statusElement = document.getElementById('status');
        this.micButton = document.getElementById('micButton');
        this.clearButton = document.getElementById('clearButton');
        this.conversation = document.getElementById('conversation');
        this.connectionInfo = document.getElementById('connectionInfo');
        this.audioPlayer = document.getElementById('audioPlayer');
        this.volumeBar = document.getElementById('volumeBar');
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.isConnected = true;
            this.updateStatus('waiting', '🎤 Нажмите микрофон чтобы начать говорить');
            this.updateConnectionInfo('Подключено');
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };

        this.ws.onclose = () => {
            this.isConnected = false;
            this.updateStatus('error', 'Соединение потеряно. Обновите страницу.');
            this.updateConnectionInfo('Отключено');
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('error', 'Ошибка соединения');
        };
    }

    setupEventListeners() {
        // Обработка клика по кнопке микрофона - toggle запись
        this.micButton.addEventListener('click', () => this.toggleRecording());
        
        // Очистка истории
        this.clearButton.addEventListener('click', () => this.clearConversation());

        // Обработка клавиатуры (пробел для toggle записи)
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.toggleRecording();
            }
        });
    }

    toggleRecording() {
        // Не позволяем начать запись если уже обрабатываем или говорит ИИ
        if (this.isProcessing) {
            // Визуально показываем что кнопка временно недоступна
            this.micButton.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.micButton.style.transform = 'scale(1)';
            }, 100);
            return;
        }
        
        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }

    async startRecording() {
        if (this.isRecording || !this.isConnected) return;

        try {
            // Получаем доступ к микрофону
            this.audioStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 16000
                }
            });

            // Настраиваем MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && this.ws.readyState === WebSocket.OPEN) {
                    this.sendAudioChunk(event.data);
                }
            };

            // Начинаем запись
            this.mediaRecorder.start(100); // Отправляем чанки каждые 100мс
            this.isRecording = true;
            
            this.updateStatus('listening', '🎤 Записываю... Нажмите кнопку еще раз чтобы остановить.');
            this.micButton.classList.remove('inactive');
            this.micButton.classList.add('active');
            this.micButton.innerHTML = '⏹️'; // Меняем иконку на стоп

            // Анализ звука для визуализации
            this.setupAudioAnalysis();

        } catch (error) {
            console.error('Ошибка доступа к микрофону:', error);
            this.updateStatus('error', 'Не удалось получить доступ к микрофону');
        }
    }

    stopRecording() {
        if (!this.isRecording) return;

        this.isRecording = false;
        
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }

        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
        }

        this.updateStatus('processing', 'Обрабатываю речь...');
        this.micButton.classList.remove('active');
        this.micButton.classList.add('inactive');
        this.micButton.innerHTML = '🎤'; // Возвращаем иконку микрофона
        this.isProcessing = true; // Блокируем новые записи

        // Сообщаем серверу о завершении записи
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'audio_end'
            }));
        }

        this.volumeBar.style.width = '0%';
    }

    setupAudioAnalysis() {
        if (!this.audioStream) return;

        const audioContext = new AudioContext();
        const analyser = audioContext.createAnalyser();
        const microphone = audioContext.createMediaStreamSource(this.audioStream);
        
        analyser.fftSize = 256;
        microphone.connect(analyser);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        
        const updateVolume = () => {
            if (!this.isRecording) return;
            
            analyser.getByteFrequencyData(dataArray);
            
            // Вычисляем средний уровень звука
            const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
            const volume = (average / 255) * 100;
            
            this.volumeBar.style.width = volume + '%';
            
            requestAnimationFrame(updateVolume);
        };
        
        updateVolume();
    }

    sendAudioChunk(audioBlob) {
        const reader = new FileReader();
        reader.onload = () => {
            const base64Audio = btoa(
                new Uint8Array(reader.result).reduce(
                    (data, byte) => data + String.fromCharCode(byte), 
                    ''
                )
            );
            
            this.ws.send(JSON.stringify({
                type: 'audio_chunk',
                data: base64Audio
            }));
        };
        reader.readAsArrayBuffer(audioBlob);
    }

    handleMessage(message) {
        switch (message.type) {
            case 'connection_established':
                this.sessionId = message.session_id;
                this.updateConnectionInfo(`Подключено (${this.sessionId})`);
                break;

            case 'speech_detected':
                this.updateStatus('listening', 'Обнаружена речь... Продолжайте говорить.');
                break;

            case 'transcription':
                this.addMessage('transcription', `Вы сказали: "${message.text}"`);
                break;

            case 'ai_response':
                this.addMessage('ai', message.text);
                this.updateStatus('speaking', 'ИИ отвечает...');
                break;

            case 'audio_response':
                this.playAudioResponse(message.data);
                break;

            case 'error':
                this.updateStatus('error', message.message);
                this.isProcessing = false; // Разблокируем после ошибки
                break;
        }
    }

    playAudioResponse(base64Audio) {
        try {
            const audioData = atob(base64Audio);
            const arrayBuffer = new ArrayBuffer(audioData.length);
            const view = new Uint8Array(arrayBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                view[i] = audioData.charCodeAt(i);
            }
            
            const blob = new Blob([arrayBuffer], { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(blob);
            
            this.audioPlayer.src = audioUrl;
            this.audioPlayer.play();
            
            this.audioPlayer.onended = () => {
                this.updateStatus('waiting', '🎤 Нажмите микрофон для следующего вопроса');
                this.isProcessing = false; // Разблокируем новые записи
                URL.revokeObjectURL(audioUrl);
            };
            
        } catch (error) {
            console.error('Ошибка воспроизведения аудио:', error);
            this.updateStatus('waiting', 'Готов к следующему вопросу');
        }
    }

    addMessage(type, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = text;
        
        this.conversation.appendChild(messageDiv);
        this.conversation.scrollTop = this.conversation.scrollHeight;
    }

    clearConversation() {
        this.conversation.innerHTML = `
            <div class="message ai">
                История очищена. Можете начать новый разговор!
            </div>
        `;
        
        // Очищаем историю на сервере (опционально)
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'clear_history'
            }));
        }
    }

    updateStatus(className, text) {
        this.statusElement.className = `status ${className}`;
        this.statusElement.textContent = text;
    }

    updateConnectionInfo(status) {
        this.connectionInfo.textContent = `Статус: ${status}`;
    }
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    new VoiceChat();
}); 