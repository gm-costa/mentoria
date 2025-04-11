const modal = document.querySelector('.relative.z-10');
const btnCancelar = document.getElementById('modalBtnCancelar');
const btnAcessar = document.getElementById('modalBtnAcessar');
const msgRetorno = document.getElementById('mensagem_retorno');

btnCancelar.addEventListener('click', (e) => {
    e.preventDefault();
    closeModal();
    window.location.href = '/mentorados/home/';
});

btnAcessar.addEventListener('click', (e) => {
    csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value;
    token = document.getElementById('token').value;
    fetch("/mentorados/autenticar/", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            'X-CSRFToken': csrf_token,
        },
        body: JSON.stringify({token: token})
        
    }).then(function(result){
        return result.json()
    }).then(function(data){
        msgRetorno.innerHTML = data.mensagem;
        if(data.status == 0){
            closeModal();
            document.location.reload(true);
            // setCookie('auth_token', token, 3600);
            setCookie('auth_token', token, 10*60);
        } else {
            msgRetorno.parentElement.classList.remove('hidden');
        }
    })
});

function closeModal() {
    modal.classList.add('ease-in', 'duration-200');
    modal.classList.add('hidden');
}

function setCookie(name, value, seconds) {
    const d = new Date();
  
    d.setSeconds(d.getSeconds() + seconds);

    const expires = "expires=" + d.toUTCString();
    const cookie = name + "=" + value + ";" + expires + ";path=/";

    document.cookie = cookie;
}

