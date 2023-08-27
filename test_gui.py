from main import GUI
from main import manager
from unittest.mock import patch, MagicMock, Mock

import tempfile
import os
import unittest


class TestGUI(unittest.TestCase):
    def setUp(self):
        self.gui = GUI()

    def tearDown(self):
        self.gui.destroy()

    ###########################################################################
    #                               CREATE Test                               #
    ###########################################################################

    #GUI Test
    def test_create_page_display_headline_label(self):
        self.gui.sidebar_create_event()
        self.assertTrue(self.gui.headline_label.winfo_exists())

    def test_create_page_display_titleText_field(self):
        self.gui.sidebar_create_event()
        self.assertTrue(self.gui.titleText_field.winfo_exists())

    def test_create_page_display_tagText_field(self):
        self.gui.sidebar_create_event()
        self.assertTrue(self.gui.tagText_field.winfo_exists())

    def test_create_page_display_kommentarText_field(self):
        self.gui.sidebar_create_event()
        self.assertTrue(self.gui.kommentarText_field.winfo_exists())

    def test_create_page_display_rechteText_field(self):
        self.gui.sidebar_create_event()
        self.assertTrue(self.gui.rechteText_field.winfo_exists())

    def test_create_page_display_förderkennzeichen_field(self):
        self.gui.sidebar_create_event()
        self.assertTrue(self.gui.förderkennzeichen_field.winfo_exists())

    def test_create_page_display_datum_field(self):
        self.gui.sidebar_create_event()
        self.assertTrue(self.gui.datum_field.winfo_exists())

    def test_create_page_display_upload_button(self):
        self.gui.sidebar_create_event()
        self.assertTrue(self.gui.upload_button.winfo_exists())

    def test_create_page_display_selected_files_button(self):
        self.gui.sidebar_create_event()
        self.assertTrue(self.gui.selected_files_button.winfo_exists())

    def test_create_page_display_myButton(self):
        self.gui.sidebar_create_event()
        self.assertTrue(self.gui.myButton.winfo_exists())



    #################################### Funktionstest - Create #####################################
    #################################################################################################

    """
    Der @patch-Dekorator aus dem Modul unittest.mock wird verwendet, um vorübergehend eine 
    angegebene Funktion oder ein angegebenes Objekt durch ein Mock-Objekt zu ersetzen. 
    Dies ermöglicht es, die zu testende Funktion oder das Objekt von ihren externen 
    Abhängigkeiten zu isolieren und ihr Verhalten für Testzwecke zu kontrollieren.
    
    """
    @patch('tkinter.filedialog.askopenfilenames')
    def test_upload_files(self, mock_askopenfilenames):
        # Setup für mock um zu testen ob "dummy" Dateien hochgeladen werden
        mock_askopenfilenames.return_value = ('/path/to/file1.txt', '/path/to/file2.txt')

        # Simuliert das Klicken auf den button
        self.gui.upload_button.invoke()

        # Prüft ob askopenfilenames aufgerufen wurde
        mock_askopenfilenames.assert_called_once()

    def test_display_metadata_window_open(self):

        # TDMS datei zum Testen erstellen
        with tempfile.NamedTemporaryFile(suffix=".tdms", delete=False) as temp_file:
            temp_file_path = temp_file.name

        self.gui.display_metadata(temp_file_path)
        self.assertTrue(self.gui.metadata_window.winfo_exists())

        # Aufräumen: Die temporäre Datei wird wieder gelöscht
        os.remove(temp_file_path)

    @patch('__main__.GUI.remove_selected_file')
    def test_remove_selected_file(self, mock_remove_selected_file):
        from __main__ import GUI
        app = GUI()

        file_to_remove = "file1.tdms"
        app.remove_selected_file(file_to_remove)

        # Überprüfen, ob die Methode remove_selected_file mit dem erwarteten Argument aufgerufen wurde
        mock_remove_selected_file.assert_called_once_with(file_to_remove)


    @patch('__main__.manager')
    @patch('__main__.GUI')
    def test_create_experiment(self, mock_GUI, mock_Manager):
        # Mocken der erforderlichen Methoden und Eigenschaften des GUIs
        mock_gui_instance = mock_GUI.return_value
        mock_gui_instance.uploaded_file_names = ["file1.txt", "file2.csv"]

        # Mocken des managers
        manager_mock = MagicMock()
        mock_Manager.return_value = manager_mock
        mock_gui_instance.create_Experiment()




    ###########################################################################
    #                               EDIT Test                                 #
    ###########################################################################



    def test_edit_page_display_experiment_id_label(self):
        self.gui.sidebar_edit_event()
        self.assertTrue(self.gui.experiment_id_label.winfo_exists())

    def test_edit_page_display_experiment_id_entry(self):
        self.gui.sidebar_edit_event()
        self.assertTrue(self.gui.experiment_id_entry.winfo_exists())

    def test_edit_page_display_tag_entry(self):
        self.gui.sidebar_edit_event()
        self.assertTrue(self.gui.tag_entry.winfo_exists())

    def test_edit_page_display_title_entry(self):
        self.gui.sidebar_edit_event()
        self.assertTrue(self.gui.title_entry.winfo_exists())

    def test_edit_page_display_selected_files_button(self):
        self.gui.sidebar_edit_event()
        self.assertTrue(self.gui.selected_files_button.winfo_exists())

    def test_edit_page_display_link_button(self):
        self.gui.sidebar_edit_event()
        self.assertTrue(self.gui.link_button.winfo_exists())

    def test_edit_page_display_body_button(self):
        self.gui.sidebar_edit_event()
        self.assertTrue(self.gui.body_button.winfo_exists())

    def test_edit_page_display_edit_exp_button(self):
        self.gui.sidebar_edit_event()
        self.assertTrue(self.gui.edit_exp_button.winfo_exists())


    #################################### Funktionstest - Edit #######################################
    #################################################################################################

    @patch('__main__.manager')
    @patch('__main__.GUI')
    def test_link_to_database(self, mock_GUI, mock_Manager):

        mock_gui_instance = mock_GUI.return_value
        mock_gui_instance.experiment_id_entry.get.return_value = "source_experiment_id"
        mock_gui_instance.database_target_entry.get.return_value = "target_database_id"


        manager_mock = MagicMock()
        mock_Manager.return_value = manager_mock

        # Testen der Methode
        mock_gui_instance.link_to_database(mock_gui_instance.link_window)




    @patch('__main__.manager')
    @patch('__main__.GUI')
    def test_upload_file_edit(self, mock_GUI, mock_Manager):
        mock_gui_instance = mock_GUI.return_value
        mock_gui_instance.uploaded_file_names = ["file1.txt", "file2.csv"]

        manager_mock = MagicMock()
        mock_Manager.return_value = manager_mock
        mock_gui_instance.upload_to_experiment()



    ###########################################################################
    #                               HELP MENU Test                            #
    ###########################################################################

    def test_help_page_display_title(self):
        self.gui.sidebar_menu_event()
        self.assertTrue(self.gui.user_guide_title.winfo_exists())

    def test_help_page_display_text(self):
        self.gui.sidebar_menu_event()
        self.assertTrue(self.gui.frame_label.winfo_exists())


if __name__ == '__main__':
    unittest.main()