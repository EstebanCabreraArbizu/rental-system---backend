document.addEventListener('DOMContentLoaded', () => {
  // Manejar el envío del formulario de búsqueda
  const searchButton = document.querySelector('.search-button');
  searchButton.addEventListener('click', () => {
    const searchType = document.querySelector('.search-type').value;
    const searchQuery = document.querySelector('.search-input').value;
    console.log(`Buscando ${searchType}: ${searchQuery}`);
  });

  // Añadir efectos hover a las tarjetas
  const cards = document.querySelectorAll('.property-card, .vehicle-card');
  cards.forEach(card => {
    card.addEventListener('click', () => {
      console.log('Card clicked:', card.querySelector('h3').textContent);
    });
  });

  // Manejar la vista previa de imágenes
  const imageInput = document.getElementById('images');
  const imagePreview = document.getElementById('imagePreview');

  imageInput.addEventListener('change', function() {
    imagePreview.innerHTML = '';
    const files = Array.from(this.files);

    files.forEach(file => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        const imgContainer = document.createElement('div');
        imgContainer.style.width = '100px';
        imgContainer.style.height = '100px';
        imgContainer.style.overflow = 'hidden';
        imgContainer.style.borderRadius = '4px';

        const img = document.createElement('img');
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';

        reader.onload = e => {
          img.src = e.target.result;
        };

        reader.readAsDataURL(file);
        imgContainer.appendChild(img);
        imagePreview.appendChild(imgContainer);
      }
    });
  });

  // Manejar el envío del formulario
  const propertyForm = document.getElementById('propertyForm');
  propertyForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const formData = new FormData(propertyForm);
    const propertyData = {
      title: formData.get('title'),
      type: formData.get('type'),
      price: formData.get('price'),
      bedrooms: formData.get('bedrooms'),
      bathrooms: formData.get('bathrooms'),
      area: formData.get('area'),
      address: formData.get('address'),
      description: formData.get('description'),
      amenities: formData.getAll('amenities'),
      contact: formData.get('contact')
    };

    console.log('Datos de la propiedad:', propertyData);
    alert('Propiedad publicada con éxito!');
    propertyForm.reset();
    imagePreview.innerHTML = '';
  });
});