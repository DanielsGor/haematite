### This code is the main code to run for the GUI of the program ###
###   Imports   ###

import sys
import tkinter as tk
import tkinter.ttk
import app.commands as cmnd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
import matplotlib.animation as anim
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
NavigationToolbar2Tk)
from matplotlib import style
import time


from PIL import ImageTk, Image
from visual.camera import Camera
from visual.calibration import *
from visual.tracker import *

# from visual.calibration import chessboard

# import visual.tracker

###    Setting time parameters    ###

dt = 25 #ms
fps = 30
exposure = 10000 #microseconds
anim_running = False
cam_running = False
# startup = False
#  amplitude, frequency, phase, phase offset
param = [0,0,0,np.pi/2]

###   Initialising the GUI window   ###
window = tk.Tk()

window.geometry(str(window.winfo_screenwidth())+"x"+str(window.winfo_screenheight()-40))
# window.configure(background = "#003050")
window.title("Pagraba spoles")
window.resizable(True, True)
style.use('ggplot')


###  The window which encloses the parameters below
frm_labels = tk.Frame(
    master=window,
    borderwidth=0,
    # background = "#003555"
)


frm_cam_btn = tk.Frame(
    master=window,
    borderwidth=0,
    # background = "#003555"
)
frm_cam_img = tk.Frame(
    master=window,
    borderwidth=3,
    width=500,
    height=500,
    relief=tk.GROOVE
    # background = "#003555"
)

### Number field windows for frequency, amplitude, phase, e.c
# the text part
lbl_freq = tk.Label(
    master=frm_labels,
    text="Frequency:",
    anchor="e",
    width=12
)
lbl_amp = tk.Label(
    master=frm_labels,
    text="Amplitude:",
    anchor="e",
    width=12
)
lbl_phase = tk.Label(
    master=frm_labels,
    text="Phase:",
    anchor="e",
    width=12
)
lbl_phase_off = tk.Label(
    master=frm_labels,
    text="Phase offset:",
    anchor="e",
    width=12
)


lbl_cam_fps = tk.Label(
    master=frm_cam_btn,
    text="Camera framerate: "+str(fps),
    anchor="w",
    width=20
)
lbl_cam_exp = tk.Label(
    master=frm_cam_btn,
    text="Camera exposure: "+str(exposure/1000)+"ms",
    anchor="w",
    width=20
)
lbl_cam_img = tk.Label(
    master=frm_cam_img,
    anchor="n",
)


# the blank field part
ent_freq = tk.Entry(
    master=frm_labels,
    width=10
)
ent_amp = tk.Entry(
    master=frm_labels,
    width=10
)
ent_phase = tk.Entry(
    master=frm_labels,
    width=10
)
ent_phase_off = tk.Entry(
    master=frm_labels,
    width=10
)


# ent_cam_fps = tk.Entry(
#     master=frm_cam_btn,
#     width=10
# )
# ent_cam_exp = tk.Entry(
#     master=frm_cam_btn,
#     width=10
# )


#setting values to the blank field
ent_freq.insert(0,"1")
ent_amp.insert(0,"1")
ent_phase.insert(0,"0")
ent_phase_off.insert(0,"90")

# ent_cam_fps.insert(0,"30")
# ent_cam_exp.insert(0,"10")

# placement of the varios components
frm_labels.place(x=5,y=5)
lbl_freq.grid(row=0,column=0)
lbl_amp.grid(row=1,column=0)
lbl_phase.grid(row=2,column=0)
lbl_phase_off.grid(row=3,column=0)

ent_freq.grid(row=0,column=1)
ent_amp.grid(row=1,column=1)
ent_phase.grid(row=2,column=1)
ent_phase_off.grid(row=3,column=1)
# puts together the window which encloses the parameters below
frm_labels.update()


frm_cam_btn.place(x=630,y=5)
lbl_cam_fps.grid(row=0,column=0)
lbl_cam_exp.grid(row=1,column=0)

# ent_cam_fps.grid(row=0,column=1)
# ent_cam_exp.grid(row=1,column=1)
frm_cam_btn.update()


frm_cam_img.place(x=630,y=180)
lbl_cam_img.pack()
frm_cam_img.update()
### Buttons
# A button to update the frequency and other parameters
btn_plot = tk.Button(
    master=window,
    text="Update plot",
    width=12,
    height=2,
    bg="#aafaaa",
    command=lambda: upd_param(lissajous_canvas)
)
# button placement
btn_plot.place(x=195, y=5)
# tip text box that appears when hovering over
cmnd.CreateToolTip(btn_plot, text =
                 'Mani nospiežot tiks nomainīta frekvence, amplitūda \n '
                 'un fāzes pēc tā, kas būs lauciņos norādīts.\n'
                 'Ja ir grafiks ir uzlikts uz pauzes, tad  \n'
                 'atjauninājumi stāsies spēkā uzspižot pogu "Start"')
