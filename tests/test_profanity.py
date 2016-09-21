from profanityfilter import profanityfilter
import unittest

TEST_STATEMENT = "Hey, I like unicorns, chocolate and oranges, Turd!"


def update_censored():
    global censored
    censored = profanityfilter.censor(TEST_STATEMENT)


class TestProfanity(unittest.TestCase):
    def setUp(self):
        global censored
        profanityfilter.set_censor("*")  # Only to restore the default censor char
        profanityfilter.restore_words()

    def test_censor(self):
        update_censored()
        self.assertEqual(censored, "Hey, I like unicorns, chocolate and oranges, ****!")
        profanityfilter.set_censor("#")
        update_censored()
        self.assertEqual(censored, "Hey, I like unicorns, chocolate and oranges, ####!")

    def test_define_words(self):
        profanityfilter.define_words(["unicorn", "chocolate"])
        update_censored()
        self.assertFalse("unicorn" in censored)
        self.assertFalse("chocolate" in censored)
        self.assertTrue("Turd" in censored)

    def test_append_words(self):
        profanityfilter.append_words(["Hey", "like"])
        update_censored()
        self.assertTrue("oranges" in censored)
        self.assertFalse("Hey" in censored)
        self.assertFalse("like" in censored)
        self.assertFalse("Turd" in censored)

    def test_restore_words(self):
        profanityfilter.define_words(["cupcakes"])
        profanityfilter.append_words(["dibs"])
        profanityfilter.restore_words()
        bad_words = profanityfilter.get_bad_words()
        self.assertFalse("dibs" in bad_words)
        self.assertFalse("cupcakes" in bad_words)

if __name__ == "__main__":
    unittest.main()

