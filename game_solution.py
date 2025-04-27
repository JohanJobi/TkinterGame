import tkinter as tk
from PIL import Image, ImageTk

window = tk.Tk()
window.title("Game")
window.geometry("900x535")

controls = {
"Move Left": "a",
"Move Right": "d",
"Jump": "w",
"Pause Toggle": "p",
"Boss Toggle": "b",
"Time Cheat Toggle": "t",
"Anit-Gravity Cheat Toggle": "g"
}

# timer variables
timer_seconds = 0
timer_running = False
coins_collected = 0


def reset_coins():
    """
    Reset the coins collected to 0
    Parameters:
        None
    Returns:
        None
        
    """
    global coins_collected
    coins_collected = 0
    coin_label.config(text=f"Coins: {coins_collected}")


# pause variables
game_paused = False
name = ""


def load_game():
    """
    Reads the file and calls the load_level function to load the player's level
    Parameters:
        None    
    Returns:
        None
    """
    global name
    # Load the player's level from the file if the name is not found then show error
    with open("levels.txt", "r") as file:
        content = file.readlines()

    level_found = False
    global current_level

    for line in content:
        file_name = (line.strip().split(":"))[0]
        level = (line.strip().split(":"))[1]
        #extracts the name and level from the file
        if file_name == name:
            level_found = True
            current_level = int(level)
            load_level(current_level)
            break

    if not level_found:
        show_error_message("No level found for this player!")
    

def show_error_message(message):
    """
    shows error message on the screen and removes it after 2 seconds
    Parameters:
        message    
    Returns:
        None
    """
    error_label = tk.Label(window, text=message, font=("Arial", 14), fg="red")
    error_label.pack(pady=10)
    # After 5 seconds, remove the error message
    window.after(2000, error_label.destroy)


def load_level(level):
    """
    Loads the level based on the level number
    Parameters:
        level    
    Returns:
        None
    """
    show_game()
    if level == 1:
        level_1
    elif level == 2:
        level_2()
    elif level == 3:
        level_3()
    elif level == 4:
        show_error_message("You have completed all levels!")


def update_timer():
    """
    Updates the timer every second
    Parameters:
        None    
    Returns:
        None
    """
    global timer_seconds, timer_running
    if timer_running:
        timer_label.config(text=f"Time: {timer_seconds} s")
        timer_seconds += 1
        window.after(1000, update_timer)


def timer_colour(colour):
    """
    Changes the colour of the timer label
    Parameters:
        None    
    Returns:
        None
    """
    timer_label.config(fg=colour)


def reset_timer():
    """
    Resets the timer to 0
    Parameters:
        None    
    Returns:
        None
    """
    global timer_seconds
    timer_seconds = 0
    timer_running = False


def start_timer():
    """
    Starts the timer
    Parameters:
        None    
    Returns:
        None
    """
    global timer_running, timer_seconds
    timer_seconds = 0
    timer_running = True
    update_timer()


def stop_timer():
    """
    Stops the timer
    Parameters:
        None    
    Returns:
        None
    """
    global timer_running
    timer_running = False


def show_menu():
    """
    Shows the menu frame and hides all other frames
    Parameters:
        None    
    Returns:
        None
    """
    global current_level, coins_collected

    for widget in window.winfo_children():
        widget.pack_forget()

    coins_collected = 0 
    current_level = 1

    try:
        leaderboard_frame.pack_forget()
    except:
        pass

    settings_frame.pack_forget()
    menu_frame.pack()


def show_game():
    """
    Shows the game frame and hides other non relevant frames
    Parameters:
        None    
    Returns:
        None
    """
    menu_frame.pack_forget()
    settings_frame.pack_forget()
    game_frame.pack()
    start_timer()
    canvas.pack()
    level_1()


def show_settings():
    """
    Shows the settings frame and hides other non relevant frames
    Parameters:
        None    
    Returns:
        None
    """
    menu_frame.pack_forget()
    game_frame.pack_forget()
    settings_frame.pack()


class Platform:
    """
    Class to represent platforms in the game  
    """
    def __init__(self, canvas, x, y, width, height, color="brown"):
        """
        Parameters:
            canvas: The canvas object where the platform will be drawn
            x: The x-coordinate of the platform
            y: The y-coordinate of the platform
            width: The width of the platform
            height: The height of the platform
            color: The color of the platform    
        """
        self.canvas = canvas
        self.platform = canvas.create_rectangle(x, y, x + width, y + height, fill=color)

    def get_coords(self):
        """
        Parameters:
            None    
        Returns:
            returns the coordinates of the platform
        """
        return self.canvas.coords(self.platform)


