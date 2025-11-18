# database.py
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash

engine = create_engine("sqlite:///alunos.db", echo=False, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")  # 'admin' or 'user'

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Aluno(Base):
    __tablename__ = "alunos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    idade = Column(Integer)
    pais = Column(String)
    passaporte = Column(String)
    serie = Column(String)
    data_entrada = Column(Date)
    responsavel = Column(String)
    observacoes = Column(Text)

    presencas = relationship("Presenca", back_populates="aluno", cascade="all, delete-orphan")


class Presenca(Base):
    __tablename__ = "presencas"
    id = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"))
    data = Column(Date, default=date.today)
    hora_entrada = Column(DateTime, nullable=True)
    hora_saida = Column(DateTime, nullable=True)
    observacao = Column(Text, nullable=True)

    aluno = relationship("Aluno", back_populates="presencas")


def criar_banco():
    Base.metadata.create_all(bind=engine)
    # criar usuário administrador padrão se não houver usuário
    session = SessionLocal()
    try:
        existe = session.query(User).first()
        if not existe:
            admin = User(username="admin", role="admin")
            admin.set_password("admin123")  # troque após primeiro login
            session.add(admin)
            session.commit()
    finally:
        session.close()


# -------- Alunos CRUD --------
def inserir_aluno(**dados):
    session = SessionLocal()
    try:
        aluno = Aluno(
            nome=dados.get("nome"),
            idade=dados.get("idade"),
            pais=dados.get("pais"),
            passaporte=dados.get("passaporte"),
            serie=dados.get("serie"),
            data_entrada=dados.get("data_entrada"),
            responsavel=dados.get("responsavel"),
            observacoes=dados.get("observacoes"),
        )
        session.add(aluno)
        session.commit()
        session.refresh(aluno)
        return aluno
    finally:
        session.close()


def listar_alunos(filtros: dict = None):
    session = SessionLocal()
    try:
        q = session.query(Aluno)
        if filtros:
            if filtros.get("nome"):
                q = q.filter(Aluno.nome.ilike(f"%{filtros['nome']}%"))
            if filtros.get("pais"):
                q = q.filter(Aluno.pais == filtros["pais"])
            if filtros.get("serie"):
                q = q.filter(Aluno.serie == filtros["serie"])
            if filtros.get("data_inicio"):
                q = q.filter(Aluno.data_entrada >= filtros["data_inicio"])
            if filtros.get("data_fim"):
                q = q.filter(Aluno.data_entrada <= filtros["data_fim"])
        return q.all()
    finally:
        session.close()


def obter_aluno_por_id(aluno_id: int):
    session = SessionLocal()
    try:
        return session.query(Aluno).get(aluno_id)
    finally:
        session.close()


def atualizar_aluno(aluno_id: int, atualizacoes: dict):
    session = SessionLocal()
    try:
        aluno = session.query(Aluno).get(aluno_id)
        if not aluno:
            return None
        for chave, valor in atualizacoes.items():
            if hasattr(aluno, chave) and valor is not None:
                setattr(aluno, chave, valor)
        session.commit()
        session.refresh(aluno)
        return aluno
    finally:
        session.close()


def deletar_aluno(aluno_id: int):
    session = SessionLocal()
    try:
        aluno = session.query(Aluno).get(aluno_id)
        if not aluno:
            return False
        session.delete(aluno)
        session.commit()
        return True
    finally:
        session.close()


# -------- Presença --------
def registrar_presenca_entrada(aluno_id: int, quando: datetime = None, observacao: str = None):
    session = SessionLocal()
    try:
        agora = quando or datetime.now()
        pres = Presenca(aluno_id=aluno_id, data=agora.date(), hora_entrada=agora, observacao=observacao)
        session.add(pres)
        session.commit()
        session.refresh(pres)
        return pres
    finally:
        session.close()


def registrar_presenca_saida(presenca_id: int, quando: datetime = None):
    session = SessionLocal()
    try:
        pres = session.query(Presenca).get(presenca_id)
        if not pres:
            return None
        pres.hora_saida = quando or datetime.now()
        session.commit()
        session.refresh(pres)
        return pres
    finally:
        session.close()


def listar_presencas(aluno_id: int = None, data_inicio: date = None, data_fim: date = None):
    session = SessionLocal()
    try:
        q = session.query(Presenca)
        if aluno_id:
            q = q.filter(Presenca.aluno_id == aluno_id)
        if data_inicio:
            q = q.filter(Presenca.data >= data_inicio)
        if data_fim:
            q = q.filter(Presenca.data <= data_fim)
        return q.order_by(Presenca.data.desc(), Presenca.hora_entrada.desc()).all()
    finally:
        session.close()


# -------- Usuários --------
def criar_usuario(username: str, password: str, role: str = "user"):
    session = SessionLocal()
    try:
        existente = session.query(User).filter(User.username == username).first()
        if existente:
            return None
        u = User(username=username, role=role)
        u.set_password(password)
        session.add(u)
        session.commit()
        session.refresh(u)
        return u
    finally:
        session.close()


def autenticar_usuario(username: str, password: str):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        if user and user.check_password(password):
            return user
        return None
    finally:
        session.close()