# neccesary for to set the locaation in the first loop
btn_plot.update()

## Start /Stop button
btn_start = tk.Button(
    master=window,
    text="Start",
    width=12,
    height = 2,
    bg="#aafaaa",
    command=lambda:start_stop()
)
btn_start.place(x=195, y=58)
cmnd.CreateToolTip(btn_start, text =
                 'Nospiežot "Start" tiks nomainīta frekvence, amplitūda \n '
                 'un fāzes pēc tā, kas būs lauciņos norādīts,\n'
                 'padarot pogu "Update plot" par bezjēdzīgu.  \n'
                 'Sāksies grafika animācija. ',text2='Grafika animācija tiks apturēta! \n'
                 'Vai tu tiešām esi gatavs apturēt animāciju?')
btn_start.update()

btn_record = tk.Button(
    master=window,
    text="Start \nrecording",
    width=8,
    height = 3,
    bg="#aafaaa",
    command=lambda:toggle_cam(cam)
)
btn_record.place(x=630, y=frm_cam_btn.winfo_height()+10)

cmnd.CreateToolTip(btn_record, text =
                 'Sāk bilžu uzņemšanu bildes nesaglabājot. \n'
                 ,text2='Beidz rādīt kameras attēlu'
                 )

btn_record.update()

btn_show = tk.Button(
    master=window,
    text="Show \nimage",
    width=8,
    height = 3,
    bg="#aafaaa",
    # command=lambda:cmnd.update_image(cam.grab(),lbl_cam_img)
)
btn_show.place(x=708, y=frm_cam_btn.winfo_height()+10)
cmnd.CreateToolTip(btn_show, text =
                 'Poga!!!'
                 )

btn_show.update()

btn_calib = tk.Button(
    master=window,
    text="Calibrate",
    width=8,
    height = 3,
    bg="#aafaaa",
    # command=lambda:cmnd.update_image(cam.grab(),lbl_cam_img)
)
btn_calib.place(x=785, y=frm_cam_btn.winfo_height()+10)
cmnd.CreateToolTip(btn_calib, text =
                 'Poga!!!'
                 )

btn_calib.update()

### Functions that need global variables to function ###

### Do not move to a diferent folder ###


# Remake of the start stop button
def start_stop():
    global anim_running
    if anim_running:
        anim_running = False
        btn_start["text"] = "Start"
        btn_start["bg"] = "#aafaaa"
        ani.event_source.stop()

    else:
        anim_running = True
        btn_start["text"] = "Stop"
        btn_start["bg"] = "#faaaaa"
        ani.event_source.start()
        upd_param(lissajous_canvas)


def toggle_cam(cam):
    print("poga")
    global cam_running
    if cam_running:
        # cam.stop_capture()
        btn_record["text"] = "Start \nrecording"
        btn_record["bg"] = "#aafaaa"
    else:
        # cam.start_capture()
        btn_record["text"] = "Stop \nrecording"
        btn_record["bg"] = "#faaaaa"
    cam_running = not cam_running



### Making the plot  ###
# making the background to the plot
plot_canvas = tk.Canvas(
    master=window,
    height=600,
    width=600,
    background="#fafafa"
)

# the figure
fig = Figure(figsize = (10, 10), dpi = 50)
x = [0]
y1 = [0]
y2 = [0]
plot1 = fig.add_subplot(111)
plot1.set_xlim(-5, 0)
line1, = plot1.plot(x,y1)
line2, = plot1.plot(x,y2)


canvas = FigureCanvasTkAgg(
    fig,
    master = plot_canvas
)
canvas.draw()
canvas.get_tk_widget().pack()

toolbar = NavigationToolbar2Tk(
    canvas,
    plot_canvas
)
toolbar.update()

canvas.get_tk_widget().pack()

### lissajous grafiks ###
# canvas
lissajous_plot_canvas = tk.Canvas(
    master=window,
    height=150,
    width=150,
    background="#fafafa"
)

# the figure
lissajous_fig = Figure(figsize = (2, 2), dpi = 100)
lissajous_a = param[0]
lissajous_b = param[0]
lissajous_delta = param[3]
lissajous_a = 1
lissajous_b = 1

lissajous_t = np.linspace(-np.pi,np.pi,51)
lissajous_x = np.sin(lissajous_a * lissajous_t + lissajous_delta)
lissajous_y = np.sin(lissajous_b * lissajous_t)

lissajous_plot = lissajous_fig.add_subplot(111)
lissajous_plot.set_xlim(-1.2, 1.2)
lissajous_plot.set_ylim(-1.2, 1.2)
print(lissajous_t,lissajous_x,lissajous_y)
lissajous_line, =lissajous_plot.plot(lissajous_x,lissajous_y)
lissajous_fig.subplots_adjust(left=0, right=1, top=1, bottom=0)