class MovingPlatform(Platform):
    """
    Class to represent moving platforms in the game (inherits from Platform)
    """
    def __init__(self, canvas, x, y, width, height, color="brown", speed=2, boundaries=[], direction=1):
        super().__init__(canvas, x, y, width, height, color)
        """
        Parameters:
            canvas: The canvas object where the platform will be drawn
            x: The x-coordinate of the platform
            y: The y-coordinate of the platform
            width: The width of the platform
            height: The height of the platform
            color: The color of the platform
            speed: The speed at which the platform will move
            boundaries: The boundaries within which the platform will move
            direction: The direction in which the platform will move (1 for right, -1 for left)    
        """
        self.speed = speed
        self.player = None  # Reference to the player object
        self.boundaries = boundaries
        self.direction = direction
        self.animate()
    
    def animate(self):
        """
        Animates the movement of the platform
        Parameters:
            None
        Returns:
            None
        """
        try:
            if  game_paused:
                return
            coords = self.get_coords()
            if coords[0] <= self.boundaries[0]:  # Left boundary
                self.direction = 1
            elif coords[2] >= self.boundaries[1]:  # Right boundary
                self.direction = -1

            dx = self.direction * self.speed
            self.canvas.move(self.platform, dx, 0)

            # Move the player if they are on top of the platform
            if self.is_player_on_top():
                self.player.move_with_platform(dx)

            self.canvas.after(30, self.animate)  # Repeat animation every 30ms
        except:
            pass

    def is_player_on_top(self):
        """
        Checks if the player is on top of the platform
        Parameters:
            None
        Returns:
            returns True if the player is on top of the platform
        """
        if not self.player:
            return False
        platform_coords = self.get_coords()
        player_coords = self.player.get_coords()

        # Check if the player's bottom is on the platform
        return (
            player_coords[2] > platform_coords[0]
            and player_coords[0] < platform_coords[2]
            and player_coords[3] == platform_coords[1]  
            # Player's bottom touching platform's top
        )


class DeathObject(Platform): 
    """
    Class to represent death objects in the game (inherits from Platform)
    """
    def __init__(self, canvas, x, y, width, height, color="red"):
        """
        Parameters:
            canvas: The canvas object where the death object will be drawn
            x: The x-coordinate of the death object
            y: The y-coordinate of the death object
            width: The width of the death object
            height: The height of the death object
            color: The color of the death object
        """
        super().__init__(canvas, x, y, width, height, color)


class NextLevel(Platform):  
    """
    Class to represent the next level object in the game (inherits from Platform)
    """
    def __init__(self, canvas, current_level, x, y, width, height, color="green"):
        """
        Parameters:
            canvas: The canvas object where the next level object will be drawn
            current_level: The current level of the player
            x: The x-coordinate of the next level object
            y: The y-coordinate of the next level object
            width: The width of the next level object
            height: The height of the next level object
            color: The color of the next level object
        """
        super().__init__(canvas, x, y, width, height, color)
        self.is_triggered = False  
        # To check if the player has touched the next level
        self.current_level = current_level
    def check_collision(self, player):
        """
        Checks if the player has touched the next level object
        Parameters:
            player: The player object
        """
        player_coords = player.get_coords()
        level_coords = self.get_coords()

        if (player_coords[2] > level_coords[0] and player_coords[0] < level_coords[2] and
                player_coords[3] > level_coords[1] and player_coords[1] < level_coords[3]):
            self.is_triggered = True

    def load_next_level(self):
        """
        Loads the next level
        Parameters:
            None
        Returns:
            None
        """
        global p1, platform, death_object, next_level
        if self.current_level == 1:
            level_2()
        elif self.current_level == 2:
            level_3()
        elif self.current_level == 3:
            end_game()
        elif self.current_level == 4:
            self.current_level = 1


class Coin:
    """
    Class to represent coins in the game
    """
    def __init__(self, canvas, x, y, size, color="yellow"):
        """
        Parameters:
            canvas: The canvas object where the coin will be drawn
            x: The x-coordinate of the coin
            y: The y-coordinate of the coin
            size: The size of the coin
            color: The color of the coin
        """
        self.canvas = canvas
        self.coin = canvas.create_oval(x, y, x + size, y + size, fill=color)
        self.origin_y = y  
        # Store the original y-coordinate for reference
        self.direction = 1  
        # 1 for down, -1 for up
        self.collected = False  
        # Tracks whether the coin has been collected
        self.animate()

    def get_coords(self):
        """
        Parameters:
            None
        Returns:
            returns the coordinates of the coin
        """
        return self.canvas.coords(self.coin)

    def remove(self):
        """
        Removes the coin from the canvas
        Parameters:
            None
        Returns:
            None
        """
        self.canvas.delete(self.coin)

    def animate(self):
        """
        Animates the movement of the coin
        Parameters:
            None
        Returns:
            None
        """
        if game_paused or self.collected:
            return
        coords = self.get_coords()
        if coords:
            # Restrict movement to 5 pixels from the original position
            if coords[1] >= self.origin_y + 5:  
                # Lower boundary
                self.direction = -1
            elif coords[1] <= self.origin_y - 5:  
                # Upper boundary
                self.direction = 1

            self.canvas.move(self.coin, 0, self.direction)  
            # Move vertically
            self.canvas.after(100, self.animate)  
            # Repeat animation every 50ms

    def collect(self, player):
        """
        Checks if the player has collected the coin
        Parameters:
            player: The player object
        Returns:
            returns True if the player has collected the coin
        """
        if not self.collected:
            player_coords = player.get_coords()
            coin_coords = self.get_coords()

            # Check if the player's block intersects with the coin
            if (player_coords[2] > coin_coords[0] and 
                player_coords[0] < coin_coords[2] and
                player_coords[3] > coin_coords[1] and 
                player_coords[1] < coin_coords[3]):
                self.collected = True
                self.remove()  
                # Remove the coin from the canvas
                return True
            
        return False


