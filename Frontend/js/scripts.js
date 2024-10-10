const json = ['json/nossa.json', 'json/10-09-2024.json', 'json/11-09-2024.json', 'json/12-09-2024.json', 'json/13-09-2024.json'];
const botao = document.querySelector("#button")
botao.addEventListener("click", (e)=>{
    executar(e);
})
document.addEventListener("keydown", (e)=>{
    if(e.key == "Enter"){
        executar(e);
    }
})
function executar(e){
    e.preventDefault();

    const orgaoInput = document.querySelector("#orgao");
    const assuntoInput = document.querySelector("#assunto");
    const orgao = orgaoInput ? orgaoInput.value.toLowerCase() : '';
    const assunto = assuntoInput ? assuntoInput.value.toLowerCase() : '';
    const datai = new Date(document.querySelector("#datai").value);
    const dataf = new Date(document.querySelector("#dataf").value);
    const nome = document.querySelector("#nome").value.toLowerCase();
    json.forEach(jsonFilePath => {
        fetch(jsonFilePath)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao carregar o arquivo JSON');
            }
            return response.json(); 
        })
        .then(arquivos => {
            const resultados = arquivos.filter(arquivo => {
                if (!orgao && !assunto && isNaN(datai) && isNaN(dataf) && !nome) {
                    return false;
                }
                const dataArquivo = new Date(arquivo.DATA.split('-').reverse().join('-'));
                const OrgaoIgual = !orgao || arquivo.NOME.toLowerCase().includes(orgao);
                const AssuntoIgual = !assunto || arquivo.assunto.toLowerCase().includes(assunto);
                const nomeIgual = !nome || arquivo.TEXTO.toLowerCase().includes(nome);
                const Data = (!isNaN(datai) && !isNaN(dataf))
                    ? (dataArquivo >= datai && dataArquivo <= dataf)//Aqui o ? funciona como um if as condições anteriores forem verdadeiras realiza o que tem dps dele, caso false aciona o : que é o else
                    : true;

                return OrgaoIgual && AssuntoIgual && Data && nomeIgual;
            });

            const resultadosDiv = document.querySelector('#resultados');
            resultadosDiv.innerHTML = ''; 
            if (resultados.length > 0) {
                resultados.forEach(resultado => {
                    const item = document.createElement('div');
                    item.innerHTML = `
                        <h3>Órgão:</h3><p>${resultado.NOME}</p>
                        <h3>Data:</h3><p>${resultado.DATA}</p>
                        <h3>Caderno:</h3><p>${resultado.CADERNO}</p>
                        <h3>Página:</h3><p>${resultado.PAGINA}</p>
                        <h3>Publicação:</h3><p>${resultado.PUBLICACAO}</p>
                        <h3>Texto:</h3><p>${resultado.TEXTO}</p>
                        <h3>Página:</h3><p>${resultado.PAGINA}</p>
                        <h3>Assunto:</h3><p>${resultado.assunto}</p>
                        <h3>Destaque:</h3><p>${resultado.DESTAQUE.join("<br>")}</p>
                        <br><br>`;
                    resultadosDiv.appendChild(item);
                });
            } else {
                resultadosDiv.innerHTML = '<p style="font-weight: 700">Nenhum arquivo encontrado</p>';
            }
        })
        .catch(error => {
            document.getElementById('resultados').innerHTML = 'Erro: ' + error;
        });
    })
};
botao.addEventListener("mouseover", () => {
    botao.style.boxShadow = "3px 3px 5px grey";
    botao.style.transition = "0.5s"
});
botao.addEventListener("mouseout", () => {
    botao.style.boxShadow = "none";
    botao.style.transition = "0.5s"
});
//Responsividade: 804
