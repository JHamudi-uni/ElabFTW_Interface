import elabapy
import json
import os
import hyperspy.api as hs
import pprint
import datetime
import customtkinter
import customtkinter as ctk
import tkinter as tk
import ssl

from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import Toplevel, Label
from nptdms import TdmsFile as td
from requests.exceptions import HTTPError
from dotenv import load_dotenv

# SSL ZERTIFIKAT
#os.environ["REQUESTS_CA_BUNDLE"] = 'c:\schoe\python\elabftw\elabftw.pem'
#os.environ["SSL_CERT_FILE"] = 'c:\schoe\python\elabftw\elabftw.pem'
#ssl.match_hostname = lambda cert, hostname: True

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


# KONFIGURATION

"""
Dotenv wird zum laden der Umgebungsvariablen token (aus der .env datei) genutzt.
Dadurch kann auf das lokale Elab zugegriffen werden, ohne den Token-key im Code abspeichern zu müssen.
"""

load_dotenv()
token = os.getenv("ELAB_TOKEN")

"""
Erstellt eine Instanz der Managerklasse aus der elabapy Bibliothek und initialisiert sie mit dem 
Endpunkt und dem API-Token
lokal: https://elabftw.iwt.zz/api/v1/
token: In die .env Datei schreiben
"""

manager = elabapy.Manager(endpoint="https://demo.elabftw.net/api/v1/", token=token)

# GLOBALE VARIABLEN
body_content = ""
date_sur = None
signal_unfolded = None
original_shape = None
original_axes_manager = None
unfolded = None
signal_type = None
hyperspy_version = None
io_plugin = None
operation = None
authors = None
original_filename = None
time = None
title_meta = None
title_id_edit = None
tag_id_edit = None
edit_json = False



