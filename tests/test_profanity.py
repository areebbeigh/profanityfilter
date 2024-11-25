from profanityfilter import ProfanityFilter
import unittest

pf = ProfanityFilter()
TEST_STATEMENT = "Hey, I like unicorns, chocolate and oranges, Turd!"
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
        self.assertEqual(censored, "Hey, I like unicorns, chocolate and oranges, ****!")
        pf.set_censor("#")
        update_censored()
        self.assertEqual(censored, "Hey, I like unicorns, chocolate and oranges, ####!")

    def test_define_words(self):
        # Testing pluralization here as well
        pf.define_words(["unicorn", "chocolate", "centaur"])
        update_censored()
        self.assertFalse("unicorns" in censored)
        self.assertFalse("chocolate" in censored)
        self.assertTrue("Turd" in censored)

    def test_append_words(self):
        pf.append_words(["Hey", "like"])
        update_censored()
        self.assertTrue("oranges" in censored)
        self.assertFalse("Hey" in censored)
        self.assertFalse("Turd" in censored)

    def test_remove_word(self):
        self.assertTrue("Turd" in censored)
        pf.append_words(["oranges", "potato"])
        update_censored()
        pf.remove_word("turd")
        self.assertRaises(ValueError, pf.remove_word, "potato", anywhere=False)
        pf.remove_word("oranges")
        update_censored()
        self.assertTrue("Turd" in censored)
        self.assertFalse("oranges" in pf.get_profane_words())
        self.assertTrue("potato" in pf.get_profane_words())
        
    def test_remove_words(self):
        pf.define_words(["chocolate", "centaur"])
        pf.append_words(["potato", "racecar", "hey"])
        self.assertTrue("chocolate" in pf.get_profane_words())
        self.assertRaises(ValueError, pf.remove_words, ["chocolate", "racecar"], anywhere=False)
        pf.remove_words(["centaur", "hey"])
        self.assertFalse("chocolate" in pf.get_profane_words())
        self.assertTrue("racecar" in pf.get_profane_words())
        self.assertFalse("centaur" in pf.get_profane_words())

    def test_restore_words(self):
        pf.define_words(["cupcakes"])
        pf.append_words(["dibs"])
        pf.remove_word("turd")
        pf.restore_words()
        bad_words = pf.get_profane_words()
        self.assertFalse("dibs" in bad_words)
        self.assertFalse("cupcakes" in bad_words)

    def test_symbols(self):
        pf.define_words(["+123456789", "@$$", r"backs\ash"])
        update_censored()
        bad_words = pf.get_profane_words()
        assert r"\+123456789" in bad_words
        assert r"@\$\$" in bad_words
        assert pf.censor("Call +123456789 for unit testing") == "Call ********** for unit testing"
        assert pf.censor("He saddled his @$$.") == "He saddled his ***."
        assert pf.censor(r"Slash, slash, backs\ash, escape.") == "Slash, slash, *********, escape."


if __name__ == "__main__":
    unittest.main()
