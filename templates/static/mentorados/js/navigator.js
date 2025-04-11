const btnOpenModal = document.getElementById('open_modal');
const modal = document.querySelector('.relative.z-10');
const btnCancelar = document.getElementById('modalBtnCancelar');
const btnClose = document.getElementById('modalBtnClose');
const btnSalvar = document.getElementById('modalBtnSalvar');

btnOpenModal.addEventListener('click', (e) => {
    e.preventDefault();
    modal.classList.add('ease-out', 'duration-300');
    modal.classList.remove('hidden');  
});

btnClose.addEventListener('click', () => {
    closeModal();
});

btnCancelar.addEventListener('click', () => {
    closeModal();
});

btnSalvar.addEventListener('click', () => {
    closeModal();
});

function closeModal() {
    modal.classList.add('ease-in', 'duration-200');
    modal.classList.add('hidden');
}
