/*Cria uma lista json com todas os jsons armazenados no sistema*/
const json = ['json/nossa.json', 'json/10-09-2024.json', 'json/11-09-2024.json', 'json/12-09-2024.json', 'json/13-09-2024.json'];
/*Cria uma constante para o botão de envio da pesquisa*/
const botao = document.querySelector("#button")
/*Quando o botão for pressionado, chama a função executar*/
botao.addEventListener("click", (e)=>{
    executar(e);
})
/*Nesse caso a  função também será chamada caso o enter seja pressionado */
document.addEventListener("keydown", (e)=>{
    if(e.key == "Enter"){
        executar(e);
    }
})
function executar(e){
    /*Evita de o site ser reniciado*/
    e.preventDefault();

    const orgaoInput = document.querySelector("#orgao");
    const assuntoInput = document.querySelector("#assunto");
    /*Se o orgão possuir algo, a palavra é tranferida para o minúsculo, caso contrário adiciona vazio a constante*/
    const orgao = orgaoInput ? orgaoInput.value.toLowerCase() : '';
    /*Aqui a contante orgao é normalizada para não possuir acentos dentro do orgaoSem */
    var orgaoSem = orgao.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    /*Abaixo, ocorre a mesma coisa com o assunto*/
    const assunto = assuntoInput ? assuntoInput.value.toLowerCase() : '';
    var assuntoSem = assunto.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    /*Adiciona as constantes data de inicio e  fim*/
    const datai = new Date(document.querySelector("#datai").value);
    const dataf = new Date(document.querySelector("#dataf").value);
    /*Nome no caso palavra-chave passa pelo mesmo processo do orgão e do assunto */
    const nome = document.querySelector("#nome").value.toLowerCase();
    var nomeSem = nome.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    /*ResultadosDiv armazenará os resultados obtidos*/
    const resultadosDiv = document.querySelector('#resultados');
    
    resultadosDiv.innerHTML = '';
    /*promises vai ser um vetor com o resultado de todas as filtragens dos jsons */
    const promises = json.map(jsonFilePath =>{
        /*Isso vai abrir cada json, esperando a filtragem do anterior para abrir o próximo*/
        return fetch(jsonFilePath)
            /*Caso der erro ao abrir, vai retornar um erro, caso seja bem sucedido, retorna um valor do tipo json*/
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao carregar o arquivo JSON');
                }
                return response.json(); 
            })
            .then(arquivos => {
                /*Filtra cada arquivo dentro do json por meio do filter, um por vez*/
                const resultados = arquivos.filter(arquivo => {
                    /*Verifica se todos os elemetos da busa estão em branco*/
                    if (!orgao && !assunto && isNaN(datai) && isNaN(dataf) && !nome) {
                        return false;
                    }
                    /**
                     * dataArquivo: A data do arquivo a ser filtrado
                     * arquivoOrgao: Orgão normalizado do arquivo
                     * OrgaoIgual: retorna true se orgao for vazio OU se o orgão corresponder com o do arquivo
                     * arquivoAssunto: Assunto do arquivo normalizado
                     * AssuntoIgual: Mesma coisa do OrgaoIgual so que com o assunto
                     * arquivoNome: Texto do arquivo normalizado
                     * nomeIgual: Mesma coisa do OrgaoIgual só que com o texto
                     * Data: Retorna true se uma das datas não forem mencionadas ou se a dataArquivo corresponder o intervalo mencionado pelo usuário
                     */
                    const dataArquivo = new Date(arquivo.DATA.split('-').reverse().join('-'));
                    var arquivoOrgao = arquivo.NOME.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
                    const OrgaoIgual = !orgao || arquivoOrgao.toLowerCase().includes(orgaoSem);
                    var arquivoAssunto = arquivo.assunto.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
                    const AssuntoIgual = !assunto || arquivoAssunto.toLowerCase().includes(assuntoSem);
                    var arquivoNome = arquivo.TEXTO.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
                    const nomeIgual = !nome || arquivoNome.toLowerCase().includes(nomeSem);
                    const Data = (!isNaN(datai) && !isNaN(dataf))
                        ? (dataArquivo >= datai && dataArquivo <= dataf)
                        : true;
                    /*O arquivo é retornado se todos os requisitos forem cumpridos */
                    return OrgaoIgual && AssuntoIgual && Data && nomeIgual;
                }); 
                /*Pra cada resultado ele vai marcar onde esta mencionado os elementos buscados*/
                resultados.forEach(resultado => {   
                    /*O regex vai servir para analisar se o elemento analisado é iual ao item buscado */
                    const regex = new RegExp(`(${orgao}|${orgaoSem})`, 'gi');
                    var orgaoDestaque = ''
                    if(!orgao.includes(" ")){
                        if(!orgao == ''){
                            /*Caso o orgão buscado não possuas espaços e não for nulo, Ele irá analisar as palavras que não sejam espaços
                            nem outros acentos(match), normalizar essas palavras a serem analisadas(normalizedMatch), e testar se essa palavra
                            normalizada é igual ao regex(regex.test(normalizedMatch)). Caso seja verdadeiro ela adicionará o <mark> à palavra */
                            orgaoDestaque = resultado.NOME.replace(/([^-\s.,;!?]+)/gi, (match)=>{
                                const normalizedMatch = match.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                                return regex.test(normalizedMatch) ? `<mark>${match}</mark>` : match;
                            })
                        }
                        else{
                            /*Caso seja nulo não marará nada */
                            orgaoDestaque = resultado.NOME
                        }    
                    }
                    else{
                        /*Caso possua espaços ela marcará a linha toda se o orgão corresponder */
                        orgaoDestaque = resultado.NOME.replace(/([^.,;!?]+)/gi, (match)=>{
                            const normalizedMatch = match.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                            return regex.test(normalizedMatch) ? `<mark>${match}</mark>` : match;
                        })       
                    }
                    if(nome.includes(" ")){
                        /*Caso a palavra-chave de busca contenha espaços, ela vai ser separada em um vetor e a função .map 
                        vai analisar palavra por palavra */
                        var vetor = nome.split(" ")
                        vetor.map(elemento =>{
                            /*Normaliza o elemento do vetor e cria o regex com base no elemento básico e normalizado */
                            normalizedElemento = elemento.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
                            regexTexto = new RegExp(`(${elemento}|${normalizedElemento})`, 'gi')
                            /*Mesmo processo de busca que ocorre no orgao, porém como a busca é ralizada mais de uma vez,
                            é necessário verificar se o match possui marked, que caso sim a busca mantém ele dentro do texto*/
                            resultado.TEXTO = resultado.TEXTO.replace(/([^\s.,;!?]+)/gi, match => {
                                const normalizedMatch = match.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
                                if (/<mark>.*?<\/mark>/ig.test(match)) {
                                    return match;
                                } else {
                                    return regexTexto.test(normalizedMatch) ? `<mark>${match}</mark>` : match;
                                }
                            });
                        })
                    }
                    else{
                        /*Caso a palavra-chave não possua chaves e não seja nula, a busca é a mesma do orgão */
                        if(!nome == ''){
                            var regexTexto = new RegExp(`(${nome}|${nomeSem})`,'gi');
                            resultado.TEXTO = resultado.TEXTO.replace(/([^\s.,;!?]+)/gi, (match)=>{
                                const normalizedMatch = match.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                                return regexTexto.test(normalizedMatch) ? `<mark>${match}</mark>` : match;
                            })
                        }       
                    }
                    /*A div item é criada e armazena os resultados das filtragens*/
                    const item = document.createElement('div');
                    item.innerHTML = `
                        <h3>Órgão:</h3><p>${orgaoDestaque}</p>
                        <h3>Data:</h3><p>${resultado.DATA}</p>
                        <h3>Caderno:</h3><p>${resultado.CADERNO}</p>
                        <h3>Página:</h3><p>${resultado.PAGINA}</p>
                        <h3>Publicação:</h3><p>${resultado.PUBLICACAO}</p>
                        <h3>Texto:</h3><p>${resultado.TEXTO}</p>
                        <h3>Página:</h3><p>${resultado.PAGINA}</p>
                        <h3>Assunto:</h3><p>${resultado.assunto}</p>
                        <h3>Destaque:</h3><p>${resultado.DESTAQUE.join("<br>")}</p>
                        <br><br>`;
                    /*Aqui o elemento resultadosDiv do html recebe essa div item */    
                    resultadosDiv.appendChild(item);
                });
            })
            /*Caso de algum erro na hora de tentar filtrar o arquivo dentro do json */
            .catch(error => {
                document.getElementById('resultados').innerHTML = 'Erro: ' + error;
            });
    })
    /**Aqui ele aguarda todos os elementos da lista de jsons serem abertos por meio do Promise.all
     * e verifica se o resultadosDiv está vazio, caso sim ele adiciona o nenhum arquivo encontrado
     */
    Promise.all(promises).then(() => {
        if(resultadosDiv.innerHTML.trim() === ''){
            const nenhum = document.createElement("p")
            nenhum.textContent = "Nenhum arquivo encontrado!"
            nenhum.classList.add("nenhum")
            resultadosDiv.appendChild(nenhum)
        }
        else{
            var nenhum = document.querySelector(".nenhum")
            nenhum.remove()
        }
    })
};
/*Adicionam efeitos de sombra quando o mouse passa por cima do botão */
botao.addEventListener("mouseover", () => {
    botao.style.boxShadow = "3px 3px 5px grey";
    botao.style.transition = "0.5s"
});
botao.addEventListener("mouseout", () => {
    botao.style.boxShadow = "none";
    botao.style.transition = "0.5s"
});
