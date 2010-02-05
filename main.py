#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
from functools import partial


from PyQt4.QtCore import *
from PyQt4.QtGui  import *


from storage import FileStorage 


class StartQT4(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        self.register_key()
        
        self.storage = FileStorage()
        
        self.input = QLineEdit(self)
        QObject.connect(self.input, SIGNAL('returnPressed()'), self.on_return)
        
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        
        self.central = QWidget()

        self.layout = QVBoxLayout()
        
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.editor)
        
        self.central.setLayout(self.layout)
        self.setCentralWidget(self.central)
        self.setWindowTitle("Snipper clip")

        for i in xrange(0, 10):
            shortcut = QShortcut(self)
            shortcut.setKey("Ctrl+%d" % i)
            self.connect(shortcut, SIGNAL("activated()"), partial(self.on_copy, i))
            
        shortcut = QShortcut(self)
        shortcut.setKey("F11")
        self.connect(shortcut, SIGNAL("activated()"), partial(self.on_copy, 1234))
        
        #self.setCentralWidget(self.central)
        #self.resize(self.minimumSizeHint().expandedTo(QSize(600, 300)))
        #QObject.connect(self.button, SIGNAL("clicked()"), self.on_save)
        
        #self.timer = QTimer(self)
        #QObject.connect(self.timer, SIGNAL('timeout()'), self.on_timer)
        #self.timer.start(200)

    #def closeEvent(self, event):
    #    self.on_save()
    #
    
    def register_key(self):
        pass
    
    def on_copy(self, nr):
        nr = nr - 1;
        if nr < len(self.result):
            text = self.result[nr][0]
            QApplication.clipboard().setText(text)
            self.close()
    
    def on_return(self, *a):
        print a
        query = unicode(self.input.text()).encode('utf-8').split()
        
        result = self.storage.search(query)
        self.result = result
        
        text = '\n----\n'.join(['%s:\n%s\ntags: %s' % (str(nr+1)[-1], i[0], ' '.join(i[1])) for nr, i in enumerate(result[:10])])
        self.editor.setPlainText(text)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())
