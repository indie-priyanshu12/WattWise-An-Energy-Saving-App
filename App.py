import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime, timedelta, time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import google.generativeai as genai
import os
import sys
import re 

# --- Dependency Checker ---
def check_and_install_packages():
    """Checks for required packages and prompts the user to install them if missing."""
    required_packages = ['pandas', 'seaborn', 'matplotlib']
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        msg = (f"The following required libraries are missing:\n\n"
               f"{', '.join(missing_packages)}\n\n"
               f"Please install them by running this command in your terminal:\n"
               f"pip install {' '.join(missing_packages)}")
        messagebox.showerror("Missing Libraries", msg)
        sys.exit(1)

check_and_install_packages()

# --- Main App Configuration ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
sns.set_style("whitegrid")
sns.set_palette("viridis")

class Device:
    """Represents a single electrical device with power rating and usage tracking."""
    def __init__(self, name, power):
        self.name = name
        self.power = power
        self.is_on = False
        self.session_usage_seconds = 0
        self.saved_usage_units = 0.0
        self.last_on_time = None

    def toggle(self):
        if self.is_on:
            self.is_on = False
            if self.last_on_time:
                self.session_usage_seconds += (datetime.now() - self.last_on_time).total_seconds()
                self.last_on_time = None
        else:
            self.is_on = True
            self.last_on_time = datetime.now()

    def update_session_usage(self):
        if self.is_on and self.last_on_time:
            now = datetime.now()
            self.session_usage_seconds += (now - self.last_on_time).total_seconds()
            self.last_on_time = now

    def get_session_units(self):
        return (self.power * self.session_usage_seconds) / (1000 * 3600)

    def get_total_units(self):
        return self.saved_usage_units + self.get_session_units()

