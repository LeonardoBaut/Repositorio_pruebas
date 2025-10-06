let map, marker;
let userSelectedTime = false;

const customIcon = L.icon({
  iconUrl: 'https://static.vecteezy.com/system/resources/previews/011/629/817/original/realistic-red-pushpin-png.png',
  iconSize: [38, 38],
  iconAnchor: [19, 38],
  popupAnchor: [0, -38]
});

function updateTimeCard(timeStr) {
    const timeCard = document.getElementById('time');
    if (!timeStr) return;

    const [hour, minute] = timeStr.split(':');
    let h = parseInt(hour);
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12 || 12;
    timeCard.textContent = `${h}:${minute} ${ampm}`;
}

function startSystemClock() {
    if (!userSelectedTime) {
        const now = new Date();
        const hours = now.getHours();
        const minutes = now.getMinutes();
        const timeStr = `${hours.toString().padStart(2,'0')}:${minutes.toString().padStart(2,'0')}`;
        updateTimeCard(timeStr);
    }
    setTimeout(startSystemClock, 1000 * 60); // se actualiza cada minuto
}

// Inicializar mapa al cargar
document.addEventListener("DOMContentLoaded", () => {
  startSystemClock(); 
  map = L.map('map').setView([20.0, -90.0], 5);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  map.on('click', function (e) {
    const lat = parseFloat(e.latlng.lat.toFixed(5));
    const lon = parseFloat(e.latlng.lng.toFixed(5));
    document.getElementById('latInput').value = lat;
    document.getElementById('lonInput').value = lon;

    if (marker) {
      marker.setLatLng(e.latlng);
    } else {
      marker = L.marker(e.latlng, { icon: customIcon }).addTo(map);
    }
  });
});

// Simulación de consulta de datos históricos
function consultarAPI(lat, lon) {
  const startDate = document.getElementById('startDate').value;
  const endDate = document.getElementById('endDate').value;
  if (!startDate || !endDate) {
    alert("Select a valid date range");
    return;
  }

  // Datos simulados
  const temp = (Math.random() * 35).toFixed(1);
  const pressure = (1000 + Math.random() * 30).toFixed(1);
  const wind = (Math.random() * 50).toFixed(1);

  if (!userSelectedTime) {
      startSystemClock(); // mantener hora automática si no hay selección del usuario
  }

  document.getElementById('temperature').innerText = `${temp}°C`;
  document.getElementById('pressure').innerText = `${pressure} hPa`;
  document.getElementById('windspeed').innerText = `${wind} km/h`;
}

// Predicción simulada
function predecir() {
  const lat = parseFloat(document.getElementById('latInput').value);
  const lon = parseFloat(document.getElementById('lonInput').value);
  const futureDate = document.getElementById('futureDate').value;

  if (isNaN(lat) || isNaN(lon) || !futureDate) {
    alert("Fill in all fields");
    return;
  }

  userSelectedTime = true;

  const temp = (Math.random() * 35).toFixed(1);
  const pressure = (1000 + Math.random() * 30).toFixed(1);
  const wind = (Math.random() * 50).toFixed(1);

  document.getElementById('temperature').innerText = `${temp}°C`;
  document.getElementById('pressure').innerText = `${pressure} hPa`;
  document.getElementById('windspeed').innerText = `${wind} km/h`;
}

// Botones
document.getElementById('btnConsultar').addEventListener('click', () => {
  const lat = parseFloat(document.getElementById('latInput').value);
  const lon = parseFloat(document.getElementById('lonInput').value);
  if (isNaN(lat) || isNaN(lon)) {
    alert("Enter valid coordinates");
    return;
  }

  if (marker && map) {
    marker.setLatLng([lat, lon]);
    map.setView([lat, lon], 8);
  }
  consultarAPI(lat, lon);
});

document.getElementById('btnPredict').addEventListener('click', () => {
  predecir();
});

document.getElementById('futureTime').addEventListener('change', function() {
    userSelectedTime = true; // usuario ha seleccionado hora
    updateTimeCard(this.value);
});

  // Función para generar el PDF con los datos de los contenedores
