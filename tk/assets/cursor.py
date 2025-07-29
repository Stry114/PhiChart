import tkinter as t
def show(cursor, i):
    t.Label(f, text=cursor, cursor=cursor).grid(column=i // 20, row=i % 20)
f = t.Tk(className='Cursor')
cursorList = ['arrow', 'xterm', 'watch', 'hand2', 'question_arrow', 'sb_h_double_arrow', 'sb_v_double_arrow', 'fleur',
              'crosshair', 'based_arrow_down', 'based_arrow_up', 'boat', 'bogosity', 'top_left_corner',
              'top_right_corner', 'bottom_left_corner', 'bottom_right_corner', 'top_side', 'bottom_side', 'top_tee',
              'bottom_tee', 'box_spiral', 'center_ptr', 'circle', 'clock', 'coffee_mug', 'cross', 'cross_reverse',
              'diamond_cross', 'dot', 'dotbox', 'double_arrow', 'top_left_arrow', 'draft_small', 'draft_large',
              'left_ptr', 'right_ptr', 'draped_box', 'exchange', 'gobbler', 'gumby', 'hand1', 'heart', 'icon',
              'iron_cross', 'left_side', 'right_side', 'left_tee', 'right_tee', 'leftbutton', 'middlebutton',
              'rightbutton', 'll_angle', 'lr_angle', 'man', 'mouse', 'pencil', 'pirate', 'plus', 'rtl_logo', 'sailboat',
              'sb_left_arrow', 'sb_right_arrow', 'sb_up_arrow', 'sb_down_arrow', 'shuttle', 'sizing', 'spider',
              'spraycan', 'star', 'target', 'tcross', 'trek', 'ul_angle', 'umbrella', 'ur_angle', 'X_cursor']
for i in range(len(cursorList)):
    show(cursorList[i], i)
f.mainloop()