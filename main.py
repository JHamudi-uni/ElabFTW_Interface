import elabapy
import json
from requests.exceptions import HTTPError
from tkinter import *
from tkinter import filedialog
import datetime
import customtkinter
from nptdms import TdmsFile as td
import os



customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


# creates an instance of the Manager class from the elabapy library, initializing it with the endpoint and API token
manager = elabapy.Manager(endpoint="https://demo.elabftw.net/api/v1/", token="e8dd740722cc59ee3e8c70d696a8275551300504ff8ec3bbdd81e7cdaf1d1387c1631b00a5c2e044f6772")



hochgeladene_tdms_dateien = []

# class App erbt von customkinter.CTk
# self ist eine instanz vom Objekt
# __init__ ist der Konstruktor
class GUI(customtkinter.CTk):
    def __init__(self):
        # Ruft den Konstruktor der übergeordneten Klasse auf, um das Hauptfenster zu initialisieren.
        super().__init__()
        self.metadata = {}
        self.uploaded_file_names = set()

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
                for index, tdms_datei in enumerate(hochgeladene_tdms_dateien):
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


            def prepare_for_upload():
                # use the filedialog module to open a file dialog box and allow the user to select a file to upload
                global hochgeladene_tdms_dateien
                file_paths = filedialog.askopenfilenames()
                #tdms_Label = customtkinter.CTkLabel(self)
                #tdms_Label.grid(row=3, column=1, padx=10, pady=(0, 10))

                for filepath in file_paths:
                    if filepath.lower().endswith(".tdms"):
                        #upload_tdms_file()
                        self.metadata = td.read_metadata(filepath).properties
                        print(file_paths)
                        print("Metadaten der TDMS-Datei:")
                        print("-----------------------------")
                        for key, value in self.metadata.items():
                            print(f"{key}: {value}")

                        #tdms_Label.configure(text="Metadata uploaded successfully.")
                        # wird in createJsonFile verwendet
                        hochgeladene_tdms_dateien.append(filepath)  # Füge den Pfad zur Liste hinzu
                        self.uploaded_file_names.add(filepath)
                        # Hier können Sie spezifische Aktionen für .tdms-Dateien durchführen, falls gewünscht
                    else:
                        self.uploaded_file_names.add(filepath)
                        print(self.uploaded_file_names)

                        # Hier können Sie den Code einfügen, um Dateien normal hochzuladen
                        # update the folderText_field Entry widget with the path(s) to the selected file(s)
                    #self.folderText_field.delete(0, END)
                    #self.folderText_field.insert(0, ";".join(file_paths))




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

            myUploadButton = customtkinter.CTkButton(self, text="Add File", command=prepare_for_upload)
            myUploadButton.grid(row=1, column=1, padx=(0,0), pady=(10, 10))

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