function function_Download_file() {
    // Usando jsPDF para crear el documento PDF
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  
    // Agregar título
  doc.setFontSize(18);
  doc.text('Climate Data', 14, 10);
  
    // Agregar información de los datos
  doc.setFontSize(12);
    
    // Obtener los datos de los contenedores
  const temperature = document.getElementById('temperature').innerText;
  const pressure = document.getElementById('pressure').innerText;
  const windspeed = document.getElementById('windspeed').innerText;
  const time = document.getElementById('time').innerText;
  
    // Obtener la latitud y longitud
  const lat = document.getElementById('latInput').value;
  const lon = document.getElementById('lonInput').value;
  
      // Obtener las fechas de inicio y fin
  const startDate = document.getElementById('startDate').value;
  const endDate = document.getElementById('endDate').value;
  
      // Obtener la fecha y hora futura de predicción
  const futureDate = document.getElementById('futureDate').value;
  const futureTime = document.getElementById('futureTime').value;
  
  let yPosition = 20;
  function addTextWithLineBreak(text) {
    doc.text(text, 14, yPosition);
    yPosition += 10; // Incrementamos la posición Y para el siguiente texto (esto genera el salto de línea)
  }
  
      // Agregar texto al PDF
  doc.text(`Latitude: ${lat}`, 14, 20);
  doc.text(`Length: ${lon}`, 14, 30);
  doc.text(`Start Date: ${startDate}`, 14, 40);
  doc.text(`End Date: ${endDate}`, 14, 50);
  doc.text(`Future Date & Hour Date: ${futureDate} ${futureTime}`, 14, 60);
  doc.text(`Temperature: ${temperature}`, 14, 70);
  doc.text(`Pressure: ${pressure}`, 14, 80);
  doc.text(`Windspeed: ${windspeed}`, 14, 90);
  doc.text(`Hour: ${time}`, 14, 100);
  
  
    // Si hay imágenes, se pueden agregar también (por ejemplo, de las gráficas)
  // const imgTemp = document.querySelector('img[src="imagenes/temp_media.png"]');
  // if (imgTemp) {
  //     const imgData = imgTemp.src;
  //     doc.addImage(imgData, 'JPEG', 14, yPosition, 180, 100); // Ajusta las coordenadas y tamaño
  //     yPosition += 130;
  // }
  
    // Guardar el PDF con un nombre específico
  doc.save('climatic data.pdf');
}
  
  // Añadir el evento al botón de descarga
document.getElementById('btnDownload').addEventListener('click', function_Download_file);
  
// --- NUEVO: Mostrar/Ocultar mapa y expandir tarjetas ---
const btnShowMap = document.getElementById("btnShowMap");
const mapContainer = document.querySelector(".map-container");
const results = document.querySelector(".results");

let mapaVisible = true;

btnShowMap.addEventListener("click", () => {
  mapaVisible = !mapaVisible;

  if (mapaVisible) {
    mapContainer.classList.remove("map-hidden");
    results.classList.remove("full-width");
    btnShowMap.textContent = "Hide Map";
    setTimeout(() => map.invalidateSize(), 450); // recalcula tamaño Leaflet
  } else {
    mapContainer.classList.add("map-hidden");
    results.classList.add("full-width");
    btnShowMap.textContent = "Show Map";

    setTimeout(() => {
      map.invalidateSize({ animate: true });
    }, 450);
  }
});


async function consultarElementos() {
  // Obtener valores desde los inputs del usuario
  const lat = document.getElementById("latInput").value;
  const lon = document.getElementById("lonInput").value;
  const fecha_inicio = document.getElementById("startDate").value;
  const fecha_fin = document.getElementById("endDate").value;

  // Validación rápida
  if (!lat || !lon || !fecha_inicio || !fecha_fin) {
    alert("⚠️ Please complete all fields before continuing.");
    return;
  }
  const url = `http://localhost:8040/calcular_elementos?lat=${lat}&lon=${lon}&fecha_inicio=${fecha_inicio}&fecha_fin=${fecha_fin}`;
  try {
    // Llamar al endpoint FastAPI
    const respuesta = await fetch(url);

    if (!respuesta.ok) {
      throw new Error(`API error: ${respuesta.status}`);
    }

    // Convertir respuesta en JSON (si el endpoint devuelve datos)
    const data = await respuesta.json();
    console.log("✅ Data received:", data);

    // Mostrar en consola o actualizar la página
    alert("✅Calculation completed. Check the updated images on the page.");

    // Opcional: actualizar las imágenes sin recargar toda la página
    actualizarGraficas();

  } catch (error) {
    console.error("❌ Error querying the API:", error);
    alert("Error getting data: " + error.message);
  }
}

// 🔄 Esta función recarga las imágenes sin recargar la página completa
function actualizarGraficas() {
  const timestamp = new Date().getTime(); // Evita caché
  document.querySelector('img[src*="temp_media.png"]').src = `imagenes/temp_media.png?t=${timestamp}`;
  document.querySelector('img[src*="presion_media.png"]').src = `imagenes/presion_media.png?t=${timestamp}`;
  document.querySelector('img[src*="viento_u10m.png"]').src = `imagenes/viento_u10m.png?t=${timestamp}`;
}