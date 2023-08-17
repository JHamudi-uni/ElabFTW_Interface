import elabapy
import json
from requests.exceptions import HTTPError
from dotenv import load_dotenv #für die .env datei
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import datetime
import customtkinter
import customtkinter as ctk
from tkinter import Toplevel, Label
from nptdms import TdmsFile as td
import os
import hyperspy.api as hs
import pprint
import tkinter as tk




customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
load_dotenv()
token = os.getenv("ELAB_TOKEN")

# creates an instance of the Manager class from the elabapy library, initializing it with the endpoint and API token
#https://134.102.38.139/api/v1/
#https://api.elabftw.net/api/v1/
manager = elabapy.Manager(endpoint="https://demo.elabftw.net/api/v1/", token=token)



hochgeladene_tdms_dateien = []

date_sur = None
signal_unfolded = None
original_axes_manager = None
sur_dates = {}


# class App erbt von customkinter.CTk
# self ist eine instanz vom Objekt
# __init__ ist der Konstruktor
class GUI(customtkinter.CTk):
    def __init__(self):
        # Ruft den Konstruktor der übergeordneten Klasse auf, um das Hauptfenster zu initialisieren.
        super().__init__()
        self.tdmsMetadata = {}
        self.metadata_window = None
        self.metadata_window_open = False
        self.uploaded_file_names = set()
        #self.uploaded_file_names = []

        # Variable zur Verfolgung des aktuellen geöffneten Fensters
        self.current_window = None
        self.open_windows = []  # List to store all open windows

        global filename

        #hochgeladene_tdms_dateien = []


        # configure window
        self.title("ElabAPI")
        self.geometry(f"{760}x{420}")



        # configure grid layout (4x4)
        # weight=1 gibt an, dass die Spalte 1 elastisch ist und sich automatisch an
        # die Breite des Fensters anpassen soll.
        self.grid_columnconfigure(1, weight=1)
        # Konfiguration für die Spalten 2 und 3 festgelegt.
        # Der Parameter weight=0 gibt an, dass diese Spalten nicht elastisch sind und keine
        # zusätzliche Breite erhalten, wenn das Fenster vergrößert wird.
        self.grid_columnconfigure((2, 3), weight=0)
        # Hier wird die Konfiguration für die Zeilen 0, 1 und 2 festgelegt.
        # Der Parameter weight=1 gibt an, dass diese Zeilen elastisch sind und sich automatisch
        # an die Höhe des Fensters anpassen sollen
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        # rowspan erlaubt es die tabellenzelle nach unten auszudehnen
        self.sidebar_frame.grid(row=0, column=0, rowspan=7, sticky="nsew") #north, south, east, west
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Innerhalb der sidebar spricht man die widgets mit self.sidebar_frame an
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="ElabFTW", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Create", command=self.sidebar_create_event)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Edit", command=self.sidebar_edit_event)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Menu",
                                                        command=self.sidebar_menu_event)
        self.sidebar_button_3.grid(row=5, column=0, padx=20, pady=(10,20))

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        #self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        #self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))

        # set default values
        self.appearance_mode_optionemenu.set("Dark")




    try:

        # uses the json.dumps function to convert the exp variable (which contains information about an experiment)
        # into a string representation in JSON format. The indent parameter is set to 4 to make the JSON output more
        # readable, and the sort_keys parameter is set to True to sort the keys in the JSON output.
        # print(json.dumps(exp, indent=4, sort_keys=True))

        # Create a database item
        # 1 stands for the ID of the category of the new item
        # If you manually display the bar next to "create" in the database, you will see all categories
        #response = manager.create_item(1)
        #print(f"Created database item with id {response['id']}.")


        # link database item 3449 to experiment 13296
        #params = {"link": 3449, "targetEntity": "items"}
        #print(manager.add_link_to_experiment(13296, params))

        #root.mainloop()



        def change_appearance_mode_event(self, new_appearance_mode: str):
            customtkinter.set_appearance_mode(new_appearance_mode)


        def sidebar_create_event(self):

            self.uploaded_file_names.clear()
            hochgeladene_tdms_dateien.clear()
            print("sidebar_button Create click")

            #self.label = customtkinter.CTkLabel(self, text="Create")
            #self.label.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

            """
            GUI OBJECTS
            """
            ###########################################################################################

            self.headline_label = customtkinter.CTkLabel(self, text="Create new Experiment",
                                                    font=customtkinter.CTkFont(size=16, weight="bold"))
            self.headline_label.grid(row=0, column=1, padx=10, pady=(20, 200), sticky="WesN")
            #self.titleLabel = customtkinter.CTkLabel(self, text="Title:")
            #self.titleLabel.grid(row=0, column=1, padx=(150, 0), pady=(50, 10), sticky="W")
            self.titleText_field = customtkinter.CTkEntry(self, placeholder_text="Title")
            self.titleText_field.grid(row=0, column=1, padx=(0, 200), pady=(0, 60))

            # sticky=w nach links positionieren
            #self.tagLabel = customtkinter.CTkLabel(self, text="Tags:")
            #self.tagLabel.grid(row=1, column=1, padx=(150, 0), pady=(0, 10), sticky="W")
            self.tagText_field = customtkinter.CTkEntry(self, placeholder_text="Tags")
            self.tagText_field.grid(row=0, column=1, padx=(0, 200), pady=(90, 50))

            self.allgemeinText_field = customtkinter.CTkEntry(self, placeholder_text="Allgemein")
            self.allgemeinText_field.grid(row=0, column=1, padx=(200, 0), pady=(90, 50))

            self.rechteText_field = customtkinter.CTkEntry(self, placeholder_text="Rechte")
            self.rechteText_field.grid(row=0, column=1, padx=(200, 0), pady=(0, 60))

            self.förderkennzeichen_field = customtkinter.CTkEntry(self, placeholder_text="Förderkennzeichen")
            self.förderkennzeichen_field.grid(row=0, column=1, padx=(0, 200), pady=(200, 60))

            self.datum_field = customtkinter.CTkEntry(self, placeholder_text="Datum")
            self.datum_field.grid(row=0, column=1, padx=(200, 0), pady=(200, 60))





            #self.folderLabel = customtkinter.CTkLabel(self, text="Files:")
            #self.folderLabel.grid(row=3, column=1, padx=(150, 0), pady=(0, 10), sticky="W")
            #self.folderText_field = customtkinter.CTkEntry(self, placeholder_text="Files")
            #self.folderText_field.grid(row=2, column=1, padx=(160, 160), pady=(10, 20))

            #self.grid_columnconfigure(1, weight=1)
            #self.grid_propagate(0)

            ###########################################################################################
            def get_current_date():
                return datetime.date.today().strftime('%Y-%m-%d')





            def display_metadata(filepath):
                #if not self.metadata_window_open and file_path.lower().endswith(".tdms"):
                self.metadata_window = Toplevel(self)
                self.metadata_window.title("Metadata")
                center_window(self.metadata_window, 480, 500)
                self.metadata_window.grab_set()


                if filepath.lower().endswith(".tdms"):
                    metadata_label = ctk.CTkLabel(self.metadata_window, text="Metadaten der TDMS-Datei:", font=("Arial", 14, "bold"))
                    metadata_label.pack()

                    tdms_metadata = td.read_metadata(filepath).properties
                    for key, value in tdms_metadata.items():
                        metadata_entry = Label(self.metadata_window, text=f"{key}: {value}")
                        metadata_entry.pack()
                elif filepath.lower().endswith(".sur"):
                    global date_sur
                    global signal_unfolded
                    global original_axes_manager

                    s = hs.load(filepath)
                    metadata = s.metadata.as_dictionary()

                    original_axes_manager = metadata['_HyperSpy']['Folding']['original_axes_manager']
                    original_shape = metadata['_HyperSpy']['Folding']['original_shape']
                    signal_unfolded = metadata['_HyperSpy']['Folding']['signal_unfolded']
                    unfolded = metadata['_HyperSpy']['Folding']['unfolded']

                    signal_type = metadata['Signal']['signal_type']

                    hyperspy_version = metadata['General']['FileIO']['0']['hyperspy_version']
                    io_plugin = metadata['General']['FileIO']['0']['io_plugin']
                    operation = metadata['General']['FileIO']['0']['operation']
                    authors = metadata['General']['authors']
                    original_filename = metadata['General']['original_filename']
                    time = metadata['General']['time']
                    title_meta = metadata['General']['title']
                    date_sur = metadata['General']['date']


                    def save_changes():

                        try:
                            global date_sur
                            global signal_unfolded
                            #updated_signal_unfolded = entry_signal_unfolded.get()
                            #updated_original_axes_manager = entry_original_axes_manager.get()
                            #updated_original_shape = entry_original_shape.get()
                            sur_dates[filepath] = entry_date.get()
                            #date_sur = entry_date.get()

                            print("entry get:" + entry_date.get())
                            print("After:" + date_sur)

                            # Update the metadata dictionary with the new values
                            #metadata['_HyperSpy']['Folding']['signal_unfolded'] = updated_signal_unfolded
                            #metadata['_HyperSpy']['Folding']['original_axes_manager'] = updated_original_axes_manager
                            #metadata['_HyperSpy']['Folding']['original_shape'] = updated_original_shape
                            metadata['General']['date'] = date_sur
                            print("Metadata: " + metadata['General']['date'])

                            # Update the textboxes with the new values
                            #entry_signal_unfolded.delete(0, tk.END)
                            #entry_signal_unfolded.insert(0, "None" if signal_unfolded is None else signal_unfolded)

                            #entry_original_axes_manager.delete(0, tk.END)
                            #entry_original_axes_manager.insert(0,
                            #                                   "None" if original_axes_manager is None else original_axes_manager)

                            #entry_original_shape.delete(0, tk.END)
                            #entry_original_shape.insert(0, "None" if original_shape is None else original_shape)

                            entry_date.delete(0, tk.END)
                            entry_date.insert(0, "None" if sur_dates.get(filepath) is None else sur_dates[filepath])

                            print("Changes saved successfully")
                        except Exception as e:
                            print("An error occurred while saving changes:", str(e))



                    def update_textboxes():

                        #Hyperspy
                        original_axes_manager = metadata['_HyperSpy']['Folding']['original_axes_manager']
                        original_shape = metadata['_HyperSpy']['Folding']['original_shape']
                        signal_unfolded = metadata['_HyperSpy']['Folding']['signal_unfolded']
                        unfolded = metadata['_HyperSpy']['Folding']['unfolded']

                        # General
                        hyperspy_version = metadata['General']['FileIO']['0']['hyperspy_version']
                        io_plugin = metadata['General']['FileIO']['0']['io_plugin']
                        operation = metadata['General']['FileIO']['0']['operation']
                        authors = metadata['General']['authors']
                        date = metadata['General']['date']
                        print(date)
                        original_filename = metadata['General']['original_filename']
                        time = metadata['General']['time']
                        title_meta = metadata['General']['title']

                        # Signal
                        signal_type = metadata['Signal']['signal_type']

                        save_changes()
                        try:
                            #entry_signal_unfolded.delete(0, tk.END)
                            #entry_signal_unfolded.insert(0, "None" if signal_unfolded is None else signal_unfolded)

                            #entry_original_axes_manager.delete(0, tk.END)
                            #entry_original_axes_manager.insert(0, "None" if original_axes_manager is None else original_axes_manager)

                            #entry_original_shape.delete(0, tk.END)
                            #entry_original_shape.insert(0, "None" if original_shape is None else original_shape)

                            entry_date.delete(0, tk.END)
                            entry_date.insert(0, "None" if date is None else date)

                        except Exception as e:
                            print("An error occurred:", str(e))




                    metadata_label = tk.Label(self.metadata_window, text="Metadaten der Surfaces-Datei:",
                                                  font=("Arial", 14, "bold"))
                    metadata_label.grid(row=0, column=1)




                    hyperspy_label = tk.Label(self.metadata_window, text="HyperSpy:", font=("Arial", 14, "bold"), anchor="w")
                    hyperspy_label.grid(row=1, column=0, sticky="w")

                    original_axes_manager_label = tk.Label(self.metadata_window, text="original_axes_manager:", font=("Arial", 14))
                    original_axes_manager_label.grid(row=2, column=0, sticky="w")
                    #original_axes_manager_label.config(text=f"original_axes_manager:")
                    original_axes_manager_value = tk.Label(self.metadata_window, text="None" if original_axes_manager is None else str(original_axes_manager), font=("Arial", 14))
                    original_axes_manager_value.grid(row=2, column=1, padx=5, pady=2)

                    original_shape_label = tk.Label(self.metadata_window, text="original_shape:", font=("Arial", 14))
                    original_shape_label.grid(row=3, column=0, sticky="w")
                    #original_shape_label.config(text=f"original_shape:")
                    original_shape_value = tk.Label(self.metadata_window, text="None" if original_shape is None else str(original_shape), font=("Arial", 14))
                    original_shape_value.grid(row=3, column=1, padx=5, pady=2)
                    #entry_original_shape = tk.Entry(self.metadata_window)
                    #entry_original_shape.grid(row=3, column=1, padx=5, pady=5)

                    signal_unfolded_label = tk.Label(self.metadata_window, text="signal_unfolded:", font=("Arial", 14))
                    signal_unfolded_label.grid(row=4, column=0, sticky="w")
                    signal_unfolded_value = tk.Label(self.metadata_window, text="None" if signal_unfolded is None else str(signal_unfolded), font=("Arial", 14))
                    signal_unfolded_value.grid(row=4, column=1, padx=5, pady=2)

                    unfolded_label = tk.Label(self.metadata_window, text="unfolded:", font=("Arial", 14))
                    unfolded_label.grid(row=5, column=0, sticky="w")
                    unfolded_value = tk.Label(self.metadata_window,
                                                     text="None" if unfolded is None else str(unfolded),
                                                     font=("Arial", 14))
                    unfolded_value.grid(row=5, column=1, padx=5, pady=2)

                    signal_label = tk.Label(self.metadata_window, text="Signal:", font=("Arial", 14, "bold"),
                                              anchor="w")
                    signal_label.grid(row=6, column=0, sticky="w")

                    signal_type_label = tk.Label(self.metadata_window, text="signal_type:", font=("Arial", 14))
                    signal_type_label.grid(row=7, column=0, sticky="w")
                    signal_type_value = tk.Label(self.metadata_window,
                                                     text="None" if signal_type is None else str(signal_type),
                                                     font=("Arial", 14))
                    signal_type_value.grid(row=7, column=1, padx=5, pady=2)

                    general_label = tk.Label(self.metadata_window, text="General:", font=("Arial", 14, "bold"),
                                            anchor="w")
                    general_label.grid(row=8, column=0, sticky="w")

                    hyperspy_version_label = tk.Label(self.metadata_window, text="hyperspy_version:", font=("Arial", 14))
                    hyperspy_version_label.grid(row=9, column=0, sticky="w")
                    hyperspy_version_value = tk.Label(self.metadata_window,
                                                     text="None" if hyperspy_version is None else str(hyperspy_version),
                                                     font=("Arial", 14))
                    hyperspy_version_value.grid(row=9, column=1, padx=5, pady=2)

                    io_plugin_label = tk.Label(self.metadata_window, text="io_plugin:", font=("Arial", 14))
                    io_plugin_label.grid(row=10, column=0, sticky="w")
                    io_plugin_value = tk.Label(self.metadata_window,
                                                     text="None" if io_plugin is None else str(io_plugin),
                                                     font=("Arial", 14))
                    io_plugin_value.grid(row=10, column=1, padx=5, pady=2)

                    operation_label = tk.Label(self.metadata_window, text="operation:", font=("Arial", 14))
                    operation_label.grid(row=11, column=0, sticky="w")
                    operation_value = tk.Label(self.metadata_window,
                                                     text="None" if operation is None else str(operation),
                                                     font=("Arial", 14))
                    operation_value.grid(row=11, column=1, padx=5, pady=2)

                    authors_label = tk.Label(self.metadata_window, text="authors:", font=("Arial", 14))
                    authors_label.grid(row=12, column=0, sticky="w")
                    authors_value = tk.Label(self.metadata_window,
                                                     text="None" if authors is None else str(authors),
                                                     font=("Arial", 14))
                    authors_value.grid(row=12, column=1, padx=5, pady=2)

                    original_filename_label = tk.Label(self.metadata_window, text="original_filename:", font=("Arial", 14))
                    original_filename_label.grid(row=13, column=0, sticky="w")
                    original_filename_value = tk.Label(self.metadata_window,
                                             text="None" if original_filename is None else str(original_filename),
                                             font=("Arial", 14))
                    original_filename_value.grid(row=13, column=1, padx=5, pady=2)

                    time_label = tk.Label(self.metadata_window, text="time:", font=("Arial", 14))
                    time_label.grid(row=14, column=0, sticky="w")
                    time_value = tk.Label(self.metadata_window,
                                             text="None" if time is None else str(time),
                                             font=("Arial", 14))
                    time_value.grid(row=14, column=1, padx=5, pady=2)

                    title_label = tk.Label(self.metadata_window, text="title:", font=("Arial", 14))
                    title_label.grid(row=15, column=0, sticky="w")
                    title_value = tk.Label(self.metadata_window,
                                             text="None" if title_meta is None else str(title_meta),
                                             font=("Arial", 14))
                    title_value.grid(row=15, column=1, padx=5, pady=2)







                    date_label = tk.Label(self.metadata_window, text="date:", font=("Arial", 14))
                    date_label.grid(row=16, column=0, sticky="w")
                    entry_date = tk.Entry(self.metadata_window)
                    entry_date.grid(row=16, column=1, padx=5, pady=5)










                    button_save = ctk.CTkButton(self.metadata_window, text="Save Changes", command=save_changes)
                    button_save.grid(row=17, column=1, pady=(20, 20), sticky = "se")
                    update_textboxes()
                    #save_changes()

                self.metadata_window.lift()
                    #self.metadata_window.protocol("WM_DELETE_WINDOW", close_metadata_window)
                    #self.metadata_window_open = True


            def close_metadata_window():
                self.metadata_window.destroy()
                self.metadata_window_open = False

            #CTkSegmentedButton
            def prepare_for_upload():
                self.current_window
                if self.current_window:
                    self.current_window.destroy()  # Schließe das aktuelle Fenster, falls geöffnet


                # use the filedialog module to open a file dialog box and allow the user to select a file to upload
                global hochgeladene_tdms_dateien
                file_paths = filedialog.askopenfilenames()
                # tdms_Label = customtkinter.CTkLabel(self)
                # tdms_Label.grid(row=3, column=1, padx=10, pady=(0, 10))

                for filepath in file_paths:

                    if filepath.lower().endswith(".tdms"):
                        if filepath in hochgeladene_tdms_dateien:
                            print(f"Die Datei '{filepath}' wurde bereits hochgeladen.")
                        else:
                            # upload_tdms_file()
                            self.tdmsMetadata = td.read_metadata(filepath).properties
                            print(file_paths)
                            print("Metadaten der TDMS-Datei:")
                            print("-----------------------------")
                            for key, value in self.tdmsMetadata.items():
                                print(f"{key}: {value}")

                            # tdms_Label.configure(text="Metadata uploaded successfully.")
                            # wird in createJsonFile verwendet
                            hochgeladene_tdms_dateien.append(filepath)  # Füge den Pfad zur Liste hinzu
                            self.uploaded_file_names.add(filepath)
                        #self.uploaded_file_names.append((os.path.basename(filepath), os.path.splitext(filepath)[1]))
                        # Hier können Sie spezifische Aktionen für .tdms-Dateien durchführen, falls gewünscht
                    elif filepath.lower().endswith(".sur"):
                        if filepath in hochgeladene_tdms_dateien:
                            print(f"Die Datei '{filepath}' wurde bereits hochgeladen.")
                        else:
                            s = hs.load(filepath)
                            surfaceMetadata = s.metadata.as_dictionary()
                            original_filename = surfaceMetadata['General']['original_filename']

                            print("Metadaten der Surface-Datei")
                            print("-------------------------------------------------------")
                            for key, value in surfaceMetadata.items():
                                print(f"{key}:")
                                pprint.pprint(value, indent=4)
                            hochgeladene_tdms_dateien.append(filepath)  # Füge den Pfad zur Liste hinzu
                            self.uploaded_file_names.add(filepath)

                    else:
                        #self.uploaded_file_names.append((os.path.basename(filepath), os.path.splitext(filepath)[1]))

                        self.uploaded_file_names.add(filepath)
                        print(self.uploaded_file_names)

                        # Hier können Sie den Code einfügen, um Dateien normal hochzuladen
                        # update the folderText_field Entry widget with the path(s) to the selected file(s)
                    # self.folderText_field.delete(0, END)
                    # self.folderText_field.insert(0, ";".join(file_paths))

            def center_window(window, width, height):
                screen_width = window.winfo_screenwidth()
                screen_height = window.winfo_screenheight()

                x = (screen_width - width) // 2
                y = (screen_height - height) // 4

                window.geometry(f"{width}x{height}+{x}+{y}")

            def display_selected_files():
                self.current_window
                if self.current_window:
                    self.current_window.destroy()  # Schließe das aktuelle Fenster, falls geöffnet
                value2_window = tk.Toplevel(self)
                self.open_windows.append(value2_window)
                value2_window.title("Selected Files")
                center_window(value2_window, 725, 400)


                #customtkinter.set_appearance_mode("Light", window=value2_window)

                self.current_window = value2_window  # Setze das aktuelle Fenster auf das neue Fenster
                value2_window.grab_set() # grab_set() erstellt ein "Modal"-Fenster, das den Fokus auf sich zieht und andere Fenster im Hintergrund blockiert

                canvas = Canvas(value2_window)
                canvas.pack(fill="both", expand=True)

                table_frame = Frame(canvas)
                canvas.create_window((0, 0), window=table_frame, anchor="nw")

                #scrollbar = Scrollbar(value2_window, orient="vertical", command=canvas.yview)
                #scrollbar.pack(side="right", fill="y")
                #canvas.configure(yscrollcommand=scrollbar.set)

                # Aufteilung der Dateien in .tdms und andere Dateitypen in drei separate listen 
                # Das erlaubt uns, die Dateien entsprechend ihrer Art zu gruppieren
                tdms_files = [file_path for file_path in self.uploaded_file_names if
                              file_path.lower().endswith(".tdms")]
                sur_files = [file_path for file_path in self.uploaded_file_names if file_path.lower().endswith(".sur")]
                other_files = [file_path for file_path in self.uploaded_file_names if
                               not file_path.lower().endswith((".tdms", ".sur"))]

                # Sortiere die Dateipfade in der gewünschten Reihenfolge
                # Je nachdem was wir zuerst sortieren, wird die reihenfolge festgelegt, wie die in der tabellenansicht angezeigt werden
                tdms_files.sort()
                sur_files.sort()
                other_files.sort()

                # Erstelle die Tabellenüberschrift
                headers = ["File Name", "File Type", "Metadaten", "Action", "Display"] # ["File Name", "File Type", "Metadaten", "Action"]
                for col, header in enumerate(headers):
                    label = ctk.CTkLabel(table_frame, text=header, font=("Arial", 14, "bold"))
                    label.grid(row=0, column=col, padx=5, pady=5)

                # Fülle die Tabelle mit den ausgewählten Dateien
                for row, file_path in enumerate(tdms_files + sur_files + other_files, start=1):
                    file_name = os.path.basename(file_path)
                    file_type = os.path.splitext(file_name)[1][1:].upper() if not file_path.lower().endswith(
                        ".tdms") else "TDMS"
                    has_metadata = "Metadaten" if file_path in hochgeladene_tdms_dateien or file_path.lower().endswith(".sur") else ""

                    file_name_label = ctk.CTkLabel(table_frame, text=file_name, font=customtkinter.CTkFont(size=12, weight="bold"))
                    file_name_label.grid(row=row, column=0, padx=5, pady=5)

                    file_type_label = Label(table_frame, text=file_type)
                    file_type_label.grid(row=row, column=1, padx=5, pady=5)

                    metadata_label = Label(table_frame, text=has_metadata)
                    metadata_label.grid(row=row, column=2, padx=5, pady=5)

                    remove_button = ctk.CTkButton(table_frame, text="Remove", width=12,
                                           command=lambda fp=file_path: remove_selected_file(fp))
                    remove_button.grid(row=row, column=3, padx=5, pady=5)

                    if file_path.lower().endswith(".tdms"):
                        display_metadata_button = ctk.CTkButton(table_frame, text="Display Metadata",
                                                         command=lambda fp=file_path: display_metadata(fp))
                        display_metadata_button.grid(row=row, column=4, padx=5, pady=5)
                    elif file_path.lower().endswith(".sur"):
                        display_metadata_button = ctk.CTkButton(table_frame, text="Display Metadata",
                                                                command=lambda fp=file_path: display_metadata(fp))
                        display_metadata_button.grid(row=row, column=4, padx=5, pady=5)

                table_frame.update_idletasks()

                canvas.config(scrollregion=canvas.bbox("all"))
                value2_window.lift()

            def remove_selected_file(file_path):

                self.uploaded_file_names.remove(file_path)
                if file_path.lower().endswith(".tdms"):
                    hochgeladene_tdms_dateien.remove(file_path)
                display_selected_files()


            def createJsonFile():



                title_tdms_file = self.tdmsMetadata.get("name", "N/A")
                date_tdms_file = self.tdmsMetadata.get("Date", "N/A")
                print(title_tdms_file)
                remark_tdms_file = self.tdmsMetadata.get("Remark", "N/A")
                formatted_remark = remark_tdms_file.replace("\r\n", " ")

                global date_sur
                global signal_unfolded
                global original_axes_manager


                datum_value = self.datum_field.get()

                if datum_value == "":
                    datum_value = get_current_date()

                #hochgeladene_tdms_dateien = ['/Users/muhamedjaber/PycharmProjects/APIv1/03_Kaltgas_316L-Al_07_vf_4000.tdms', '/Users/muhamedjaber/PycharmProjects/APIv1/03_Kaltgas_316L-Al_10_vf_4600.tdms']

                data = {
                    'Title': self.titleText_field.get(),
                    'Tags': self.tagText_field.get(),
                    'Allgemein': self.allgemeinText_field.get(),
                    'Datum': datum_value,
                }



                # Verwende die Liste hochgeladene_tdms_dateien, um die Pfade der hochgeladenen TDMS-Dateien zu durchlaufen
                for index, metadata_datei in enumerate(self.uploaded_file_names):
                    if metadata_datei.lower().endswith(".tdms"):
                        #sorted(self.uploaded_file_names, key=lambda x: (not x.lower().endswith('.tdms'), x))
                        abschnitt_name = os.path.basename(metadata_datei)
                        abschnitt_daten = {
                            'Ersteller/in (ID: 2)': os.getlogin(),
                            'Titel (ID: 3)': os.path.basename(metadata_datei),
                            'Herausgeber (ID: 4)': 'Leibniz-Institut für Werkstofforientierte Technologien IWT-Universität Bremen',
                            'Jahr der Veröffentlichung/Datum (ID: 5/8)': date_tdms_file,
                            'Ressourcentyp (ID: 10)': 'Dataset-TDMS (Forces)',
                            'Rechte (ID: 16)': self.rechteText_field.get(),  # Nutzereingabe
                            'Description (ID: 17)': formatted_remark,
                            'GeoLocation (ID: 18)': 'Bremen, Germany',
                            'Förderkennzeichen (ID: 19)': self.förderkennzeichen_field.get(),  # Nutzereingabe
                            # 'Folder (ID: 1)': '',
                            # 'Software': 'VNWA3',
                            # 'Software Version': 'VNWA36.6 (2015)',
                            # 'Subject (ID: 6)': 'Generator',
                            # 'Language (ID: 7)': 'English'
                            # 'Date (ID: 8)': get_current_date(),
                            # 'RelatedIdentifier (ID: 12)': '',
                        }
                        # Das abschnitt_daten-Dictionary wird dem data-Dictionary hinzugefügt
                        data[abschnitt_name] = abschnitt_daten
                    else:
                        if metadata_datei.lower().endswith(".sur"):
                            #s = hs.load(metadata_datei)
                            #metadata = s.metadata.as_dictionary()
                            #date_sur = metadata['General']['date']

                            if metadata_datei in sur_dates:
                                date_sur = sur_dates[metadata_datei]
                                #signal_unfolded = sur_dates[metadata_datei]

                            else:
                                s = hs.load(metadata_datei)
                                metadata = s.metadata.as_dictionary()
                                date_sur = metadata['General']['date']
                                signal_unfolded = metadata['_HyperSpy']['Folding']['signal_unfolded']
                                original_axes_manager = metadata['_HyperSpy']['Folding']['original_axes_manager']
                                original_shape = metadata['_HyperSpy']['Folding']['original_shape']
                                unfolded = metadata['_HyperSpy']['Folding']['unfolded']
                                signal_type = metadata['Signal']['signal_type']
                                hyperspy_version = metadata['General']['FileIO']['0']['hyperspy_version']
                                io_plugin = metadata['General']['FileIO']['0']['io_plugin']
                                operation = metadata['General']['FileIO']['0']['operation']
                                authors = metadata['General']['authors']
                                original_filename = metadata['General']['original_filename']
                                time = metadata['General']['time']
                                title_meta = metadata['General']['title']
                                date_sur = metadata['General']['date']





                            abschnitt_name = os.path.basename(metadata_datei)
                            abschnitt_daten = {
                                'Ersteller/in (ID: 2)': os.getlogin(),
                                'Titel (ID: 3)': os.path.basename(metadata_datei),
                                'Herausgeber (ID: 4)': 'Leibniz-Institut für Werkstofforientierte Technologien IWT-Universität Bremen',
                                'Jahr der Veröffentlichung/Datum (ID: 5/8)': date_sur,
                                'Ressourcentyp (ID: 10)': 'Dataset-SUR (surface topography)',
                                'Rechte (ID: 16)': self.rechteText_field.get(),  # Nutzereingabe
                                'Description (ID: 17)': formatted_remark,
                                'GeoLocation (ID: 18)': 'Bremen, Germany',
                                'Förderkennzeichen (ID: 19)': self.förderkennzeichen_field.get(),  # Nutzereingabe
                                'Zusätzliche Informationen': {
                                    'original_axes_manager': original_axes_manager,
                                    #'original_shape': original_shape,
                                    'signal_unfolded': signal_unfolded,
                                    #'unfolded': unfolded,
                                    #'signal_type': signal_type,
                                    #'hyperspy_version': hyperspy_version,
                                    #'io_plugin': io_plugin,
                                    #'operation': operation,
                                    #'authors': authors,
                                    #'original_filename':original_filename,
                                    #'time': time,
                                    #'title': title_meta,

                                    # Weitere Einträge hier hinzufügen
                                },
                            }
                            data[abschnitt_name] = abschnitt_daten
                # Nachdem alle Abschnitte und Daten hinzugefügt wurden, wird das data-Dictionary in die Datei "daten.json" geschrieben.
                with open('daten.json', 'w') as json_datei:
                    json.dump(data, json_datei, indent=4)


                # Dateiname und Pfad für die JSON-Datei
                #filename = 'daten.json'
                #filepath = filename


                #with open(filepath, 'w') as outfile:
                #    json.dump(data, outfile)

                #print(f"Die Datei {filename} wurde erfolgreich erstellt!")


            def uploadJsonFile(exp_id):
                daten_json_path = 'daten.json'
                if os.path.exists(daten_json_path):
                    with open(daten_json_path, 'rb') as f:
                        params = {'file': f}
                        manager.upload_to_experiment(exp_id, params)
                        print(f"Uploaded file '{daten_json_path}' to experiment {exp_id}.")
                else:
                    print(f"File '{daten_json_path}' does not exist.")




            def upload_tdms_file():
                # Durch das Hinzufügen der Zeile global hochgeladene_tdms_dateien wird die Variable als global
                # markiert und alle Änderungen, die in der Funktion vorgenommen werden, wirken
                # sich auf die globale Variable aus.

                # filedialog ist ein Modul in Tkinter, das Funktionen für den Dateiauswahldialog bereitstellt.
                # askopenfilename() ist eine Funktion des filedialog-Moduls. Sie öffnet den Dateiauswahldialog und
                # gibt den ausgewählten Dateipfad zurück. Der Benutzer kann eine Datei auswählen und den Dialog schließen.
                # Der filetypes Parameter wird verwendet, um die Dateitypen festzulegen, die im
                # Dateiauswahldialog angezeigt werden sollen. In diesem Fall ist es eine Liste mit einem einzelnen
                # Tuple: ("TDMS files", "*.tdms").
                # Das Tuple enthält zwei Werte: der erste Wert ist eine Beschreibung des
                # Dateityps ("TDMS files") und der zweite Wert ist ein Muster, das angibt, welche Dateien angezeigt werden
                # sollen ("*.tdms" für TDMS-Dateien). Der Dateityp wird im Dateiauswahldialog angezeigt und hilft dem Benutzer,
                # die gewünschte Datei zu finden.
                # Die filepath Variable speichert den ausgewählten Dateipfad, der vom Dateiauswahldialog zurückgegeben wird.
                # Nachdem der Benutzer eine Datei ausgewählt und den Dialog geschlossen hat, enthält filepath den Pfad zur
                # ausgewählten TDMS-Datei.

                #global hochgeladene_tdms_dateien

                tdms_Label = customtkinter.CTkLabel(self)
                tdms_Label.grid(row=3, column=1, padx=10, pady=(0, 10))
                file_paths = filedialog.askopenfilenames(filetypes=[("TDMS files", "*.tdms")])

                if file_paths:
                     #hochgeladene_tdms_dateien.clear()  # Leere die Liste vor dem Hinzufügen der neuen Pfade

                    for filepath in file_paths:
                        self.tdmsMetadata = td.read_metadata(filepath).properties
                        print(file_paths)
                        print("Metadaten der TDMS-Datei:")
                        print("-----------------------------")
                        for key, value in self.tdmsMetadata.items():
                            print(f"{key}: {value}")

                        tdms_Label.configure(text="Metadata uploaded successfully.")
                        hochgeladene_tdms_dateien.append(filepath)  # Füge den Pfad zur Liste hinzu


                else:

                    tdms_Label.configure(text="No file was selected.")

            # Create an experiment

            def create_Experiment(title, tag, allgemein, rechte, förderkennzeichen, datum):

                response = manager.create_experiment()
                print(f"Created experiment with id {response['id']}")
                myLabel = customtkinter.CTkLabel(self, text=f"Created experiment with id {response['id']}.")
                myLabel.grid(row=4, column=1, padx=5, pady= (0,10))

                params = {"title": title,
                          "allgemein": allgemein,
                          "förderkennzeichen": förderkennzeichen,
                          "datum": datum,
                          "rechte": rechte}

                print(manager.post_experiment(response['id'], params))




                if tag != "":
                    tags = tag.split(",")
                    for t in tags:
                        params = {"tag": t.strip()}
                        print(manager.add_tag_to_experiment(response['id'], params))
                createJsonFile()

                exp_id = response['id']
                uploadJsonFile(exp_id)



                # upload the selected files to the experiment
                print(self.uploaded_file_names)
                for attached_files in self.uploaded_file_names:
                    if not attached_files.lower().endswith(".tdms") and not attached_files.lower().endswith(".sur"):
                        with open(attached_files, 'rb') as f:
                            params = {'file': f}
                            manager.upload_to_experiment(exp_id, params)
                            print(f"Uploaded file '{attached_files}' to experiment {exp_id}.")

                #file_paths = self.folderText_field.get().split(";")
               # for file_path in file_paths:
                #    with open(file_path, 'rb') as f:
                 #       params = {'file': f}
                  #      manager.upload_to_experiment(exp_id, params)
                   #     print(f"Uploaded file '{file_path}' to experiment {exp_id}.")



            myButton = customtkinter.CTkButton(self, text="Create Experiment",
                              command=lambda: create_Experiment(self.titleText_field.get(), self.tagText_field.get(), self.allgemeinText_field.get(),
                                                                self.rechteText_field.get(), self.förderkennzeichen_field.get(), self.datum_field.get()))
            myButton.grid(row=4, column=1, padx=(20, 20), pady=(10, 20), sticky = "es")

            #myUploadButton = customtkinter.CTkButton(self, text="Add File", command=prepare_for_upload)
            #myUploadButton.grid(row=1, column=1, padx=(0,0), pady=(10, 10))

            upload_button = ctk.CTkButton(self, text="Upload File", command=prepare_for_upload)
            upload_button.grid(row=1, column=1, padx=(0,0), pady=(10,10))

            selected_files_button = ctk.CTkButton(self, text="...", width=10, command=display_selected_files)
            selected_files_button.grid(row=1, column=1, padx=(175, 0), pady=(10, 10))

            #metaDataButton = customtkinter.CTkButton(self, text="Add Metadata", command=upload_tdms_file)
            #metaDataButton.grid(row=3, column=1, padx=(20, 20), pady=(10, 10), sticky= "e")





        def sidebar_edit_event(self):
            print("sidebar_button click")
            self.label = customtkinter.CTkLabel(self, text="")
            self.label.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        def sidebar_menu_event(self):
            print("sidebar_button click")
            self.label = customtkinter.CTkLabel(self, text="")
            self.label.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")


    # if something goes wrong, the corresponding HTTPError will be raised
    except HTTPError as e:
        print(e)



if __name__ == "__main__":
        app = GUI()
        app.mainloop()

