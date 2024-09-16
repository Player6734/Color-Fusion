from tkinter import ttk, filedialog, simpledialog, messagebox, colorchooser
from ttkthemes import ThemedTk, ThemedStyle
from tkinter.colorchooser import askcolor
from PIL import Image, ImageDraw
import tkinter as tk
import colorsys
import random
import re
import os


# GUI Application Class
class ColorFusionApp:
    def __init__(self, root):
        """
        Objectives:
        - Develop a GUI application named 'Color Fusion' for blending colors.
        - Enable users to input two colors and visualize the resulting gradient.
        - Provide a button for generating random color pairs.
        - Include a slider for selecting the number of intermediate colors in the gradient.
        - Display the gradient on a canvas, with options for different gradient styles.
        - Offer interactive features like AI color suggestions, gradient exporting, and detailed color information.

        Challenges and Solutions:
        - Challenge: Creating a user-friendly and visually appealing GUI.
        Solution: Used ttk (themed Tkinter) widgets for a modern look. Organized the layout with frames and grids to ensure a
        clean and intuitive interface. Custom styles were applied for buttons and other elements to enhance visual appeal.

        - Challenge: Managing color input, validation, and user guidance.
        Solution: Implemented a color picker dialog for easy color selection. Added validation logic in the 'pick_color'
        method to ensure correct color format. Provided an entry field for users to input guidance for AI-based color
        suggestions, enhancing the app's interactivity.

        - Challenge: Developing a robust color blending algorithm and dynamic gradient display.
        Solution: Created 'blend_colors' to calculate intermediate colors between two selected colors. Used
        'update_gradient_display' to redraw the gradient on the canvas whenever the user changes color inputs or the number
        of intermediate colors, ensuring a responsive and dynamic display.


        - Challenge: Allowing users to interact with the gradient and access detailed color information.
        Solution: Added functionality for users to click on the gradient, triggering a popup window that displays detailed
        color information (Hex, RGB, HSL) and a button to copy the Hex code. This feature enhances user engagement and
        utility.

        - Challenge: Providing a feature to export the created gradient as an image.
        Solution: Implemented 'export_gradient_as_png' to enable users to save their gradient as a PNG file. This function
        includes a file dialog for choosing the save location and filename, making the application more versatile.

        - Challenge: Ensuring text legibility over various color backgrounds.
        Solution: Developed 'get_legible_text_color' to dynamically adjust text color for optimal contrast against different
        background colors. This method calculates the brightness of the background and selects a legible text color
        accordingly.
        """

        # Root configuration
        self.root = root
        self.root.title("Color Fusion")

        # Set up the icon
        icon_path = "color_fusion.gif"  # Assuming the icon is in the same directory
        self.root.iconphoto(True, tk.PhotoImage(file=icon_path))

        # Set minimum window size
        self.root.minsize(500, 700)

        # Configure ttk Style using ThemedStyle
        style = ThemedStyle(self.root)
        style.theme_use("clam")

        # Define a new style for the hover state
        style.map(
            "Hover.TButton",
            background=[("active", "#eff0f1")],
            foreground=[("active", "#31363b")],
        )

        style.configure("TFrame", background="#31363b")
        style.configure("TButton", background="#3daee9", foreground="#eff0f1")

        self.root.configure(bg="#31363b")
        entry_padding = 5

        # Create a frame for the buttons
        self.button_frame = ttk.Frame(root)
        self.button_frame.pack(pady=10)

        # Create the input boxes with placeholders for Color One
        self.color_one_frame = ttk.Frame(root, style="TFrame", padding=(5, 5, 5, 5))

        # Random Color Button for Color One
        self.random_color_button = ttk.Button(
            self.color_one_frame,
            text="Random",
            command=lambda: self.fill_random_color(
                self.color_one_entry
            ),  # Updated to use the new method
            style="Hover.TButton",
        )
        self.random_color_button.pack(side=tk.LEFT, padx=entry_padding)

        # Color One Entry
        self.color_one_entry = PlaceholderEntry(
            self.color_one_frame,
            placeholder="Enter Color 1 Hex Code",
            width=20,
            bg="#32302F",
            fg="#eff0f1",
        )
        self.color_one_entry.pack(side=tk.LEFT, padx=entry_padding)
        self.color_one_entry.bind("<FocusIn>")

        # Color One Picker Button
        self.color_one_picker = ttk.Button(
            self.color_one_frame,
            text="Pick Color",
            command=lambda: self.pick_color(self.color_one_entry),
            style="Hover.TButton",
        )
        self.color_one_picker.pack(side=tk.LEFT, padx=entry_padding)
        self.color_one_frame.pack(pady=10)

        # Color Two Frame
        self.color_two_frame = ttk.Frame(root, style="TFrame", padding=(5, 5, 5, 5))

        # Random Color Button for Color Two
        self.random_color_two_button = ttk.Button(
            self.color_two_frame,
            text="Random",
            command=lambda: self.fill_random_color(
                self.color_two_entry
            ),  # Use the generalized method
            style="Hover.TButton",
        )
        self.random_color_two_button.pack(side=tk.LEFT, padx=entry_padding)

        # Color Two Entry
        self.color_two_entry = PlaceholderEntry(
            self.color_two_frame,
            placeholder="Enter Color 2 Hex Code",
            width=20,
            bg="#32302F",
            fg="#eff0f1",
        )
        self.color_two_entry.pack(side=tk.LEFT, padx=entry_padding)
        self.color_two_entry.bind("<FocusIn>")

        # Color Two Picker Button
        self.color_two_picker = ttk.Button(
            self.color_two_frame,
            text="Pick Color",
            command=lambda: self.pick_color(self.color_two_entry),
            style="Hover.TButton",
        )
        self.color_two_picker.pack(side=tk.LEFT, padx=entry_padding)
        self.color_two_frame.pack(pady=10)

        # Bind KeyRelease event to color entry widgets
        self.color_one_entry.bind("<KeyRelease>", self.update_gradient_display)
        self.color_two_entry.bind("<KeyRelease>", self.update_gradient_display)

        # Create label and scale for selecting intermediate colors
        self.intermediate_colors_label = tk.Label(
            root,
            text="Number of Intermediate Colors:",
            bg="#31363b",
            fg="#eff0f1",
        )

        self.intermediate_colors_label.pack(pady=5)
        self.intermediate_colors_scale = tk.Scale(
            root,
            from_=1,
            to=64,
            orient=tk.HORIZONTAL,
            length=300,
            command=self.update_gradient_display,
            bg="#31363b",
            fg="#eff0f1",
        )
        self.intermediate_colors_scale.set(10)
        self.intermediate_colors_scale.pack(pady=10)

        # Create gradient display canvas
        self.gradient_display = tk.Canvas(root, bg="#32302F")

        self.show_separations = tk.BooleanVar(
            value=True
        )  # Default is True to show separations
        self.separations_checkbox = tk.Checkbutton(
            root,
            text="Separations  ",
            variable=self.show_separations,
            command=self.update_gradient_display,
            bg="#3daee9",
            fg="#eff0f1",
        )
        self.separations_checkbox.pack(pady=5)
        self.gradient_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Bind click event
        self.gradient_display.bind("<Button-1>", self.on_gradient_click)

        # Track last valid gradient
        self.last_valid_gradient = None

        # Update gradient display
        self.update_gradient_display()

        self.export_button = ttk.Button(
            root,
            text="Export Gradient",
            command=self.export_gradient_as_png,
            style="Hover.TButton",
        )

        self.export_button.pack(pady=10)

        # Bind resize event
        root.bind("<Configure>", self.handle_resize)

    def fill_random_color(self, color_entry):
        """
        Fills the given color entry field with a random color.

        Generates a random hex color code and updates the specified color entry field with
        this value. Also triggers an update of the gradient display.
        """
        random_color = "#{:02X}{:02X}{:02X}".format(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        )

        color_entry.delete(0, tk.END)
        color_entry.insert(0, random_color)

        # Update text color to default
        color_entry["fg"] = color_entry.default_fg_color

        self.update_gradient_display()

    def update_scale_length(self):
        gradient_width = self.gradient_display.winfo_width()
        new_scale_length = max(gradient_width - 20, 100)  # Ensures a minimum length
        self.intermediate_colors_scale.configure(length=new_scale_length)

    def handle_resize(self, event):
        # Handle window resize event.
        self.update_gradient_display()
        self.update_scale_length()

    def pick_color(self, entry):
        """
        Open a color picker dialog and update the entry with the selected color.
        If the entry contains a placeholder, the color picker will open with a default color.

        Args:
            entry (tk.Entry): The entry widget to update with the selected color.
        """
        color_value = entry.get().lstrip("#")

        # Check if the current value is a placeholder, and set a default color if it is
        if color_value in [
            self.color_one_entry.placeholder,
            self.color_two_entry.placeholder,
        ]:
            color_value = "000000"  # Default color, e.g., black

        color = colorchooser.askcolor(title="Pick a Color", color="#" + color_value)
        if color[1]:
            entry.delete(0, tk.END)
            entry.insert(0, color[1])
            self.update_gradient_display()

    def update_gradient_display(self, event=None):
        """
        Update the gradient display based on user inputs.
        """
        try:
            color_one_hex = self.color_one_entry.get()
            color_two_hex = self.color_two_entry.get()

            # Default colors if inputs are placeholders or empty
            color_one_hex = color_one_hex if color_one_hex not in [self.color_one_entry.placeholder, ""] else "#000000"
            color_two_hex = color_two_hex if color_two_hex not in [self.color_two_entry.placeholder, ""] else "#ffffff"

            rgb_color1 = self.get_rgb_from_hex(color_one_hex)
            rgb_color2 = self.get_rgb_from_hex(color_two_hex)

            number_of_colors = self.intermediate_colors_scale.get()
            blended_colors = self.blend_colors(rgb_color1, rgb_color2, number_of_colors)

            self.last_valid_gradient = blended_colors
            self.draw_horizontal_gradient(blended_colors, rgb_color2)

        except ValueError as e:
            self.handle_gradient_error(e)

    def handle_gradient_error(self, error):
        """
        Handle errors that occur during gradient generation and display.
        """
        if self.last_valid_gradient:
            self.draw_horizontal_gradient(self.last_valid_gradient, self.get_rgb_from_hex("#ffffff"))
        else:
            self.display_error_message(f"Error: {error}")

    def display_error_message(self, message):
        """
        Display an error message on the gradient display area.
        """
        self.gradient_display.delete("all")
        self.gradient_display.create_text(
            self.gradient_display.winfo_reqwidth() // 2,
            self.gradient_display.winfo_reqheight() // 2,
            text=message,
            fill="black",
            anchor="center",
        )

    def get_legible_text_color(self, rgb):
        """
        Determines a legible text color (white or black) based on the brightness of the given color.

        This method calculates the brightness of the provided RGB color and returns a contrasting
        text color (white for dark backgrounds and black for light backgrounds) to ensure legibility.

        Parameters:
        rgb (tuple): A tuple representing the RGB color (e.g., (255, 255, 255) for white).

        Returns:
        str: A hex string representing the chosen text color ('#FFFFFF' for white, '#000000' for black).
        """
        return "#EFF0F1" if self.is_color_dark(rgb) else "#31363B"

    def draw_horizontal_gradient(self, blended_colors, color2):
        """
        Draws a horizontal gradient on the canvas using the provided color list.

        This method iterates over the list of blended colors and draws them as
        rectangles on the canvas. If the 'show_separations' option is enabled, it
        draws separations between the colors.

        Parameters:
        blended_colors (list): A list of RGB tuples representing the colors to be displayed.
        color2 (tuple): The RGB tuple of the second color, used for error handling.
        """

        self.gradient_display.delete("all")

        canvas_height = self.gradient_display.winfo_height()
        canvas_width = self.gradient_display.winfo_width()
        color_width = canvas_width / len(blended_colors)

        for i in range(len(blended_colors)):
            color_hex = "#{:02X}{:02X}{:02X}".format(
                blended_colors[i][0], blended_colors[i][1], blended_colors[i][2]
            )
            if self.show_separations.get():
                # Draw rectangles with default outline for separation
                self.gradient_display.create_rectangle(
                    i * color_width,
                    0,
                    (i + 1) * color_width,
                    canvas_height,
                    fill=color_hex,
                )
            else:
                # Extend each rectangle slightly to the right to overlap with the next one and remove outline
                self.gradient_display.create_rectangle(
                    i * color_width,
                    0,
                    (i + 1) * color_width + 1,
                    canvas_height,
                    fill=color_hex,
                    outline=color_hex,
                )

    def on_gradient_click(self, event):
        """
        Handles the click event on the gradient display.

        This method calculates which color was clicked on the gradient and opens
        a popup window to show details about that color.

        Parameters:
        event (Event): The event object containing information about the click event.
        """
        color_index = int(
            event.x
            / (self.gradient_display.winfo_width() / len(self.last_valid_gradient))
        )
        clicked_color = self.last_valid_gradient[
            min(color_index, len(self.last_valid_gradient) - 1)
        ]
        color_hex = "#{:02X}{:02X}{:02X}".format(
            clicked_color[0], clicked_color[1], clicked_color[2]
        )

        # Show color details popup
        self.show_color_details_popup(color_hex)

    def show_color_details_popup(self, color_hex):
        """
        Displays a popup window with details of the selected color.

        This method creates a new window showing the hex, RGB, and HSL values of
        the provided color. It also includes a button to copy the hex code to the clipboard.

        Parameters:
        color_hex (str): The hex string of the color to display details for.
        """
        rgb = self.get_rgb_from_hex(color_hex)
        hsl = colorsys.rgb_to_hls(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

        popup = tk.Toplevel(self.root)
        popup.title("Color Details")
        popup.geometry("300x200")  # Adjust size as needed

        # Determine text color for legibility
        text_color = self.get_legible_text_color(rgb)

        # Set the background to the selected color
        popup.configure(bg=color_hex)

        tk.Label(
            popup,
            text=f"Hex: {color_hex}",
            font=("Arial", 12),
            bg=color_hex,
            fg=text_color,
        ).pack(pady=5)
        tk.Label(
            popup, text=f"RGB: {rgb}", font=("Arial", 12), bg=color_hex, fg=text_color
        ).pack(pady=5)
        tk.Label(
            popup,
            text=f"HSL: ({round(hsl[0]*360)}, {round(hsl[1]*100)}%, {round(hsl[2]*100)}%)",
            font=("Arial", 12),
            bg=color_hex,
            fg=text_color,
        ).pack(pady=5)

        rgb = self.get_rgb_from_hex(color_hex)
        button_bg_color = self.adjust_color_brightness(
            rgb, 1.5 if self.is_color_dark(rgb) else 0.8
        )

        copy_button = tk.Button(
            popup,
            text="Copy Hex Code",
            bg=button_bg_color,
            fg=self.get_legible_text_color(rgb),
            command=lambda: self.copy_to_clipboard(color_hex, copy_button),
        )
        copy_button.pack(pady=10)

    def copy_to_clipboard(self, text, button):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        original_text = button.cget("text")
        button.config(text="Copied!")

        # Revert the button text after a delay
        button.after(1500, lambda: button.config(text=original_text))

    def adjust_color_brightness(self, rgb, factor, min_threshold=30):  # this way it can deal with very dark colors too
        # Adjust the brightness of the color
        adjusted_rgb = (
            max(min_threshold, min(255, int(rgb[0] * factor))),
            max(min_threshold, min(255, int(rgb[1] * factor))),
            max(min_threshold, min(255, int(rgb[2] * factor))),
        )
        return "#{:02X}{:02X}{:02X}".format(*adjusted_rgb)

    def is_color_dark(self, rgb):
        # Calculate brightness
        brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
        return brightness < 123

    def get_rgb_from_hex(self, hex_code):
        """
        Convert a hex color code to an RGB tuple.

        Args:
            hex_code (str): The hex color code.

        Returns:
            tuple: The corresponding RGB tuple.

        Raises:
            ValueError: If the hex code is invalid.
        """
        if hex_code == self.color_one_entry.placeholder:
            return (0, 0, 0)  # Default black for color one
        elif hex_code == self.color_two_entry.placeholder:
            return (255, 255, 255)  # Default white for color two

        hex_code = hex_code.lstrip("#")

        if len(hex_code) != 6:
            raise ValueError("Hex color code must be 6 characters long")

        try:
            r = int(hex_code[0:2], 16)
            g = int(hex_code[2:4], 16)
            b = int(hex_code[4:6], 16)
            return r, g, b
        except ValueError:
            raise ValueError("Invalid hex color code")

    def blend_colors(self, color1, color2, num_midpoints):
        blended_colors = [color1]

        if num_midpoints >= 1:
            for i in range(1, num_midpoints + 1):
                ratio = i / (num_midpoints + 1)
                blended_color = (
                    round(color1[0] + ratio * (color2[0] - color1[0])),
                    round(color1[1] + ratio * (color2[1] - color1[1])),
                    round(color1[2] + ratio * (color2[2] - color1[2])),
                )
                blended_colors.append(blended_color)

        blended_colors.append(color2)  # Include color2 in the list
        return blended_colors

    def export_gradient_as_png(self):
        """
        Exports the current gradient as a PNG file.

        This method allows the user to save the currently displayed gradient as a PNG image.
        The user is prompted to choose a file location and name for saving the image.
        The default filename is based on the hex codes of the two primary colors used in the gradient.

        Exceptions:
        Catches and displays an error message if there is an issue during the file saving process.
        """
        try:
            color_one_hex = self.color_one_entry.get() or "#000000"
            color_two_hex = self.color_two_entry.get() or "#ffffff"
            default_filename = f"{color_one_hex}_fused_with_{color_two_hex}.png"
            default_dir = os.path.join(os.path.expanduser("~"), "Downloads")

            file_path = filedialog.asksaveasfilename(
                initialdir=default_dir,
                defaultextension=".png",
                initialfile=default_filename,
                filetypes=[("PNG files", "*.png")],
            )
            if not file_path:
                return

            gradient_image = self.generate_gradient(
                color_one_hex, color_two_hex, 2160, 2160
            )
            gradient_image.save(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def generate_gradient(self, color_one_hex, color_two_hex, width, height):
        """
        Generates a gradient image based on two color hex codes.

        This method creates a new image with the specified width and height, and draws a gradient
        between the two provided hex color codes. The gradient is created by blending the colors
        and drawing rectangles of these colors side by side on the image.

        Parameters:
        color_one_hex (str): The hex code of the first color.
        color_two_hex (str): The hex code of the second color.
        width (int): The width of the generated image.
        height (int): The height of the generated image.

        Returns:
        Image: The generated image with the gradient.
        """
        gradient_image = Image.new("RGB", (width, height), "#FFFFFF")
        draw = ImageDraw.Draw(gradient_image)

        blended_colors = self.blend_colors(
            self.get_rgb_from_hex(color_one_hex),
            self.get_rgb_from_hex(color_two_hex),
            self.intermediate_colors_scale.get(),
        )
        color_width = width / len(blended_colors)

        for i, color in enumerate(blended_colors):
            color_hex = "#{:02X}{:02X}{:02X}".format(color[0], color[1], color[2])
            draw.rectangle(
                [i * color_width, 0, (i + 1) * color_width, height], fill=color_hex
            )

        return gradient_image


class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color="grey", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self["fg"]

        self.bind("<FocusIn>", self._handle_focus_in)
        self.bind("<FocusOut>", self._add_placeholder)

        self._add_placeholder(initial=True)

    def _handle_focus_in(self, e):
        if self.get() == self.placeholder and self["fg"] == self.placeholder_color:
            self.delete(0, "end")
            self["fg"] = self.default_fg_color
        else:
            # Select all text
            self.select_range(0, tk.END)

    def _add_placeholder(self, e=None, initial=False):
        if not self.get() or (initial and self.get() == self.placeholder):
            self.insert(0, self.placeholder)
            self["fg"] = self.placeholder_color

    def _handle_typing(self, e):
        if self.get() == self.placeholder:
            self.delete(0, "end")
            self["fg"] = self.default_fg_color

    def is_placeholder_active(self):
        return self.get() == self.placeholder and self["fg"] == self.placeholder_color



if __name__ == "__main__":
    root = ThemedTk(theme="alt")
    app = ColorFusionApp(root)
    root.mainloop()
