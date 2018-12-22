from profanityfilter import ProfanityFilter
import unittest

pf = ProfanityFilter()
TEST_STATEMENT = "Hey, I like unicorns, chocolate and oranges, Turd!"
CLEAN_STATEMENT = "Hey there, I like chocolate too mate."

def update_censored(pf_instance=pf):
    global censored
    censored = pf_instance.censor(TEST_STATEMENT)

class TestInstanciation(unittest.TestCase):
    def setUp(self):
        self.custom_pf = ProfanityFilter(custom_censor_list=["chocolate", "orange"])
        self.extended_pf = ProfanityFilter(extra_censor_list=["chocolate", "orange"])

    def test_custom_list(self):
        update_censored(self.custom_pf)
        self.assertFalse("chocolate" in censored)
        self.assertFalse("oranges" in censored)
        self.assertTrue("Turd" in censored)

    def test_extended_list(self):
        update_censored(self.extended_pf)
        self.assertFalse("chocolate" in censored)
        self.assertFalse("oranges" in censored)
        self.assertFalse("Turd" in censored)
        self.assertTrue("Hey" in censored)

if __name__ == "__main__":
    unittest.main()
