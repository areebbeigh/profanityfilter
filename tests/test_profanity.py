from profanityfilter import ProfanityFilter
import unittest

pf = ProfanityFilter()
TEST_STATEMENT = "Hey, I like unicorns, chocolate, oranges and man's blood, Turd!"
CLEAN_STATEMENT = "Hey there, I like chocolate too mate."

def update_censored(pf_instance=pf):
    global censored
    censored = pf_instance.censor(TEST_STATEMENT)
    #print(censored)


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
        update_censored()
        self.assertEqual(censored, "Hey, I like unicorns, chocolate, oranges and man's blood, ****!")
        pf.set_censor("#")
        update_censored()
        self.assertEqual(censored, "Hey, I like unicorns, chocolate, oranges and man's blood, ####!")

    def test_define_words(self):
        pf.define_words(["unicorn", "chocolate"])  # Testing pluralization here as well
        update_censored()
        self.assertFalse("unicorns" in censored)
        self.assertFalse("chocolate" in censored)
        self.assertTrue("Turd" in censored)

    def test_append_words(self):
        pf.append_words(["hey", "like"])
        update_censored()
        self.assertTrue("oranges" in censored)
        self.assertFalse("Hey" in censored)
        self.assertFalse("like" in censored)
        self.assertFalse("Turd" in censored)

    def test_restore_words(self):
        pf.define_words(["cupcakes"])
        pf.append_words(["dibs"])
        pf.restore_words()
        bad_words = pf.get_profane_words()
        self.assertFalse("dibs" in bad_words)
        self.assertFalse("cupcakes" in bad_words)

    def test_tokenization(self):
        pf.define_words(["man"])
        update_censored()
        self.assertEqual(censored, "Hey, I like unicorns, chocolate, oranges and ***'s blood, Turd!")

    def test_lemmatization(self):
        self.assertTrue(pf.is_profane("Dick"))
        self.assertTrue(pf.is_profane("DICK"))
        self.assertTrue(pf.is_profane("dIcK"))
        self.assertTrue(pf.is_profane("dicks"))
        self.assertTrue(pf.is_profane("fucks"))


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
