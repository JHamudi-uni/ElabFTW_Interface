import elabapy
import json
from requests.exceptions import HTTPError
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import datetime
import customtkinter
import customtkinter as ctk
from tkinter import Toplevel, Label
from nptdms import TdmsFile as td
import os



customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


# creates an instance of the Manager class from the elabapy library, initializing it with the endpoint and API token
manager = elabapy.Manager(endpoint="https://demo.elabftw.net/api/v1/", token="c066a0aa5e90d53561e00d064219943761df45d2475a6fd608f0b68f153150a31e3b157ddee4b00e77232")



hochgeladene_tdms_dateien = []

# class App erbt von customkinter.CTk
# self ist eine instanz vom Objekt
# __init__ ist der Konstruktor
class GUI(customtkinter.CTk):
    def __init__(self):
        # Ruft den Konstruktor der übergeordneten Klasse auf, um das Hauptfenster zu initialisieren.
        super().__init__()
        self.metadata = {}
        self.metadata_window = None
        self.metadata_window_open = False
        self.uploaded_file_names = set()
        #self.uploaded_file_names = []

        # Variable zur Verfolgung des aktuellen geöffneten Fensters
        self.current_window = None

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

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))

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
            self.headline_label.grid(row=0, column=1, padx=10, pady=(20, 110), sticky="WesN")
            #self.titleLabel = customtkinter.CTkLabel(self, text="Title:")
            #self.titleLabel.grid(row=0, column=1, padx=(150, 0), pady=(50, 10), sticky="W")
            self.titleText_field = customtkinter.CTkEntry(self, placeholder_text="Title")
            self.titleText_field.grid(row=0, column=1, padx=(160, 160), pady=(0, 10))

            # sticky=w nach links positionieren
            #self.tagLabel = customtkinter.CTkLabel(self, text="Tags:")
            #self.tagLabel.grid(row=1, column=1, padx=(150, 0), pady=(0, 10), sticky="W")
            self.tagText_field = customtkinter.CTkEntry(self, placeholder_text="Tags")
            self.tagText_field.grid(row=0, column=1, padx=(160, 160), pady=(90, 0))

            #self.folderLabel = customtkinter.CTkLabel(self, text="Files:")
            #self.folderLabel.grid(row=3, column=1, padx=(150, 0), pady=(0, 10), sticky="W")
            #self.folderText_field = customtkinter.CTkEntry(self, placeholder_text="Files")
            #self.folderText_field.grid(row=2, column=1, padx=(160, 160), pady=(10, 20))

            #self.grid_columnconfigure(1, weight=1)
            #self.grid_propagate(0)

            ###########################################################################################
            def get_current_date():
                return datetime.date.today().strftime('%Y-%m-%d')



            def display_metadata(file_path):
                #if not self.metadata_window_open and file_path.lower().endswith(".tdms"):
                    self.metadata_window = Toplevel(self)
                    self.metadata_window.title("Metadata")
                    center_window(self.metadata_window, 400, 500)
                    self.metadata_window.grab_set()

                    metadata_label = Label(self.metadata_window, text="Metadaten der TDMS-Datei:")
                    metadata_label.pack()

                    tdms_metadata = td.read_metadata(file_path).properties
                    for key, value in tdms_metadata.items():
                        metadata_entry = Label(self.metadata_window, text=f"{key}: {value}")
                        metadata_entry.pack()

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
                            self.metadata = td.read_metadata(filepath).properties
                            print(file_paths)
                            print("Metadaten der TDMS-Datei:")
                            print("-----------------------------")
                            for key, value in self.metadata.items():
                                print(f"{key}: {value}")

                            # tdms_Label.configure(text="Metadata uploaded successfully.")
                            # wird in createJsonFile verwendet
                            hochgeladene_tdms_dateien.append(filepath)  # Füge den Pfad zur Liste hinzu
                            self.uploaded_file_names.add(filepath)
                        #self.uploaded_file_names.append((os.path.basename(filepath), os.path.splitext(filepath)[1]))
                        # Hier können Sie spezifische Aktionen für .tdms-Dateien durchführen, falls gewünscht
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
                value2_window = Toplevel(self)
                value2_window.title("Selected Files")
                center_window(value2_window, 725, 400)
                self.current_window = value2_window  # Setze das aktuelle Fenster auf das neue Fenster
                value2_window.grab_set() # grab_set() erstellt ein "Modal"-Fenster, das den Fokus auf sich zieht und andere Fenster im Hintergrund blockiert

                canvas = Canvas(value2_window)
                canvas.pack(fill="both", expand=True)

                table_frame = Frame(canvas)
                canvas.create_window((0, 0), window=table_frame, anchor="nw")

                #scrollbar = Scrollbar(value2_window, orient="vertical", command=canvas.yview)
                #scrollbar.pack(side="right", fill="y")
                #canvas.configure(yscrollcommand=scrollbar.set)

                # Aufteilung der Dateien in .tdms und andere Dateitypen
                tdms_files = [file_path for file_path in self.uploaded_file_names if
                              file_path.lower().endswith(".tdms")]
                other_files = [file_path for file_path in self.uploaded_file_names if
                               not file_path.lower().endswith(".tdms")]

                # Erstelle die Tabellenüberschrift
                headers = ["File Name", "File Type", "Metadaten", "Action", "Display"] # ["File Name", "File Type", "Metadaten", "Action"]
                for col, header in enumerate(headers):
                    label = ctk.CTkLabel(table_frame, text=header, font=("Arial", 14, "bold"))
                    label.grid(row=0, column=col, padx=5, pady=5)

                # Fülle die Tabelle mit den ausgewählten Dateien
                for row, file_path in enumerate(tdms_files + other_files, start=1):
                    file_name = os.path.basename(file_path)
                    file_type = os.path.splitext(file_name)[1][1:].upper() if not file_path.lower().endswith(
                        ".tdms") else "TDMS"
                    has_metadata = "Metadaten" if file_path in hochgeladene_tdms_dateien else ""

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

                table_frame.update_idletasks()

                canvas.config(scrollregion=canvas.bbox("all"))
                value2_window.lift()

            def remove_selected_file(file_path):

                self.uploaded_file_names.remove(file_path)
                if file_path.lower().endswith(".tdms"):
                    hochgeladene_tdms_dateien.remove(file_path)
                display_selected_files()


            def createJsonFile():


                title_tdms_file = self.metadata.get("name", "N/A")
                print(title_tdms_file)
                description = self.metadata.get("description", "N/A")

                #hochgeladene_tdms_dateien = ['/Users/muhamedjaber/PycharmProjects/APIv1/03_Kaltgas_316L-Al_07_vf_4000.tdms', '/Users/muhamedjaber/PycharmProjects/APIv1/03_Kaltgas_316L-Al_10_vf_4600.tdms']

                data = {
                    'Title': self.titleText_field.get(),
                    'Tags': self.tagText_field.get(),
                }

                # Verwende die Liste hochgeladene_tdms_dateien, um die Pfade der hochgeladenen TDMS-Dateien zu durchlaufen
                for index, tdms_datei in enumerate(self.uploaded_file_names):
                    if tdms_datei.lower().endswith(".tdms"):
                        #sorted(self.uploaded_file_names, key=lambda x: (not x.lower().endswith('.tdms'), x))
                        abschnitt_name = f'Kraftmessung{index + 1}.tdms'
                        abschnitt_daten = {
                            'Folder': '',
                            'Creator (ID: 2)': '',
                            'Identifier (ID: 1)': '',
                            'Software': 'VNWA3',
                            'Software Version': 'VNWA36.6 (2015)',
                            'Description (ID: 17)': description,
                            'Date (ID: 8)': get_current_date(),
                            'Subject (ID: 6)': 'Generator',
                            'Title': tdms_datei,
                            'Publisher (ID: 4)': '',
                            'PublicationYear (ID: 5)': '',
                            'ResourceType (ID: 10)': 'Measurement',
                            'Contribter (ID: 7)': '',
                            'RelatedIdentifier (ID: 12)': '',
                            'GeoLocation (ID: 18)': 'Bremen, Germany',
                            'Language (ID: 7)': 'English'
                        }
                        # Das abschnitt_daten-Dictionary wird dem data-Dictionary hinzugefügt
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
                        self.metadata = td.read_metadata(filepath).properties
                        print(file_paths)
                        print("Metadaten der TDMS-Datei:")
                        print("-----------------------------")
                        for key, value in self.metadata.items():
                            print(f"{key}: {value}")

                        tdms_Label.configure(text="Metadata uploaded successfully.")
                        hochgeladene_tdms_dateien.append(filepath)  # Füge den Pfad zur Liste hinzu


                else:

                    tdms_Label.configure(text="No file was selected.")

            # Create an experiment

            def create_Experiment(title, tag):

                response = manager.create_experiment()
                print(f"Created experiment with id {response['id']}")
                myLabel = customtkinter.CTkLabel(self, text=f"Created experiment with id {response['id']}.")
                myLabel.grid(row=4, column=1, padx=5, pady= (0,10))

                params = {"title": title}
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
                    if not attached_files.lower().endswith(".tdms"):
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
                              command=lambda: create_Experiment(self.titleText_field.get(), self.tagText_field.get()))
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
    # if something goes wrong, the corresponding HTTPError will be raised
    except HTTPError as e:
        print(e)





if __name__ == "__main__":
        app = GUI()
        app.mainloop()

