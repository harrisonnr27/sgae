from flask import Blueprint, render_template, request

from app.models import Produto


site = Blueprint(
    "site",
    __name__,
)


@site.route("/")
def home():

    produtos = (
        Produto.query
        .filter_by(ativo=True)
        .order_by(Produto.id.desc())
        .limit(4)
        .all()
    )

    return render_template(
        "pages/index.html",
        produtos=produtos
    )


@site.route("/catalogo")
def catalogo():

    categoria = request.args.get("categoria")

    query = Produto.query.filter_by(ativo=True)

    if categoria:
        query = query.filter_by(categoria=categoria)

    produtos = (
        query
        .order_by(Produto.nome)
        .all()
    )

    return render_template(
        "pages/catalogo.html",
        produtos=produtos,
        categoria=categoria
    )


@site.route("/produto/<int:id>")
def produto(id):

    produto = Produto.query.get_or_404(id)

    return render_template(
        "pages/produto.html",
        produto=produto
    )


@site.route("/sobre")
def sobre():
    return render_template("pages/sobre.html")


@site.route("/personalizados")
def personalizados():
    return render_template("pages/personalizados.html")


@site.route("/contato")
def contato():
    return render_template("pages/contato.html")