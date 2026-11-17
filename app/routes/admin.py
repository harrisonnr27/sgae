import os

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Produto, Categoria


admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)


# =========================================================
# AUTENTICAÇÃO
# =========================================================

@admin.before_request
def exigir_login():

    if request.endpoint == "admin.login":
        return None

    if "admin_logado" not in session:
        return redirect(
            url_for("admin.login")
        )


# =========================================================
# LOGIN
# =========================================================

@admin.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        usuario = request.form.get(
            "usuario",
            ""
        ).strip()

        senha = request.form.get(
            "senha",
            ""
        )

        usuario_correto = current_app.config[
            "ADMIN_USERNAME"
        ]

        senha_correta = current_app.config[
            "ADMIN_PASSWORD"
        ]

        if (
            usuario == usuario_correto
            and senha == senha_correta
        ):

            session["admin_logado"] = True

            return redirect(
                url_for("admin.dashboard")
            )

        return render_template(
            "admin/login.html",
            erro="Usuário ou senha incorretos."
        )

    return render_template(
        "admin/login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@admin.route("/logout")
def logout():

    session.pop(
        "admin_logado",
        None
    )

    return redirect(
        url_for("admin.login")
    )


# =========================================================
# FUNÇÃO PARA SALVAR IMAGEM
# =========================================================

def salvar_imagem(arquivo):
    """Salva a imagem e retorna o nome do arquivo."""

    if not arquivo or arquivo.filename == "":
        return None

    nome_arquivo = secure_filename(
        arquivo.filename
    )

    pasta = current_app.config[
        "UPLOAD_FOLDER"
    ]

    os.makedirs(
        pasta,
        exist_ok=True
    )

    caminho = os.path.join(
        pasta,
        nome_arquivo
    )

    arquivo.save(caminho)

    return nome_arquivo


# =========================================================
# DASHBOARD
# =========================================================

@admin.route("/")
def dashboard():

    total_produtos = Produto.query.count()

    produtos_ativos = Produto.query.filter_by(
        ativo=True
    ).count()

    produtos_sem_estoque = Produto.query.filter(
        Produto.estoque <= 0
    ).count()

    categorias = Categoria.query.filter_by(
        ativo=True
    ).count()

    return render_template(
        "admin/dashboard.html",
        total_produtos=total_produtos,
        produtos_ativos=produtos_ativos,
        produtos_sem_estoque=produtos_sem_estoque,
        categorias=categorias,
    )


# =========================================================
# PRODUTOS
# =========================================================

@admin.route("/produtos")
def produtos():

    produtos = Produto.query.order_by(
        Produto.id.desc()
    ).all()

    return render_template(
        "admin/produtos.html",
        produtos=produtos,
    )


# =========================================================
# NOVO PRODUTO
# =========================================================

@admin.route(
    "/produtos/novo",
    methods=["GET", "POST"]
)
def novo_produto():

    categorias = Categoria.query.filter_by(
        ativo=True
    ).order_by(
        Categoria.nome
    ).all()

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        categoria_nome = request.form.get(
            "categoria",
            ""
        ).strip()

        descricao = request.form.get(
            "descricao",
            ""
        ).strip()

        # -------------------------------------------------
        # VALIDAÇÃO DO NOME
        # -------------------------------------------------

        if not nome:

            return render_template(
                "admin/novo_produto.html",
                categorias=categorias,
                erro="O nome do produto é obrigatório."
            )

        # -------------------------------------------------
        # VALIDAÇÃO DA CATEGORIA
        # -------------------------------------------------

        categoria = Categoria.query.filter_by(
            nome=categoria_nome,
            ativo=True
        ).first()

        if not categoria:

            return render_template(
                "admin/novo_produto.html",
                categorias=categorias,
                erro="Selecione uma categoria válida."
            )

        # -------------------------------------------------
        # VALIDAÇÃO DO PREÇO
        # -------------------------------------------------

        try:

            preco = float(
                request.form.get(
                    "preco",
                    ""
                )
            )

        except (ValueError, TypeError):

            return render_template(
                "admin/novo_produto.html",
                categorias=categorias,
                erro="Informe um preço válido."
            )

        if preco < 0:

            return render_template(
                "admin/novo_produto.html",
                categorias=categorias,
                erro="O preço não pode ser negativo."
            )

        # -------------------------------------------------
        # VALIDAÇÃO DO ESTOQUE
        # -------------------------------------------------

        try:

            estoque = int(
                request.form.get(
                    "estoque",
                    ""
                )
            )

        except (ValueError, TypeError):

            return render_template(
                "admin/novo_produto.html",
                categorias=categorias,
                erro="Informe um estoque válido."
            )

        if estoque < 0:

            return render_template(
                "admin/novo_produto.html",
                categorias=categorias,
                erro="O estoque não pode ser negativo."
            )

        # -------------------------------------------------
        # UPLOAD DA IMAGEM
        # -------------------------------------------------

        nome_imagem = salvar_imagem(
            request.files.get("imagem")
        )

        # -------------------------------------------------
        # CRIAÇÃO DO PRODUTO
        # -------------------------------------------------

        produto = Produto(
            nome=nome,
            categoria=categoria.nome,
            descricao=descricao,
            preco=preco,
            estoque=estoque,
            imagem=nome_imagem or "sem-imagem.png",
        )

        db.session.add(produto)

        db.session.commit()

        return redirect(
            url_for("admin.produtos")
        )

    return render_template(
        "admin/novo_produto.html",
        categorias=categorias,
    )


# =========================================================
# EDITAR PRODUTO
# =========================================================

@admin.route(
    "/produtos/editar/<int:id>",
    methods=["GET", "POST"]
)
def editar_produto(id):

    produto = Produto.query.get_or_404(id)

    categorias = Categoria.query.filter_by(
        ativo=True
    ).order_by(
        Categoria.nome
    ).all()

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        categoria_nome = request.form.get(
            "categoria",
            ""
        ).strip()

        descricao = request.form.get(
            "descricao",
            ""
        ).strip()

        # -------------------------------------------------
        # VALIDAÇÃO DO NOME
        # -------------------------------------------------

        if not nome:

            return render_template(
                "admin/editar_produto.html",
                produto=produto,
                categorias=categorias,
                erro="O nome do produto é obrigatório."
            )

        # -------------------------------------------------
        # VALIDAÇÃO DA CATEGORIA
        # -------------------------------------------------

        categoria = Categoria.query.filter_by(
            nome=categoria_nome,
            ativo=True
        ).first()

        if not categoria:

            return render_template(
                "admin/editar_produto.html",
                produto=produto,
                categorias=categorias,
                erro="Selecione uma categoria válida."
            )

        # -------------------------------------------------
        # VALIDAÇÃO DO PREÇO
        # -------------------------------------------------

        try:

            preco = float(
                request.form.get(
                    "preco",
                    ""
                )
            )

        except (ValueError, TypeError):

            return render_template(
                "admin/editar_produto.html",
                produto=produto,
                categorias=categorias,
                erro="Informe um preço válido."
            )

        if preco < 0:

            return render_template(
                "admin/editar_produto.html",
                produto=produto,
                categorias=categorias,
                erro="O preço não pode ser negativo."
            )

        # -------------------------------------------------
        # VALIDAÇÃO DO ESTOQUE
        # -------------------------------------------------

        try:

            estoque = int(
                request.form.get(
                    "estoque",
                    ""
                )
            )

        except (ValueError, TypeError):

            return render_template(
                "admin/editar_produto.html",
                produto=produto,
                categorias=categorias,
                erro="Informe um estoque válido."
            )

        if estoque < 0:

            return render_template(
                "admin/editar_produto.html",
                produto=produto,
                categorias=categorias,
                erro="O estoque não pode ser negativo."
            )

        # -------------------------------------------------
        # ATUALIZAÇÃO DO PRODUTO
        # -------------------------------------------------

        produto.nome = nome

        produto.categoria = categoria.nome

        produto.descricao = descricao

        produto.preco = preco

        produto.estoque = estoque

        # -------------------------------------------------
        # ALTERAÇÃO DA IMAGEM
        # -------------------------------------------------

        nome_imagem = salvar_imagem(
            request.files.get("imagem")
        )

        if nome_imagem:

            produto.imagem = nome_imagem

        db.session.commit()

        return redirect(
            url_for("admin.produtos")
        )

    return render_template(
        "admin/editar_produto.html",
        produto=produto,
        categorias=categorias,
    )


# =========================================================
# DESATIVAR PRODUTO
# =========================================================

@admin.route(
    "/produtos/desativar/<int:id>"
)
def desativar_produto(id):

    produto = Produto.query.get_or_404(id)

    produto.ativo = False

    db.session.commit()

    return redirect(
        url_for("admin.produtos")
    )


# =========================================================
# ATIVAR PRODUTO
# =========================================================

@admin.route(
    "/produtos/ativar/<int:id>"
)
def ativar_produto(id):

    produto = Produto.query.get_or_404(id)

    produto.ativo = True

    db.session.commit()

    return redirect(
        url_for("admin.produtos")
    )


# =========================================================
# EXCLUIR PRODUTO
# =========================================================

@admin.route(
    "/produtos/excluir/<int:id>"
)
def excluir_produto(id):

    produto = Produto.query.get_or_404(id)

    db.session.delete(produto)

    db.session.commit()

    return redirect(
        url_for("admin.produtos")
    )


# =========================================================
# CATEGORIAS
# =========================================================

@admin.route("/categorias")
def categorias():

    categorias = Categoria.query.order_by(
        Categoria.nome
    ).all()

    return render_template(
        "admin/categorias.html",
        categorias=categorias,
    )


# =========================================================
# NOVA CATEGORIA
# =========================================================

@admin.route(
    "/categorias/nova",
    methods=["GET", "POST"]
)
def nova_categoria():

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        descricao = request.form.get(
            "descricao",
            ""
        ).strip()

        if nome:

            categoria = Categoria(
                nome=nome,
                descricao=descricao,
            )

            db.session.add(categoria)

            db.session.commit()

        return redirect(
            url_for("admin.categorias")
        )

    return render_template(
        "admin/nova_categoria.html"
    )


# =========================================================
# EDITAR CATEGORIA
# =========================================================

@admin.route(
    "/categorias/editar/<int:id>",
    methods=["GET", "POST"]
)
def editar_categoria(id):

    categoria = Categoria.query.get_or_404(id)

    if request.method == "POST":

        categoria.nome = request.form.get(
            "nome",
            ""
        ).strip()

        categoria.descricao = request.form.get(
            "descricao",
            ""
        ).strip()

        db.session.commit()

        return redirect(
            url_for("admin.categorias")
        )

    return render_template(
        "admin/editar_categoria.html",
        categoria=categoria,
    )


# =========================================================
# DESATIVAR CATEGORIA
# =========================================================

@admin.route(
    "/categorias/desativar/<int:id>"
)
def desativar_categoria(id):

    categoria = Categoria.query.get_or_404(id)

    categoria.ativo = False

    db.session.commit()

    return redirect(
        url_for("admin.categorias")
    )


# =========================================================
# ATIVAR CATEGORIA
# =========================================================

@admin.route(
    "/categorias/ativar/<int:id>"
)
def ativar_categoria(id):

    categoria = Categoria.query.get_or_404(id)

    categoria.ativo = True

    db.session.commit()

    return redirect(
        url_for("admin.categorias")
    )


# =========================================================
# EXCLUIR CATEGORIA
# =========================================================

@admin.route(
    "/categorias/excluir/<int:id>"
)
def excluir_categoria(id):

    categoria = Categoria.query.get_or_404(id)

    db.session.delete(categoria)

    db.session.commit()

    return redirect(
        url_for("admin.categorias")
    )