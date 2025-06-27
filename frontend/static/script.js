// let e const = variaveis 

let video;
let resultado;

//camera web do reconhecimento facial
function startCameraRecognition() {
  video = document.getElementById('video');
  resultado = document.getElementById('resultado');

  //ativação do botão do reconhecimento facial que fica no html
  navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
    .then(stream => {
      video.srcObject = stream;
      video.play();
      recognizeLoop();
      const buttons = document.querySelectorAll('button');
      buttons.forEach(btn => btn.style.display = 'none');
    })
};


//captura cada frame do video e das imagens e compara para um resultado mais eficas
function captureFrame() {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 100, 100, canvas.width, canvas.height);
  return canvas.toDataURL('image/jpeg');
}


//deixa o reconhecimento rodando em loop
function recognizeLoop() {
  const imageData = captureFrame();

  //busca a função de ativação do reconhecimento facial que está no app.py
  fetch('/reconhecer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ image: imageData })
  })
  .then(response => response.json())
  .then(data => {
    if (data.length === 0) {
      resultado.textContent = 'Nenhum rosto detectado.';
    } else {
      resultado.textContent = data.map(r => `${r.nome} (${(r.probabilidade * 100).toFixed(0)}%)`).join(', ');
    }
  });

  setTimeout(recognizeLoop, 2000);
}
