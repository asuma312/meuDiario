let currentElement = null;
let currentHash = null;

function editName(element, diaryhash) {
    currentElement = element;
    currentHash = diaryhash;

    document.getElementById('popup-input').value = element.innerText;

    document.getElementById('overlay').style.display = 'block';
    document.getElementById('popup').style.display = 'block';
}

async function saveName() {
    let newname = document.getElementById('popup-input').value;

    let data = {
        "title": newname,
        "hash": currentHash
    };

    let response = await fetch('/api/changewriting', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    data = await response.json();

    if (data.status) {
        currentElement.innerText = newname;

        currentElement.onclick = function() {
            editName(this, currentHash);
        }

        closePopupNoEl();
    }
}

function closePopupNoEl() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('popup').style.display = 'none';
}



 async function deleteDiario(diaryhash){
        let confirm = window.confirm('Tem certeza que deseja deletar este diário?');
        if (!confirm){
            return;
        }
        let data = {
        "hash": diaryhash
        }
        let response = await fetch('/api/deletewriting', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        data = await response.json();
        if (data.status){
            window.location.reload();
        }
    }




    async function newDiarioPopUp(){
        let diario = await fetch("/backend/popups/newdiariopopup");
        let data = await diario.json();
        let html = data.html;

        let overlay = document.createElement('div');
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.background = 'rgba(0, 0, 0, 0.5)';
        overlay.style.display = 'flex';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.zIndex = '1000';

        let popup = document.createElement('div');
        popup.style.backgroundColor = 'white';
        popup.style.padding = '20px';
        popup.style.borderRadius = '10px';
        popup.style.boxShadow = '0px 0px 15px rgba(0, 0, 0, 0.3)';
        popup.style.width = '400px';
        popup.style.position = 'relative';

        popup.innerHTML = html;

        let closeButton = document.createElement('button');
        closeButton.innerText = 'X';
        closeButton.style.position = 'absolute';
        closeButton.style.top = '10px';
        closeButton.style.right = '10px';
        closeButton.style.backgroundColor = 'red';
        closeButton.style.color = 'white';
        closeButton.style.border = 'none';
        closeButton.style.padding = '5px 10px';
        closeButton.style.cursor = 'pointer';
        closeButton.onclick = function() {
            document.body.removeChild(overlay);
        };

        popup.appendChild(closeButton);

        overlay.appendChild(popup);

        document.body.appendChild(overlay);
    }

    async function createDiario(){
        let title = document.getElementById('title').value;
        let response = await fetch('/api/createwriting', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({title})
        });
        let data = await response.json();
        if (data.status){
            window.location = `${data.url}`;
        }
    }

    function closePopup(element){
        element.parentElement.remove();
    }



async function editCapa(element, hash) {
    let fileinput = document.createElement('input');
    fileinput.type = 'file';
    fileinput.accept = 'image/*';
    fileinput.click();

    fileinput.onchange = async function() {
        let file = fileinput.files[0];
        let tempUrl = URL.createObjectURL(file);
        element.src = tempUrl;

        let formData = new FormData();
        formData.append('capa', file);
        formData.append('hash', hash);

        let response = await fetch('/api/changecapa', {
            method: 'POST',
            body: formData
        });

        let data = await response.json();
        element.src = blobToUrl(data.capa);
    };
}

function blobToUrl(blob) {
    return URL.createObjectURL(blob);
}