class Player:
    """
    Class to represent the player in the game
    """
    def __init__(self, canvas, platforms, coins, x, y, size, color="blue", move_amount=5, gravity=2, jump_strength=15,
                 death_objects=None, next_level_object=None):
        """
        Parameters:
            canvas: The canvas object where the player will be drawn
            platforms: List of platforms in the game
            coins: List of coins in the game
            x: The x-coordinate of the player
            y: The y-coordinate of the player
            size: The size of the player
            color: The color of the player
            move_amount: The amount by which the player will move
            gravity: The gravity acting on the player
            jump_strength: The strength of the jump
            death_objects: List of death objects in the game
            next_level_object: The next level object in the game
            """
        self.canvas = canvas 
        self.platforms = platforms  
        # List of platforms
        self.death_objects = death_objects 
        #List of death objects
        for platform in self.platforms:
            if isinstance(platform, MovingPlatform):
                platform.player = self
        for death_object in death_objects:
            if isinstance(death_object, DeathObject):
                death_object.player = self
        self.gravity_cheat = False
        self.current = gravity
        self.coins = coins
        self.next_level_object = next_level_object
        self.death_object = death_object
        self.killed = False
        self.move_amount = move_amount
        self.jump_strength = jump_strength
        self.gravity = gravity
        self.block = canvas.create_rectangle(x, y, x + size,
                                              y + size, fill=color)
        self.y_velocity = 0
        self.is_jumping = False
        self.apply_gravity()
        self.a_pressed = False
        self.d_pressed = False
        self.update_movement()
        self.check_next_level_collision()
        self.bind_controls()

    def bind_controls(self):
        """
        Binds the controls to the player
        Parameters:
            None
        Returns:
            None
        """
        window.bind(f"<KeyPress-{controls['Move Left']}>", 
            self.move_left_start)
        window.bind(f"<KeyRelease-{controls['Move Left']}>", 
                    self.move_left_stop)
        window.bind(f"<KeyPress-{controls['Move Right']}>", 
                    self.move_right_start)
        window.bind(f"<KeyRelease-{controls['Move Right']}>",
                     self.move_right_stop)
        window.bind(f"<KeyPress-{controls['Jump']}>", 
                    self.jump)
        window.bind(f"<KeyPress-{controls['Pause Toggle']}>",
                     self.pause)
        window.bind(f"<KeyPress-{controls['Boss Toggle']}>", 
                    self.boss_key)
        window.bind(f"<KeyPress-{controls['Time Cheat Toggle']}>", 
                    self.time_cheat_key)
        window.bind(f"<KeyPress-{controls['Anit-Gravity Cheat Toggle']}>", 
                    self.grav_cheat_key)
        # event=None used as window bind requires an
        #  event parameter for the function 

    def grav_cheat_key(self, event=None):
        """
        Toggles the anti-gravity cheat
        Parameters:
            event
        Returns:
            None
        """
        self.gravity_cheat = not self.gravity_cheat
        if self.gravity_cheat:
            self.current = self.gravity
            self.gravity = 0.5
        else:
            self.gravity = self.current

    def time_cheat_key(self, event=None):
        """
        Toggles the time cheat
        Parameters:
            event
        Returns:
            None
        """
        global timer_running, timer_seconds
        timer_running = not timer_running
        if timer_running:
            timer_colour("black")
            start_timer()
        else:
            timer_seconds = 0
            timer_colour("red")
            start_timer()
            stop_timer()

    def boss_key(self, event=None):
        """
        Toggles the boss key
        Parameters:
            event
        Returns:
            None
        """
        global game_paused, timer_running
        self.pause()

        if game_paused: 
            timer_running = False
            stop_timer()
            self.boss_window = tk.Toplevel()
            self.boss_window.title("Maths Work")
            self.boss_window.attributes("-fullscreen", True) 
            # Makes the window fullscreen
            self.boss_window.bind(f"<KeyPress-{controls['Boss Toggle']}>", 
                                  lambda event: self.boss_key())

            image = Image.open("image.png")

            # Resize the image to fit the screen
            screen_width = self.boss_window.winfo_screenwidth()
            screen_height = self.boss_window.winfo_screenheight()
            image = image.resize((screen_width, screen_height), 
                                 Image.LANCZOS)
            # Image.Resampling.LANCZOS is used to resize the image 
            # and maintian quality
            # Convert the image to a format Tkinter can use
            self.boss_image = ImageTk.PhotoImage(image) 
            # Create a label and display the image
            label = tk.Label(self.boss_window, image=self.boss_image)
            label.pack(fill="both", expand=True)
        else:
            self.boss_window.destroy()

    def move_with_platform(self, dx):
        """
        Moves the player with the platform
        Parameters:
            dx: velocity of player
        Returns:
            None
        """
        self.canvas.move(self.block, dx, 0)

    def apply_gravity(self):
        """
        Applies gravity to the player
        Also checks for collision with platforms, death objects,coins 
        and next level object

        Parameters:
            None
        Returns:
            None
        """
        # put this in try except as it will throw an error when the player is killed 
        try:
            if self.killed or game_paused:
                return
            self.y_velocity -= self.gravity
            self.canvas.move(self.block, 0, -self.y_velocity)

            # platfomr collision detection
            for platform in self.platforms:
                platform_coords = platform.get_coords()
                [px1, py1, px2, py2] = platform_coords
                [x1, y1, x2, y2] = self.canvas.coords(self.block)

                # Check for overlap on the x-axis and y axis to indicate
                # a collision on the side of platform
                x_overlap = x1 < px2 and x2 > px1
                y_overlap = y1 < py2 and y2 > py1

                if x_overlap and y_overlap:
                    # work out  smallest depth between the two 
                    # (of the collision)
                    x_depth = min(x2 - px1, px2 - x1)  
                    # Horizontal overlap depth
                    y_depth = min(y2 - py1, py2 - y1) 
                    # Vertical overlap depth

                    # Resolve collision based on the smaller overlap depth
                    if y_depth < x_depth: 
                        if y2 >= py1 and y1 < py1: 
                            # Player's bottom collides with platform's top
                            # then stop downward motion
                            # allow jumping again
                            self.canvas.move(self.block, 0, py1 - y2)
                            self.y_velocity = 0  
                            self.is_jumping = False  
                        elif y1 <= py2 and y2 > py2:  
                            # Player's top collides with platform's 
                            # bottom then stop upward motion
                            self.canvas.move(self.block, 0, py2 - y1 + 1)
                            self.y_velocity = 0 
                    else:
                        if x2 > px1 and x1 < px1:  
                            # Player's right collides with platform's left
                            self.canvas.move(self.block, px1 - x2, 0)
                        elif x1 < px2 and x2 > px2:  
                            # Player's left collides with platform's right
                            self.canvas.move(self.block, px2 - x1, 0)

            self.canvas.after(30, self.apply_gravity)

            # Check collision with death objects
            for death_object in self.death_objects:
                [dx1, dy1, dx2, dy2] = death_object.get_coords()
                [x1, y1, x2, y2] = self.get_coords()
                if x1 < dx2 and x2 > dx1 and y1 < dy2 and y2 > dy1:
                    self.killed = True
                    level_1()  
                    # Restart the level if the player dies
                    return
         
            self.check_next_level_collision()

            self.collect_coins()

        except:
            pass

    def check_next_level_collision(self):
        """
        Checks if the player has touched the next level object
        Parameters:
            None
        Returns:
            None
        """
        if self.next_level_object:
            self.next_level_object.check_collision(self)
            if self.next_level_object.is_triggered:
                self.next_level_object.load_next_level()

    def collect_coins(self):
        """
        Checks if the player has collected the coins
        Parameters:
            None
        Returns:
            None
        """
        global coins_collected
        for coin in self.coins:
            if not coin.collected and coin.collect(self):
                coins_collected += 1
                coin_label.config(text=f"Coins: {coins_collected}")

    def update_movement(self):
        """
        Updates the movement of the player every 30ms
        Parameters:
            None
        Returns:
            None
        """
        if self.killed or game_paused:
            return
        
        if self.a_pressed:
            x1 = self.canvas.coords(self.block)[0]
            if x1 > 0:  # Boundary check
                self.canvas.move(self.block, -self.move_amount, 0)

        if self.d_pressed:
            x2= self.canvas.coords(self.block)[2]
            if x2 < self.canvas.winfo_width():  # Boundary check
                self.canvas.move(self.block, self.move_amount, 0)

        self.canvas.after(30, self.update_movement)

    def get_coords(self):
        """
        Parameters:
            None
        Returns:
            returns the coordinates of the player
        """
        return self.canvas.coords(self.block)

    def jump(self, event=None):
        """
        Makes the player jump
        Parameters:
            event=None
        Returns:
            None
        """
        if not self.is_jumping:
            self.y_velocity = self.jump_strength
            self.is_jumping = True

    def move_left_start(self, event=None):
        """
        Moves the player left
        Parameters:
            event=None
        Returns:
            None
        """
        self.a_pressed = True

    def move_left_stop(self, event=None):
        """
        Stops the player from moving left
        Parameters:
            event=None
        Returns:
            None
        """
        self.a_pressed = False

    def move_right_start(self, event=None):
        """
        Moves the player right
        Parameters:
            event=None
        Returns:
            None
        """ 
        self.d_pressed = True

    def move_right_stop(self, event=None):
        """
        Stops the player from moving right
        Parameters:
            event=None
        Returns:
            None
        """
        self.d_pressed = False

    def pause(self, event=None):
        """
        Pauses the game
        Parameters:
            event=None
        Returns:
            None
        """
        global timer_running, game_paused
        game_paused = not game_paused
        if game_paused:
            self.a_pressed = False
            self.d_pressed = False
            self.is_jumping = False
            pause_menu.place(relx=0.5, rely=0.5, anchor="center") 
            timer_running = False
            stop_timer()
  
        else:
            timer_running = True
            pause_menu.place_forget()
            update_timer()

            # Restart animations and movement when unpausing
            for platform in self.platforms:
                if isinstance(platform, MovingPlatform):
                    platform.animate()
            for coin in self.coins:
                coin.animate()
            self.update_movement()
            self.apply_gravity()