hochgeladene_metadaten_dateien = []
sur_dates = {}
liste_daten_json = []
edit_json_data = {" "}


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
        self.value2_window = None

        # Variable zur Verfolgung des aktuellen geöffneten Fensters
        self.current_window = None
        self.open_windows = []  # Liste um alle geöffneten Fenster zu speicher

        global filename

        # GUI Fenster konfiguration
        self.title("ElabAPI")
        self.geometry(f"{780}x{525}")

        self.user_guide_text = """
    Diese Software bietet zwei Hauptoptionen: Das Erstellen eines neuen Experiments ins 
    eLabFTW (Create) und das Bearbeiten eines bestehenden Experiments (Edit).
    
    Create Experiment:
        1. Title: Erwartet Eingabe von Titel des Experiments.
        2. Tags: Erwartet Tags des Experiments, mehrere Tags sind möglich 
        (Tags mit einem Komma trennen, z.B.: tag1, tag2, usw.).
        3. Förderkennzeichen: Hier können  Organisationen oder 
        Behörden angegeben werden, die die Forschung finanziert haben.
        4. Rechte: Wahl der Rechte für das geistige Eigentum an den Daten erwartet. 
        z.B.: 'CC-BY'(BY Attribution), 'CC-0'(Daten) & 'CC Version 4.0'(schriftliche Dokumente).
        5. Allgemein: Feld für allgemeine Angaben, die in der JSON-Datei gespeichert werden.
        6. Datum: Standardmäßig wird das heutige Datum verwendet. 
        Anderes Datum eingeben oder das Feld leer lassen.
        7. Upload File: Wählen Sie eine Datei aus, die hochgeladen werden soll. 
        Unter "..." werden alle ausgewählten Dateien strukturiert angezeigt. 
        Einige Einträge können bearbeitet und durch Klicken auf "Speichern" bestätigt werden.
        8. Sobald alle erforderlichen Informationen eingegeben wurden, klicken Sie 
        auf "Create Experiment", um das Experiment in eLabFTW anzulegen.
    Hinweis: Durch Klicken auf "Create" werden alle ausgewählten Dateien geleert. 
    Bitte nur auf "Create" klicken, wenn ein neues Experiment erstellen werden soll.
            
    Experiment bearbeiten:
        1. Experiment-ID: Geben Sie die ID des Experiments ein, das Sie bearbeiten möchten.    
        2. Add Tags: zusätzliche Tags hinzufügen, bestehende Tags werden beibehalten.
        3. Change Title: aktuellen Titel des Experiments überschreiben
        4. Link Database: erwartet die ID eines Database Items welches mit dem Experiment 
        verlinkt werden soll
        5. Add Body: Nach eingabe der Experiment ID kann der Inhalt der Textbox im ElabFtw 
        verändert werden 
        """


    # GRID LAYOUT KONFIGURATION
        """
        konfiguriere grid layout (4x4)
        weight=1 gibt an, dass die Spalte 1 elastisch ist und sich automatisch an
        die Breite des Fensters anpassen soll.
        """
        self.grid_columnconfigure(1, weight=1)

        """
        Konfiguration für die Spalten 2 und 3 festgelegt.
        Der Parameter weight=0 gibt an, dass diese Spalten nicht elastisch sind und keine
        zusätzliche Breite erhalten, wenn das Fenster vergrößert wird.
        """
        self.grid_columnconfigure((2, 3), weight=0)

        """
        Hier wird die Konfiguration für die Zeilen 0, 1 und 2 festgelegt.
        Der Parameter weight=1 gibt an, dass diese Zeilen elastisch sind und sich automatisch
        an die Höhe des Fensters anpassen sollen
        """
        self.grid_rowconfigure((0, 1, 2), weight=1)


    # SIDEBAR ERSTELLEN

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        # rowspan erlaubt es die tabellenzelle nach unten auszudehnen
        self.sidebar_frame.grid(row=0, column=0, rowspan=7, sticky="nsew") #north, south, east, west
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Innerhalb der sidebar spricht man die widgets mit self.sidebar_frame an
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="ElabFTW", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Buttons der Sidebar
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Create", command=self.sidebar_create_event)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Edit", command=self.sidebar_edit_event)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Help",
                                                        command=self.sidebar_menu_event)
        self.sidebar_button_3.grid(row=5, column=0, padx=20, pady=(10,20))

        # Darkmode/Lightmode
        #self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        #self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        #self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       #command=self.change_appearance_mode_event)
        #self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))
        #self.appearance_mode_optionemenu.set("Dark")



    ###########################################################################
    #                               HELP-MENU GUI                             #
    ###########################################################################

        #self.user_guide_label = customtkinter.CTkLabel(self, text=self.user_guide_text, justify="left", padx=10, pady=10)
        #self.user_guide_label.grid_forget()

        self.user_guide_title = customtkinter.CTkLabel(self, text="Willkommen in der GUI-Benutzeranleitung:",
                                                       font=customtkinter.CTkFont(size=16, weight="bold"))
        self.user_guide_title.grid_forget()

        self.frame = customtkinter.CTkFrame(self, width=200, height=150)
        self.frame.grid_forget()
        self.frame_label = customtkinter.CTkLabel(self.frame, text=self.user_guide_text, anchor="w", justify="left", font=customtkinter.CTkFont(size=12))
        self.frame_label.grid_forget()



        ###########################################################################
        #                               EDIT GUI                                  #
        ###########################################################################

        self.experiment_id_label = customtkinter.CTkLabel(self, text="Edit Experiment",
                                                font=customtkinter.CTkFont(size=16, weight="bold"))
        self.experiment_id_label.grid_forget()

        self.experiment_id_entry = customtkinter.CTkEntry(self, placeholder_text="Experiment ID")
        self.experiment_id_entry.grid_forget()

        self.tag_entry = customtkinter.CTkEntry(self, placeholder_text="Add Tags")
        self.tag_entry.grid_forget()

        self.title_entry = customtkinter.CTkEntry(self, placeholder_text="Change Title")
        self.title_entry.grid_forget()

        self.upload_button_edit = customtkinter.CTkButton(self, text="Add Files", command=self.prepare_for_upload)
        self.upload_button_edit.grid_forget()

        self.edit_exp_button = customtkinter.CTkButton(self, text="Edit Experiment", command=self.upload_file_edit)
        self.edit_exp_button.grid_forget()

        self.link_button = customtkinter.CTkButton(self, text="Link Database", command=self.open_link_window)
        self.link_button.grid_forget()

        self.body_button = customtkinter.CTkButton(self, text="Add Body", command=self.open_body_window)
        self.body_button.grid_forget()

        self.myLabel_edit = customtkinter.CTkLabel(self)
        self.myLabel_edit.grid_forget()



        ###########################################################################
        #                               CREATE GUI                                #
        ###########################################################################

        self.headline_label = customtkinter.CTkLabel(self, text="Create new Experiment",
                                                     font=customtkinter.CTkFont(size=16, weight="bold"))
        self.headline_label.grid_forget()

        self.titleText_field = customtkinter.CTkEntry(self, placeholder_text="Title")
        self.titleText_field.grid_forget()

        self.tagText_field = customtkinter.CTkEntry(self, placeholder_text="Tags")
        self.tagText_field.grid_forget()

        self.allgemeinText_field = customtkinter.CTkEntry(self, placeholder_text="Allgemein")
        self.allgemeinText_field.grid_forget()

        self.rechteText_field = customtkinter.CTkEntry(self, placeholder_text="Rechte")
        self.rechteText_field.grid_forget()

        self.förderkennzeichen_field = customtkinter.CTkEntry(self, placeholder_text="Förderkennzeichen")
        self.förderkennzeichen_field.grid_forget()

        self.datum_field = customtkinter.CTkEntry(self, placeholder_text="Datum")
        self.datum_field.grid_forget()

        self.upload_button = ctk.CTkButton(self, text="Upload File", command=self.prepare_for_upload)
        self.upload_button.grid_forget()

        self.selected_files_button = ctk.CTkButton(self, text="...", width=10, command=self.display_selected_files)
        self.selected_files_button.grid_forget()

        self.myButton = customtkinter.CTkButton(self, text="Create Experiment",
                                           command=lambda: self.create_Experiment(self.titleText_field.get(),
                                                                             self.tagText_field.get(),
                                                                             self.allgemeinText_field.get(),
                                                                             self.rechteText_field.get(),
                                                                             self.förderkennzeichen_field.get(),
                                                                             self.datum_field.get()))
        self.myButton.grid_forget()

        self.myLabel = customtkinter.CTkLabel(self)
        self.myLabel.grid_forget()




    ###########################################################################
    #                               HELP-MENU FUNKTIONEN                      #
    ###########################################################################


    # HELP-MENU Funktionen hier erstellen



    ###########################################################################
    #                               EDIT FUNKTIONEN                           #
    ###########################################################################

    def get_uploaded_files_for_experiment(self, experiment_id):
        experiment = manager.get_experiment(experiment_id)
        print(experiment)
        experiment_files = experiment.get('uploads', [])
        print("Experiment files:")
        print(experiment_files)
        return experiment_files

    def load_body_text(self):
        global body_content
        experiment_id_edit = self.experiment_id_entry.get()

        # Hier rufst du den aktuellen Body-Inhalt des Experiments ab
        experiment = manager.get_experiment(experiment_id_edit)
        current_body_content = experiment.get('body', '')

        # Setze den geladenen Textinhalt im GUI-Textfeld
        self.body_text.delete("1.0", tk.END)  # Lösche den vorhandenen Text im Textfeld
        self.body_text.insert("1.0", current_body_content)  # Füge den geladenen Textinhalt hinzu


        """
           Öffnet ein neues Fenster zur verlinkung von Database items mit einem Experiment.
           Wenn ein aktuelles Fenster bereits offen ist, wird es geschlossen.
        
           @return: None
        """
    def open_link_window(self):
        if self.current_window:
            self.current_window.destroy()
        self.link_window = tk.Toplevel(self)
        self.link_window.title("Link Databases")
        self.link_window.geometry("340x200")  # Größe des Fensters setzen

        self.current_window = self.link_window  # Setze das aktuelle Fenster auf das neue Fenster
        self.link_window.grab_set()

        # Database Linking Sektion
        database_frame = tk.Frame(self.link_window)
        database_frame.grid(padx=20, pady=20)

        database_label = customtkinter.CTkLabel(database_frame, text="Database Linking",
                                                font=customtkinter.CTkFont(size=14, weight="bold"))
        database_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        self.database_source_label = customtkinter.CTkLabel(database_frame, text="Source Experiment ID:")
        self.database_source_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(0, 5))
        self.database_source_entry = customtkinter.CTkEntry(database_frame, placeholder_text=self.experiment_id_entry.get())
        self.database_source_entry.grid(row=1, column=1, padx=(0, 10), pady=(0, 5))

        self.database_target_label = customtkinter.CTkLabel(database_frame, text="Target Database ID:")
        self.database_target_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(0, 5))
        self.database_target_entry = customtkinter.CTkEntry(database_frame, placeholder_text="ID of Database Item")
        self.database_target_entry.grid(row=2, column=1, padx=(0, 10), pady=(0, 5))

        self.database_link_button = customtkinter.CTkButton(database_frame, text="Link to Database",
                                                            command=lambda: self.link_to_database(self.link_window))
        self.database_link_button.grid(row=3, column=0, columnspan=2, pady=(10, 0))

    def save_body_text(self):
        global body_content
        body_content = self.body_text.get("1.0", tk.END)  # Hole den gesamten Text
        print("Saved body content:", body_content)
        self.link_window.destroy()

    def open_body_window(self):
        if self.current_window:
            self.current_window.destroy()
        self.link_window = tk.Toplevel(self)
        self.link_window.title("Add Body")
        self.link_window.geometry("460x400")  # Größe des Fensters setzen

        self.current_window = self.link_window  # Setze das aktuelle Fenster auf das neue Fenster
        self.link_window.grab_set()

        # Textfeld für langen Text
        self.body_text = scrolledtext.ScrolledText(self.link_window, wrap=tk.WORD)
        self.body_text.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")  # Oben mittig positionieren
        self.link_window.grid_rowconfigure(0, weight=1)
        self.link_window.grid_columnconfigure(0, weight=1)

        # Lade den aktuellen Body-Inhalt aus dem Experiment und zeige ihn im Textfeld an
        self.load_body_text()

        # Button zum Speichern des Texts
        save_button = customtkinter.CTkButton(self.link_window, text="Save", command=self.save_body_text)
        save_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="s")

        """
        Verknüpft die ausgewählte Experiment-ID mit der Ziel-Datenbank-ID.

        @param link_window: Das Fenster, in dem die Verknüpfung stattfindet.
        @return: None
        """
    def link_to_database(self, link_window):
        source_experiment_id = self.experiment_id_entry.get()
        target_database_id = self.database_target_entry.get()
        # Hier die Logik zur Verlinkung von Experiment zu Datenbank einfügen
        # link database item xx to experiment yy
        params = {"link": target_database_id, "targetEntity": "items"}
        print(manager.add_link_to_experiment(source_experiment_id, params))

        messagebox.showinfo("Database Linking", f"Experiment {source_experiment_id} linked to Database {target_database_id} successfully!")
        link_window.destroy()


        """
        Aktualisiert das ausgewählte Experiment mit den eingefügten Informationen und Dateien.

        Lädt ausgewählte Dateien in ein Experiment hoch, aktualisiert Titel, Datum und Inhalt des Experiments,
        fügt Tags hinzu und erstellt zum Schluss eine JSON-Datei mit den aktualisierten Informationen.

        @return: None
        """
    def upload_file_edit(self):
        self.hide_experiment_id_label()
        self.myLabel_edit = customtkinter.CTkLabel(self, text="Successfully Edited",
                                                   font=customtkinter.CTkFont(size=13))
        self.myLabel_edit.grid(row=5, column=1, padx=10, pady=10)
        experiment_id_edit = self.experiment_id_entry.get()
        global tag_id_edit
        tag_id_edit = self.tag_entry.get()
        global title_id_edit
        title_id_edit = self.title_entry.get()
        global liste_daten_json
        global body_content
        global edit_json
        edit_json = True


        # Lädt die ausgewählten Dateien zum Experiment
        print(self.uploaded_file_names)

        for attached_files in self.uploaded_file_names:
            if not attached_files.lower().endswith(".tdms") and not attached_files.lower().endswith(".sur"):
                with open(attached_files, 'rb') as file:
                    params_file = {'file': file}
                    manager.upload_to_experiment(experiment_id_edit, params_file)
                    print(f"Uploaded file '{attached_files}' to experiment {experiment_id_edit}.")

        if tag_id_edit != "":
            tags = tag_id_edit.split(",")
            for t in tags:
                params_tag = {"tag": t.strip()}
                print(manager.add_tag_to_experiment(experiment_id_edit, params_tag))



        params_update = {"title": title_id_edit, "date": self.get_current_date(), "body": body_content}
        params_body = {"bodyappend": "appended text<br>"}
        print(manager.post_experiment(experiment_id_edit, params_body))
        print(manager.post_experiment(experiment_id_edit, params_update))

        #kfile = self.get_uploaded_files_for_experiment(experiment_id_edit)
        #print("kfile:")
        #print(kfile)
        #print("----")

        self.createJsonFile()
        self.uploadJsonFile(experiment_id_edit)

        # Überprüfen, ob eine JSON-Datei im Experiment vorhanden ist
        experiment = manager.get_experiment(experiment_id_edit)
        experiment_files = experiment.get('files', [])
        json_files = [file for file in experiment_files if file['name'] == 'daten.json']

        if len(liste_daten_json) == 0:
                #self.createJsonFile()
                #self.uploadJsonFile(experiment_id_edit)
                print(liste_daten_json)


        else:
            print("end")
            # Andernfalls lade die bestehende JSON-Datei, füge Daten hinzu oder ändere sie
            #existing_json_file = json_files[0]  # Annahme: Es gibt nur eine JSON-Datei im Experiment
            #existing_json_content = manager.get_experiment_file(experiment_id_edit, existing_json_file['id'])
            # Hier kannst du die bestehende_json_content bearbeiten und anpassen
            #updated_json_content = existing_json_content  # Beispiel: Keine Änderungen
            # Dann die aktualisierte JSON-Datei hochladen
            #self.uploadUpdatedJsonFile(experiment_id_edit, existing_json_file['id'], updated_json_content)


        #print(manager.add_tag_to_experiment(experiment_id_edit, params_tag))





    ###########################################################################
    #                               CREATE FUNKTIONEN                         #
    ###########################################################################
        """
        Bereite die Dateien zum Upload vor.
        Unterschiedliche Dateitypen werden anders behandelt bzw. gespeichert.
        
        Schließt ein aktuelles Fenster, falls geöffnet, und öffnet ein Dateidialogfeld,
        um den Benutzern die Auswahl von Dateien zum hochladen zu ermöglichen.

        @return: None
        """
    def prepare_for_upload(self):
        self.current_window
        if self.current_window:
            self.current_window.destroy()  # Schließe das aktuelle Fenster, falls geöffnet

        # Das Modul filedialog wird verwendet, um ein Dateidialogfeld zu öffnen und dem Benutzer die Möglichkeit zu
        # geben, eine Datei zum Hochladen auszuwählen
        global hochgeladene_metadaten_dateien
        file_paths = filedialog.askopenfilenames()


        for filepath in file_paths:

            if filepath.lower().endswith(".tdms"):
                if filepath in hochgeladene_metadaten_dateien:
                    print(f"Die Datei '{filepath}' wurde bereits hochgeladen.")
                else:
                    self.tdmsMetadata = td.read_metadata(filepath).properties
                    print(file_paths)
                    print("Metadaten der TDMS-Datei:")
                    print("-----------------------------")
                    for key, value in self.tdmsMetadata.items():
                        print(f"{key}: {value}")

                    # wird in createJsonFile verwendet
                    hochgeladene_metadaten_dateien.append(filepath)  # Füge den Pfad zur Liste hinzu
                    self.uploaded_file_names.add(filepath)

            elif filepath.lower().endswith(".sur"):
                if filepath in hochgeladene_metadaten_dateien:
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
                    hochgeladene_metadaten_dateien.append(filepath)  # Füge den Pfad zur Liste hinzu
                    self.uploaded_file_names.add(filepath)

            else:
                self.uploaded_file_names.add(filepath)
                print(self.uploaded_file_names)

    """
        Zentriert ein Fenster auf dem Bildschirm.

        Berechnet die Position (x, y) basierend auf der Bildschirmgröße
        und positioniert dann das Fenster in der Mitte des Bildschirms.

        @param window: Das Fenster, das zentriert werden soll.
        @param width: Die Breite des Fensters.
        @param height: Die Höhe des Fensters.
        @return: None
        """
    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 4

        window.geometry(f"{width}x{height}+{x}+{y}")

    """
        Öffnet eine Tabelle mit den ausgewählten Dateien und ihren Eigenschaften (Name, Typ, Metadaten) an.
    
        Ebenso werden die möglichen Aktionen auf die jeweiligen Dateien angezeigt.
        @return: None
        """
    def display_selected_files(self):
        if self.current_window:
            self.current_window.destroy()
        self.value2_window = tk.Toplevel(self)
        self.open_windows.append(self.value2_window)
        self.value2_window.title("Selected Files")
        self.center_window(self.value2_window, 725, 400)


        self.current_window = self.value2_window  # Setze das aktuelle Fenster auf das neue Fenster
        # grab_set() erstellt ein "Modal"-Fenster, das den Fokus auf sich zieht und andere Fenster im
        # Hintergrund blockiert
        self.value2_window.grab_set()

        canvas = Canvas(self.value2_window)
        canvas.pack(fill="both", expand=True)

        table_frame = Frame(canvas)
        canvas.create_window((0, 0), window=table_frame, anchor="nw")


        # Aufteilung der Dateien in .tdms und andere Dateitypen in drei separate listen
        # Das ermöglicht es, die Dateien entsprechend ihrer Art zu gruppieren
        tdms_files = [file_path for file_path in self.uploaded_file_names if
                      file_path.lower().endswith(".tdms")]
        sur_files = [file_path for file_path in self.uploaded_file_names if file_path.lower().endswith(".sur")]
        other_files = [file_path for file_path in self.uploaded_file_names if
                       not file_path.lower().endswith((".tdms", ".sur"))]

        # Sortiere die Dateipfade in der gewünschten Reihenfolge
        # Je nachdem was wir zuerst sortieren, wird die reihenfolge festgelegt, wie die in der
        # tabellenansicht angezeigt werden
        tdms_files.sort()
        sur_files.sort()
        other_files.sort()

        # Erstelle die Tabellenüberschrift
        headers = ["File Name", "File Type", "Metadaten", "Action",
                   "Display"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(table_frame, text=header, font=("Arial", 14, "bold"))
            label.grid(row=0, column=col, padx=5, pady=5)

        # Fülle die Tabelle mit den ausgewählten Dateien
        for row, file_path in enumerate(tdms_files + sur_files + other_files, start=1):
            file_name = os.path.basename(file_path)
            file_type = os.path.splitext(file_name)[1][1:].upper() if not file_path.lower().endswith(
                ".tdms") else "TDMS"
            has_metadata = "Metadaten" if file_path in hochgeladene_metadaten_dateien or file_path.lower().endswith(
                ".sur") else ""

            file_name_label = ctk.CTkLabel(table_frame, text=file_name,
                                           font=customtkinter.CTkFont(size=12, weight="bold"))
            file_name_label.grid(row=row, column=0, padx=5, pady=5)

            file_type_label = Label(table_frame, text=file_type)
            file_type_label.grid(row=row, column=1, padx=5, pady=5)

            metadata_label = Label(table_frame, text=has_metadata)
            metadata_label.grid(row=row, column=2, padx=5, pady=5)

            remove_button = ctk.CTkButton(table_frame, text="Remove", width=12,
                                          command=lambda fp=file_path: self.remove_selected_file(fp))
            remove_button.grid(row=row, column=3, padx=5, pady=5)


            if file_path.lower().endswith(".tdms"):
                display_metadata_button = ctk.CTkButton(table_frame, text="Display Metadata",
                                                        command=lambda fp=file_path: self.display_metadata(fp))
                display_metadata_button.grid(row=row, column=4, padx=5, pady=5)
            elif file_path.lower().endswith(".sur"):
                display_metadata_button = ctk.CTkButton(table_frame, text="Display Metadata",
                                                        command=lambda fp=file_path: self.display_metadata(fp))
                display_metadata_button.grid(row=row, column=4, padx=5, pady=5)

        table_frame.update_idletasks()

        canvas.config(scrollregion=canvas.bbox("all"))
        self.value2_window.lift()

    """
       Entfernt die ausgewählte Datei aus der Liste der hochgeladenen Dateien (Wenn auf den Remove button
       geklickt wird).
       Falls die Datei Metadaten hatte, werden auch die Metadaten aus der entsprechenden Liste entfernt.

       @param file_path: Der Dateipfad der zu entfernenden Datei.
       @return: None
       """
    def remove_selected_file(self, file_path):
        self.uploaded_file_names.remove(file_path)
        if file_path.lower().endswith(".tdms") or file_path.lower().endswith(".sur"):
            hochgeladene_metadaten_dateien.remove(file_path)
        self.display_selected_files()

    def get_current_date(self):
        return datetime.date.today().strftime('%Y-%m-%d')


    """
       Zeigt die Metadaten der ausgewählten Datei an (Mit dem display Metedata Button).
       Je nach Dateityp werden verschiedene Metadaten angezeigt.

       @param filepath: Der Dateipfad der Datei, deren Metadaten angezeigt werden sollen.
       @return: None
       """
    def display_metadata(self, filepath):

        self.metadata_window = Toplevel(self)
        self.metadata_window.title("Metadata")
        self.center_window(self.metadata_window, 480, 500)
        self.metadata_window.grab_set()

        if filepath.lower().endswith(".tdms"):
            metadata_label = ctk.CTkLabel(self.metadata_window, text="Metadaten der TDMS-Datei:",
                                          font=("Arial", 14, "bold"))
            metadata_label.pack()

            tdms_metadata = td.read_metadata(filepath).properties
            for key, value in tdms_metadata.items():
                metadata_entry = Label(self.metadata_window, text=f"{key}: {value}")
                metadata_entry.pack()
        elif filepath.lower().endswith(".sur"):
            global date_sur
            global signal_unfolded
            global unfolded
            global original_axes_manager
            global original_shape
            global signal_type
            global hyperspy_version
            global io_plugin
            global operation
            global authors
            global original_filename
            global time
            global title_meta

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


                    # Falls self.filepath ungleich None ist:
                    sur_dates[filepath] = self.entry_date.get()

                    print("entry get:" + self.entry_date.get())

                    # Aktualisiert das metadata dictionary mit den neuen Werten
                    self.metadata['General']['date'] = date_sur
                    print("Metadata: " + self.metadata['General']['date'])

                    # Aktualisiert die textbox mit den neuen Werten
                    self.entry_date.delete(0, tk.END)
                    self.entry_date.insert(0,
                                           "None" if sur_dates.get(filepath) is None else sur_dates[filepath])

                    print("Changes saved successfully")

                except Exception as e:
                    print("An error occurred while saving changes:", str(e))

            """
               Aktualisiert die Daten mit den Metadatenwerten (Aus dem Dictionary in dem die eingelesenen 
               Daten gespeichert sind).

               @return: None
               """
            def update_textboxes():

                # Hyperspy
                original_axes_manager = self.metadata['_HyperSpy']['Folding']['original_axes_manager']
                original_shape = self.metadata['_HyperSpy']['Folding']['original_shape']
                signal_unfolded = self.metadata['_HyperSpy']['Folding']['signal_unfolded']
                unfolded = self.metadata['_HyperSpy']['Folding']['unfolded']

                # General
                hyperspy_version = self.metadata['General']['FileIO']['0']['hyperspy_version']
                io_plugin = self.metadata['General']['FileIO']['0']['io_plugin']
                operation = self.metadata['General']['FileIO']['0']['operation']
                authors = self.metadata['General']['authors']
                date = self.metadata['General']['date']
                print(date)
                original_filename = self.metadata['General']['original_filename']
                time = self.metadata['General']['time']
                title_meta = self.metadata['General']['title']

                # Signal
                signal_type = self.metadata['Signal']['signal_type']

                save_changes()
                try:
                    self.entry_date.delete(0, tk.END)
                    self.entry_date.insert(0, "None" if date is None else date)

                except Exception as e:
                    print("An error occurred:", str(e))



            ###########################################################################
            #                               SURFACE METADATA GUI                      #
            ###########################################################################

            metadata_label = tk.Label(self.metadata_window, text="Metadaten der Surfaces-Datei:",
                                            font=("Arial", 14, "bold"))
            metadata_label.grid(row=0, column=1)

            hyperspy_label = tk.Label(self.metadata_window, text="HyperSpy:", font=("Arial", 14, "bold"), anchor="w")
            hyperspy_label.grid(row=1, column=0, sticky="w")

            original_axes_manager_label = tk.Label(self.metadata_window, text="original_axes_manager:", font=("Arial", 14))
            original_axes_manager_label.grid(row=2, column=0, sticky="w")
            original_axes_manager_value = tk.Label(self.metadata_window, text="None" if original_axes_manager is None else str(original_axes_manager), font=("Arial", 14))
            original_axes_manager_value.grid(row=2, column=1, padx=5, pady=2)

            original_shape_label = tk.Label(self.metadata_window, text="original_shape:", font=("Arial", 14))
            original_shape_label.grid(row=3, column=0, sticky="w")
            original_shape_value = tk.Label(self.metadata_window, text="None" if original_shape is None else str(original_shape), font=("Arial", 14))
            original_shape_value.grid(row=3, column=1, padx=5, pady=2)

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
            self.entry_date = entry_date  # Save entry_date as an instance variable
            self.metadata = metadata  # Save metadata as an instance variable
            update_textboxes()

        self.metadata_window.lift()



    def close_metadata_window(self):
        self.metadata_window.destroy()
        self.metadata_window_open = False

    """
       Erstellt die JSON-Datei mit Metadaten für die hochgeladenen Dateien.
       Die Metadaten werden aus verschiedenen "Quellen" abgerufen und strukturiert in das JSON-Format eingefügt.
       Die JSON-Datei wird im aktuellen Verzeichnis als "daten.json" gespeichert.

       @return: None
       """
    def createJsonFile(self):

        title_tdms_file = self.tdmsMetadata.get("name", "N/A")
        date_tdms_file = self.tdmsMetadata.get("Date", "N/A")
        print(title_tdms_file)
        remark_tdms_file = self.tdmsMetadata.get("Remark", "N/A")
        formatted_remark = remark_tdms_file.replace("\r\n", " ")

        global tag_id_edit
        global title_id_edit
        global date_sur
        global signal_unfolded
        global unfolded
        global original_axes_manager
        global original_shape
        global signal_type
        global hyperspy_version
        global io_plugin
        global operation
        global authors
        global original_filename
        global time
        global title_meta

        datum_value = self.datum_field.get()

        if datum_value == "":
            datum_value = self.get_current_date()

        if edit_json:
            title_value = self.titleText_field.get()
            tags_value = self.tagText_field.get()
            title_value = None
            tags_value = None

        else:
            title_value = self.titleText_field.get()
            tags_value = self.tagText_field.get()



        data = {
            'Title': title_value or title_id_edit,
            'Tags': tags_value or tag_id_edit,
            'Allgemein': self.allgemeinText_field.get(),
            'Datum': datum_value,
        }

        # Verwende die Liste hochgeladene_metadaten_dateien, um die Pfade der hochgeladenen TDMS-Dateien zu durchlaufen
        for index, metadata_datei in enumerate(self.uploaded_file_names):
            if metadata_datei.lower().endswith(".tdms"):
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

                    if metadata_datei in sur_dates:
                        date_sur = sur_dates[metadata_datei]

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
                            'original_shape': original_shape,
                            'signal_unfolded': signal_unfolded,
                            'unfolded': unfolded,
                            'signal_type': signal_type,
                            'hyperspy_version': hyperspy_version,
                            'io_plugin': io_plugin,
                            'operation': operation,
                            'authors': authors,
                            'original_filename':original_filename,
                            'time': time,
                            'title': title_meta,

                        },
                    }
                    data[abschnitt_name] = abschnitt_daten
        # Nachdem alle Abschnitte und Daten hinzugefügt wurden, wird das data-Dictionary in die Datei "daten.json" geschrieben.
        with open('daten.json', 'w') as json_datei:
            json.dump(data, json_datei, indent=4)

    """
      Lädt die JSON-Datei "daten.json" zu dem Experiment hinzu.

      Diese Funktion überprüft, ob die JSON-Datei "daten.json" im aktuellen Verzeichnis vorhanden ist.
      Falls ja, dann wird sie zu dem angegebenen Experiment mit der angegebenen ID hochgeladen.
      Andernfalls wird eine entsprechende Fehlermeldung ausgegeben.

      @param exp_id: Die ID des Experiments, zu dem die JSON-Datei hochgeladen werden soll.
      @return: None
      """
    def uploadJsonFile(self, exp_id):
        daten_json_path = 'daten.json'
        if os.path.exists(daten_json_path):
            with open(daten_json_path, 'rb') as f:
                params = {'file': f}
                manager.upload_to_experiment(exp_id, params)
                liste_daten_json.append(daten_json_path)
                hochgeladene_metadaten_dateien.clear()
                print(liste_daten_json)
                print(f"Uploaded file '{daten_json_path}' to experiment {exp_id}.")
        else:
            print(f"File '{daten_json_path}' does not exist.")

    """
        Wird am anfang der create_Experiment Funktion aufgerufen.
        Soll verhindern, dass wenn man zweimal hintereinander die create_Experiment funktion aufruft, das
        self.myLabel nicht auf dem Fenster bleibt und beim wechseln der Fenster weiterhin angezeigt wird.
        
        @return: None 
    
        """
    def hide_experiment_id_label(self):
        self.myLabel.grid_forget()
        self.myLabel_edit.grid_forget()

    """
       Erstellt ein neues Experiment und lädt Dateien sowie Metadaten hoch.

       @param title: Der Titel des Experiments.
       @param tag: Die Tags für das Experiment (kommagetrennt).
       @param allgemein: Allgemeine Informationen zum Experiment.
       @param rechte: Rechteinformationen für das Experiment.
       @param förderkennzeichen: Das Förderkennzeichen für das Experiment.
       @param datum: Das Datum des Experiments.
       @return: None
       """
    def create_Experiment(self, title, tag, allgemein, rechte, förderkennzeichen, datum):
        global edit_json
        edit_json = False
        self.hide_experiment_id_label()
        global liste_daten_json
        liste_daten_json.clear()
        response = manager.create_experiment()
        print(f"Created experiment with id {response['id']}")
        self.myLabel = customtkinter.CTkLabel(self, text=f"Created experiment with id {response['id']}.")
        self.myLabel.grid(row=4, column=1, padx=5, pady=(0, 10))
        #self.after(15000, self.hide_experiment_id_label)

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
        self.createJsonFile()

        exp_id = response['id']
        self.uploadJsonFile(exp_id)

        # Lädt die ausgewählte Datei zum Experiment hoch
        print(self.uploaded_file_names)
        for attached_files in self.uploaded_file_names:
            if not attached_files.lower().endswith(".tdms") and not attached_files.lower().endswith(".sur"):
                with open(attached_files, 'rb') as f:
                    params = {'file': f}
                    manager.upload_to_experiment(exp_id, params)
                    print(f"Uploaded file '{attached_files}' to experiment {exp_id}.")

        self.uploaded_file_names.clear()



    try:

        def change_appearance_mode_event(self, new_appearance_mode: str):
            customtkinter.set_appearance_mode(new_appearance_mode)


        def sidebar_create_event(self):

            self.uploaded_file_names.clear()
            hochgeladene_metadaten_dateien.clear()
            print("sidebar_button Create click")

            # Unhide Create GUI Objects (nachdem zuerst alles andere ausgeblendet wurde)
            self.hide_all_labels()
            self.headline_label.grid(row=0, column=1, padx=10, pady=(20, 200), sticky="WesN")
            self.titleText_field.grid(row=0, column=1, padx=(0, 200), pady=(0, 60))
            self.tagText_field.grid(row=0, column=1, padx=(0, 200), pady=(90, 50))
            self.allgemeinText_field.grid(row=0, column=1, padx=(200, 0), pady=(90, 50))
            self.rechteText_field.grid(row=0, column=1, padx=(200, 0), pady=(0, 60))
            self.förderkennzeichen_field.grid(row=0, column=1, padx=(0, 200), pady=(200, 60))
            self.datum_field.grid(row=0, column=1, padx=(200, 0), pady=(200, 60))
            self.upload_button.grid(row=1, column=1, padx=(0, 0), pady=(10, 10))
            self.selected_files_button.grid(row=1, column=1, padx=(175, 0), pady=(10, 10))
            self.myButton.grid(row=4, column=1, padx=(20, 20), pady=(10, 20), sticky="es")



        def hide_all_labels(self):
            # Edit Elements
            self.experiment_id_label.grid_forget()
            self.experiment_id_entry.grid_forget()
            self.tag_entry.grid_forget()
            self.title_entry.grid_forget()
            self.upload_button_edit.grid_forget()
            self.edit_exp_button.grid_forget()
            self.link_button.grid_forget()
            self.myLabel_edit.grid_forget()
            self.body_button.grid_forget()

            # Create Elements
            self.headline_label.grid_forget()
            self.titleText_field.grid_forget()
            self.tagText_field.grid_forget()
            self.allgemeinText_field.grid_forget()
            self.rechteText_field.grid_forget()
            self.förderkennzeichen_field.grid_forget()
            self.datum_field.grid_forget()
            self.upload_button.grid_forget()
            self.selected_files_button.grid_forget()
            self.myButton.grid_forget()
            self.myLabel.grid_forget()

            # Help-Menu Elements
            self.user_guide_title.grid_forget()
            self.frame.grid_forget()
            self.frame_label.grid_forget()


        def sidebar_edit_event(self):
                self.hide_all_labels()
                self.uploaded_file_names.clear()

                self.experiment_id_label.grid(row=0, column=1, padx=10, pady=(40, 0), sticky="wesn")
                self.experiment_id_entry.grid(row=1, column=1, padx=10, pady=(0, 80))
                self.tag_entry.grid(row=1, column=1, padx=10, pady=(120, 80))
                self.title_entry.grid(row=1, column=1, padx=10, pady=(200, 40))
                self.upload_button_edit.grid(row=4, column=1, padx=10, pady=20)
                self.selected_files_button.grid(row=4, column=1, padx=(185,10), pady=20)
                self.link_button.grid(row=4, column=1, padx=(10,360), pady=20)
                self.body_button.grid(row=4, column=1, padx=(20, 20), pady=(5, 4), sticky="e")
                self.edit_exp_button.grid(row=5, column=1, padx=(20, 20), pady=(5, 20), sticky="es")


                print("sidebar_button click")

        def sidebar_menu_event(self):
            self.hide_all_labels()
            #self.user_guide_title.grid(row=0, column=1, sticky="wesn")

            self.user_guide_title.grid(row=0, column=1, sticky="wesn")
            self.frame.grid(row=1, column=1, padx=(10, 10))
            self.frame_label.grid(row=0, column=0, sticky="wesn", padx=(5, 5))

            print("sidebar_button click")



    # if something goes wrong, the corresponding HTTPError will be raised
    except HTTPError as e:
        print(e)




if __name__ == "__main__":
        app = GUI()
        app.mainloop()

