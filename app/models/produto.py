from app.extensions import db


class Produto(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(120), nullable=False)

    categoria = db.Column(db.String(60), nullable=False)

    descricao = db.Column(db.Text)

    preco = db.Column(db.Float, nullable=False)

    imagem = db.Column(db.String(255))

    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Produto {self.nome}>"