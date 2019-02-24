from profanityfilter import ProfanityFilter
import unittest

pf = ProfanityFilter()
TEST_STATEMENT = "Hey, I like unicorns, chocolate and oranges, big old Turd!"
CLEAN_STATEMENT = "Hey there, I like chocolate too mate."

def update_censored(pf_instance=pf):
    global censored
    censored = pf_instance.censor(TEST_STATEMENT)


class TestProfanity(unittest.TestCase):
    def setUp(self):
        global censored
        pf.set_censor("*")  # Only to restore the default censor char
        pf.restore_words()

    def test_checks(self):
        self.assertTrue(pf.is_profane(TEST_STATEMENT))
        self.assertFalse(pf.is_clean(TEST_STATEMENT))
        self.assertTrue(pf.is_clean(CLEAN_STATEMENT))
        self.assertFalse(pf.is_profane(CLEAN_STATEMENT))

    def test_censor(self):
        self.assertEqual(
            pf.censor("My email is fuckyoubitch@fuck.com"),
            "My email is fuckyoubitch@****.com"
        )
        update_censored()
        self.assertEqual(censored, "Hey, I like unicorns, chocolate and oranges, big old ****!")
        pf.set_censor("#")
        update_censored()
        self.assertEqual(censored, "Hey, I like unicorns, chocolate and oranges, big old ####!")

    def test_define_words(self):
        # Testing pluralization here as well
        pf.define_words(["unicorn", "chocolate"])
        update_censored()
        self.assertFalse("unicorns" in censored)
        self.assertFalse("chocolate" in censored)
        self.assertTrue("Turd" in censored)

    def test_append_words(self):
        pf.append_words(["Hey", "like", "old"])
        update_censored()
        self.assertTrue("oranges" in censored)
        self.assertFalse("Hey" in censored)
        self.assertFalse("like" in censored)
        self.assertFalse("Turd" in censored)
        self.assertTrue("big" in censored)
        self.assertFalse("old" in censored)

    def test_remove_word(self):
        self.assertFalse("Turd" in censored)
        self.assertFalse("old" in censored)
        pf.remove_word("turd")
        pf.remove_word("old")
        update_censored()
        self.assertTrue("Turd" in censored)
        self.assertTrue("old" in censored)
        
    def test_remove_words(self):
        self.assertFalse("like" in censored)
        self.assertTrue("there" in censored)
        self.assertFalse("xxx" in censored)
        pf.remove_words(["chocolate", "like", "xxx"])
        update_censored()
        self.assertTrue("there" in censored)
        self.assertTrue("like" in censored)
        self.assertTrue("xxx" in censored)
        self.assertFalse("unicorn" in censored)

    def test_restore_words(self):
        pf.define_words(["cupcakes"])
        pf.append_words(["dibs"])
        pf.remove_word("turd")
        pf.restore_words()
        bad_words = pf.get_profane_words()
        self.assertFalse("dibs" in bad_words)
        self.assertFalse("cupcakes" in bad_words)

if __name__ == "__main__":
    unittest.main()
