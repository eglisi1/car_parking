document.addEventListener("DOMContentLoaded", function () {
    init();
});

function init() {
    let video = document.getElementById('webcam');

    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                video.srcObject = stream;
            })
            .catch(function (err) {
                console.error("Oops! Something went wrong with the webcam: " + err);
            });
    } else {
        console.error("getUserMedia is not supported in this browser.");
    }
}


function captureImage() {
    const video = document.getElementById('webcam');
    let canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    let ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    sendPredictRequest(canvas.toDataURL('image/png').split(',')[1]);
}

async function sendPredictRequest(photoBase64) {
    const apiURL = 'http://127.0.0.1:8000';
    try {
        const fetchResponse = await fetch(apiURL + '/predict', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ photo_base64: photoBase64 })
        });
        if (fetchResponse.ok) {
            const data = await fetchResponse.json();
            console.log('Prediction response:', data);

            // Update the page with the prediction response
            displayPrediction(data);
        } else {
            console.error('Error in prediction:', await fetchResponse.text());
        }
    } catch (error) {
        console.error('Error sending predict request:', error);
    }
}

function displayPrediction(data) {
    const photo = document.getElementById('photo');
    const advice = document.getElementById('advice');

    photo.src = 'data:image/png;base64,' + data.photo_base64;
    advice.textContent = data.instructions;
}