from datetime import datetime
from typing import List
from PySide6.QtCore import Qt, QAbstractTableModel


class PendingItemsTableModel(QAbstractTableModel):
    def __init__(self,data:List[List]):
        super(PendingItemsTableModel,self).__init__()
        self._data=data
    def data(self,index,role=Qt.ItemDataRole.DisplayPropertyRole):
        if role==Qt.ItemDataRole.DisplayPropertyRole:
            value=self._data[index.row()][index.column()]
            if isinstance(value,datetime):
                return value.strftime(r"%H:%M:%S")
            if isinstance(value,float):
                return "%.2f"%value
            if isinstance(value,str):
                return '"%s"' % value
            return value
    def rowCount(self,parent=None):
        return len(self._data)
    def columnCount(self,parent=None):
        return len(self._data[0])
