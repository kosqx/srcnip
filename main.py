#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
from functools import partial


from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

from PyQt4.QtCore import *
from PyQt4.QtGui  import *

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


from storage import FileStorage 


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        self.systray = KSystemTrayIcon(self)
        self.systray.setIcon(QIcon(BarIcon("battery-charging")))
        self.systray.show()
        
        menu = self.systray.contextMenu()
        
        suspendAction = self.systray.actionCollection().addAction("suspend")
        suspendAction.setText("Suspend")
        suspendAction.setIcon(QIcon('battery-charging'))
        #sk =  KShortcut(Qt.CTRL + Qt.ALT + Qt.Key_N)
        sk =  KShortcut(Qt.Key_F6)
        suspendAction.setShortcut(sk)
        suspendAction.setGlobalShortcut(sk)
        self.connect(suspendAction, SIGNAL("triggered()"), self.on_toogle)
        menu.addAction(suspendAction)

        self.storage = FileStorage()
        
        self.input = QLineEdit(self)
        self.input.setMinimumWidth(300)
        QObject.connect(self.input, SIGNAL('returnPressed()'), self.on_return)
        
        #self.editor = QTextEdit()
        #self.editor.setAcceptRichText(False)
        self.results = QLabel("")
        
        self.central = QWidget()

        self._layout = QVBoxLayout()
        
        self._layout.addWidget(self.input)
        self._layout.addWidget(self.results)
        
        self._layout.setSizeConstraint(QLayout.SetFixedSize)
        self.central.setLayout(self._layout)
        self.layout().setSizeConstraint(QLayout.SetFixedSize)
        
        self.setCentralWidget(self.central)
        self.setWindowTitle("Snipper clip")

        for i in xrange(0, 10):
            shortcut = QShortcut(self)
            shortcut.setKey("Ctrl+%d" % i)
            self.connect(shortcut, SIGNAL("activated()"), partial(self.on_copy, i))
            
        shortcut = QShortcut(self)
        shortcut.setKey("Esc")
        self.connect(shortcut, SIGNAL("activated()"), self.on_escape)
    
    def closeEvent(self, event):
        self.setVisible(False)
        event.ignore()
    
    def on_toogle(self, *a):
        self.setVisible(not self.isVisible())
    
    def on_copy(self, nr):
        nr = nr - 1;
        if nr < len(self.result):
            text = self.result[nr][0]
            QApplication.clipboard().setText(text)
            self.close()
    
    def on_return(self, *a):
        query = unicode(self.input.text()).encode('utf-8').split()
        
        result = self.storage.search(query)
        self.set_results(result)
    
    def on_escape(self, *a):
        self.set_results([])
        self.input.setText('')
        self.setVisible(False)
    
    def set_results(self, results):
        self.result = results
        if results:
            data = ['<table>']
            for i, r in enumerate(results):
                lexer = get_lexer_by_name("python", stripall=True)
                formatter = HtmlFormatter(linenos=False, noclasses=True)
                code = highlight(r[0], lexer, formatter)
                tags = ' '.join(['<b>%s</b>' % tag for tag in r[1]])
                data.append('<tr><td><div style="font-size:32px; margin-right: 10px">%d</div></td><td>%s%s</td></tr>' % (i, code, tags))
            data.append('</table>')
            text = '\n'.join(data)
            
            self.results.show()
            self.results.setText(text)
        else:
            self.results.hide()
    

if __name__ == "__main__":
    aboutData = KAboutData (
        "python-kde-tutorial", "", ki18n("PyKDE Tutorial"), "0.2", ki18n("A Small Qt WebKit Example"),
        KAboutData.License_GPL, ki18n("(c) 2008 Krzysztof Kosyl"),
        ki18n("none"), "www.kubuntu.org", ''
    )
    KCmdLineArgs.init(sys.argv, aboutData)
    app = KApplication()
    
    main_window = MainWindow()
    #main_window.show()
    
    sys.exit(app.exec_())

