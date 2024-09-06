from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from openai import AzureOpenAI
import pysrt
from tkinter import filedialog
import os
from utils import filename, rm_pm
import datetime
import vlc

OUTPUT_PATH = ".\output"

client = AzureOpenAI(
    azure_endpoint="https://openai-translation.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-03-15-preview",
    api_key="d5069013ce5942f4b8f7500a96f91793",
    api_version="2023-03-15-preview"
)


def on_ai():
    # 获取当前选中的行数
    selected_row = view.selectedIndexes()[0].row()

    # 获取选中行的数据
    model = view.model()
    selected_data = model.data(model.index(selected_row, 1))
    print(f"行索引：{selected_row}，数据：{selected_data}")

    # 前一行英文
    bw_index = selected_row - 1
    bw_data = ""
    if bw_index >= 0:
        bw_data = model.data(model.index(bw_index, 2))

    # 当前行英文
    c_data = model.data(model.index(selected_row, 2))

    # 后一行
    fw_index = selected_row + 1
    num_rows = model.rowCount()
    fw_data = ""
    if fw_index <= num_rows:
        fw_data = model.data(model.index(fw_index, 2))

    print(f"前一行英文：{bw_data}，当前行英文：{c_data}，后一行英文：{fw_data}")

    # 获取前一行，当前行和后一行英文原文，来校准当前行中文，并要求给出3个备选
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "system", "content": f"你是个很有用的内容校准优化助手"},
            {"role": "system", "content": "校准文本以体育训练和电子学内容为主"},
            {"role": "system", "content": "你会参考当前内容的上下文进行校准"},
            {"role": "user", "content": f"给出以下文字的3个中文校准备选方案:\n {selected_data} \n "},
            {"role": "user", "content": f"它的前一句英文原文是:\n {bw_data} \n 它自己的英文原文是:\n {c_data} \n 它的下一句英文原文是:\n {fw_data}"},
        ],
        temperature=0.5
    )

    result = rm_pm(response.choices[0].message.content)
    text_edit.setText(result)


def on_save():
    modified_data = model.getModifiedData()
    if len(sub_file_paths) == 0 or len(modified_data) == 0:
        return

    srt_proofing_path = sub_file_paths[0]
    subs = pysrt.open(srt_proofing_path)

    for md in modified_data:
        # print(subs[md[0]].text)
        subs[md[0]].text = md[2]

    dt_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    srt_path_proofed = os.path.join(
        OUTPUT_PATH, f"{filename(srt_proofing_path)}_p_{dt_str}.srt")

    subs.save(srt_path_proofed)


def cvt_t_str_ms(t_str: str):
    time_parts = t_str.split(":")
    ret = 0
    if len(time_parts) > 0:
        h = int(time_parts[0])
        m = int(time_parts[1])
        s_ms_parts = time_parts[2].split(",")
        s = 0
        ms = 0
        if len(s_ms_parts) > 0:
            s = int(s_ms_parts[0])
            ms = int(s_ms_parts[1])

        h_ms = h * 3600000
        m_ms = m * 60000
        s_ms = s * 1000
        ret = h_ms + m_ms + s_ms + ms

    return ret


def row_sel(selected, deselected):
    # 获取当前选中的行数
    selected_row = view.selectedIndexes()[0].row()
    selected_col = view.selectedIndexes()[0].column()

    # 获取选中行的数据
    model = view.model()
    selected_data = model.data(model.index(selected_row, selected_col))
    print(f"行索引：{selected_row}，列索引：{selected_col}，数据：{selected_data}")
    text_edit.setText(selected_data)

    if selected_col == 0:
        player.set_time(cvt_t_str_ms(selected_data))
        player.play()

        pause_prev_btn.setText("暂停视频预览")


subs_col_text = []
sub_file_paths = []