lissajous_canvas = FigureCanvasTkAgg(
    lissajous_fig,
    master = lissajous_plot_canvas
)
lissajous_canvas.draw()
lissajous_canvas.get_tk_widget().pack()

#lissajous_toolbar = NavigationToolbar2Tk(
#    lissajous_canvas,
#    lissajous_plot_canvas
#)
#lissajous_toolbar.update()

#lissajous_canvas.get_tk_widget().pack()

def animate(i):

    t = np.around(dt*i/1000,3)
    x.append(t)
    y1_new = cmnd.next_sin_val(param[0],param[1],param[2],param[3],t)[0]
    y2_new = cmnd.next_sin_val(param[0],param[1],param[2],param[3],t)[1]
    y1.append(y1_new)
    y2.append(y2_new)

    plot1.set_xlim(x[-1]-5,x[-1])
    plot1.set_ylim(-max(np.max(y1[int(-5000/dt):])*1.1,np.max(y2[int(-5000/dt):])*1.1,0.5),max(np.max(y1[int(-5000/dt):])*1.1,np.max(y2[int(-5000/dt):])*1.1,0.5))

    line1.set_data(x,y1)
    line2.set_data(x,y2)

def upd_param(lissajous_canvas):
    ################### ŠĪĪĪĪĪĪĪ ##############
    global param
    if (cmnd.check_num(ent_amp.get()) and cmnd.check_num(ent_freq.get()) and cmnd.check_num(ent_phase.get()) and cmnd.check_num(ent_phase_off.get())):
        param = [ent_amp.get(),ent_freq.get(),ent_phase.get(),ent_phase_off.get()]

    #cmnd.clear_canvas(lissajous_canvas)

    lissajous_a = float(param[1])
    lissajous_b = float(param[1])
    lissajous_A = float(param[0])
    lissajous_B = float(param[0])
    lissajous_delta = float(param[3])/180*np.pi
    #lissajous_a = 1
    #lissajous_b = 1
    minf = min(lissajous_a,lissajous_b)
    lissajous_t = np.linspace(-np.pi,np.pi,300)/minf*2
    lissajous_y = lissajous_B*np.sin(lissajous_b * lissajous_t)
    lissajous_x = lissajous_A*np.sin(lissajous_a * lissajous_t + lissajous_delta)


    #lissajous_line.set_data(lissajous_x,lissajous_y)

    lissajous_plot = lissajous_fig.add_subplot(111)
    #lissajous_plot.set_xlim(-1.2, 1.2)
    #lissajous_plot.set_ylim(-1.2, 1.2)
    #print(lissajous_t,lissajous_x,lissajous_y)
    lissajous_line, =lissajous_plot.plot(lissajous_x,lissajous_y)
    lissajous_fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Stopping the animation in the begining


    lissajous_plot = lissajous_fig.add_subplot(111)
    #lissajous_plot.set_xlim(-1.2, 1.2)
    #lissajous_plot.set_ylim(-1.2, 1.2)
    #print(lissajous_t,lissajous_x,lissajous_y)
    lissajous_line, =lissajous_plot.plot(lissajous_x,lissajous_y)
    lissajous_fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    #cmnd.clear_canvas(lissajous_canvas)
    #former_canvas.delete('all')
    #lissajous_canvas = FigureCanvasTkAgg(
    #    lissajous_fig,
    #    master = lissajous_plot_canvas
    #)

    lissajous_canvas.draw()
    #lissajous_canvas.get_tk_widget().pack()



# Stopping the animation in the begining

ani = anim.FuncAnimation(fig, animate, interval=dt, blit=False)





def plot():
    fig = Figure(figsize = (10, 10), dpi = 50)
    x,y = cmnd.get_values(ent_amp.get(),ent_freq.get(),ent_phase.get())
    plot1 = fig.add_subplot(111)
    plot1.plot(x,y)

    canvas = FigureCanvasTkAgg(
        fig,
        master = plot_canvas
    )
    canvas.draw()
    canvas.get_tk_widget().pack()

    toolbar = NavigationToolbar2Tk(
        canvas,
        plot_canvas
    )
    toolbar.update()

    canvas.get_tk_widget().pack()

plot_canvas.place(x=20, y=155)
<<<<<<< HEAD
lissajous_plot_canvas.place(x=620, y=155)
#lissajous_plot_canvas.update()
#Bplot_canvas.update()

=======
>>>>>>> 7050b4fe7de3b84c9e2496a2c08f511977207e52
# tkinter.ttk.Separator(master=window,orient=tk.VERTICAL).pack(fill="y")


#Camera stuff
cam = 5#Camera(fps,exposure)
window.mainloop()
