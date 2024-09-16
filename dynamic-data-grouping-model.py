import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QTreeView, QHBoxLayout, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex

class Item:
    def __init__(self, name, category):
        self.name = name
        self.category = category

class DynamicGroupModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()
        self._items = []
        self._grouped = False
        self._categories = set()

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        if not parent.isValid():
            if self._grouped:
                return self.createIndex(row, column, list(self._categories)[row])
            else:
                return self.createIndex(row, column, self._items[row])
        
        parent_item = parent.internalPointer()
        if isinstance(parent_item, str):  # It's a category
            children = [item for item in self._items if item.category == parent_item]
            return self.createIndex(row, column, children[row])
        
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        
        child_item = index.internalPointer()
        if isinstance(child_item, Item) and self._grouped:
            category_index = list(self._categories).index(child_item.category)
            return self.createIndex(category_index, 0, child_item.category)
        
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0
        
        if not parent.isValid():
            return len(self._categories) if self._grouped else len(self._items)
        
        if self._grouped and isinstance(parent.internalPointer(), str):
            category = parent.internalPointer()
            return len([item for item in self._items if item.category == category])
        
        return 0

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role != Qt.DisplayRole:
            return None
        
        item = index.internalPointer()
        if isinstance(item, Item):
            return item.name
        return item

    def toggleGrouping(self):
        self.layoutAboutToBeChanged.emit()
        self._grouped = not self._grouped
        self.layoutChanged.emit()

    def addItem(self, name, category):
        self.layoutAboutToBeChanged.emit()
        self._items.append(Item(name, category))
        self._categories.add(category)
        self.layoutChanged.emit()

    def removeItem(self, name):
        self.layoutAboutToBeChanged.emit()
        for item in self._items:
            if item.name == name:
                self._items.remove(item)
                if not any(i.category == item.category for i in self._items):
                    self._categories.remove(item.category)
                break
        self.layoutChanged.emit()

class DynamicGroupingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Add item controls
        addLayout = QHBoxLayout()
        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("Item Name")
        self.categoryInput = QLineEdit()
        self.categoryInput.setPlaceholderText("Category")
        self.addButton = QPushButton("Add Item")
        self.addButton.clicked.connect(self.onAddItem)
        addLayout.addWidget(self.nameInput)
        addLayout.addWidget(self.categoryInput)
        addLayout.addWidget(self.addButton)
        layout.addLayout(addLayout)

        # Remove item control
        removeLayout = QHBoxLayout()
        self.removeInput = QLineEdit()
        self.removeInput.setPlaceholderText("Item Name to Remove")
        self.removeButton = QPushButton("Remove Item")
        self.removeButton.clicked.connect(self.onRemoveItem)
        removeLayout.addWidget(self.removeInput)
        removeLayout.addWidget(self.removeButton)
        layout.addLayout(removeLayout)

        # Toggle grouping button
        self.toggleButton = QPushButton("Toggle Grouping")
        self.toggleButton.clicked.connect(self.onToggleGrouping)
        layout.addWidget(self.toggleButton)

        # Tree view
        self.treeView = QTreeView()
        layout.addWidget(self.treeView)

        self.model = DynamicGroupModel()
        self.treeView.setModel(self.model)

        self.setLayout(layout)
        self.setWindowTitle('Dynamic Grouping Example')
        self.setGeometry(300, 300, 400, 500)

    def onAddItem(self):
        name = self.nameInput.text()
        category = self.categoryInput.text()
        if name and category:
            self.model.addItem(name, category)
            self.nameInput.clear()
            self.categoryInput.clear()
            self.treeView.expandAll()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter both name and category.")

    def onRemoveItem(self):
        name = self.removeInput.text()
        if name:
            self.model.removeItem(name)
            self.removeInput.clear()
            self.treeView.expandAll()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter the name of the item to remove.")

    def onToggleGrouping(self):
        self.model.toggleGrouping()
        self.treeView.expandAll()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DynamicGroupingWidget()
    ex.show()
    sys.exit(app.exec_())
