from sqlalchemy import Column, Integer, Table, ForeignKey
from ..database import Base


user_report_table = Table("user_report", Base.metadata,
                          Column("Uid", Integer, ForeignKey("user.Uid")),
                          Column("Rid", Integer, ForeignKey("report.Rid"))
                          )