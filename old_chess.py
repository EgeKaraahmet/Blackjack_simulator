import tkinter as tk
import bidict
from bidict import bidict


def open_blackjack():
    # TODO
    return



root_width = 1280
root_height = 960

main_menu_frame_width = 1280
main_menu_frame_height = 200
main_menu_button_width = 25
main_menu_button_height = 4




# Create main application window
root = tk.Tk()
root.title("Chess Menu")
root.geometry(newGeometry=f"{root_width}x{root_height}")  # Width x Height
root.configure(bg="black")  # Set background color



# Widgets for main menu
main_menu_frame = tk.Frame(root, bg="white", width=main_menu_frame_width, height=main_menu_frame_height)
button_chessboard = tk.Button(
main_menu_frame,                   # Attach to main window
    text="Open Chess Board",       # Button text
    command=open_chessboard,   # Function to call on click
    bg="lightblue",         # Background color
    fg="black",             # Text color
    height=4,               # Height in text lines
    width=25                # Width in characters
)
button_chessboard2 = tk.Button(
main_menu_frame,                   # Attach to main window
    text="Open Chess Board",       # Button text
    command=idle,   # Function to call on click
    bg="lightblue",         # Background color
    fg="black",             # Text color
    height=4,               # Height in text lines
    width=25                # Width in characters
)
button_chessboard3 = tk.Button(
main_menu_frame,                   # Attach to main window
    text="Open Chess Board",       # Button text
    command=idle,   # Function to call on click
    bg="lightblue",         # Background color
    fg="black",             # Text color
    height=4,               # Height in text lines
    width=25                # Width in characters
)




main_menu_frame.pack(side=tk.TOP)
main_menu_frame.pack_propagate(False)  # Prevent frame from resizing to fit contents


main_menu_image = tk.PhotoImage(file="media/Linux_logo.png")

main_menu_thumbnail = main_menu_image.subsample(1, 1)  # Resize image

tk.Label(root, image=main_menu_thumbnail).pack()

# Calculate positions for equal horizontal spacing
frame_width = 1280
frame_height = 200
button_width = 25 * 7  # Rough estimate: 7 pixels per character
button_height = 4 * 20  # Rough estimate: 20 pixels per text line

# Center vertically
y_pos = (frame_height - button_height) // 2

# Horizontal positions with 10px padding for outer buttons
x1 = 10
x3 = frame_width - button_width - 10
x2 = (frame_width - button_width) // 2

button_chessboard.place(x=x1, y=y_pos)
button_chessboard2.place(x=x2, y=y_pos)
button_chessboard3.place(x=x3, y=y_pos)

# Start the GUI event loop
root.mainloop()