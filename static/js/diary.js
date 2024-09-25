    let maxwords = 1000;
    let maxchar = maxwords * 5;
    let deleting = false;


    async function novaPagina(){
    url = window.location.href;
    hash = url.split("/")[4];
    nextpage = await fetch("/api/newpage", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({"hash": hash})
    });
    data = await nextpage.json();
    if (data.status){
        window.location = `/diario/${hash}/${data.page}`;
        }
    }

        async function deletePage(){
        let confirm = window.confirm('Tem certeza que deseja deletar esta página?');
        if (!confirm){
            return;
        }
        hash = window.location.href.split("/")[4];
        page = window.location.href.split("/")[5];
        let data = {
        "hash": hash,
        "page": page
        }
        let response = await fetch('/api/deletepage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        data = await response.json();
        if (data.status){
        let prevpage = data.prevurl;
        window.location = prevpage;

        }
    }


    function wordObserver(){
        let trix = document.querySelector("trix-editor");
        let words = trix.editor.getDocument().toString().split(" ").length;
        let wordcounter = document.getElementById("wordcount");
        wordcounter.innerHTML = words;
    }

    function letterObserver() {
        let trix = document.querySelector("trix-editor");
        let letters = trix.editor.getDocument().toString().replace(/\s/g, '').length;
        let lettercounter = document.getElementById("lettercount");
        lettercounter.innerHTML = letters;
    }

    function charLeftObserver() {
        let trix = document.querySelector("trix-editor");
        let letters = trix.editor.getDocument().toString().replace(/\s/g, '').length;
        let charleft = document.getElementById("charleft");
        charleft.innerHTML = maxchar - letters;
        return charleft;
    }

    function wordLeftObserver() {
        let trix = document.querySelector("trix-editor");
        let words = trix.editor.getDocument().toString().split(" ").length - 1;
        let wordleft = document.getElementById("wordleft");
        wordleft.innerHTML = maxwords - words;
        return wordleft;
    }

    window.onload = function(){
        let trix = document.querySelector("trix-editor");
        trix.addEventListener("trix-change", wordObserver);
        trix.addEventListener("trix-change", letterObserver);
        trix.addEventListener("trix-change", charLeftObserver);
        trix.addEventListener("trix-change", wordLeftObserver);
        loadDiario();
    }

    function deleteUseless(){
    let toolbar = document.querySelector(".trix-button-row");
    uselessparents = ["trix-button-group trix-button-group--block-tools","trix-button-group-spacer"]
    uselesschildrens = ["trix-button trix-button--icon trix-button--icon-link","trix-button trix-button--icon trix-button--icon-undo","trix-button trix-button--icon trix-button--icon-redo"]
    toolbar.childNodes.forEach((node) => {
        if (uselessparents.includes(node.className)){
            node.remove();
        }

        if (node.classList){
            node.style.margin = "0px";
        }
        let children = node.childNodes;
        for (let i = 0; i < children.length; i++){
            if (uselesschildrens.includes(children[i].className)){
                children[i].remove();
            }
        }
    });
    }

    function centralizeToolbar(){
        let toolbar = document.querySelector(".trix-button-row");
        toolbar.style.justifyContent = "center";
        toolbar.style.padding = "0px";
        toolbar.style.textAlign = "center";
    }

    function changeTextSize(){
        let trix = document.querySelector("trix-editor");
        trix.style.fontSize = "1.1em";
        trix.style.height = "auto";
    }

    function changeToolbar(){
        deleteUseless();
        centralizeToolbar();
    }

    document.addEventListener("trix-initialize", function(){
        changeToolbar();
})





async function salvarPagina(){
    let trix = document.querySelector("trix-editor");
    let innerstring = trix.editor.getDocument().toString();
    let innerhtml = trix.innerHTML;
    let url = window.location.href;
    let diariohash = url.split("/")[4];
    let pagina = url.split("/")[5];
    data = {
        "content": innerstring,
        "html": innerhtml,
        "hash": diariohash,
        "pagina": pagina
    }

    response = await fetch("/api/salvar", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });
}

async function loadDiario(){
    let url = window.location.href;
    let diariohash = url.split("/")[4];
    let pagina = url.split("/")[5];
    data = {
        "hash": diariohash,
        "pagina": pagina
    }
    let response = await fetch("/api/getwriting", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });
    data = await response.json();
    html = data.data.html
    let trix = document.querySelector("trix-editor");
    trix.innerHTML = html;
}

async function saveFile(file, hash) {
    let formData = new FormData();
    formData.append("file", file);
    formData.append("hash", hash);

    let response = await fetch("/api/savefiles", {
        method: "POST",
        body: formData
    });

    data = await response.json();
}


async function deleteFile(filename, hash){
    let data = {
        "filename": filename,
        "hash": hash,
    }

    let response = await fetch("/api/deletefile", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    data = await response.json();
}

document.addEventListener("trix-change", function() {
    if (!deleting) {
        let wordsLeftElement = wordLeftObserver();
        let charsLeftElement = charLeftObserver();
        let wordsLeft = parseInt(wordsLeftElement.innerHTML);
        let charsLeft = parseInt(charsLeftElement.innerHTML);

        let error = false

        let trix = document.querySelector("trix-editor");
        let trixContent = trix.editor.getDocument().toString().trim();
        let errodiv = document.getElementById("error");

        if (wordsLeft <= 0) {
            let words = trixContent.split(/\s+/);
            let currentWordCount = words.length;
            let errostring = "Você atingiu o limite de palavras. O texto foi truncado.";
            errodiv.innerHTML = errostring;
            if (currentWordCount > maxwords) {
                let truncatedWords = words.slice(0, maxwords);
                trix.editor.loadHTML(truncatedWords.join(" "));
            }

            error = true;
        }

        if (charsLeft <= 0) {
            let currentCharCount = trixContent.replace(/\s+/g, '').length;
            let errostring = "Você atingiu o limite de caracteres. O texto foi truncado.";
            errodiv.innerHTML = errostring;
            if (currentCharCount > maxchar) {
                let truncatedChars = trixContent.replace(/\s+/g, '').slice(0, maxchar);
                trix.editor.loadHTML(truncatedChars);
            }
            error = true;
        }

        if (!error) {
            errodiv.innerHTML = "";
        }
    }
});


document.addEventListener("trix-file-accept", function(){
    let file = event.file;
    let hash = window.location.href.split("/")[4];
    let pagina = window.location.href.split("/")[5];
    saveFile(file, hash);
})


document.addEventListener("trix-attachment-add", function(event) {
    let hash = window.location.href.split("/")[4];
    let pagina = window.location.href.split("/")[5];
    let fullurl = `/static/nosql/files/${hash}/${event.attachment.attachment.attributes.values.filename}`;

    event.attachment.setAttributes({
        url: fullurl
    });
});


document.addEventListener("trix-attachment-remove", function(){
    let attachment = event.attachment;
    let hash = window.location.href.split("/")[4];
    let pagina = window.location.href.split("/")[5];
    deleteFile(attachment.attachment.attributes.values.filename, hash);
})


