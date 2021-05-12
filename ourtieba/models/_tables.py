from sqlalchemy import Column, Integer, Table, ForeignKey

from ..database import my_db

user_report_table = Table("user_report", my_db.Base.metadata,
                          Column("Uid", Integer, ForeignKey("user.Uid")),
                          Column("Rid", Integer, ForeignKey("report.Rid"))
                          )