# LEVEL 1
def level_1():
    """
    Creates the first level of the game
    Parameters:
        None
    Returns:
        None
    """
    global current_level
    current_level = 1
    reset_coins()
    canvas.delete("all")
    # Sets up timer and coin label
    timer_label.pack(side="left")
    coin_label.pack(side="left", padx=20)   
    
    
    # Static platforms
    platforms = [
        Platform(canvas, x=0, y=300, width=50, height=10, color="brown"),
        Platform(canvas, x=130, y=300, width=50, height=10, color="brown"),
        Platform(canvas, x=250, y=310, width=50, height=10, color="brown"),
        Platform(canvas, x=350, y=280, width=50, height=10, color="brown"),
        Platform(canvas, x=450, y=280, width=50, height=10, color="brown"),
        Platform(canvas, x=550, y=280, width=50, height=10, color="brown"),
        Platform(canvas, x=650, y=280, width=50, height=10, color="brown"),
        Platform(canvas, x=620, y=400, width=50, height=10, color="brown"),
        Platform(canvas, x=540, y=400, width=50, height=10, color="brown"),
        Platform(canvas, x=440, y=400, width=50, height=10, color="brown"),
        Platform(canvas, x=700, y=400, width=50, height=10, color="brown")
    ]

    death_objects = [
        DeathObject(canvas, x=0, y=490, width=900, height=10, color="red"),
    ]

    next_level_object = NextLevel(canvas, current_level, x=820, y=400, width=20, height=20, color="green")

    coins = [
        Coin(canvas, 200, 250, 20),
        Coin(canvas, 400, 200, 20),
        Coin(canvas, 600, 250, 20),
        Coin(canvas, 600, 360, 20),
        Coin(canvas, 540, 360, 20),
        Coin(canvas, 440, 360, 20)
    ]
    # Create player, passing the list of platforms and coins
    p1 = Player(canvas, platforms, coins, x=0, y=200, size=30, color="blue", death_objects=death_objects,
                next_level_object=next_level_object)


