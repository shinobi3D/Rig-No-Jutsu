import maya.cmds as cmds
import maya.mel as mel
from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QAction, QMenu, QLabel, QMessageBox
from PySide2.QtCore import Qt, QUrl
from PySide2.QtGui import QDesktopServices
import json

cmds.optionVar(stringValue=("source_items",''))
cmds.optionVar(stringValue=("target_items",''))

class MayaGUI(QMainWindow):
    def __init__(self):
        super(MayaGUI, self).__init__()

        self.setWindowTitle("Copy Weights To Vert Selection")
        self.setFixedSize(400, 400)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # Set window flag to stay on top

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Create the first row layout
        row_layout1 = QHBoxLayout()
        main_layout.addLayout(row_layout1)

        # Create the first column layout
        column_layout1 = QVBoxLayout()
        row_layout1.addLayout(column_layout1)

        self.label1 = QLabel("Source Mesh:")
        column_layout1.addWidget(self.label1)

        self.list_widget1 = QListWidget()
        column_layout1.addWidget(self.list_widget1)

        self.label1 = QLabel("Source Skin Cluster:")
        column_layout1.addWidget(self.label1)

        self.list_widget3 = QListWidget()
        column_layout1.addWidget(self.list_widget3)

        self.button1 = QPushButton("Add Source Mesh")
        self.button1.clicked.connect(self.populate_list)
        column_layout1.addWidget(self.button1)

        self.button3 = QPushButton("Select Object")
        self.button3.clicked.connect(self.select_objects)
        column_layout1.addWidget(self.button3)

        self.button5 = QPushButton("Clear Selection")
        self.button5.clicked.connect(self.clear_object_list)
        column_layout1.addWidget(self.button5)

        # Create the second column layout
        column_layout2 = QVBoxLayout()
        row_layout1.addLayout(column_layout2)

        self.label3 = QLabel("Target Verts:")
        self.label3.setAlignment(Qt.AlignRight)
        column_layout2.addWidget(self.label3)

        self.list_widget2 = QListWidget()
        column_layout2.addWidget(self.list_widget2)

        self.button2 = QPushButton("Add Verts")
        self.button2.clicked.connect(self.populate_vertex_list)
        column_layout2.addWidget(self.button2)

        self.button4 = QPushButton("Select Verts")
        self.button4.clicked.connect(self.select_verts)
        column_layout2.addWidget(self.button4)

        self.button6 = QPushButton("Clear Selection")
        self.button6.clicked.connect(self.clear_vert_list)
        column_layout2.addWidget(self.button6)

        # Create the bottom button
        self.bottom_button = QPushButton("Copy Weights")
        self.bottom_button.clicked.connect(self.copy_weights)
        main_layout.addWidget(self.bottom_button)

        # Set window flag to stay on top
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Help menu
        self.create_main_menu()

        # Load Saved selections
        self.load_saved_data()

    def get_skin_cluster(self):
        pass

    def populate_cluster_list(self, source_mesh):
        if self.has_skin_cluster( source_mesh ):
            skin_clus = [x for x in cmds.listHistory( 'body' ) if cmds.objectType(x) == 'skinCluster' ][0]
            self.list_widget3.addItem(skin_clus)
        else:
            self.list_widget3.addItem("<NO SKIN CLUSTER DETECTED>")
            self.list_widget3.item(0).setForeground(Qt.red)

    def select_verts(self):
        selected_verts = [self.list_widget2.item(i).text() for i in range(self.list_widget2.count())]
        if not selected_verts:
            cmds.warning("No Target Verts Have Been Added")
        else:
            print("Selected verts in the list.")
            selection = cmds.select(selected_verts, add=True)


    def select_objects(self):
        selected_objects= [self.list_widget1.item(i).text() for i in range(self.list_widget1.count())]
        pprint("Selected Source Mesh")
        cmds.select(selected_objects, add=True)

    def copy_weights(self):
        contents = [self.list_widget1.item(i).text() for i in range(self.list_widget1.count())]
        source_obj, target_verts = '', []
        if self.list_widget2.count() > 0:
            target_verts = [self.list_widget2.item(i).text() for i in range(self.list_widget2.count())]
        if self.list_widget1.count() > 0:
            source_obj = self.list_widget1.item(0).text()
            if not self.has_skin_cluster(source_obj):
                cmds.warning("Source Mesh is not skinned.")
                return
        if source_obj and target_verts:
            if self.has_skin_cluster(target_verts[0].split('.')[0]):
                cmds.select( source_obj, target_verts, r=True )
                mel.eval( "CopySkinWeights;")
                # cmds.copySkinWeights(sourceSkin=source_obj, destinationSkin=target_verts, noMirror=True)
                cmds.select(target_verts, r=True)
                print("Weights have been copied to selected verts")
                return
            else:
                cmds.warning("Target Mesh is not skinned.")
                return
        else:
            cmds.warning( "Please make sure you have selected a Source and Target." )
            return

    def has_skin_cluster(self, mesh):
        # List all history nodes of the mesh
        history_nodes = cmds.listHistory(mesh)
        # Check if any of the history nodes are skin clusters
        for node in history_nodes:
            if cmds.nodeType(node) == "skinCluster":
                return True

        return False

    def clear_object_list(self):
        self.list_widget1.clear()
        self.list_widget3.clear()
        self.save_object_list_data()
        print("Source Mesh Cleared.")

    def clear_vert_list(self):
        self.list_widget2.clear()
        self.save_vert_list_data()
        print("Vert Selection Cleared.")

    def clear_all(self):
        self.clear_object_list()
        self.clear_vert_list()

    def populate_list(self):
        # Clear the list widget
        self.list_widget1.clear()
        self.list_widget3.clear()
        # Get selected objects in Maya
        selected_object = cmds.ls(selection=True, type='transform')[0]

        # Populate the list widget with names of selected objects
        # for obj in selected_objects:
        self.list_widget1.addItem(selected_object)
        print("Source Object Selection Added.")
        # populate cluster list
        self.populate_cluster_list(selected_object)
        #save
        self.save_object_list_data()

    def populate_vertex_list(self):
        # Clear the list widget
        self.list_widget2.clear()
        # Ensure only one object is selected
        if self.is_vertex_selection():
            vertex_selection = cmds.ls(selection=True, flatten=True)
            for vertex in vertex_selection:
                self.list_widget2.addItem(vertex)
            self.save_vert_list_data()
            print("Target Vert Selection Added.")
            return
        else:
            cmds.warning("Please select verts for the weight transfer")
            return

    def is_vertex_selection(self):
        selection = cmds.ls(selection=True)
        if not selection:
            print("No selection.")
            return False
        components = cmds.filterExpand(selection, selectionMask=31, expand=True)
        if not components:
            print("Selection contains no vertices.")
            return False

        print("Selection contains vertices.")
        return True

    def create_main_menu(self):
        action_menu = self.menuBar().addMenu("Action")

        clear_action = QAction("Clear All", self)
        clear_action.triggered.connect(self.clear_all)
        action_menu.addAction(clear_action)

        help_menu = self.menuBar().addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_dialog_clicked)
        help_menu.addAction(about_action)

        clear_action = QAction("Help", self)
        clear_action.triggered.connect(self.open_help_page)
        help_menu.addAction(clear_action)

    def open_about_page(self):
        # Replace the URL with the actual URL of your About page
        QDesktopServices.openUrl(QUrl("https://anthonylynch.xyz/copy-vert-weight-script"))

    def open_help_page(self):
        # Replace the URL with the actual URL of your Help page
        QDesktopServices.openUrl(QUrl("https://anthonylynch.xyz/copy-vert-weight-script"))
    def save_vert_list_data(self):
        # Save data to optionVars
        target_items = [self.list_widget2.item(i).text() for i in range(self.list_widget2.count())]
        cmds.optionVar(stringValue=("target_items", json.dumps(target_items)))
        print
        target_items

    def save_object_list_data(self):
        # Save data to optionVars
        source_items = [self.list_widget1.item(i).text() for i in range(self.list_widget1.count())]
        cmds.optionVar(stringValue=("source_items", json.dumps(source_items)))
        print
        source_items

    def load_saved_data(self):
        # Load data from optionVars
        source_items_json = cmds.optionVar(query="source_items")
        if source_items_json:
            source_items = json.loads(source_items_json)
            for item in source_items:
                self.list_widget1.addItem(item)
                self.populate_cluster_list(item)

        target_items_json = cmds.optionVar(query="target_items")
        if target_items_json:
            target_items = json.loads(target_items_json)
            for item in target_items:
                self.list_widget2.addItem(item)

        # self.populate_cluster_list(source_items_json)
    def show_about_dialog(self):
        message_box = QMessageBox()
        message_box.setWindowTitle("About")
        message_box.setText("<center>Created by: Anthony L.<br>Website: anthonylynch.xyz<br>Date: Jan.2024")
        message_box.setStandardButtons(QMessageBox.Close)
        message_box.setWindowFlags(Qt.WindowStaysOnTopHint)
        response = message_box.exec_()
    def show_dialog_clicked(self):
        cmds.evalDeferred(self.show_about_dialog())
        # self.show_about_dialog()

def show_gui():
    global maya_gui
    try:
        maya_gui.close()  # Close the existing window if it's open
    except:
        pass

    maya_gui = MayaGUI()
    maya_gui.show()

show_gui()
