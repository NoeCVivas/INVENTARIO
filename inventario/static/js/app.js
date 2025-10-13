// Mensaje de confirmación para eliminar
document.addEventListener("DOMContentLoaded", function () {
    const deleteButtons = document.querySelectorAll(".btn-delete");

    deleteButtons.forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            if (!confirm("¿Estás segura de que querés eliminar este registro?")) {
                e.preventDefault();
            }
        });
    });
});