def level_2():
    """
    Creates the second level of the game
    Parameters:
        None
    Returns:
        None
    """
    global current_level
    current_level = 2
    canvas.delete("all")  

    # Static platforms
    platforms = [
        Platform(canvas, x=0, y=400, width=100, height=10, color="brown"),
        Platform(canvas, x=700, y=300, width=100, height=10, color="brown"),
        Platform(canvas, x=570, y=420, width=50, height=10, color="brown"),
        Platform(canvas, x=570, y=350, width=50, height=10, color="brown"),
        Platform(canvas, x=670, y=380, width=50, height=10, color="brown"),
        Platform(canvas, x=670, y=450, width=50, height=10, color="brown"),
        Platform(canvas, x=0, y=350, width=100, height=10, color="brown"),
        Platform(canvas, x=450, y=250, width=80, height=10, color="brown"),
        Platform(canvas, x=350, y=200, width=50, height=10, color="brown"),
        Platform(canvas, x=250, y=200, width=50, height=10, color="brown"),
        Platform(canvas, x=170, y=170, width=50, height=10, color="brown"),
        Platform(canvas, x=100, y=150, width=50, height=10, color="brown"),
        Platform(canvas, x=190, y=120, width=50, height=10, color="brown"),
        Platform(canvas, x=300, y=100, width=100, height=10, color="brown"),
        MovingPlatform(canvas, x=300, y=450, width=40, height=10, color="brown", 
                       speed=2.5, boundaries=[100, 580]),
        MovingPlatform(canvas, x=300, y=350, width=90, height=10, color="brown", 
                       speed=3, boundaries=[100, 580]),
        MovingPlatform(canvas, x=500, y=280, width=50, height=10, color="brown", 
                       speed=2, boundaries=[200, 600]),
        MovingPlatform(canvas, x=100, y=300, width=50, height=10, color="brown", 
                       speed=2, boundaries=[100, 200]),
        MovingPlatform(canvas, x=300, y=100, width=90, height=10, color="brown", 
                       speed=4, boundaries=[300, 840]),
    ]

    # Death objects
    death_objects = [
        DeathObject(canvas, x=0, y=490, width=900, height=10, color="red"),  
        DeathObject(canvas, x=300, y=340, width=7, height=7, color="red"),  
        DeathObject(canvas, x=700, y=390, width=100, height=10, color="red"),  
        DeathObject(canvas, x=510, y=230, width=100, height=10, color="red"),  
        DeathObject(canvas, x=600, y=90, width=20, height=10, color="red"),  
    ]

    # Next level object
    next_level_object = NextLevel(canvas, current_level, x=840, y=50, width=20, height=20, color="green")

    # Coins
    coins = [
        Coin(canvas, 300, 365, 20),
        Coin(canvas, 670, 430, 20),
        Coin(canvas, 100, 300, 20),
        Coin(canvas, 440, 200, 20),
        Coin(canvas, 620, 400, 20),
        Coin(canvas, 500, 230, 20),  
        Coin(canvas, 300, 140, 20),  
    ]

    # Player
    p1 = Player(canvas, platforms, coins, x=50, y=350, size=30, color="blue", death_objects=death_objects,
                next_level_object=next_level_object)

