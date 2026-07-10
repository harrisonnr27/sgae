from flask import Blueprint, render_template

site = Blueprint("site", __name__)


@site.route("/")
def home():
    return render_template("pages/index.html")


@site.route("/catalogo")
def catalogo():
    return render_template("pages/catalogo.html")


@site.route("/sobre")
def sobre():
    return render_template("pages/sobre.html")


@site.route("/personalizados")
def personalizados():
    return render_template("pages/personalizados.html")


@site.route("/contato")
def contato():
    return render_template("pages/contato.html")