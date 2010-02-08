#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys
from functools import partial


from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

from PyQt4.QtCore import *
from PyQt4.QtGui  import *

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import pygments.util


from storage import FileStorage, get_languages

class AddDialog(QDialog):
    def __init__(self, parent=None):
        super(AddDialog, self).__init__(parent)
        self.parent = parent
        
        self.code_editor = QTextEdit(self)
        self.code_editor.setAcceptRichText(False)
        if os.name == 'nt':
            self.code_editor.setFontFamily("Courier")
        else:
            self.code_editor.setFontFamily("mono")
        
        
        self.tags_input = QLineEdit(self)
        self.tags_input.setMinimumWidth(300)
        self.tags_label = QLabel("&Tags:")
        self.tags_label.setBuddy(self.tags_input)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['Text'] + get_languages())
        self.lang_label = QLabel("&Language:")
        self.lang_label.setBuddy(self.lang_combo)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

        
        layout = QGridLayout()
        layout.addWidget(self.code_editor, 0, 0, 1, 2)
        layout.addWidget(self.tags_label,  1, 0)
        layout.addWidget(self.tags_input,  1, 1)
        layout.addWidget(self.lang_label,  2, 0)
        layout.addWidget(self.lang_combo,  2, 1)
        layout.addWidget(buttonBox,        3, 0, 1, 2)
        self.setLayout(layout)
        
        #self.connect(okButton, SIGNAL("clicked()"), self, SLOT("accept()"))
        #self.connect(cancelButton, SIGNAL("clicked()"), self, SLOT("reject()"))
        self.connect(buttonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        #self.connect(buttonBox, SIGNAL("accepted()"), self.on_add)
        #self.connect(buttonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.setWindowTitle("Add snippet")
        
    def reset_dialog(self):
        self.code_editor.clear()
        self.tags_input.setText('')
        self.lang_combo.setCurrentIndex(0)
        self.code_editor.setFocus()
        
    def on_add(self):
        dialog = self
        code = unicode(dialog.code_editor.toPlainText()).encode('utf8')
        tags = unicode(dialog.tags_input.text()).encode('utf8').split()
        lang = unicode(dialog.lang_combo.currentText()).encode('utf8').lower()
        print code, tags, lang
        self.parent.storage.add(code, tags, lang)
        #self.storage.add(code, tags, lang)
        #print 'stored'
        
       

    def accept(self):
        self.on_add()
        self.reset_dialog()
        self.hide()

    def reject(self):
        print 'reject'
        self.reset_dialog()
        self.hide()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        self.systray = QSystemTrayIcon(QIcon('icon.png'), self)
        self.systray.show()
        
        menu = QMenu(self)
        
        showAction = menu.addAction('Show')
        self.connect(showAction, SIGNAL("triggered()"), self.on_toogle)
        
        addAction = menu.addAction('Add')
        self.connect(addAction, SIGNAL("triggered()"), self.on_add)
        
        menu.addSeparator()
        
        exitAction = menu.addAction('Exit')
        self.connect(exitAction, SIGNAL("triggered()"), self.on_exit)
        
        menu.setDefaultAction(showAction)
        self.systray.setContextMenu(menu)
        self.connect(self.systray, SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.on_systray)
        
        
        #self.systray = KSystemTrayIcon(self)
        #self.systray.setIcon(QIcon(BarIcon("battery-charging")))
        #self.systray.show()
        #
        #menu = self.systray.contextMenu()
        #
        #suspendAction = self.systray.actionCollection().addAction("suspend")
        #suspendAction.setText("Suspend")
        #suspendAction.setIcon(QIcon('battery-charging'))
        ##sk =  KShortcut(Qt.CTRL + Qt.ALT + Qt.Key_N)
        #sk =  KShortcut(Qt.Key_F6)
        #suspendAction.setShortcut(sk)
        #suspendAction.setGlobalShortcut(sk)
        #self.connect(suspendAction, SIGNAL("triggered()"), self.on_toogle)
        #menu.addAction(suspendAction)
        
        
        self.storage = FileStorage()
        
        self.input = QLineEdit(self)
        self.input.setMinimumWidth(300)
        QObject.connect(self.input, SIGNAL('returnPressed()'), self.on_return)
        
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
        
        self.add_dialog = AddDialog(self)
    
    def closeEvent(self, event):
        self.setVisible(False)
        event.ignore()
    
    def on_exit(self):
        exit(0)
    
    def on_systray(self, reason):
        # QSystemTrayIcon.DoubleClick
        if reason == QSystemTrayIcon.Trigger:
            self.on_toogle()
        if reason == QSystemTrayIcon.MiddleClick:
            self. on_add()
    
    def on_toogle(self, *a):
        print a
        self.setVisible(not self.isVisible())
    
    def on_add(self):
        self.add_dialog.show()
        
    def on_copy(self, nr):
        nr = nr - 1;
        if nr < len(self.result):
            text = self.result[nr][0]
            QApplication.clipboard().setText(text)
            self.close()
    
    def on_return(self, *a):
        query = unicode(self.input.text()).encode('utf-8').split()
        
        result = self.storage.search(query)
        self.set_results(result, query)
    
    def on_escape(self, *a):
        self.set_results([])
        self.input.setText('')
        self.setVisible(False)
    
    def set_results(self, results, query_tags=[]):
        self.result = results
        if results:
            data = ['<table width="100%" cellspacing="0">']
            for i, r in enumerate(results):
                try:
                    lexer = get_lexer_by_name(r[2], stripall=True, tabsize=4)
                except pygments.util.ClassNotFound:
                    lexer = get_lexer_by_name('text', stripall=True, tabsize=4)
                formatter = HtmlFormatter(linenos=False, noclasses=True)
                code = highlight(r[0].rstrip(), lexer, formatter)
                sufix = '</pre></div>\n'
                if code.endswith(sufix):
                    code = code[:-len(sufix)].rstrip() + sufix
                code = code.rstrip()
                print `code`
                #tags = ' '.join(['<b>%s</b>' % tag for tag in r[1]])
                tags = []
                for tag in sorted(list(r[1])):
                    if tag in query_tags:
                        tags.append('<b>%s</b>' % tag)
                    else:
                        tags.append(tag)
                tags = ' '.join(tags)
                data.append('<tr style="background-color:%s"><td width="1%%"><div style="font-size:32px; margin: 10px">%d</div></td><td>%s%s</td></tr>' % (['#cccccc', '#dddddd'][i % 2], i + 1, code, tags))
            data.append('</table>')
            text = '\n'.join(data)
            
            self.results.show()
            self.results.setText(text)
        else:
            self.results.hide()


if __name__ == "__main__":
    #aboutData = KAboutData (
    #    "python-kde-tutorial", "", ki18n("PyKDE Tutorial"), "0.2", ki18n("A Small Qt WebKit Example"),
    #    KAboutData.License_GPL, ki18n("(c) 2008 Krzysztof Kosyl"),
    #    ki18n("none"), "www.kubuntu.org", ''
    #)
    #KCmdLineArgs.init(sys.argv, aboutData)
    #app = KApplication()
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    
    main_window.show()
    
    sys.exit(app.exec_())

