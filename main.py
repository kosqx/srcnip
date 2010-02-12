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


from storage import FileStorage
from languages import Languages


def add_combo_items(combo, items):
    for item in items:
        if item is None:
            if hasattr(combo, 'insertSeparator'):
                combo.insertSeparator(1000)
            else:
                combo.insertItem(1000, '----')
        else:
            combo.insertItem(1000, item)


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
        add_combo_items(self.lang_combo, ['Text', None] + self.parent.languages.get_names())
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
        
        self.connect(buttonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
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
    
    def closeEvent(self, event):
        self.reject()
        event.ignore()
    
    def accept(self):
        self.on_add()
        self.reset_dialog()
        self.hide()
    
    def reject(self):
        print 'reject'
        self.reset_dialog()
        self.hide()


class MainWindow(QDialog):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        
        self.storage   = FileStorage()
        self.languages = Languages()
        
        
        self.setWindowTitle("Snipper clip")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        
        # -----------------------------------------------------------
        # Window layout
        self.input = QLineEdit(self)
        self.input.setMinimumWidth(300)
        QObject.connect(self.input, SIGNAL('returnPressed()'), self.on_return)
        
        self.results = QLabel("")
        
        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.results)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(layout)
        
        
        # -----------------------------------------------------------
        # In window shortcuts
        def create_shortcut(keys, slot, *args):
            shortcut = QShortcut(self)
            shortcut.setKey(keys)
            if slot:
                if args:
                    QObject.connect(shortcut, SIGNAL("activated()"), partial(slot, *args))
                else:
                    QObject.connect(shortcut, SIGNAL("activated()"), slot)
            
        for i in xrange(0, 10):
            create_shortcut("Ctrl+%d" % i, self.on_copy, i)
            create_shortcut("Shift+Ctrl+%d" % i, self.on_delete, i)
            
        create_shortcut("Esc", self.on_escape)
        
        
        # -----------------------------------------------------------
        # Systray and global shortcuts
        self.systray = KSystemTrayIcon(self)
        self.systray.setIcon(QIcon('icon.png'))
        self.systray.show()
        
        def add_action(systray, id, text, icon, shortcut, slot):
            action = systray.actionCollection().addAction(id)
            action.setText(text)
            action.setIcon(icon)
            if shortcut:
                shortcut =  KShortcut(shortcut)
                action.setShortcut(shortcut)
                action.setGlobalShortcut(shortcut)
            self.connect(action, SIGNAL("triggered()"), slot)
            
            menu = systray.contextMenu()
            menu.addAction(action)
            
        add_action(self.systray, 'find-snippet', "Find snippet", QIcon('icon.png'), 'Ctrl+Alt+B', self.on_toogle)
        add_action(self.systray, 'add-snippet',  "Add snippet",  QIcon('icon.png'), 'Ctrl+Alt+N', self.on_add)
        
        
        self.add_dialog = AddDialog(self)
        self.set_results([])
    
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
            self.on_add()
    
    def on_toogle(self, *a):
        if self.isVisible():
            self.hide()
        else:
            self.show()
    
    def on_add(self):
        self.add_dialog.show()
        
    def on_copy(self, nr):
        nr = nr - 1;
        if nr < len(self.result):
            text = self.result[nr][0]
            QApplication.clipboard().setText(text)
            self.close()
    
    def on_delete(self, nr):
        nr = nr - 1;
        if nr < len(self.result):
            reply = QMessageBox.question(
                self,
                "Snipper - delete snippet",
                "Delete snippet?",
                QMessageBox.Yes|QMessageBox.Default,
                QMessageBox.No|QMessageBox.Escape
            )
            if reply:
                text = self.result[nr][0]
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
    aboutData = KAboutData (
        "snipper", "", ki18n("Code Snipper"), "0.2", ki18n("Easy acces to code snippets"),
        KAboutData.License_GPL, ki18n("(c) 2008 Krzysztof Kosyl"),
        ki18n("none"), "www.examlpe.com", ''
    )
    KCmdLineArgs.init(sys.argv, aboutData)
    app = KApplication()
    
    main_window = MainWindow()
    sys.exit(app.exec_())

