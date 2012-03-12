
"""
    Berisi widget custom yang sering dipakai

    Arif Widi Nugroho
    < arif@hexarius.com >
"""

import wx
import wx.lib.newevent
#import thread
import threading
from wx.lib.wordwrap import wordwrap

(ThreadProgressUpdateEvent, EVT_UPDATE_THREAD_PROGRESS) = wx.lib.newevent.NewEvent()
(ThreadProgressDoneEvent, EVT_THREAD_DONE) = wx.lib.newevent.NewEvent()

class ThreadProgressDialog(wx.Dialog):
    def __init__(self, thread_proc, parent=None, id=-1, title="Processing"):
        self.thread_proc = thread_proc
        wx.Dialog.__init__(self, parent, id, title, style=wx.CAPTION)
        self.panel = ThreadProgressPanel(self, thread_proc)
        self.SetSize((350,150))
        sizer = wx.BoxSizer()
        self.SetSizer(sizer)
        sizer.Add(self.panel, 1, wx.ALL | wx.EXPAND)
        
    def show_and_start(self):
        self.Center()
        self.Show()
        self.panel.start()
    
class ThreadProgressPanel(wx.Panel):
    def __init__(self, parent, thread_proc, id=-1):
        wx.Panel.__init__(self, parent, id)
        self.thread_proc = thread_proc
        self.thread_proc.receiver = self
        self.thread_id = None
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)
        
        self.gauge = wx.Gauge(self, -1, 50, (110, 95), (250, 25))
        main_sizer.Add(self.gauge, 0, wx.ALL | wx.EXPAND, 5)
        self.info = wx.StaticText(self, -1, "")
        main_sizer.Add(self.info, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_abort = wx.Button(self, -1, "Cancel")
        abort_sizer = wx.BoxSizer(wx.HORIZONTAL)
        abort_sizer.Add(wx.BoxSizer(), 1, wx.ALL | wx.EXPAND, 5)
        abort_sizer.Add(self.btn_abort, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(wx.BoxSizer(wx.VERTICAL), 1, wx.ALL | wx.EXPAND)
        main_sizer.Add(wx.StaticLine(self, -1), 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(abort_sizer, 0, wx.ALL | wx.EXPAND, 0)
        
        self.Bind(EVT_UPDATE_THREAD_PROGRESS, self.OnUpdateProgress)
        self.Bind(EVT_THREAD_DONE, self.OnDone)
        self.Bind(wx.EVT_BUTTON, self.OnAbort, self.btn_abort)
    
    def start(self):
        try:
            top = self.GetTopLevelParent().Parent.GetTopLevelParent()
            top.Disable()
        except:
            print 'Disable fail'
#        self.thread_id = thread.start_new_thread(self.thread_proc.run, ())
        
        self.thread_proc.abort = False
        self.thread_proc.queue = 0
        self.thread_proc.start()
        
    def OnUpdateProgress(self, event):
        self.thread_proc.queue = self.thread_proc.queue - 1
        self.gauge.Pulse()
        wrp = wordwrap(event.info_str, self.GetSize()[0], wx.ClientDC(self))
        self.info.SetLabel(wrp)
    
    def OnDone(self, event):
        """tutup parent dialog"""
        self.thread_proc.queue = self.thread_proc.queue - 1
        try:
            top = self.GetTopLevelParent().Parent.GetTopLevelParent()
            top.Enable()
        except:
            print 'Disable fail'
        try:
            self.Parent.Show(False)
        except:
            print "close fail"
        
        if self.thread_proc.abort:
            wx.MessageBox(self.thread_proc.abort_msg, 'Failed!', wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox(self.thread_proc.done_msg, 'Done!', wx.OK | wx.ICON_INFORMATION)
    
    def OnAbort(self, event):
        if self.thread_proc.isAlive() == False:
            print "Error! Thread is KIA!"
            self.thread_proc.abort = True
            self.thread_proc.abort_msg = "Unexpected error occur!"
            self.OnDone(None)
            
        self.thread_proc.abort = True
        self.btn_abort.SetLabel("Canceling...")
        self.btn_abort.Disable()
        
class BaseThreadProc(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.receiver     = None #set win sebagai receiver event
        self.evt_progress = ThreadProgressUpdateEvent()
        self.evt_done     = ThreadProgressDoneEvent()
        self.abort        = False
        self.done_msg     = "Operation succeed!"
        self.abort_msg    = "Operation canceled!"
        self.queue        = 0
        
        
    def progress(self, info_str):
        if self.queue < 20:
            pg = ThreadProgressUpdateEvent()
            pg.info_str = info_str
            wx.PostEvent(self.receiver, pg)
            self.queue = self.queue + 1
#        self.evt_progress.info_str = info_str
#        wx.PostEvent(self.receiver, self.evt_progress)
    
    def done(self):
        dn = ThreadProgressDoneEvent()
        wx.PostEvent(self.receiver, dn)
        self.queue = self.queue + 1
        exit()
#        wx.PostEvent(self.receiver, self.evt_done)
        
    def run(self):
        pass
    
class SampleThreadProc(BaseThreadProc):
    def __init__(self):
        BaseThreadProc.__init__(self)
        
    def run(self):
        import  time
        
        for i in range(100):
            time.sleep(0.1)
            self.progress("Tick: {0}".format(i))
            print 'tick', i
            if self.abort:
                print "Aborting..."
                break
        
        self.done()


# Textbox custom
class GrayTextCtrl(wx.TextCtrl):
    def __init__(self, parent, id=-1, default_value="", 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 style=wx.TE_RICH2, validator=None):
        if validator==None:
            validator = wx.DefaultValidator
        wx.TextCtrl.__init__(self, parent, id, default_value, 
                             pos, size, style=style, 
                             validator=validator )
        self.default_value = default_value
        ln = len(self.default_value)
        self.SetStyle(0,ln,wx.TextAttr("GRAY"))
        self.SetToolTipString(default_value)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.EvtOnClick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.EvtOnClick)
        self.Bind(wx.EVT_KILL_FOCUS, self.EvtKillFocus)
        self.Bind(wx.EVT_SET_FOCUS, self.EvtFocus)
    
    def set_num_value(self, num):
        self.SetValue(num.__str__())
    
    def color_reset(self):
        self.SetBackgroundColour("white")
        
    def color_pink(self):
        self.SetBackgroundColour("pink")
    
    def reset(self):
        self.Value = self.default_value
        ln = len(self.default_value)
        self.SetStyle(0,ln,wx.TextAttr("GRAY"))
    
    def EvtOnClick(self, event):
        if self.Value == self.default_value:
            self.Clear()
        event.Skip()
    
    def EvtFocus(self, event):
        if self.Value == self.default_value:
            ln = len(self.default_value)
            self.SetStyle(0,ln,wx.TextAttr("BLACK"))
        event.Skip()    
           
    def EvtKillFocus(self, event):
        if self.Value == "":
            self.Value = self.default_value
        if self.Value == self.default_value:
            ln = len(self.default_value)
            self.SetStyle(0,ln,wx.TextAttr("GRAY"))
        event.Skip()
    
    def Validate(self):
        return self.Validator.Validate(self.Parent)
    
    def ValidateSilent(self):
        return self.Validator.ValidateSilent(self.Parent)
    
    def get_result(self):
        txt = self.GetValue()
        if txt == self.default_value:
            return ""
        else:
            return txt
    
    def get_result_int(self):
        txt = self.GetValue()
        if txt == self.default_value:
            return None
        else:
            try:
                res = int(txt)
                return res
            except:
                return None
    
    def get_result_float(self):
        txt = self.GetValue()
        if txt == self.default_value:
            return None
        else:
            try:
                res = float(txt)
                return res
            except:
                return None
    
    def get_eval_result_int(self):
        txt = self.GetValue()
        if txt == self.default_value:
            return None
        else:
            try:
                res_eval = eval(txt)
                res = int(res_eval)
                return res
            except:
                return None
    
    def get_eval_result_float(self):
        txt = self.GetValue()
        if txt == self.default_value:
            return None
        else:
            try:
                res_eval = eval(txt)
                res = float(res_eval)
                return res
            except:
                return None
    
class EvalNumberTextValidator(wx.PyValidator):
    def __init__(self, optional=False):
        wx.PyValidator.__init__(self)
        self.optional = optional
        
    def Clone(self):
        return EvalNumberTextValidator(self.optional)
    
    def Validate(self, win):
        tc    = self.GetWindow()
        val   = tc.GetValue()
        valid = True
        try:
            res_eval = eval(val)
            float(res_eval)
        except:
            valid = False
        if valid:
            tc.SetBackgroundColour("white")
            tc.Refresh()
            return True
        else:
            if self.optional:
                txt = ""
                try:
                    txt = tc.default_value
                except:
                    pass
                if val==txt:
                    tc.SetBackgroundColour("white")
                    tc.Refresh()
                    return True
            tc.SetBackgroundColour("pink")
            tc.Refresh()
            return False
    
    def ValidateSilent(self, win):
        tc    = self.GetWindow()
        val   = tc.GetValue()
        valid = True
        try:
            res_eval = eval(val)
            float(res_eval)
        except:
            valid = False
        if valid:
            return True
        else:
            if self.optional:
                txt = ""
                try:
                    txt = tc.default_value
                except:
                    pass
                if val==txt:
                    return True
            return False
    
class NumberTextValidator(wx.PyValidator):
    def __init__(self, optional=False):
        wx.PyValidator.__init__(self)
        self.optional = optional
        
    def Clone(self):
        return NumberTextValidator(self.optional)
    
    def Validate(self, win):
        tc    = self.GetWindow()
        val   = tc.GetValue()
        valid = True
        try:
            float(val)
        except:
            valid = False
        if valid:
            tc.SetBackgroundColour("white")
            tc.Refresh()
            return True
        else:
            if self.optional:
                txt = ""
                try:
                    txt = tc.default_value
                except:
                    pass
                if val==txt:
                    tc.SetBackgroundColour("white")
                    tc.Refresh()
                    return True
            tc.SetBackgroundColour("pink")
            tc.Refresh()
            return False
    
    def ValidateSilent(self, win):
        tc    = self.GetWindow()
        val   = tc.GetValue()
        valid = True
        try:
            float(val)
        except:
            valid = False
        if valid:
            return True
        else:
            if self.optional:
                txt = ""
                try:
                    txt = tc.default_value
                except:
                    pass
                if val==txt:
                    return True
            return False
        
class CoordinateTextValidator(wx.PyValidator):
    def __init__(self, optional=False):
        wx.PyValidator.__init__(self)
        self.optional = optional
        
    def Clone(self):
        return CoordinateTextValidator(self.optional)
    
    def Validate(self, win):
        tc    = self.GetWindow()
        val   = tc.GetValue()
        valid = True
        try:
            dat = val.split(',')
            lat = float(dat[0])
            lon = float(dat[1])
        except:
            valid = False
        if valid:
            tc.SetBackgroundColour("white")
            tc.Refresh()
            return True
        else:
            if self.optional:
                txt = ""
                try:
                    txt = tc.default_value
                except:
                    pass
                if val==txt:
                    tc.SetBackgroundColour("white")
                    tc.Refresh()
                    return True
            tc.SetBackgroundColour("pink")
            tc.Refresh()
            return False

    def ValidateSilent(self, win):
        tc    = self.GetWindow()
        val   = tc.GetValue()
        valid = True
        try:
            dat = val.split(',')
            lat = float(dat[0])
            lon = float(dat[1])
        except:
            valid = False
        if valid:
            return True
        else:
            if self.optional:
                txt = ""
                try:
                    txt = tc.default_value
                except:
                    pass
                if val==txt:
                    return True
            return False


class AlphaTextValidator(wx.PyValidator):
    def __init__(self, default_text=""):
        wx.PyValidator.__init__(self)
        self.default_text = default_text
    
    def Clone(self):
        return AlphaTextValidator(self.default_text)
    
    def Validate(self, win):
        tc    = self.GetWindow()
        val   = tc.GetValue()
        valid = True
        txt = self.default_text
        if txt=="":
            try:
                txt=tc.default_value
            except:
                txt=""
        if val==txt:
            valid = False
        elif len(val.strip())==0:
            valid = False
        if valid:
            tc.SetBackgroundColour("white")
            tc.Refresh()
            return True
        else:
            tc.SetBackgroundColour("pink")
            tc.Refresh()
            return False


class ValidateError(Exception):
    """Exception yang diakibatkan oleh hasil validasi yang salah"""
    pass

class BitmapPanel(wx.Panel):
    """
    Panel untuk merender bitmap yang besar
    Agar gambar tidak blank, taruh panel ini di dalam sizer yang
    exclusive (hanya berisi panel ini saja)
    
    ------------------------------------------
    self.panel_new = commons.BitmapPanel(self, -1, bmp, size=(bmp.GetWidth(), bmp.GetHeight()))
    new_sizer = wx.BoxSizer(wx.HORIZONTAL)
    new_sizer.SetMinSize((bmp.GetWidth(),bmp.GetHeight()))
    new_sizer.Add(self.panel_new, 1, wx.ALL | wx.EXPAND, 0)
    """
    def __init__(self, parent, id=-1, bitmap = None, size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, id, size=size)
        self.bitmap = bitmap
        self.draw_from_x = 0
        self.draw_from_y = 0
        self.brush_bg = wx.Brush("WHITE")
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.os_win = False
        if 'wxMSW' in wx.PlatformInfo:
            self.os_win = True

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBackground(self.brush_bg)
        dc.SetBackgroundMode(wx.TRANSPARENT)
        if self.os_win==False:
            dc.Clear()
        dc.DrawBitmap(self.bitmap, self.draw_from_x, self.draw_from_y, True)