class App(ctk.CTk):
    """The main application window for the Power Usage Tracker."""
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.title(f"Device Power Usage Tracker - {self.username}")
        self.geometry("850x700")

        self.devices = []
        self.device_widgets = []
        
        self.data_file = f"{self.username}_data.txt"
        self.is_closing = False

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabview.configure(
            fg_color="#393E46",
            segmented_button_fg_color="#393E46",
            segmented_button_selected_color="#FFD369",
            segmented_button_unselected_color="#393E46",
            segmented_button_unselected_hover_color="#5cb85c",
            segmented_button_selected_hover_color="#FFD369"
        )

        self.home_tab = self.tabview.add("  Home  ")
        self.stats_tab = self.tabview.add("  Stats  ")
        self.leaderboard_tab = self.tabview.add("Leaderboard") # Added Leaderboard Tab

        self.setup_home_tab()
        self.setup_stats_tab()
        self.setup_leaderboard_tab() # Setup the leaderboard tab
        
        self.load_state()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.last_selected_tab = "Home"
        self.check_tab_change()
        self.update_all_usages()

    def setup_home_tab(self):
        top_frame = ctk.CTkFrame(self.home_tab, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(5,0))
        username_label = ctk.CTkLabel(top_frame, text=f"User: {self.username}", font=("Arial", 16, "bold"), text_color="#FFD369")
        username_label.pack(anchor="w", side="left")
        save_button = ctk.CTkButton(top_frame, text="Save Usage", command=self.save_usage, fg_color="#FFD369", text_color="#222831", font=("Arial", 14, "bold"))
        save_button.pack(anchor="e", side="right")
        add_frame = ctk.CTkFrame(self.home_tab, fg_color="transparent")
        add_frame.pack(pady=10, padx=10, fill="x")
        self.name_entry = ctk.CTkEntry(add_frame, placeholder_text="Device Name", fg_color="#222831", text_color="#FFD369", font=("Arial", 16), height=40)
        self.name_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.power_entry = ctk.CTkEntry(add_frame, placeholder_text="Power (Watts)", fg_color="#222831", text_color="#FFD369", font=("Arial", 16), height=40)
        self.power_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.add_btn = ctk.CTkButton(add_frame, text="Add Device", command=self.add_device, fg_color="#FFD369", text_color="#222831", font=("Arial", 16, "bold"), height=40, width=140, corner_radius=10)
        self.add_btn.pack(side="left", padx=5)
        self.devices_frame = ctk.CTkScrollableFrame(self.home_tab, fg_color="transparent")
        self.devices_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.total_usage_label = ctk.CTkLabel(self.home_tab, text="Total Usage: 0.000 units", font=("Arial", 18, "bold"), text_color="#FFD369")
        self.total_usage_label.pack(pady=10)
        
        self.recommendation_label = ctk.CTkLabel(self.home_tab, text="AI Recommendations:", font=("Arial", 14, "bold"), text_color="#FFD369")
        self.recommendation_label.pack(pady=(10, 0))
        
        # Using tk.Text with styling to match CTkinter theme for rich text
        self.recommendation_box = tk.Text(self.home_tab, 
                                          state="disabled", 
                                          bg="#222831", 
                                          fg="#FFFFFF", # White text
                                          insertbackground="#FFD369", 
                                          font=("Arial", 14), 
                                          height=7, 
                                          relief="flat", 
                                          bd=0, 
                                          wrap="word",
                                          padx=5, pady=5) # Added padding to the textbox itself
        self.recommendation_box.pack(pady=(5, 10), padx=10, fill="x")
        
        # Define tags for formatting
        self.recommendation_box.tag_configure("bold", font=("Arial", 14, "bold"))
        self.recommendation_box.tag_configure("italic", font=("Arial", 14, "italic"))
        self.recommendation_box.tag_configure("underline", underline=True)
        
        self.recommend_btn = ctk.CTkButton(self.home_tab, text="Get Recommendations", command=self.get_ai_recommendations, fg_color="#FFD369", text_color="#222831", font=("Arial", 16, "bold"), height=40, width=220, corner_radius=10)
        self.recommend_btn.pack(pady=(0, 10))
        clock_frame = ctk.CTkFrame(self.home_tab, fg_color="transparent")
        clock_frame.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.clock_time_label = ctk.CTkLabel(clock_frame, text="", font=("Arial", 32, "bold"), text_color="#FFD369")
        self.clock_time_label.pack(pady=(5, 0), padx=20)
        self.clock_date_label = ctk.CTkLabel(clock_frame, text="", font=("Arial", 12), text_color="#EEEEEE")
        self.clock_date_label.pack(pady=(0, 5), padx=20)
        self.update_clock()

    def setup_stats_tab(self):
        self.stats_frame = ctk.CTkFrame(self.stats_tab, fg_color="transparent")
        self.stats_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # --- New method for Leaderboard Tab Setup ---
    def setup_leaderboard_tab(self):
        # This tab will be populated dynamically by show_leaderboard
        pass # Initial setup is minimal, content is generated on tab switch

    def check_tab_change(self):
        if self.is_closing: return
        try:
            current_tab = self.tabview.get()
            if current_tab != self.last_selected_tab:
                self.last_selected_tab = current_tab
                if current_tab == "  Stats  ":
                    self.show_stats()
                elif current_tab == "Leaderboard": # Call show_leaderboard when tab is selected
                    self.show_leaderboard()
        except Exception as e:
            print(f"Error in check_tab_change: {e}")
        self.after(250, self.check_tab_change)

    def update_clock(self):
        if self.is_closing: return
        ist_time = datetime.now()
        self.clock_time_label.configure(text=ist_time.strftime("%H:%M:%S"))
        self.clock_date_label.configure(text=ist_time.strftime("%A, %B %d"))
        self.after(1000, self.update_clock)

    def add_device(self):
        name = self.name_entry.get().strip()
        try:
            power = float(self.power_entry.get())
        except (ValueError, TypeError):
            messagebox.showerror("Invalid Input", "Please enter a valid number for power.")
            return
        if name and power > 0:
            if any(d.name == name for d in self.devices):
                messagebox.showwarning("Duplicate Device", f"A device named '{name}' already exists.")
                return
            device = Device(name, power)
            self.devices.append(device)
            self.add_device_widget(device)
            self.name_entry.delete(0, tk.END)
            self.power_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Invalid Input", "Device name cannot be empty and power must be greater than zero.")

    def add_device_widget(self, device):
        frame = ctk.CTkFrame(self.devices_frame, fg_color="#222831", corner_radius=8)
        frame.pack(fill="x", pady=4, padx=4)
        name_label = ctk.CTkLabel(frame, text=f"{device.name} ({device.power}W)", font=("Arial", 14), text_color="#FFD369")
        name_label.pack(side="left", padx=10, pady=5)
        usage_label = ctk.CTkLabel(frame, text=f"Usage: {device.get_total_units():.3f} units", font=("Arial", 14), text_color="#FFFFFF")
        usage_label.pack(side="left", padx=10, pady=5)
        toggle_btn = ctk.CTkButton(frame, text="Turn ON", width=80, command=lambda d=device, b=frame: self.toggle_device(d, b))
        toggle_btn.pack(side="right", padx=10, pady=5)
        remove_btn = ctk.CTkButton(frame, text="Remove", width=80, fg_color="#E84545", hover_color="#B83B3B", command=lambda d=device, f=frame: self.remove_device(d, f))
        remove_btn.pack(side="right", padx=5, pady=5)
        self.device_widgets.append({"device": device, "usage_label": usage_label, "frame": frame, "toggle_btn": toggle_btn})
        if device.is_on:
            toggle_btn.configure(text="Turn OFF", fg_color="#E84545", hover_color="#B83B3B")

    def remove_device(self, device_to_remove, frame):
        if device_to_remove.is_on:
            device_to_remove.toggle() 
            log_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {device_to_remove.name} turned OFF (Removed)\n"
            try:
                with open(self.data_file, "a") as f:
                    f.write(log_message)
            except IOError as e:
                print(f"Error logging device removal: {e}")
        device_to_remove.saved_usage_units += device_to_remove.get_session_units()
        device_to_remove.session_usage_seconds = 0
        self.devices.remove(device_to_remove)
        self.device_widgets = [dw for dw in self.device_widgets if dw["device"] != device_to_remove]
        frame.destroy()
        self.update_all_usages()
        self.save_state()

    def toggle_device(self, device, frame):
        device.toggle()
        toggle_button = frame.winfo_children()[2]
        if device.is_on:
            toggle_button.configure(text="Turn OFF", fg_color="#E84545", hover_color="#B83B3B")
        else:
            toggle_button.configure(text="Turn ON", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"])
        now = datetime.now()
        log_message = f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {device.name} turned {'ON' if device.is_on else 'OFF'}\n"
        try:
            with open(self.data_file, "a") as f:
                f.write(log_message)
        except IOError as e:
            print(f"Error writing to log file: {e}")

    def update_all_usages(self):
        if self.is_closing: return
        grand_total_usage = 0
        for dw in self.device_widgets:
            device = dw["device"]
            usage_label = dw["usage_label"]
            device.update_session_usage()
            device_total = device.get_total_units()
            usage_label.configure(text=f"Usage: {device_total:.3f} units")
            grand_total_usage += device_total
        self.total_usage_label.configure(text=f"Total Usage: {grand_total_usage:.3f} units")
        self.after(1000, self.update_all_usages)

    def _consolidate_session_usage(self):
        for dw in self.device_widgets:
            device = dw["device"]
            if device.is_on and device.last_on_time:
                device.session_usage_seconds += (datetime.now() - device.last_on_time).total_seconds()
                device.last_on_time = datetime.now() 
            device.saved_usage_units += device.get_session_units()
            device.session_usage_seconds = 0

    def save_usage(self):
        self._consolidate_session_usage()
        self.save_state()
        messagebox.showinfo("Saved", "Current device usage has been saved successfully.")
        
    def load_state(self):
        if not os.path.exists(self.data_file): 
            if not self.username.startswith("Guest"):
                if messagebox.askyesno("AI Setup", "No data file found. Would you like to set up AI recommendations now? (Requires Google API Key)"):
                    self.prompt_for_api_key()
            return
            
        with open(self.data_file, "r") as f: lines = f.readlines()
        in_devices_section = False
        for line in lines:
            stripped = line.strip()
            if not stripped: continue
            if stripped == "## DEVICES ##": in_devices_section = True; continue
            if stripped == "## LOGS ##": in_devices_section = False; break
            if in_devices_section:
                try:
                    info_part, usage_part = stripped.split(" | ")
                    name_part, power_part = info_part.split(" (")
                    name = name_part.strip()
                    power = float(power_part.split("W)")[0])
                    saved_usage = float(usage_part)
                    device = Device(name, power)
                    device.saved_usage_units = saved_usage
                    self.devices.append(device)
                    self.add_device_widget(device)
                except Exception as e:
                    print(f"Failed to load device line: '{stripped}' - Error: {e}")
        
        if os.getenv("GOOGLE_API_KEY") is None:
            if messagebox.askyesno("AI Setup", "Google API Key is not set. Would you like to add it now for AI recommendations?"):
                self.prompt_for_api_key()

    def save_state(self):
        logs = []
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                in_logs_section = False
                for line in f:
                    if line.strip() == "## LOGS ##": in_logs_section = True; continue
                    if in_logs_section: logs.append(line)
        with open(self.data_file, "w") as f:
            f.write("## DEVICES ##\n")
            for device in self.devices:
                f.write(f"{device.name} ({device.power}W) | {device.saved_usage_units}\n")
            f.write("\n## LOGS ##\n")
            f.writelines(logs)
        print(f"State saved for {self.username}")

    def on_closing(self):
        self.is_closing = True
        self._consolidate_session_usage()
        self.save_state()
        self.destroy()

    def show_stats(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        plt.close('all')

        try:
            device_power_map = {d.name: d.power for d in self.devices}
            
            daily_usage_seconds_cumulative = {}
            
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    lines = f.readlines()
                
                logs_section_started = False
                processed_logs = []
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line == "## LOGS ##":
                        logs_section_started = True
                        continue
                    if not logs_section_started or not stripped_line:
                        continue
                    
                    try:
                        timestamp_str = stripped_line[1:20]
                        dt_obj = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        status_part_raw = stripped_line[22:]
                        device_name = status_part_raw.split(' turned ')[0].strip()
                        status = status_part_raw.split(' turned ')[1].split(' ')[0].strip()
                        
                        processed_logs.append({'timestamp': dt_obj, 'device': device_name, 'status': status})
                    except (ValueError, IndexError):
                        continue
                
                open_sessions = {}
                for log in sorted(processed_logs, key=lambda x: x['timestamp']):
                    device_name = log['device']
                    if device_name not in device_power_map: continue

                    if log['status'] == 'ON':
                        open_sessions[device_name] = log['timestamp']
                    elif log['status'] == 'OFF' and device_name in open_sessions:
                        start_time = open_sessions.pop(device_name)
                        end_time = log['timestamp']
                        
                        current_date_iter = start_time.date()
                        while current_date_iter <= end_time.date():
                            day_start = datetime.combine(current_date_iter, time.min)
                            day_end = datetime.combine(current_date_iter, time.max)
                            
                            session_start_on_day = max(start_time, day_start)
                            session_end_on_day = min(end_time, day_end)
                            
                            duration = (session_end_on_day - session_start_on_day).total_seconds()
                            if duration > 0:
                                key = (current_date_iter, device_name)
                                daily_usage_seconds_cumulative[key] = daily_usage_seconds_cumulative.get(key, 0) + duration
                            current_date_iter += timedelta(days=1)
            
            now = datetime.now()
            today_date_only = now.date()
            for device in self.devices:
                if device.is_on and device.last_on_time:
                    start_time = device.last_on_time
                    end_time = now
                    
                    current_date_iter = start_time.date()
                    while current_date_iter <= end_time.date():
                        day_start = datetime.combine(current_date_iter, time.min)
                        day_end = datetime.combine(current_date_iter, time.max)
                        
                        session_start_on_day = max(start_time, day_start)
                        session_end_on_day = min(end_time, day_end)
                        
                        duration = (session_end_on_day - session_start_on_day).total_seconds()
                        if duration > 0:
                            key = (current_date_iter, device.name)
                            daily_usage_seconds_cumulative[key] = daily_usage_seconds_cumulative.get(key, 0) + duration
                        current_date_iter += timedelta(days=1)
            
            if not daily_usage_seconds_cumulative and not self.devices:
                ctk.CTkLabel(self.stats_frame, text="No usage data to display. Add devices and use them.", font=("Arial", 16)).pack(pady=20)
                return

            today_date_obj = datetime.now().date()
            dates_for_columns = [today_date_obj - timedelta(days=i) for i in range(6, -1, -1)]
            
            all_device_names = sorted(list(set([d.name for d in self.devices] + [key[1] for key in daily_usage_seconds_cumulative.keys()])))

            df = pd.DataFrame(0.0, index=all_device_names, columns=dates_for_columns)

            for (date, device_name), seconds in daily_usage_seconds_cumulative.items():
                if date in df.columns and device_name in df.index:
                    power = device_power_map.get(device_name, 0)
                    kwh = (power * seconds) / (1000 * 3600)
                    df.loc[device_name, date] = kwh

            for device in self.devices:
                if device.name in df.index and today_date_obj in df.columns:
                    df.loc[device.name, today_date_obj] = device.get_total_units()

            column_headers = [d.strftime('%b %d') for d in df.columns[:-1]]
            column_headers.append("Today")
            df.columns = column_headers

            ctk.CTkLabel(self.stats_frame, text="Last 7 Days Usage (Units/kWh)", font=("Arial", 16, "bold"), text_color="#FFD369").pack(pady=(5,10))
            style = ttk.Style()
            style.theme_use("default")
            style.configure("Treeview", background="#222831", foreground="#EEEEEE", fieldbackground="#222831", borderwidth=0, rowheight=25)
            style.configure("Treeview.Heading", background="#393E46", foreground="#FFD369", font=('Arial', 11, 'bold'))
            style.map('Treeview', background=[('selected', '#FFD369')])
            
            tree_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            tree_frame.pack(fill="x", padx=10)
            
            tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
            tree = ttk.Treeview(tree_frame, columns=['Device'] + list(df.columns), show='headings', height=min(len(df.index), 10), xscrollcommand=tree_scroll_x.set)
            tree_scroll_x.config(command=tree.xview)
            tree_scroll_x.pack(side="bottom", fill="x")

            tree.heading('Device', text='Device'); tree.column('Device', anchor='w', width=120)
            for col in df.columns: 
                tree.heading(col, text=col)
                tree.column(col, anchor='center', width=100)
            
            for index, row in df.iterrows():
                values = [index] + [f"{val:.3f}" for val in row]
                tree.insert('', 'end', values=values)
            tree.pack(fill="both", expand=True)

            ctk.CTkLabel(self.stats_frame, text=f"Today's Consumption Distribution", font=("Arial", 16, "bold"), text_color="#FFD369").pack(pady=(20,10))
            
            data_for_pie = df[df.columns[-1]][df[df.columns[-1]] > 0]
            
            pie_frame = ctk.CTkFrame(self.stats_frame, fg_color="#393E46")
            pie_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            if not data_for_pie.empty:
                fig, ax = plt.subplots(figsize=(5, 4), facecolor="#393E46")
                ax.pie(data_for_pie, labels=data_for_pie.index, autopct='%1.1f%%', startangle=90, 
                       textprops={'color': "w", 'fontsize': 10}, pctdistance=0.85)
                ax.axis('equal')
                fig.patch.set_facecolor("#393E46")
                
                canvas = FigureCanvasTkAgg(fig, master=pie_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            else:
                ctk.CTkLabel(pie_frame, text=f"No usage recorded for Today.", font=("Arial", 14), text_color="#EEEEEE").pack(pady=20)

        except Exception as e:
            ctk.CTkLabel(self.stats_frame, text=f"An error occurred while generating stats:\n{e}", font=("Arial", 14), text_color="red").pack(pady=20)
            print(f"Stats Error: {e}")
            plt.close('all')

    def prompt_for_api_key(self):
        """Prompts the user to enter their Google API Key and sets it as an environment variable."""
        api_key = simpledialog.askstring("Google API Key", 
                                        "Please enter your Google API Key for AI recommendations:",
                                        parent=self)
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            messagebox.showinfo("API Key Set", "Google API Key has been set for this session.", parent=self)
        else:
            messagebox.showwarning("API Key Not Set", "AI recommendations will not be available without an API Key.", parent=self)

    def _apply_rich_text_formatting(self, textbox_widget, text_content):
        """Parses Markdown-like syntax and applies tags to the tk.Text widget."""
        textbox_widget.configure(state="normal")
        textbox_widget.delete("1.0", tk.END)

        # Regex patterns for bold, italics, underline. Order matters: longer patterns first.
        patterns = {
            r'\*\*(.*?)\*\*': 'bold',      # **bold**
            r'\*(.*?)\*': 'italic',       # *italic*
            r'__(.*?)__': 'underline',    # __underline__ (common markdown for underline)
            r'_(.*?)_': 'italic'          # _italic_ (common markdown for italic)
        }
        
        segments = [(text_content, None)] 
        
        for pattern_str, tag_name in patterns.items():
            new_segments = []
            for segment_text, current_tag in segments:
                if current_tag: 
                    new_segments.append((segment_text, current_tag))
                    continue
                
                last_end = 0
                for match in re.finditer(pattern_str, segment_text):
                    if match.start() > last_end:
                        new_segments.append((segment_text[last_end:match.start()], None))
                    new_segments.append((match.group(1), tag_name))
                    last_end = match.end()
                
                if last_end < len(segment_text):
                    new_segments.append((segment_text[last_end:], None))
            segments = new_segments
            
        for segment_text, tag_name in segments:
            textbox_widget.insert(tk.END, segment_text, tag_name)
            
        textbox_widget.configure(state="disabled")

    def get_ai_recommendations(self):
        """Fetches energy-saving recommendations from Google Gemini AI."""
        self._apply_rich_text_formatting(self.recommendation_box, "Getting recommendations from AI... Please wait.")
        self.update_idletasks()

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self._apply_rich_text_formatting(self.recommendation_box, "AI recommendations unavailable: **API Key not set**. Please set your Google API Key via the prompt on app launch or restart the app to set it.")
            return

        try:
            with open(self.data_file, "r") as f: data = f.read()
            if not data.strip(): 
                raise FileNotFoundError
        except FileNotFoundError:
            self._apply_rich_text_formatting(self.recommendation_box, "No usage data found. Please use the app (turn devices ON/OFF, save usage) to generate logs for AI analysis.")
            return
        
        prompt = (
            "Analyze the following device power usage log and current device states.\n"
            "Provide 3-5 concise, actionable, bulleted recommendations to save energy. "
            "Use **bold**, *italics*, or __underline__ formatting to highlight key terms or actions.\n\n"
            "Log Data:\n" + data +
            "\n\nCurrent Device States:\n" + 
            "\n".join([f"- {d.name}: {'ON' if d.is_on else 'OFF'}, Power: {d.power}W, Total Usage: {d.get_total_units():.3f} units" for d in self.devices])
        )

        try:
            genai.configure(api_key=api_key) 
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            recommendations = response.text.strip()
        except Exception as e:
            recommendations = f"**Error fetching AI recommendations:**\n_{e}_\nEnsure your API Key is correct and you have internet access."
        
        self._apply_rich_text_formatting(self.recommendation_box, recommendations)

    # --- New method for Leaderboard ---
    def show_leaderboard(self):
        # Clear existing widgets in stats_frame to refresh
        for widget in self.leaderboard_tab.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.leaderboard_tab, text="Energy Efficiency Leaderboard", font=("Arial", 20, "bold"), text_color="#FFD369").pack(pady=(10,20))

        leaderboard_data = []
        
        # Calculate current user's total usage (saved + session) for their own ranking
        current_user_total_usage = 0
        for device in self.devices:
            current_user_total_usage += device.get_total_units()
        
        # Scan for all user data files in the current directory
        for filename in os.listdir('.'): 
            if filename.endswith("_data.txt"):
                try:
                    username_from_file = filename.replace("_data.txt", "")
                    total_usage_from_file = 0.0
                    
                    with open(filename, "r") as f:
                        lines = f.readlines()
                    
                    in_devices_section = False
                    for line in lines:
                        stripped = line.strip()
                        if not stripped: continue
                        if stripped == "## DEVICES ##":
                            in_devices_section = True
                            continue
                        if stripped == "## LOGS ##": # Stop at logs section
                            in_devices_section = False
                            break # No need to read logs for total usage from devices section
                        
                        if in_devices_section:
                            try:
                                # Example line: "DeviceName (100W) | 12.345"
                                # We only need the usage part
                                info_part, usage_part = stripped.split(" | ")
                                saved_usage = float(usage_part)
                                total_usage_from_file += saved_usage
                            except Exception as e:
                                print(f"Error parsing device line in {filename}: '{stripped}' - {e}")
                                continue # Skip this line, try next one
                    
                    # For the current user, use their real-time total usage (saved + session)
                    if username_from_file == self.username:
                        final_user_usage = current_user_total_usage
                    else:
                        # For other users, use the total_usage_from_file which reflects their last saved state
                        final_user_usage = total_usage_from_file

                    leaderboard_data.append({'username': username_from_file, 'total_usage': final_user_usage})

                except Exception as e:
                    print(f"Could not read data from file {filename}: {e}")
                    continue

        if not leaderboard_data:
            ctk.CTkLabel(self.leaderboard_tab, text="No users found for leaderboard. Create more user data files.", font=("Arial", 16)).pack(pady=20)
            return

        # Sort by total_usage in ascending order (least usage at top)
        leaderboard_data.sort(key=lambda x: x['total_usage'])

        # Setup Treeview for leaderboard display
        style = ttk.Style()
        style.theme_use("default") # Important to reset theme for custom styling
        style.configure("Treeview", background="#222831", foreground="#EEEEEE", fieldbackground="#222831", borderwidth=0, rowheight=35) # Increased rowheight for medal/bigger font
        style.configure("Treeview.Heading", background="#393E46", foreground="#FFD369", font=('Arial', 12, 'bold'))
        style.map('Treeview', background=[('selected', '#FFD369')]) # Selection color
        
        tree_frame = ctk.CTkFrame(self.leaderboard_tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10)

        columns = ['Rank', 'User', 'Total_Usage']
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=min(len(leaderboard_data), 10)) # Limit height to 10 rows or actual data size
        
        # Configure column headings and widths
        tree.heading('Rank', text='Rank'); tree.column('Rank', anchor='center', width=60)
        tree.heading('User', text='User'); tree.column('User', anchor='w', width=200) # Left-align User names
        tree.heading('Total_Usage', text='Total Usage (Units)'); tree.column('Total_Usage', anchor='center', width=150)
        
        # Define tags for special formatting
        # You can adjust the font size for 'top_rank_bold' here (e.g., 18 or 20)
        tree.tag_configure('top_rank_bold', font=('Arial', 18, 'bold'), foreground='#FFD369') # Bigger font and highlight color
        tree.tag_configure('current_user_highlight', background='#5cb85c', foreground='#FFFFFF') # Highlight current user with green

        # Populate Treeview
        for i, entry in enumerate(leaderboard_data):
            rank = i + 1
            user_name = entry['username']
            total_usage = f"{entry['total_usage']:.3f}"
            
            tags = [] # List to hold tags for current row
            
            # Apply gold medal and biggest font for the rank 1 user
            if rank == 1:
                display_user_name = f"🥇 {user_name}" # Unicode gold medal icon
                tags.append('top_rank_bold')
            else:
                display_user_name = user_name
            
            # Highlight the current user's row
            if user_name == self.username:
                tags.append('current_user_highlight') 
            
            tree.insert('', 'end', values=(rank, display_user_name, total_usage), tags=tuple(tags)) # Insert with combined tags

        tree.pack(fill="both", expand=True)

        ctk.CTkLabel(self.leaderboard_tab, text="*Total Usage includes all saved and current session units for all users.", font=("Arial", 10), text_color="#EEEEEE").pack(pady=(5,0))
        ctk.CTkLabel(self.leaderboard_tab, text="**Leaderboard updates based on last saved state of each user.", font=("Arial", 10), text_color="#EEEEEE").pack(pady=(0,5))


# --- Main Application Execution ---
if __name__ == "__main__":
    root_for_dialog = tk.Tk()
    root_for_dialog.withdraw() # Hide the root window

    username = simpledialog.askstring("Welcome to WattWise", "Please enter your name:", parent=root_for_dialog)
    
    root_for_dialog.destroy() # Destroy the temporary root window

    if username:
        app = App(username)
        app.mainloop()
    else:
        # If user cancels username prompt, exit gracefully
        messagebox.showinfo("Goodbye", "Application will now exit.", parent=None)
        sys.exit()