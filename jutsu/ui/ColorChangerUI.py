import maya.cmds as cmds

cb_shape_state = False
color_slider_state = 0


class BaseUI(object):
    ACTIVE = []

    def __init__(self, name):
        self.name = name
        self.window = None
        self.ACTIVE.append(self)

    def close_active(self):
        for i in self.ACTIVE:
            if i.name == self.name and i.window:
                if cmds.window(i.window, q=True, ex=True):
                    cmds.deleteUI(i.window)

    def run(self):
        self.close_active()
        self.show()

    def ui_elements(self):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError


class PaletteUI(BaseUI):

    def __init__(self, name='Color Changer no Jutsu'):
        super(PaletteUI, self).__init__(name=name)
        self.color_slider = None
        self.selection_color = None
        self.shape_checkbox = None
        self.website_link = 'http://www.anthonylynch.xyz'
        self.color_chart = [
            ((.627, .627, .627), "Medium Gray"), ((.467, .467, .467), "Dark Gray"), ((.000, .000, .000), "Black"),
            ((.247, .247, .247), "Dark Gray"), ((.498, .498, .498), "Light Gray"), ((0.608, 0, 0.157), "Dark Red"),
            ((0, 0.016, 0.373), "Dark Blue"), ((0, 0, 1), "Blue"), ((0, 0.275, 0.094), "Dark Green"),
            ((0.145, 0, 0.263), "Dark Purple"), ((0.78, 0, 0.78), "Purple"), ((0.537, 0.278, 0.2), "Brown"),
            ((0.243, 0.133, 0.122), "Dark Brown"), ((0.6, 0.145, 0), "Dark Orange"), ((1, 0, 0), "Red"),
            ((0, 1, 0), "Green"), ((0, 0.255, 0.6), "Dark Cyan"), ((1, 1, 1), "White"), ((1, 1, 0), "Yellow"),
            ((0.388, 0.863, 1), "Light Cyan"), ((0.263, 1, 0.635), "Light Green"), ((1, 0.686, 0.686), "Light Pink"),
            ((0.89, 0.675, 0.475), "Light Brown"), ((1, 1, 0.384), "Light Yellow"), ((0, 0.6, 0.325), "Dark Green"),
            ((0.627, 0.412, 0.188), "Dark Orange"), ((0.62, 0.627, 0.188), "Yellow-Green"),
            ((0.408, 0.627, 0.188), "Green-Yellow"),
            ((0.188, 0.627, 0.365), "Cyan-Green"), ((0.188, 0.627, 0.627), "Cyan"),
            ((0.188, 0.404, 0.627), "Cyan-Blue"),
            ((0.435, 0.188, 0.627), "Purple-Blue")
        ]
        self.color_chart_sorted = sorted(self.color_chart, key=lambda x: sum(x[0]))

    def set_prev_config(self):
        if cb_shape_state:
            cmds.checkBox(self.shape_checkbox, e=True, v=cb_shape_state)
        if color_slider_state:
            cmds.colorIndexSliderGrp(self.color_slider, e=True, v=color_slider_state)

    def current_gui_settings(self):
        global cb_shape_state
        cb_shape_state = cmds.checkBox(self.shape_checkbox, q=True, v=True)
        global color_slider_state
        color_slider_state = cmds.colorIndexSliderGrp(self.color_slider, q=True, v=True)
        print("Values Stored! Current Color: %s, Current CB state: %s" % (color_slider_state, cb_shape_state))

    def update_slider(self, color_id, color_name, *args):
        slider_id = self.find_matching_index(self.color_chart, self.color_chart_sorted, color_id)
        cmds.colorIndexSliderGrp(self.color_slider, e=True, value=slider_id)
        self.current_gui_settings()
        print(color_name + ": Color is selected.")

    def find_matching_index(self, list1, list2, list2_index):
        value_to_find = list2[list2_index][1]
        for index, item in enumerate(list1):
            if item[1] == value_to_find:
                return index
        return -1

    def change_selection_color(self):
        cb = cmds.checkBox(self.shape_checkbox, q=True, v=True)
        current_color = cmds.colorIndexSliderGrp(self.color_slider, q=True, value=True)
        print
        current_color
        if cb == True:
            self.update_control_shape_color(current_color)
        else:
            self.update_control_color()

    def update_control_color(self):
        selected_ctrls = cmds.ls(sl=True)
        for ctrl in selected_ctrls:
            cmds.setAttr(ctrl + '.overrideEnabled', 1)
            color = cmds.colorIndexSliderGrp(self.color_slider, q=True, v=True)
            if color > 0:
                cmds.setAttr(ctrl + '.overrideColor', (color - 1))
                # self.current_gui_settings()
        print("Control Color Changed")

    def update_control_shape_color(self, color_id):
        selected_ctrls = cmds.ls(sl=True)
        rgb_color = self.color_chart[color_id][0]
        print
        rgb_color
        for ctrl in selected_ctrls:
            shapes = cmds.listRelatives(ctrl, shapes=True)
            for shape in shapes:
                cmds.setAttr(shape + '.overrideEnabled', 1)
                color = cmds.colorIndexSliderGrp(self.color_slider, q=True, v=True)
                if color > 0:
                    cmds.setAttr(shape + '.overrideColor', (color - 1))
                    # self.current_gui_settings()
                    cmds.setAttr(shape + '.overrideColorR', rgb_color[0])
                    cmds.setAttr(shape + '.overrideColorG', rgb_color[1])
                    cmds.setAttr(shape + '.overrideColorB', rgb_color[2])

        print("Shape Color Changed")
        print("R=%s, G=%s, B=%s" % (rgb_color[0], rgb_color[1], rgb_color[2]))

    def about_dialog(self):
        cmds.confirmDialog(title='About Color Changer',
                           message="1) Select any controls you wish to change. \n" +
                                   "2) Select desired color from palette or slider\n" +
                                   "Developed by : Anthony Lynch\n" +
                                   "www.anthonylynch.xyz\n",
                           ma='center', button="Close", parent=self.window)

    def show_help(self):
        cmds.showHelp(self.website_link, a=True)

    def ui_elements(self, *args):
        cmds.menuBarLayout()
        cmds.menu(label='Help')
        cmds.menuItem(label='About Color Changer', c=lambda *args: self.about_dialog())
        cmds.menuItem(label='Website', c=lambda *args: self.show_help(), ann="Visit Website")
        cmds.text(label="----- Rig-Jutsu -----", align='center')
        cmds.columnLayout()
        cmds.setParent('..')
        cmds.setParent('..')

        self.frame_color = cmds.frameLayout(label='Pick a Color', w=280, height=180, collapsable=False)
        cmds.gridLayout(numberOfRows=4, numberOfColumns=8, cellWidthHeight=(35, 20))
        for ind, (rgb, color_name) in enumerate(self.color_chart_sorted):
            # Use a default argument in the lambda function to capture the current value of ind and color_name
            cmds.iconTextButton(bgc=rgb, command=lambda num=ind, name=color_name: self.update_slider(num, name))
        cmds.setParent('..')

        self.selection_color = cmds.frameLayout(label='Selected Color', w=300, h=30, collapsable=False)
        cmds.columnLayout(adj=True)
        self.color_slider = cmds.colorIndexSliderGrp(min=0, max=31, value=color_slider_state, w=300)
        cmds.setParent('..')

        cmds.setParent('..')
        self.shape_checkbox = cmds.checkBox(label='Set Color of Shape Node', align='left', v=cb_shape_state,
                                            cc=lambda *args: self.current_gui_settings())

        cmds.setParent('..')
        cmds.button(label='Click To Update Color on Selection', w=255, bgc=(.9, .9, .9),
                    c=lambda *args: self.change_selection_color())
        # cmds.setParent('..')

    # Other methods remain unchanged
    def show(self):
        self.window = cmds.window(title=self.name, sizeable=False, width=280, height=230)
        self.ui_elements()
        self.set_prev_config()
        cmds.showWindow(self.window)


#PaletteUI().run()