def level_3():
    """
    Creates the third level of the game
    Parameters:
        None
    Returns:
        None
    """
    global current_level
    current_level = 3
    canvas.delete("all")  

    # Static platforms
    platforms = [
        Platform(canvas, x=0, y=450, width=150, height=10, color="brown"),
        Platform(canvas, x=180, y=420, width=100, height=10, color="brown"),
        Platform(canvas, x=330, y=340, width=150, height=10, color="brown"),
        Platform(canvas, x=500, y=300, width=70, height=10, color="brown"),
        Platform(canvas, x=500, y=400, width=70, height=10, color="brown"),
        Platform(canvas, x=600, y=400, width=70, height=10, color="brown"),
        Platform(canvas, x=700, y=385, width=70, height=10, color="brown"),
        Platform(canvas, x=800, y=350, width=90, height=10, color="brown"),
        Platform(canvas, x=725, y=300, width=70, height=10, color="brown"),
        Platform(canvas, x=380, y=255, width=70, height=10, color="brown"),
        Platform(canvas, x=280, y=255, width=70, height=10, color="brown"),
        Platform(canvas, x=180, y=255, width=70, height=10, color="brown"),
        Platform(canvas, x=80, y=205, width=70, height=10, color="brown"),
        Platform(canvas, x=650, y=260, width=90, height=10, color="brown"),
        Platform(canvas, x=800, y=230, width=80, height=10, color="brown"),
        Platform(canvas, x=300, y=100, width=100, height=10, color="brown"),
        MovingPlatform(canvas, x=150, y=380, width=70, height=10, color="brown", 
                       speed=2, boundaries=[50, 300]),
        MovingPlatform(canvas, x=400, y=300, width=100, height=10, color="brown", 
                       speed=3, boundaries=[500, 700]),
        MovingPlatform(canvas, x=200, y=150, width=120, height=10, color="brown", 
                       speed=2.5, boundaries=[150, 400]),
        MovingPlatform(canvas, x=750, y=100, width=70, height=10, color="brown", 
                       speed=4, boundaries=[450, 850]),
    ]


    # Death objects
    death_objects = [
        DeathObject(canvas, x=0, y=490, width=900, height=10, color="red"),  
        DeathObject(canvas, x=150, y=430, width=80, height=10, color="red"),  
        DeathObject(canvas, x=600, y=270, width=100, height=10, color="red"),  
        DeathObject(canvas, x=400, y=200, width=10, height=10, color="red"),  
        DeathObject(canvas, x=500, y=140, width=150, height=10, color="red"),  
        DeathObject(canvas, x=750, y=70, width=10, height=10, color="red"),  
    ]

    # Next level object
    next_level_object = NextLevel(canvas, current_level, x=820, y=100, width=30, height=30, color="green")

    # Coins
    coins = [
        Coin(canvas, 100, 420, 20),
        Coin(canvas, 350, 330, 20),
        Coin(canvas, 650, 230, 20),
        Coin(canvas, 200, 130, 20),
        Coin(canvas, 800, 180, 20),
        Coin(canvas, 750, 50, 20),
        Coin(canvas, 400, 50, 20),
    ]

    # Create player, passing the list of platforms and coins
    p1 = Player(canvas, platforms, coins, x=50, y=400, size=30, color="blue", death_objects=death_objects,
                next_level_object=next_level_object)

    
