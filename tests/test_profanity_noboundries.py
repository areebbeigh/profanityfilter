from profanityfilter import ProfanityFilter
import unittest

pf = ProfanityFilter(no_word_boundaries=True)
TEST_STATEMENT = "Hey, my efuckingmail is fuckyoucunt@bitch.com"
CENSORED_STATEMENT = "Hey, my e*******mail is ****you****@*****.com"
CLEAN_STATEMENT = "Hey there, I like chocolate too mate."


def update_censored(pf_instance=pf):
    global censored
    censored = pf_instance.censor(TEST_STATEMENT)


class TestProfanity(unittest.TestCase):

    def setUp(self):
        global censored
        # Only to restore the default censor char
        pf.set_censor("*")
        pf.restore_words()

    def test_checks(self):
        self.assertTrue(pf.is_profane(TEST_STATEMENT))
        self.assertFalse(pf.is_clean(TEST_STATEMENT))
        self.assertTrue(pf.is_clean(CLEAN_STATEMENT))
        self.assertFalse(pf.is_profane(CLEAN_STATEMENT))

    def test_censor(self):
        update_censored()
        self.assertEqual(censored, CENSORED_STATEMENT)
        pf.set_censor("#")
        update_censored()
        self.assertEqual(censored, CENSORED_STATEMENT.replace("*", "#"))


if __name__ == "__main__":
    unittest.main()
