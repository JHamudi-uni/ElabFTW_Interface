import unittest
from main import GUI

class TestGUI(unittest.TestCase):
    def setUp(self):
        self.gui = GUI()

    ###########################################################################
    #                               CREATE Test                               #
    ###########################################################################





    ###########################################################################
    #                               EDIT Test                                 #
    ###########################################################################




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