def submit(input, name_label, submit_button):
    """
    Submits the name entered by the user
    Parameters:
        input: The text entry widget
        name_label: The label displaying the name prompt
        submit_button: The submit button
    Returns:
        None
    """
    global name
    # remove the name label, input box and submit button
    name = input.get()
    name_label.destroy()
    submit_button.destroy()
    input.destroy()
    if name == "":
        show_error_message("Name cannot be empty!")
        ask_name()
    else:
        show_menu()


def ask_name():
    """
    Asks the user to enter their name
    Parameters:
        None
    Returns: 
        None
    """
    name_label = tk.Label(window, text="Enter your name:", font=("Arial", 20))
    name_label.pack(pady=10)

    # Create and place a text entry box
    input = tk.Entry(window, width=30)
    input.pack(pady=5)

    # Create and place a submit button
    submit_button = tk.Button(window, text="Submit", command=lambda: submit(input, name_label, submit_button))
    submit_button.pack(pady=10)
    

def calculate_score():
    """
    Calculates the score of the player
    Parameters:
        None
    Returns:
        returns the score of the player
    """
    score = timer_seconds - (coins_collected*5)
    if score < 0:   
        score = 0
    return score


def show_leaderboard():
    """
    Shows the leaderboard by reading the scores from gameInfo.txt
    Parameters:
        None
    Returns:
        None
    """

    global leaderboard_frame
    #removes relevant frames
    endgame_frame.pack_forget()
    canvas.delete("all")
    menu_frame.pack_forget()
    canvas.pack_forget()
    leaderboard_frame = tk.Frame(window)
    leaderboard_frame.pack()
    tk.Label(leaderboard_frame, text="Leaderboard", font=("Arial", 24), fg="red").pack(pady=20)
    tk.Label(leaderboard_frame, text="NAME | SCORE", font=("Arial", 11)).pack(pady=20)
    f = open("gameInfo.txt", "r")
    scores = f.readlines()
    dict = {}
    # stops file reading error when reading white space in file
    
    for line in scores:
        # extracts name and score from each line
        [name, score] = (line.strip().split(":"))
        dict[name] = int(score)
    # stores the scores and names in dictionary
    dict = sorted(dict.items(), key=lambda item: item[1])
    rank = 1 

    for name, score in dict[:5]:  # Top 5 entries
        tk.Label(leaderboard_frame, text=f"{rank}. {name} | {score}", font=("Arial", 16)).pack(pady=10)
        rank += 1 

    f.close()
    tk.Button(leaderboard_frame, text="Back to Menu", command=show_menu, font=("Arial", 16)).pack(pady=10)
    

def save_level():
    """
    Saves the level of the player in levels.txt
    Parameters:
        None
    Returns:
        None
    """
    global current_level, name
    updated = False

    try:
        with open("levels.txt", "r") as f:
            lines = f.readlines()
    except:
        #make a file if not exists
        with open("levels.txt", "w") as f:
            f.write(f"{name}: {current_level}\n")
        return
    
    #updates if entry of name is already in file
    for i in range(len(lines)):
        if name in lines[i]:
            file_level = int(lines[i].split(": ")[1].strip()) 
            if current_level > file_level:
                lines[i] = f"{name}: {current_level}\n"
                updated = True
            break

    if not updated:
        for line in lines:
            if name in line:
                return  # Exit if no update is necessary
        lines.append(f"{name}: {current_level}\n")

    # writes updates into file
    with open("levels.txt", "w") as f:
        f.writelines(lines)


def save_score():
    """
    Saves the score of the player in gameInfo.txt
    Parameters:
        None
    Returns:
        None
    """
    global name
    updated = False
    current_score = calculate_score()

    try:
        with open("gameInfo.txt", "r") as f:
            lines = f.readlines()
    except:
        # If the file doesn't exist, create it and save the score
        with open("gameInfo.txt", "w") as f:
            f.write(f"{name}: {current_score}\n")
        save_level()  
        return

    # Update the score if the entry for the player's name exists
    for i in range(len(lines)):
        if name in lines[i]:
            file_score = int(lines[i].split(": ")[1].strip())  
            # Get the score from the file
            if current_score < file_score:
                lines[i] = f"{name}: {current_score}\n"  
                # Update the line with the new score
                updated = True
            break
    

    # If no update occurred, add the new entry for the player
    if not updated:
        for line in lines:
            if name in line:
                return  # Exit if no update is necessary (this should be redundant now)
        lines.append(f"{name}: {current_score}\n")

    # Write the updated lines back to the file
    with open("gameInfo.txt", "w") as f:
        f.writelines(lines)

    save_level()

