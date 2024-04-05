import maya.cmds as cmds

'''
About: Limit Helper
'''
cb_shape_state = True

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

class LimitUI(BaseUI):
    def __init__(self, name='Limit No Jutsu'):
        super(LimitUI, self).__init__(name=name)
        self.win_width = 220
        self.win_height = 210
        self.attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        self.attr_limits = {'tx': 'etx', 'ty': 'ety', 'tz': 'etz',
                       'rx': 'erx', 'ry': 'ery', 'rz': 'erz'}
        self.but_col = (.6,.6,.6)
        self.website_link = 'http://www.anthonylynch.xyz/limit-script/'
        self.about_message = ("\nSET: \n" +
                                "1) Position or rotate control and 'Set Limit'. \n" + "\n" +
                                "COPY: \n" +
                                "1) Y --> Z, Z, Z, Z \n" + "\n" +
                                "MIRROR: \n" +
                                "1) Auto detect opposite control and sets limits\n" + "\n" +
                                "REMOVE: \n" +
                                "1) Remove limits on all or individual axis. \n" +
                                "\n" +
                                "Developed by : Anthony Lynch\n" +
                                "URL: www.anthonylynch.xyz\n")

    def copy_limit_data(self):
        '''About: the first selected object info will be transfered to the rest
        old - ja.copyLimit()
        '''
        sel = cmds.ls(selection=True)
        source, targets = sel[0], sel[1:]
        sourceVal = {}
        for y in self.attrs:
            source_val = cmds.transformLimits(source, query=True, **{y: True})
            source_val_bool = cmds.transformLimits(source, query=True, **{self.attr_limits[y]: True})
            # setting target values
            for target in targets:
                cmds.transformLimits(target, **{y: tuple(source_val), self.attr_limits[y]: tuple(source_val_bool)})
    def set_minMax_limit(self):
        '''
        Sets value for min and max limit, for every value not at zero
        :param self:
        :return:
        :legacy: ja.quickSetMaxMinLimit()
        '''
        # set max and min limit value based on value in set in ChannelBox
        sel = cmds.ls(selection=True)
        for x in sel:
            for y in self.attrs:
                value, locked = cmds.getAttr('%s.%s' % (x, y)), cmds.getAttr('%s.%s' % (x, y), lock=True)
                if value != 0 and not locked:
                    inv_value = value * -1
                    # Determine trans or rot
                    cmds.transformLimits(x, **{y: (min(value, inv_value), max(value, inv_value)),
                                               self.attr_limits[y]: (True, True)})
                    if cb_shape_state == True:
                        cmds.setAttr('%s.%s' % (x, y), 0)
    def set_limit(self):
        '''
        Setting the transform limits based on value set currently on it
        :param self:
        :return:
        '''
        sel = cmds.ls(selection=True)
        for x in sel:
            for y in self.attrs:
                current_attr = '%s.%s' % (x, y)
                value, locked = cmds.getAttr(current_attr), cmds.getAttr(current_attr, lock=True)
                if value != 0 and not locked:
                    limitVal = value
                    curMinAttr = 'minTrans' if y[0] == 't' else 'minRot'
                    curMaxAttr = 'maxTrans' if y[0] == 't' else 'maxRot'
                    curMin = cmds.getAttr('%s.%s%sLimit' % (x, curMinAttr, y[1].upper()))
                    curMax = cmds.getAttr('%s.%s%sLimit' % (x, curMaxAttr, y[1].upper()))
                    if limitVal > 0:
                        op_lock = cmds.transformLimits(x, q=True, **{self.attr_limits[y]: True})[0]
                        cmds.transformLimits(x, **{y: (curMin, value), self.attr_limits[y]: (op_lock, True)})
                    elif limitVal < 0:
                        op_lock = cmds.transformLimits(x, q=True, **{self.attr_limits[y]: True})[1]
                        cmds.transformLimits(x, **{y: (value, curMax), self.attr_limits[y]: (True, op_lock)})
                    if cb_shape_state == True:
                        cmds.setAttr(current_attr, 0)
    def mirror_limit_data(self):
        '''
        Mirror limit values of selected controls to the opposite control
        :param self:
        :return:
        '''
        selection = cmds.ls( sl=True )
        if selection:
            opposites = self.get_opposite_transform( selection )
        if len(opposites) == len(selection):
            transfer = zip( selection, opposites )
            for source, target in transfer:
                for y in self.attrs:
                    source_val = cmds.transformLimits(source, query=True, **{y: True})
                    source_val_bool = cmds.transformLimits(source, query=True, **{self.attr_limits[y]: True})
                    cmds.transformLimits(target, **{y: tuple(source_val), self.attr_limits[y]: tuple(source_val_bool)})
            cmds.select(selection, opposites, r=True )
    def remove_limit_data(self):
        sel = cmds.ls(selection=True)
        for x in sel:
            for y in self.attrs:
                current_attr = '%s.%s' % (x, y)
                cmds.transformLimits(x, **{y: (0, 0), self.attr_limits[y]: (False, False)})
                if cb_shape_state:
                    cmds.setAttr(current_attr, 0)
    def remove_value_limit_data(self, val):
        sel = cmds.ls(selection=True)
        attrs = [val]
        for x in sel:
            for y in attrs:
                current_attr = '%s.%s' % (x, y)
                cmds.transformLimits(x, **{y: (0, 0), self.attr_limits[y]: (False, False)})
                if cb_shape_state:
                    cmds.setAttr(current_attr, 0)
    def get_opposite_transform(self, lst):
        for itr in range(2):
            pfx_token, ifx_token, sfx_token = ['l_', 'r_'], ['_l_', '_r_'], ['_l', '_r']
            if itr == 1:
                pfx_token = [token.upper() for token in pfx_token]
                ifx_token = [token.upper() for token in ifx_token]
                sfx_token = [token.upper() for token in sfx_token]

            prefix_naming = [x for x in lst if x.startswith(pfx_token[0]) or x.startswith(pfx_token[1])]
            infix_naming = [x for x in lst if ifx_token[0] in x or ifx_token[1] in x]
            suffix_naming = [x for x in lst if x.endswith(sfx_token[0]) or x.endswith(sfx_token[1])]

            prefix_L = [x for x in prefix_naming if x.startswith(pfx_token[0])]
            prefix_L = [pfx_token[1] + x[2:] for x in prefix_L if cmds.objExists(pfx_token[1] + x[2:])]
            prefix_R = [x for x in prefix_naming if x.startswith(pfx_token[1])]
            prefix_R = [pfx_token[0] + x[2:] for x in prefix_R if cmds.objExists(pfx_token[0] + x[2:])]
            prefix = prefix_L + prefix_R

            infix_L = [x.replace(ifx_token[0], ifx_token[1]) for x in infix_naming if ifx_token[0] in x]
            infix_L = [x.replace(ifx_token[0], ifx_token[1]) for x in infix_L if
                       cmds.objExists(x.replace(ifx_token[0], ifx_token[1]))]
            infix_R = [x.replace(ifx_token[0], ifx_token[1]) for x in infix_naming if ifx_token[1] in x]
            infix_R = [x.replace(ifx_token[1], ifx_token[0]) for x in infix_R if
                       cmds.objExists(x.replace(ifx_token[1], ifx_token[0]))]
            infix = infix_L + infix_R

            suffix_L = [x for x in suffix_naming if x.endswith(sfx_token[0])]
            suffix_L = [x[:-2] + sfx_token[1] for x in suffix_L if cmds.objExists(x[:-2] + sfx_token[1])]
            suffix_R = [x for x in suffix_naming if x.endswith(sfx_token[1])]
            suffix_R = [x[:-2] + sfx_token[0] for x in suffix_R if cmds.objExists(x[:-2] + sfx_token[0])]
            suffix = suffix_L + suffix_R

            if itr == 1:
                all_opposites_uppercase = prefix + infix + suffix
            else:
                all_opposites_lowercase = prefix + infix + suffix

        all_opposites = all_opposites_lowercase + all_opposites_uppercase

        return (all_opposites)
    def current_gui_settings(self):
        global cb_shape_state
        cb_shape_state = cmds.checkBox(self.shape_checkbox, q=True, v=True)
    def about_dialog(self):
        cmds.confirmDialog(title='About Limit No Jutsu',
                           message=self.about_message,
                           ma='center', button="Close", parent=self.window)
    def show_help(self):
        cmds.showHelp(self.website_link, a=True)
    def ui_elements(self, *args):
        # menu
        cmds.menuBarLayout()
        cmds.menu(label='Help', hm=True)
        cmds.menuItem(label='About Limit Jutsu', c=lambda *args: self.about_dialog())
        cmds.menuItem(label='Website', c=lambda *args: self.show_help(), ann="Visit Website")
        cmds.menuBarLayout()

        self.main_layout = cmds.columnLayout(adjustableColumn=True)

        #title
        cmds.text(label="----------------- Limit No Jutsu -----------------", align='center')
        cmds.setParent(self.main_layout)

        # Set
        self.section1_layout = cmds.frameLayout(label="Set", collapsable=True, collapse=False)
        cmds.rowColumnLayout(nc=1, columnWidth=[(1, self.win_width)])
        cmds.button(label="Set Limit", w=self.win_width,  c=lambda *args: self.set_limit(), bgc=self.but_col )
        cmds.button(label="Set Min/Max Limits", w=self.win_width,  c=lambda *args: self.set_minMax_limit(), bgc=self.but_col )
        cmds.button(label="Copy Limits", w=self.win_width,  c=lambda *args: self.copy_limit_data(), bgc=self.but_col )

        cmds.setParent(self.main_layout)
        # Mirror
        self.section2_layout = cmds.frameLayout(label="Mirror", collapsable=True, collapse=False)
        cmds.rowColumnLayout(nc=1, columnWidth=[(1, self.win_width)])
        cmds.button(label="Mirror Limits To Opposite Control", w=self.win_width,  c=lambda *args: self.mirror_limit_data(), bgc=self.but_col )

        cmds.setParent(self.main_layout)
        # Remove
        self.section3_layout = cmds.frameLayout(label="Remove", collapsable=True, collapse=False)
        cmds.rowColumnLayout(nc=1, columnWidth=[(1, self.win_width)])
        cmds.button(label="Remove Limits", w=self.win_width, c=lambda *args: self.remove_limit_data(), bgc=self.but_col )
        remove_value_button = cmds.rowColumnLayout(nc=2, columnWidth=[(1, (self.win_width/2)), (2, (self.win_width/2))])
        cmds.button(label='Remove TX Limits', w=(self.win_width/2), c=lambda *args: self.remove_value_limit_data('tx'), bgc=(1,0,0) )
        cmds.button(label='Remove RX Limits', w=(self.win_width/2), c=lambda *args: self.remove_value_limit_data('rx'), bgc=(1,0,0) )
        cmds.button(label='Remove TY Limits', w=(self.win_width/2), c=lambda *args: self.remove_value_limit_data('ty'), bgc=(0,0,1) )
        cmds.button(label='Remove RY Limits', w=(self.win_width/2), c=lambda *args: self.remove_value_limit_data('ry'), bgc=(0,0,1) )
        cmds.button(label='Remove TZ Limits', w=(self.win_width/2), c=lambda *args: self.remove_value_limit_data('tz'), bgc=(0,1,0) )
        cmds.button(label='Remove RZ Limits', w=(self.win_width/2), c=lambda *args: self.remove_value_limit_data('rz'), bgc=(0,1,0) )
        # Reset Position Checkbox
        cmds.setParent(self.main_layout)
        self.shape_checkbox = cmds.checkBox(label='Reset Position When Set', align='left', v=cb_shape_state,
                                            cc=lambda *args: self.current_gui_settings())
    def show(self):
        self.window = cmds.window( title=self.name, sizeable=False, width=self.win_width, height=self.win_height, mxb=False )
        self.ui_elements()
        cmds.showWindow( self.window )