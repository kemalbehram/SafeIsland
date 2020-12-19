from pydal import DAL, Field
db = DAL("sqlite://certificates.sqlite")
tb = db.define_table(
    "certificate",
    Field("diag_id", type="text", unique=True, notnull=True),
    Field("hash", type="text", unique=True, notnull=True),
    Field("cert", type="text", notnull=True),
    migrate=False
    )

print(tb)

for row in db().select(db.certificate.ALL):
    print(row.diag_id)