def on_header_clicked(col_i):
    if col_i not in range(1, 3):
        return

    global sub_file_path
    sub_file_path = filedialog.askopenfilename(
        filetypes=[("SRT files", "*.srt"), ("All files", "*.*")])

    if sub_file_path == "":
        return
    else:
        sub_file_paths.append(sub_file_path)

    subs = pysrt.open(sub_file_path)
    for sub in subs:
        if col_i == 1:
            subs_col_text.append([sub.start, rm_pm(sub.text), ""])
        else:
            subs_col_text[sub.index-1][2] = sub.text

    if len(subs_col_text[0][1]) > 0 and len(subs_col_text[0][2]) > 0:
        model.initData(subs_col_text)
    # else:
    #     QMessageBox.information(window, "提示", "无效字幕文件")


instance = vlc.Instance()
player = instance.media_player_new()


def on_prev():
    v_file_path = filedialog.askopenfilename(
        filetypes=[("Video files", "*.mp4"), ("All files", "*.*")])

    media = instance.media_new(v_file_path)
    player.set_media(media)

    # 播放视频
    player.play()
    # time.sleep(0.5)
    # player.pause()

    # 定位视频的播放时间
    # player.set_time(500000)


def on_pause_player():
    if player.is_playing():
        # Stop the media player
        player.pause()
        pause_prev_btn.setText("恢复视频预览")
    else:
        player.play()
        pause_prev_btn.setText("暂停视频预览")

    # Release the VLC instance
    # time.sleep(3)
    # instance.release()


def on_close_player():
    # Stop the media player
    player.stop()

    # Release the VLC instance
    instance.release()


# 创建一个数据模型类，继承自 QStandardItemModel


