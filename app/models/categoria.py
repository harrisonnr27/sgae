from app.extensions import db


class Categoria(db.Model):

    __tablename__ = "categoria"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(60),
        nullable=False,
        unique=True
    )

    descricao = db.Column(
        db.String(255),
        default=""
    )

    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    def __repr__(self):
        return f"<Categoria {self.nome}>"