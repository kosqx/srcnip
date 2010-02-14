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


from storage import FileStorage, Snippet
from languages import languages


def format_code(code, lang):
    MAX_LINES = 5
    lines = code.splitlines()
    if len(lines) > MAX_LINES:
        result = []
        for line in lines:
            if line.strip():
                result.append(line)
        code = '\n'.join(result[:MAX_LINES])
    
    try:
        lexer = get_lexer_by_name(lang, stripall=True, tabsize=4)
    except pygments.util.ClassNotFound:
        lexer = get_lexer_by_name('text', stripall=True, tabsize=4)
    formatter = HtmlFormatter(linenos=False, noclasses=True)
    code = highlight(code.rstrip(), lexer, formatter)
    sufix = '</pre></div>\n'
    if code.endswith(sufix):
        code = code[:-len(sufix)].rstrip() + sufix
    code = code.rstrip()
    
    return code


def add_combo_items(combo, items):
    combo.clear()
    for item in items:
        if item is None:
            if hasattr(combo, 'insertSeparator'):
                combo.insertSeparator(1000)
            else:
                combo.insertItem(1000, '----')
        else:
            combo.insertItem(1000, item)


def popular_list(popular_dict):
    result = [(-popular_dict[key], u'%s' % languages[key].name) for key in popular_dict if key]
    result.sort()
    tmp = [b for a, b in result[:5]]
    if tmp:
        tmp.append(None)
    return tmp


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
        
        self.reset_dialog()
    
    def reset_dialog(self):
        add_combo_items(self.lang_combo, ['Text', None] + popular_list(self.parent.storage.lang_count()) + languages.get_names())
        
        self.code_editor.clear()
        self.tags_input.setText('')
        self.lang_combo.setCurrentIndex(0)
        self.code_editor.setFocus()
    
    def on_add(self):
        code = unicode(self.code_editor.toPlainText())
        tags = unicode(self.tags_input.text())
        lang = unicode(self.lang_combo.currentText())
        
        self.parent.storage.add(Snippet(code, tags, lang))
    
    def closeEvent(self, event):
        self.reject()
        event.ignore()
    
    def accept(self):
        self.on_add()
        self.reset_dialog()
        self.hide()
    
    def reject(self):
        self.reset_dialog()
        self.hide()


class MainWindow(QDialog):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        
        self.storage   = FileStorage()
        #self.languages = Languages()
        
        
        self.setWindowTitle("Snipper clip")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        
        # -----------------------------------------------------------
        # Window layout
        self.input = QLineEdit(self)
        self.input.setMinimumWidth(300)
        QObject.connect(self.input, SIGNAL('returnPressed()'), self.on_return)
        
        self.outcome = QLabel("")
        
        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.outcome)
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
        
        create_shortcut("Ctrl+Up",   self.on_page, 'prev')
        create_shortcut("Ctrl+Down", self.on_page, 'next')
        create_shortcut("Up",   self.on_page, 'prev')
        create_shortcut("Down", self.on_page, 'next')
        
        
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
        if nr < (len(self.search_results) - 10 * self.search_page):
            text = self.search_results[10 * self.search_page + nr].code
            QApplication.clipboard().setText(text)
            self.close()
    
    def on_delete(self, nr):
        nr = nr - 1;
        if nr < (len(self.search_results) - 10 * self.search_page):
            reply = QMessageBox.question(
                self,
                "Snipper - delete snippet",
                "Delete snippet?",
                QMessageBox.Yes|QMessageBox.Default,
                QMessageBox.No|QMessageBox.Escape
            )
            if reply:
                text = self.search_results[10 * self.search_page + nr].code
                self.close()
    
    def on_return(self, *a):
        query = unicode(self.input.text()).encode('utf-8').split()
        
        result = self.storage.search(query)
        self.set_results(result, query)
        
    def on_page(self, where):
        if where == 'prev':
            page = self.search_page - 1
        if where == 'next':
            page = self.search_page + 1
        if where == 'first':
            page = 0
        if where == 'last':
            page = 1000000
        
        self.search_page = min(max(page, 0), self.search_pages - 1)
        
        self.display_page()
    
    def on_escape(self, *a):
        self.set_results([])
        self.input.setText('')
        self.setVisible(False)
    
    def set_results(self, results, query_tags=[]):
        self.search_results = results
        self.search_tags = query_tags
        self.search_page = 0
        self.search_pages = (len(results) - 1) / 10 + 1
        
        self.display_page()
    
    def display_page(self):
        results = self.search_results[self.search_page * 10: self.search_page * 10 + 10]
        query_tags = self.search_tags
        
        if results:
            data = []
            if self.search_pages > 1:
                data.append('Page %d of %d <br />' % (self.search_page + 1, self.search_pages))
            data.append('<table width="100%" cellspacing="0">')
            for i, r in enumerate(results):
                code = format_code(r.code, r.lang)
                
                tags = []
                for tag in sorted(list(r.tags)):
                    if tag in query_tags:
                        tags.append('<b>%s</b>' % tag)
                    else:
                        tags.append(tag)
                tags = ' '.join(tags)
                
                if r.lang in languages:
                    lang = u' - <i>%s</i>' % languages[r.lang].name
                else:
                    lang = ''
                
                data.append('<tr style="background-color:%s"><td width="1%%"><div style="font-size:32px; margin: 10px">%s</div></td><td>%s%s%s</td></tr>' % (['#cccccc', '#dddddd'][i % 2], str(i + 1)[-1], code, tags, lang))
            data.append('</table>')
            text = '\n'.join(data)
            
            self.outcome.show()
            self.outcome.setText(text)
        else:
            self.outcome.hide()


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