class MyStandardItemModel(QStandardItemModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._data = data
        self._header = ["开始时间", "中文字幕", "英文字幕"]
        self._modified_cells = []  # 用于保存被修改的单元格的索引
        self._populateModel()

    def _populateModel(self):
        # 设置表格的标题行
        self.setHorizontalHeaderLabels(self._header)

        # 添加数据行
        for row in range(len(self._data)):
            data_row = [QStandardItem(str(val)) for val in self._data[row]]
            self.appendRow(data_row)

    def flags(self, index):
        # 重写 flags() 方法，设置指定单元格为可编辑状态
        if index.column() == 0 or index.column() == 2:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        # 重写 setData() 方法，将编辑后的数据保存到 self._data 中
        row = index.row()
        col = index.column()
        # 如果修改值不变就不触发修改
        if str(self._data[row][col]) == value:
            return True
        self._data[row][col] = value
        self._modified_cells.append(index)
        return super().setData(index, value, role)

    def isModified(self, index):
        # 判断指定单元格是否被修改过
        return index in self._modified_cells

    def getModifiedData(self):
        # 获取被修改过的单元格的数据
        data = []
        for index in self._modified_cells:
            row = index.row()
            col = index.column()
            data.append([row, col, self.data(index)])
        return data

    def initData(self, data):
        # 初始化表格数据源
        self._data = data
        self._populateModel()


# 创建应用程序对象
app = QApplication([])

# 创建一个数据模型实例
model = MyStandardItemModel([])

# 创建一个表格视图实例
view = QTableView()

# 将数据模型设置为表格视图的模型
view.setModel(model)

# 设置表格列的宽度比例
view.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

# 设置表格属性和事件
view.setEditTriggers(QTableWidget.DoubleClicked)
view.setMinimumHeight(700)
view.setSelectionMode(QTableWidget.SingleSelection)
view.setWordWrap(True)
view.resizeColumnsToContents()
view.setSortingEnabled(False)
view.setShowGrid(False)
view.setColumnWidth(0, 110)
view.setColumnWidth(1, 800)
view.setColumnWidth(2, 700)
# view.setFont(QtGui.QFont("YaHei", 9))
view.setAutoScroll(True)
view.setStyleSheet("""
    QTableView {
        border: 2px solid #999999;
        gridline-color: #cccccc;
    }
    
    QTableView::item {
        border: 1px solid #999999;
    }
    
    QTableView::item:selected {
        background-color: #a2c4cc;
        color: #ffffff;
    }
""")


# 创建一个委托类，用于处理编辑单元格的委托事件


class MyItemDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QTextEdit(parent)
        editor.setLineWrapMode(QTextEdit.WidgetWidth)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        value = editor.toPlainText()
        model.setData(index, value, Qt.EditRole)

        # # 调整行高
        # row = index.row()

        # text_height = editor.document().size().height()
        # if text_height > 0:
        #     text_height += editor.document().documentMargin() * 2

        # view.setRowHeight(row, int(text_height))

    def updateEditorGeometry(self, editor, option, index):
        size_hint = self.sizeHint(option, index)
        option.rect.setHeight(size_hint.height()+50)

        row = index.row()
        editor_height = view.rowHeight(row)
        view.setRowHeight(row, size_hint.height()+50)

        editor.setGeometry(option.rect)

    def sizeHint(self, option, index):
        text = index.data()
        font = option.font
        document = QtGui.QTextDocument()
        document.setDefaultFont(font)
        document.setPlainText(text)
        size = document.size().toSize()
        return size

    def paint(self, painter, option, index):
        # 重写 paint() 方法，在绘制单元格时绘制被修改过的单元格的背景色
        model = index.model()
        if model.isModified(index):
            painter.save()
            painter.fillRect(option.rect, QColor(255, 255, 0))
            painter.restore()
        QStyledItemDelegate.paint(self, painter, option, index)

    def destroyEditor(self, editor, index):
        row = index.row()
        text_height = editor.document().size().height()
        if text_height > 0:
            text_height += editor.document().documentMargin() * 2

        view.setRowHeight(row, int(text_height))

        # editor_height = view.rowHeight(row)
        # if text_height < editor_height:
        #     view.setRowHeight(row, int(text_height))
        # else:
        #     view.setRowHeight(row, editor_height)
        QtWidgets.QStyledItemDelegate.destroyEditor(self, editor, index)


# 创建一个委托实例
delegate = MyItemDelegate()

# 设置表格视图的委托为委托实例
view.setItemDelegate(delegate)

# 获取表格视图的选择模型
selection_model = view.selectionModel()

# 将选择模型的 selectionChanged 信号连接到槽函数中
selection_model.selectionChanged.connect(row_sel)

# 获取表格视图的水平表头
header = view.horizontalHeader()

# 将水平表头的 clickable 属性设置为 True，以启用单击事件
header.setSectionsClickable(True)

# 将水平表头的 sectionClicked 信号连接到处理函数
header.sectionDoubleClicked.connect(on_header_clicked)

# 创建一个 QWidget 实例
window = QWidget()

# 设置窗口的大小
window.resize(1680, 960)

# 创建一个垂直布局管理器
layout = QVBoxLayout()

# 将表格添加到布局管理器中
# layout.addWidget(table)

# 将表格视图添加到布局管理器中
layout.addWidget(view)

v_prev_btn = QPushButton("打开视频预览")
pause_prev_btn = QPushButton("暂停视频预览")
close_prev_btn = QPushButton("关闭视频预览")

v_prev_btn.setFixedHeight(30)
pause_prev_btn.setFixedHeight(30)
close_prev_btn.setFixedHeight(30)

v_prev_btn.clicked.connect(on_prev)
pause_prev_btn.clicked.connect(on_pause_player)
close_prev_btn.clicked.connect(on_close_player)

layout.addWidget(v_prev_btn)
layout.addWidget(pause_prev_btn)
layout.addWidget(close_prev_btn)

# 创建一个 QTextEdit 实例
text_edit = QTextEdit()
text_edit.setMinimumHeight(300)

layout.addWidget(text_edit)


upd_btn = QPushButton("获取校准建议")
save_btn = QPushButton("保存修改")

upd_btn.setFixedHeight(30)
save_btn.setFixedHeight(30)

upd_btn.clicked.connect(on_ai)
save_btn.clicked.connect(on_save)

layout.addWidget(upd_btn)
layout.addWidget(save_btn)

# 将布局管理器设置为窗口的主布局
window.setLayout(layout)
window.setFont(QtGui.QFont("KaiTi", 12))

# 显示窗口
window.show()

# 运行应用程序
app.exec_()
