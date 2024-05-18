document.addEventListener("DOMContentLoaded", function() {
    // Obtener todos los botones para mostrar/ocultar comentarios
    var toggleButtons = document.querySelectorAll('.toggle-comments');

    toggleButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Encontrar la sección de comentarios más cercana al botón clicado
            var commentsSection = this.nextElementSibling;

            // Alternar la visibilidad de la sección de comentarios
            if (commentsSection.style.display === 'none' || commentsSection.style.display === '') {
                commentsSection.style.display = 'block';
            } else {
                commentsSection.style.display = 'none';
            }
        });
    });

    const modal = document.getElementById("modal");
    const modalContent = document.getElementById("modal-body");
    const closeButton = document.querySelector(".close-button");

    document.querySelectorAll('.enlarge-button').forEach(button => {
        button.addEventListener('click', function() {
            const publicacionId = this.closest('.enlarge-form').querySelector('input[name="publicacion_id"]').value;
            fetch('/agrandar-publicacion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `publicacion_id=${publicacionId}`
            })
            .then(response => response.text())
            .then(data => {
                modalContent.innerHTML = data;
                modal.style.display = "block";
            })
            .catch(error => console.error('Error al obtener la publicación:', error));
        });
    });

    closeButton.addEventListener('click', () => {
        modal.style.display = "none";
    });

    window.addEventListener('click', (event) => {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    });

});