# Frame for the game
game_frame = tk.Frame(window)
canvas = tk.Canvas(game_frame, width=900, height=500)
canvas.pack()

# Add timer and coin label in a single frame
status_frame = tk.Frame(game_frame)
status_frame.pack(anchor="nw", padx=10, pady=5)
timer_label = tk.Label(status_frame, text="Time: 0 s", font=("Arial", 16), fg="black")
coin_label = tk.Label(status_frame, text="Coins: 0", font=("Arial", 16), fg="black")


# Function to update a control binding
def update_control(action):
    """
    Updates the key binding for a specific action
    Parameters:
        action: The action to update 
    Returns:
        None
    """
    def set_key(event):
        """
        Sets the key binding for an action
        Parameters:
            event: The key press event
        Returns:
            None
        """
        new_key = event.keysym 
        # Get the name of key pressed
        controls[action] = new_key  
        # Update the controls dictionary
        control_buttons[action].config(text=f"{action}: {new_key}")  
        # Update button label
        window.unbind("<KeyPress>")  
        # Unbind the key press event after assignment

        # Bind a key press event to capture the new key
    window.bind("<KeyPress>", set_key)


# Settings screen
settings_frame = tk.Frame(window)
tk.Label(settings_frame, text="Customize Controls", font=("Arial", 24)).pack(pady=20)
controls_frame = tk.Frame(settings_frame)
controls_frame.pack(pady=20)
control_buttons = {}

for action, key in controls.items():
    # Create a button for each control
    button = tk.Button(
        controls_frame,
        text=f"{action}: {key}",
        font=("Arial", 16),
        command=lambda action=action: update_control(action)
    )
    button.pack(pady=5)
    control_buttons[action] = button  
    # Store button references for updates

tk.Button(settings_frame, text="Back to Menu", command=show_menu, font=("Arial", 12)).pack(pady=10)


# PAUSE MENU
pause_menu = tk.Frame(game_frame, bg="gray", width=300, height=200)
pause_menu.pack_propagate(False)  # this is used to prevent the frame from resizing to fit its contents
tk.Label(pause_menu, text="Paused", font=("Arial", 24), bg="gray", fg="white").pack(pady=20)
tk.Button(pause_menu, text="Back to Menu", font=("Arial", 16), command=show_menu).pack(pady=10)
tk.Button(pause_menu, text="Save", font=("Arial", 16), command=save_level).pack(pady=10)

def update_endgame():
    # END GAME MENU
    global endgame_frame
    endgame_frame = tk.Frame(window)
    tk.Label(endgame_frame, text="Congratulations! You have completed all levels!", font=("Arial", 24)).pack(pady=20)
    tk.Label(endgame_frame, text=f"Time: {timer_seconds} s", font=("Arial", 16)).pack(pady=10)
    tk.Label(endgame_frame, text=f"Coins Collected: {coins_collected}", font=("Arial", 16)).pack(pady=10)
    tk.Label(endgame_frame, text=f"Score: {calculate_score()}", font=("Arial", 16)).pack(pady=10)
    tk.Button(endgame_frame, text="Show LeaderBoard", command=show_leaderboard, font=("Arial", 16)).pack(pady=10)
    tk.Button(endgame_frame, text="Back to Menu", command=show_menu, font=("Arial", 16)).pack(pady=10)


# MENU
menu_frame = tk.Frame(window)
tk.Label(menu_frame, text="The Block Game", font=("Arial", 24)).pack(pady=20)
tk.Button(menu_frame, text="Play", command=show_game, font=("Arial", 16)).pack(pady=10)
tk.Button(menu_frame, text="Settings", command=show_settings, font=("Arial", 16)).pack(pady=10)
tk.Button(menu_frame, text="Show LeaderBoard", command=show_leaderboard, font=("Arial", 16)).pack(pady=10)
tk.Button(menu_frame, text="Load", command=load_game, font=("Arial", 16)).pack(pady=10)


def end_game():
    """
    Ends the game and shows the end game menu
    Parameters:
        None
    Returns:
        None
    """
    global current_level
    current_level = 4
    stop_timer()
    canvas.delete("all")
    timer_label.pack_forget()
    coin_label.pack_forget()
    canvas.pack_forget()
    update_endgame()
    endgame_frame.pack()
    save_score()


ask_name()
window.mainloop()