import tkinter as tk
from datetime import datetime

# Define 5x3 grids for numbers 0-9 and 1x5 grid for ":"
numbers = {
    0: [[1, 1, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 1]],
    1: [[0, 1, 0], [1, 1, 0], [0, 1, 0], [0, 1, 0], [1, 1, 1]],
    2: [[1, 1, 1], [0, 0, 1], [1, 1, 1], [1, 0, 0], [1, 1, 1]],
    3: [[1, 1, 1], [0, 0, 1], [1, 1, 1], [0, 0, 1], [1, 1, 1]],
    4: [[1, 0, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 0, 1]],
    5: [[1, 1, 1], [1, 0, 0], [1, 1, 1], [0, 0, 1], [1, 1, 1]],
    6: [[1, 1, 1], [1, 0, 0], [1, 1, 1], [1, 0, 1], [1, 1, 1]],
    7: [[1, 1, 1], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 0]],
    8: [[1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 1, 1]],
    9: [[1, 1, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [1, 1, 1]],
    ":": [[0], [1], [0], [1], [0]],  # Colon shape
    "-": [[0, 0, 0], [0, 0, 0], [1, 1, 1], [0, 0, 0], [0, 0, 0]],  # Dash shape
}

# Hardcoded namedays and birthdays
special_dates = {
    "24-12": "XMAS",

}

# Draw a number or symbol (like ":") using a grid on the canvas
def draw_number(canvas, number, x, y, size=20):
    grid = numbers[number]
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if cell == 1:
                canvas.create_rectangle(
                    x + j * size, y + i * size,
                    x + (j + 1) * size, y + (i + 1) * size,
                    fill="green", outline=""
                )

# Update the clock display
def update_clock():
    now = datetime.now()
    hours, minutes, seconds = now.hour, now.minute, now.second
    day = now.strftime("%a")  # Day as Mon, Tue, etc.
    date = now.strftime("%d-%m-%Y")  # Date as dd-mm-yyyy
    today_key = now.strftime("%d-%m")  # Key for namedays and birthdays

    # Clear the canvas
    canvas.delete("all")

    # Draw hours and minutes in the larger grid
    draw_number(canvas, hours // 10, 10, 10)  # First digit of hour
    draw_number(canvas, hours % 10, 90, 10)  # Second digit of hour

    # Draw colon (:) between hours and minutes
    draw_number(canvas, ":", 170, 10, size=20)

    # Draw minutes
    draw_number(canvas, minutes // 10, 210, 10)  # First digit of minute
    draw_number(canvas, minutes % 10, 290, 10)  # Second digit of minute

    # Draw seconds in a smaller grid to the right of minutes
    draw_number(canvas, seconds // 10, 370, 60, size=10)  # First digit of seconds
    draw_number(canvas, seconds % 10, 410, 60, size=10)  # Second digit of seconds

    # Draw the day (e.g., Mon) above the seconds
    canvas.create_text(400, 30, text=day, font=("Fixedsys", 30), fill="green")

    # Draw the date below the clock (same size as seconds)
    y_offset = 120  # Offset for date alignment
    draw_number(canvas, int(date[0]), 10, y_offset, size=5)  # First digit of day
    draw_number(canvas, int(date[1]), 30, y_offset, size=5)  # Second digit of day
    draw_number(canvas, "-", 50, y_offset, size=5)  # Dash
    draw_number(canvas, int(date[3]), 70, y_offset, size=5)  # First digit of month
    draw_number(canvas, int(date[4]), 90, y_offset, size=5)  # Second digit of month
    draw_number(canvas, "-", 110, y_offset, size=5)  # Dash
    draw_number(canvas, int(date[6]), 130, y_offset, size=5)  # First digit of year
    draw_number(canvas, int(date[7]), 150, y_offset, size=5)
    draw_number(canvas, int(date[8]), 170, y_offset, size=5)
    draw_number(canvas, int(date[9]), 190, y_offset, size=5)

    # Add names for namedays and birthdays
    name = special_dates.get(today_key, "")
    if name:
        canvas.create_text(350, 130, text=name, font=("Fixedsys", 30), fill="green")

    # Schedule the next update
    root.after(1000, update_clock)

# Create the main tkinter window
root = tk.Tk()
root.title("Smart Clock")
root.overrideredirect(True)

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set the position of the window to the bottom right corner
window_width = 450
window_height = 160
x_position = screen_width - window_width - 0
y_position = screen_height - window_height - 40

# Set the window geometry (position + size)
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Create a canvas for the clock display
canvas = tk.Canvas(root, width=window_width, height=window_height, bg="black", highlightthickness=0)
canvas.pack()

# Close the window when "Esc" key is pressed
root.bind("<Escape>", lambda e: root.quit())

# Start the clock
update_clock()

# Run the tkinter main loop
root.mainloop()