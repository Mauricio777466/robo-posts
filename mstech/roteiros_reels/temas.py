"""Banco de templates curtos, um tema por dor do comércio local.

Regras de conteúdo (não mudar sem conferir):
- Só falar do que o Gestão Comercial e o Caixa Rápido já fazem hoje.
- Nota fiscal (NFC-e) ainda é "em breve": nunca dizer que já emite.
- Cartão no Caixa Rápido é na maquininha da loja, com o atendente
  confirmando. Não dizer que a maquininha é integrada (TEF).
- Gancho com no máximo 8 palavras (cabe em 3 segundos de fala).

Marcadores aceitos nos textos: {cidade}, {empresa}, {sistema}, {whatsapp},
{instagram}, {palavra}.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Tema:
    chave: str
    titulo: str
    palavra_direct: str  # palavra que a pessoa manda no direct
    ganchos: tuple[str, ...]
    dores: tuple[str, ...]
    solucoes: tuple[str, ...]
    hashtags: tuple[str, ...] = ()
    visuais: dict[str, str] = field(default_factory=dict)


CHAMADAS = (
    "Manda {palavra} no direct que eu te mostro funcionando na sua loja.",
    "Comenta {palavra} aqui embaixo que eu te chamo no direct.",
    "Quer testar sete dias grátis? O link está na bio. Ou manda {palavra} no direct.",
    "Me chama no WhatsApp {whatsapp} e fala {palavra}. A demonstração é por nossa conta.",
    "Manda {palavra} pra {empresa} no direct e veja isso funcionando na prática.",
)

# Fecho do formato longo, depois da chamada.
FECHO_LONGO = "E segue a gente pra mais dicas pro seu comércio em {cidade}."

PERGUNTAS_ENGAJAMENTO = (
    "Isso já aconteceu na sua loja? Conta aqui nos comentários 👇",
    "Você é do time que sofre com isso ou já resolveu? Comenta 👇",
    "Marca aquele amigo dono de comércio que precisa ver isso 👀",
    "Salva esse vídeo pra mostrar pro seu sócio 📌",
)

TEMAS: dict[str, Tema] = {}


def _tema(t: Tema) -> None:
    TEMAS[t.chave] = t


_tema(Tema(
    chave="filas",
    titulo="Fila no caixa",
    palavra_direct="FILA",
    ganchos=(
        "Cliente desistiu da compra por causa da fila?",
        "Essa fila está levando seu dinheiro embora.",
        "Fila grande não é sinal de sucesso.",
        "Sabe quanto você perde no horário de pico?",
    ),
    dores=(
        "Sábado de manhã em {cidade}: um caixa só, dez pessoas esperando, e tem cliente largando a cesta e indo pro concorrente.",
        "O cliente só quer pagar um refrigerante e um pão, mas espera atrás de uma compra do mês inteira. Ele não volta.",
        "Contratar mais um operador custa caro, e no horário calmo ele fica parado.",
    ),
    solucoes=(
        "Com o Caixa Rápido da {empresa}, o próprio cliente passa o produto no leitor, vê tudo na tela e paga no PIX ou no cartão. A compra pequena sai da fila.",
        "O Caixa Rápido é o autoatendimento do {sistema}: puxa os preços do seu cadastro, mostra o QR do PIX com o valor certo, e a venda cai direto no sistema.",
        "Coloca um Caixa Rápido do lado do balcão: quem leva pouca coisa paga sozinho em segundos, e seu operador cuida das compras grandes.",
    ),
    hashtags=("#CaixaRapido", "#Autoatendimento", "#Mercadinho", "#FilaNoCaixa"),
    visuais={
        "gancho": "Close na fila do caixa ou cesta largada no chão.",
        "dor": "Relógio na parede, cliente impaciente olhando o celular.",
        "solucao": "Tela do Caixa Rápido: leitor, lista de produtos e QR do PIX.",
        "cta": "Você apontando para a tela com o @ da MS Tech.",
    },
))

_tema(Tema(
    chave="fechamento",
    titulo="Fechamento do caixa",
    palavra_direct="CAIXA",
    ganchos=(
        "Seu caixa fechou com diferença de novo?",
        "Fechar o caixa não pode levar uma hora.",
        "Sumiu dinheiro do caixa e ninguém sabe?",
        "Ainda fecha o caixa no caderninho?",
    ),
    dores=(
        "Fim do dia, todo mundo cansado, e o dinheiro da gaveta não bate com o que foi vendido. Aí começa a caça à diferença.",
        "Tirou dinheiro do caixa pra pagar fornecedor e esqueceu de anotar. No fechamento ninguém lembra de nada.",
        "Você confia na sua equipe, mas sem registro não tem como saber onde o dinheiro foi parar.",
    ),
    solucoes=(
        "No {sistema}, toda sangria e todo suprimento ficam registrados com hora e funcionário. No fechamento você vê na tela quanto tem que ter em dinheiro, PIX e cartão.",
        "Com o {sistema}, o fechamento sai separado por forma de pagamento. É só contar a gaveta e comparar. Acabou o caderninho.",
        "O {sistema} registra cada venda, cada retirada e cada reforço do caixa. A diferença aparece na hora, não no fim do mês.",
    ),
    hashtags=("#FechamentoDeCaixa", "#ControleFinanceiro", "#PDV"),
    visuais={
        "gancho": "Mão contando notas, cara de preocupação.",
        "dor": "Caderno rabiscado e calculadora.",
        "solucao": "Tela de fechamento do Gestão Comercial com os totais por forma de pagamento.",
        "cta": "Gaveta fechada, sorriso, texto do @ na tela.",
    },
))

_tema(Tema(
    chave="seguranca",
    titulo="Segurança no caixa",
    palavra_direct="SEGURO",
    ganchos=(
        "Quem mexeu no preço do seu produto?",
        "Desconto sem você saber é prejuízo.",
        "Seu computador quebrou. E as vendas de hoje?",
        "Você sabe o que acontece no seu caixa?",
    ),
    dores=(
        "O operador muda o preço na hora de passar, dá desconto pro conhecido, e você só descobre quando o lucro some.",
        "Um dia o computador do caixa queima, e com ele vão embora o cadastro, as vendas e o histórico da loja.",
        "Você não consegue ficar o dia todo no balcão vigiando cada venda, e nem deveria precisar.",
    ),
    solucoes=(
        "No {sistema}, trocar o preço no caixa só com a senha do gerente, e fica tudo registrado: quem trocou, quando e de quanto pra quanto.",
        "O {sistema} faz backup automático todo dia. Se o computador der problema, seus dados estão guardados.",
        "Cada funcionário entra com o próprio login no {sistema}, e cada um só faz o que você liberou. Desconto e troca de preço ficam registrados.",
    ),
    hashtags=("#SegurancaNoCaixa", "#PrevencaoDePerdas", "#Backup"),
    visuais={
        "gancho": "Close numa etiqueta de preço sendo riscada.",
        "dor": "Computador desligado com fumaça (efeito) ou caixa vazio.",
        "solucao": "Tela pedindo a senha do gerente para trocar o preço.",
        "cta": "Cadeado na tela com o @ da MS Tech.",
    },
))

_tema(Tema(
    chave="tributacao",
    titulo="Reforma tributária",
    palavra_direct="REFORMA",
    ganchos=(
        "IBS e CBS: seu comércio já ouviu falar?",
        "A reforma tributária vai chegar no seu balcão.",
        "Cadastro bagunçado vai virar dor de cabeça.",
        "Seu contador já te falou da reforma?",
    ),
    dores=(
        "A reforma tributária está chegando com o IBS e a CBS, e quem tem cadastro de produto bagunçado vai sofrer na hora de se adaptar.",
        "Produto sem NCM, preço anotado no papel, venda sem registro. Na hora de se adequar à lei, isso vira correria e gasto.",
        "Muito comerciante em {cidade} vai deixar pra última hora e pagar caro pela pressa.",
    ),
    solucoes=(
        "Com o {sistema}, você já organiza hoje o cadastro dos produtos e o registro das vendas. A emissão de nota fiscal está chegando em breve, e quem já está organizado sai na frente.",
        "A {empresa} implanta o {sistema} e ajuda a deixar o cadastro em ordem agora, com calma. A nota fiscal no sistema vem em breve.",
        "Organiza seu comércio agora com o {sistema}: produtos cadastrados, vendas registradas e relatório pro contador. A nota fiscal é a próxima novidade, em breve.",
    ),
    hashtags=("#ReformaTributaria", "#IBS", "#CBS", "#Contabilidade"),
    visuais={
        "gancho": "Texto grande na tela: IBS + CBS.",
        "dor": "Pilha de papéis e notas bagunçadas.",
        "solucao": "Tela de cadastro de produtos organizada, selo EM BREVE para a nota fiscal.",
        "cta": "Calendário com o texto: comece agora.",
    },
))

_tema(Tema(
    chave="caixa_rapido",
    titulo="Caixa Rápido (autoatendimento)",
    palavra_direct="RÁPIDO",
    ganchos=(
        "Mercadinho com autoatendimento em {cidade}? Tem sim.",
        "O cliente passa e paga sozinho.",
        "Autoatendimento não é só pra supermercado grande.",
        "Olha esse caixa trabalhando sem operador.",
    ),
    dores=(
        "Você vê autoatendimento nos mercados grandes e acha que é caro demais pra sua loja.",
        "No horário de almoço todo mundo quer pagar rápido, e seu único caixa não dá conta.",
        "Você precisa de mais um caixa, mas não de mais um salário todo mês.",
    ),
    solucoes=(
        "O Caixa Rápido da {empresa} funciona com o seu cadastro do {sistema}: o cliente passa no leitor, lê até a etiqueta da balança, paga no PIX ou na sua maquininha e leva o cupom.",
        "O Caixa Rápido tem câmera ao vivo com aviso de monitoramento, PIX com QR na tela, e a venda cai no seu sistema. Estoque e caixa batem.",
        "O cliente passa no leitor, paga no PIX ou na sua maquininha e leva o cupom. E se a internet cair, o Caixa Rápido guarda a venda e manda depois. Nada se perde.",
    ),
    hashtags=("#CaixaRapido", "#Autoatendimento", "#Conveniencia", "#Padaria"),
    visuais={
        "gancho": "Cliente passando produto no leitor do Caixa Rápido.",
        "dor": "Fila no balcão no horário de almoço.",
        "solucao": "Tela do PIX com QR e a tela de compra aprovada.",
        "cta": "Cupom saindo da impressora.",
    },
))

_tema(Tema(
    chave="dono_longe",
    titulo="Acompanhar a loja de longe",
    palavra_direct="DONO",
    ganchos=(
        "Dono de loja também merece folga.",
        "Quanto sua loja vendeu agora? Você sabe?",
        "Saiu da loja e ficou preocupado?",
        "Sua loja cabe no seu bolso.",
    ),
    dores=(
        "Você não consegue sair da loja nem pra resolver um problema no banco, porque precisa ver se está tudo certo.",
        "Pra saber quanto vendeu no dia, você tem que ligar pro funcionário ou esperar o fechamento.",
        "Tem mais de uma loja e passa o dia correndo de uma pra outra.",
    ),
    solucoes=(
        "Com o app do dono da {empresa}, você acompanha as vendas do {sistema} pelo celular, de onde estiver.",
        "No app do dono você vê o que está sendo vendido e como está o dia, sem precisar ligar pra ninguém.",
        "O {sistema} manda as vendas para o painel na nuvem, e você confere tudo pelo celular, até de casa.",
    ),
    hashtags=("#DonoDeLoja", "#Empreendedor", "#GestaoPeloCelular"),
    visuais={
        "gancho": "Você numa rede ou na praia olhando o celular.",
        "dor": "Ligação perdida: 'Fulano do caixa'.",
        "solucao": "Tela do app do dono com as vendas do dia.",
        "cta": "Celular na mão com o @ da MS Tech.",
    },
))

_tema(Tema(
    chave="balanca",
    titulo="Etiqueta da balança no caixa",
    palavra_direct="BALANÇA",
    ganchos=(
        "Ainda digita o peso na mão?",
        "Erro no peso é dinheiro jogado fora.",
        "Açougue e padaria, prestem atenção.",
        "Bipou a etiqueta, já saiu o valor.",
    ),
    dores=(
        "No açougue ou na padaria, o operador lê o peso na etiqueta e digita na mão. Um número errado e você perde dinheiro.",
        "Fila parada porque o produto pesado não entra no caixa e alguém precisa ir conferir.",
        "Cliente reclamando no balcão que o valor do caixa está diferente da etiqueta, e a fila toda esperando.",
    ),
    solucoes=(
        "O {sistema} lê a etiqueta da balança direto no leitor do caixa: produto e valor certinhos, sem digitar nada.",
        "No {sistema} você liga cada produto ao código da balança uma vez só. Depois é só bipar a etiqueta.",
        "Com o {sistema}, a etiqueta da balança entra no caixa e no Caixa Rápido do mesmo jeito: bipou, está lançado.",
    ),
    hashtags=("#Balanca", "#Acougue", "#Padaria", "#Hortifruti"),
    visuais={
        "gancho": "Close na etiqueta da balança sendo bipada.",
        "dor": "Operador digitando o peso devagar.",
        "solucao": "Produto pesado aparecendo sozinho na tela do caixa.",
        "cta": "Balança com o @ da MS Tech.",
    },
))

_tema(Tema(
    chave="estoque",
    titulo="Controle de estoque",
    palavra_direct="ESTOQUE",
    ganchos=(
        "Cliente pediu e o produto tinha acabado?",
        "Seu estoque está só na sua cabeça?",
        "Comprou de novo o que ainda tinha?",
        "Prateleira vazia é venda perdida.",
    ),
    dores=(
        "O cliente pede, você jura que tinha, vai procurar e acabou. Ele compra no vizinho.",
        "Sem controle, você compra o que ainda tem no depósito e deixa faltar o que mais vende.",
        "Contar estoque no papel toma o seu domingo inteiro, e mesmo assim no outro dia a conta já não bate mais.",
    ),
    solucoes=(
        "No {sistema}, cada venda já baixa o estoque sozinha. Você abre o sistema e vê quanto tem de cada produto.",
        "Com o {sistema}, a entrada de mercadoria e as vendas ficam registradas, e você compra olhando o número, não o achismo.",
        "O {sistema} junta caixa e estoque no mesmo lugar: vendeu, baixou. Simples assim.",
    ),
    hashtags=("#ControleDeEstoque", "#Mercadinho", "#Varejo"),
    visuais={
        "gancho": "Prateleira vazia.",
        "dor": "Depósito cheio do produto errado.",
        "solucao": "Tela de produtos do Gestão Comercial com a quantidade em estoque.",
        "cta": "Prateleira cheia com o @ da MS Tech.",
    },
))


_tema(Tema(
    chave="novidades",
    titulo="Novidades do Gestão Comercial",
    palavra_direct="NOVIDADE",
    ganchos=(
        "Tem novidade chegando no seu caixa.",
        "Seu sistema parou no tempo?",
        "O que vem por aí no {sistema}.",
        "Sistema bom é sistema que evolui.",
    ),
    dores=(
        "Muito comércio em {cidade} ainda usa sistema que nunca recebe melhoria. A lei muda, o cliente muda, e o programa continua igual.",
        "Você paga por um sistema e, quando pede uma melhoria, ninguém responde. Fica tudo do mesmo jeito por anos.",
        "Sistema antigo trava, não conversa com o celular e deixa o dono no escuro.",
    ),
    solucoes=(
        "O {sistema} da {empresa} recebe atualização direto no computador. Já chegaram o Caixa Rápido, o app do dono e o app do vendedor. E a nota fiscal vem em breve.",
        "No {sistema}, as novidades chegam sem você reinstalar nada: troca de preço com senha do gerente, leitura da etiqueta da balança e o painel no celular. A nota fiscal está a caminho, em breve.",
        "A {empresa} é daqui do Amapá e escuta o lojista. Cada pedido vira melhoria no {sistema}, e quem já é cliente recebe a atualização.",
    ),
    hashtags=("#Novidades", "#SistemaDeVendas", "#PDV", "#Tecnologia"),
    visuais={
        "gancho": "Tela de 'Atualizações' do Gestão Comercial.",
        "dor": "Computador velho com sistema travado.",
        "solucao": "Montagem: Caixa Rápido, app do dono e app do vendedor.",
        "cta": "Selo EM BREVE: nota fiscal.",
    },
))

# Dados extras do cartão animado do robo-posts (content/reels.json):
# título curto (até 22 letras), cor de destaque, subtítulo (*palavra* = sublinhada), texto digitado e 6 itens curtos.
CARTAO_REEL: dict[str, dict] = {
    "filas": {"titulo": "Fila no caixa?", "cor": "#2563EB", "sub": "o cliente paga *sozinho*", "typing": "Caixa Rápido",
              "checks": ["Leitor de código", "PIX na tela", "Cartão na maquininha", "Cupom impresso", "Menos fila", "Venda no sistema"]},
    "fechamento": {"titulo": "Caixa com diferença?", "cor": "#06B6D4", "sub": "e o caixa *bate*", "typing": "Fechar caixa",
                   "checks": ["Sangria registrada", "Suprimento", "Total por pagamento", "Login por usuário", "Sem caderninho", "Relatório do dia"]},
    "seguranca": {"titulo": "Caixa seguro", "cor": "#EF4444", "sub": "tudo *registrado*", "typing": "Senha do gerente",
                  "checks": ["Senha p/ trocar preço", "Login por usuário", "Permissões", "Backup diário", "Histórico", "Mais controle"]},
    "tributacao": {"titulo": "Reforma tributária", "cor": "#FACC15", "sub": "comece a se *organizar*", "typing": "IBS + CBS",
                   "checks": ["Cadastro em ordem", "Vendas registradas", "Relatórios", "Ajuda ao contador", "Nota fiscal em breve", "Sem correria"]},
    "caixa_rapido": {"titulo": "Caixa Rápido", "cor": "#22D3EE", "sub": "autoatendimento *de verdade*", "typing": "Passe o produto",
                     "checks": ["Leitor de código", "Etiqueta da balança", "PIX com QR", "Sua maquininha", "Câmera ao vivo", "Funciona sem internet"]},
    "dono_longe": {"titulo": "Loja no celular", "cor": "#2563EB", "sub": "a loja no seu *celular*", "typing": "App do dono",
                   "checks": ["Vendas do dia", "De qualquer lugar", "Painel na nuvem", "Sem ligar pra loja", "Mais de uma loja", "Mais folga"]},
    "balanca": {"titulo": "Etiqueta da balança", "cor": "#F97316", "sub": "bipou, *lançou*", "typing": "Etiqueta lida",
                "checks": ["Sem digitar peso", "Valor certo", "Açougue", "Padaria", "Hortifrúti", "Fila andando"]},
    "novidades": {"titulo": "Novidades", "cor": "#22D3EE", "sub": "o sistema que *evolui*", "typing": "Atualização",
                  "checks": ["Caixa Rápido", "App do dono", "App do vendedor", "Senha do gerente", "Etiqueta da balança", "Nota fiscal em breve"]},
    "estoque": {"titulo": "Estoque em dia", "cor": "#10B981", "sub": "vendeu, *baixou*", "typing": "Estoque",
                "checks": ["Baixa automática", "Entrada de nota", "Quantidade na hora", "Compra certa", "Menos falta", "Menos sobra"]},
}


# Partes extras do formato LONGO (45 a 60 s): o prejuízo (agravante) e o resultado (benefício).
LONGO: dict[str, dict[str, tuple[str, ...]]] = {
    "filas": {
        "agravantes": (
            "E cliente que vai embora irritado conta pros amigos. Você perde a venda de hoje e a de amanhã.",
            "No fim do mês, essas vendas perdidas somam um dinheiro que faria muita diferença no seu caixa.",
        ),
        "beneficios": (
            "Resultado: fila menor, cliente satisfeito e o seu operador livre pra atender quem precisa.",
            "E o melhor: a venda entra no sistema na hora, com estoque e caixa batendo certinho.",
        ),
    },
    "fechamento": {
        "agravantes": (
            "E quando o caixa não bate todo dia, a desconfiança cresce e o clima da equipe fica pesado.",
            "Diferenças de dez, vinte reais por dia viram centenas de reais no fim do mês.",
        ),
        "beneficios": (
            "Fechamento em poucos minutos, sem briga e sem caderninho.",
            "E você ainda vê o relatório do dia pra saber quanto entrou de verdade.",
        ),
    },
    "seguranca": {
        "agravantes": (
            "Um desconto aqui, um preço trocado ali, e no fim do mês o prejuízo é grande e ninguém sabe explicar.",
            "E perder o cadastro de produtos significa dias parado, digitando tudo de novo.",
        ),
        "beneficios": (
            "Você define o que cada funcionário pode fazer e confere tudo depois.",
            "Mais controle pra você e mais tranquilidade pra equipe honesta trabalhar.",
        ),
    },
    "tributacao": {
        "agravantes": (
            "Quem deixar pra última hora vai correr, pagar mais caro e ainda arriscar errar.",
            "E o seu contador vai precisar de informação organizada, não de uma caixa de sapato cheia de papel.",
        ),
        "beneficios": (
            "Com tudo registrado, você conversa com o contador com os números na mão.",
            "E quando a nota fiscal chegar ao sistema, em breve, o seu cadastro já vai estar pronto.",
        ),
    },
    "caixa_rapido": {
        "agravantes": (
            "Enquanto isso, o cliente da compra rápida desiste e vai na loja do lado.",
            "E contratar mais gente pesa na folha de pagamento todo mês.",
        ),
        "beneficios": (
            "O cliente ganha tempo, e você vende mais no mesmo horário.",
            "É ideal pra mercadinho, conveniência, padaria e açaiteria.",
        ),
    },
    "dono_longe": {
        "agravantes": (
            "Resultado: você vive preso no balcão e não sobra tempo pra família nem pra fazer o negócio crescer.",
            "E quando sai, fica com o celular na mão ligando pra loja de hora em hora.",
        ),
        "beneficios": (
            "Mais tempo pra você, sem perder o controle da loja.",
            "Você decide com os números na mão, e não no achismo.",
        ),
    },
    "balanca": {
        "agravantes": (
            "Um erro de cem gramas por venda parece pouco, mas no fim do mês vira um prejuízo que dói.",
            "E cliente que vê valor errado perde a confiança na sua loja.",
        ),
        "beneficios": (
            "Mais rapidez no caixa e o valor sempre certo, pra você e pro cliente.",
            "Serve pra açougue, padaria, hortifrúti e tudo que sai pesado na balança.",
        ),
    },
    "novidades": {
        "agravantes": (
            "E sistema parado custa caro: você perde tempo, perde venda e fica pra trás do concorrente.",
            "Quando a lei muda, quem tem sistema sem atualização corre atrás de outro na pressa.",
        ),
        "beneficios": (
            "Você acompanha as mudanças sem trocar de sistema e sem dor de cabeça.",
            "E tem suporte daqui, que fala a sua língua e conhece o comércio da região.",
        ),
    },
    "estoque": {
        "agravantes": (
            "Dinheiro parado em mercadoria que não vende é dinheiro que falta pra pagar as contas.",
            "E produto em falta faz o cliente se acostumar a comprar no concorrente.",
        ),
        "beneficios": (
            "Você compra melhor, gasta menos e não deixa faltar o que mais vende.",
            "Tudo no mesmo sistema do caixa, sem planilha separada.",
        ),
    },
}
