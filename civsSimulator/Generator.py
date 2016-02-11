import random


class NameGenerator:
    """This class represents a name generator.

    This is a python conversion of the generator found in
    `<http://forum.codecall.net/topic/49665-java-random-name-generator/>`_ all credits to the creator.

    This class generates random names from syllables, and provides a simple way to set a group of rules for generating
    names.

    **Syllable Requirements/Format**

    1. All syllables are in a list
    2. "+" and "-" characters are used to set rules, and using them in other way may result in unpredictable results.

    **Syllable Classification**

    A name is usually composed from 3 different class of syllables, which include prefix, middle part and suffix.
    To declare syllable as a prefix insert "-" as a first character of the word.
    To declare syllable as a suffix insert "+" as a first character of the word.
    Everything else is read as a middle part.

    **Number of Syllables**

    Names may have any positive number of syllables. In case of 2 syllables, name will be composed from a prefix and a
    suffix.
    In case of 1 syllable, the name will be chosen from amongst the prefixes.
    In case of 3 and more syllables, the name will begin with a prefix, will be filled with middle parts and ended with
    a suffix.

    **Assigning Rules**

    A set of 4 kind of rules is used for every syllable. To add rules to the syllables, write them right after the
    syllable and SEPARATE WITH WHITESPACE. (Example: "aad +v -c"). The order of the rules is not important.

    **RULES**

    1. +v means that next syllable must definitely start with a vowel.
    2. +c means that next syllable must definitely start with a consonant.
    3. -v means that this syllable can only be added to another syllable that ends with a vowel.
    4. -c means that this syllable can only be added to another syllable that ends with a consonant.

    So, the example "aad +v -c" means that "aad" can only be after consonant and the next syllable must start with
    vowel.

    Beware of creating logical mistakes, like providing only syllables ending with consonants, but expecting only
    vowels, which will be detected and AssertionError will be thrown.
    """
    def __init__(self, vowels, consonants, syllables):
        self._vowels = vowels
        self._consonants = consonants
        self.syllables = syllables
        self._pre = []
        self._mid = []
        self._sur = []
        self._load_names()

    def _load_names(self):
        for n in self.syllables:
            if n.startswith('-'):
                self._pre.append(n[1:])
            elif n.startswith('+'):
                self._sur.append(n[1:])
            else:
                self._mid.append(n)

    def compose(self, syls):
        """
        Generates a name with the number of given syllables.

        If no combination is found an AssertionError is raised
        :param syls: Number of syllables.
        :return: The word generated.
        :raises: AssertionError
        """
        if syls > 2 and not self._mid:
            raise AssertionError("No middle parts in the given parts. Every word, which doesn't have + or  for a "
                                 "prefix is counted as middle part.")
        if not self._pre:
            raise AssertionError("No prefixes in the given parts. Add some and use - prefix to identify it as a prefix "
                                 "for a name. (Example: -asd)")
        if not self._sur:
            raise AssertionError("No suffixes in the given parts. Add some and use + prefix to identify it as a suffix "
                                 "for a name. (Example: +asd")
        if syls < 1:
            raise AssertionError("Composed words cannot have less than 1 syllable")
        expecting = 0
        pre = random.choice(self._pre)
        last = 1 if self._vowel_last(self._pure_syl(pre)) else 2  # 1 for vowel, 2 for consonant
        if syls > 2:
            if self._expects_vowel(pre):
                expecting = 1
                if not self._contains_vowel_first(self._mid):
                    raise AssertionError("Expecting middle part stating with vowel, but there is none. "
                                         "You should add one, or remove requirement for one.. ")
            if self._expects_consonant(pre):
                expecting = 2
                if not self._contains_consonant_first(self._mid):
                    raise AssertionError("Expecting middle part starting with consonant, but there is none. "
                                         "You should add one, or remove requirement for one.. ")
        else:
            if self._expects_vowel(pre):
                expecting = 1
                if not self._contains_vowel_first(self._sur):
                    raise AssertionError("Expecting suffix part starting with vowel, but there is none. "
                                         "You should add one, or remove requirement for one.. ")
            if self._expects_consonant(pre):
                expecting = 2
                if not self._contains_consonant_first(self._sur):
                    raise AssertionError("Expecting suffix part starting with consonant, but there is none. "
                                         "You should add one, or remove requirement for one.. ")
        if self._vowel_last(self._pure_syl(pre)) and not self._allow_vowels(self._mid):
            raise AssertionError("Expecting middle part that allows last characters of prefix to be a vowel, "
                                 "but there is none. You should add one, or remove requirements that cannot be "
                                 "fulfilled.. the prefix used was: {}, which means there should be a part available "
                                 "that has -v requirement or no requirements for previous syllables at all.".format(
                                  pre))
        if self._consonant_last(self._pure_syl(pre)) and not self._allow_consonants(self._mid):
            raise AssertionError("Expecting middle part that allows last characters of prefix to be a consonant, "
                                 "but there is none. You should add one, or remove requirements that cannot be "
                                 "fulfilled.. the prefix used was: {}, which means there should be a part available "
                                 "that has -c requirement or no requirements for previous syllables at all.".format(
                                  pre))
        mid = []
        for i in range(0, syls - 2):
            new_mid = random.choice(self._mid)
            while (expecting == 1 and not self._vowel_first(self._pure_syl(new_mid))) or \
                    (expecting == 2 and not self._consonant_last(self._pure_syl(new_mid))) or \
                    (last == 1 and self._hates_previous_vowel(new_mid)) or \
                    (last == 2 and self._hates_previous_consonant(new_mid)):
                new_mid = random.choice(self._mid)
            if self._expects_vowel(new_mid):
                expecting = 1
                if i < syls - 3 and not self._contains_vowel_first(self._mid):
                    raise AssertionError("Expecting middle part stating with vowel, but there is none. "
                                         "You should add one, or remove requirement for one.. ")
                if i == syls - 3 and not self._contains_vowel_first(self._sur):
                    raise AssertionError("Expecting suffix part stating with vowel, but there is none. "
                                         "You should add one, or remove requirement for one.. ")
            if self._expects_consonant(new_mid):
                expecting = 2
                if i < syls - 3 and not self._contains_consonant_first(self._mid):
                    raise AssertionError("Expecting middle part starting with consonant, but there is none. "
                                         "You should add one, or remove requirement for one.. ")
                if i == syls - 3 and not self._contains_consonant_first(self._sur):
                    raise AssertionError("Expecting suffix part starting with consonant, but there is none. "
                                         "You should add one, or remove requirement for one.. ")
            if self._vowel_last(self._pure_syl(new_mid)) and not self._allow_vowels(self._mid) and syls > 3:
                raise AssertionError("Expecting middle part that allows last characters of part to be a vowel, "
                                     "but there is none. You should add one, or remove requirements that cannot be "
                                     "fulfilled.. the part used was: {}, which means there should be a part "
                                     "available that has -v requirement or no requirements for previous syllables at"
                                     " all.".format(new_mid))
            if self._consonant_last(self._pure_syl(new_mid)) and not self._allow_consonants(self._mid) and syls > 3:
                raise AssertionError("Expecting middle part that allows last characters of part to be a consonant, "
                                     "but there is none. You should add one, or remove requirements that cannot be "
                                     "fulfilled.. the part used was: {}, which means there should be a part "
                                     "available that has -c requirement or no requirements for previous syllables at"
                                     " all.".format(new_mid))
            if i == syls - 3:
                if self._vowel_last(self._pure_syl(new_mid)) and not self._allow_vowels(self._sur):
                    raise AssertionError("Expecting suffix part that allows last characters of part to be a vowel, "
                                         "but there is none. You should add one, or remove requirements that cannot be "
                                         "fulfilled.. the part used was: {}, which means there should be a suffix "
                                         "available that has -v requirement or no requirements for previous syllables "
                                         "at all.".format(new_mid))
                if self._consonant_last(self._pure_syl(new_mid)) and not self._allow_consonants(self._sur):
                    raise AssertionError("Expecting suffix part that allows last characters of part to be a consonant, "
                                         "but there is none. You should add one, or remove requirements that cannot be "
                                         "fulfilled.. the part used was: {}, which means there should be a suffix "
                                         "available that has -c requirement or no requirements for previous syllables "
                                         "at all.".format(new_mid))
            last = 1 if self._vowel_last(self._pure_syl(pre)) else 2
            mid.append(self._pure_syl(new_mid))
        sur = random.choice(self._sur)
        while (expecting == 1 and not self._vowel_first(self._pure_syl(sur))) or \
                (expecting == 2 and not self._consonant_last(self._pure_syl(sur))) or \
                (last == 1 and self._hates_previous_vowel(sur)) or \
                (last == 2 and self._hates_previous_consonant(sur)):
            sur = random.choice(self._sur)
        mid.insert(0, self._pure_syl(pre))
        if syls > 1:
            mid.append(self._pure_syl(sur))
        return ''.join(mid).capitalize()

    def _vowel_last(self, s):
        return s[-1:] in self._vowels

    def _vowel_first(self, s):
        return s[:1] in self._vowels

    def _consonant_last(self, s):
        return s[-1:] in self._consonants

    def _consonant_first(self, s):
        return s[:1] in self._consonants

    @staticmethod
    def _pure_syl(s):
        return s.split()[0]

    @staticmethod
    def _expects_vowel(s):
        return '+v' in s

    @staticmethod
    def _expects_consonant(s):
        return '+c' in s

    @staticmethod
    def _hates_previous_vowel(s):
        return '-v' in s

    @staticmethod
    def _hates_previous_consonant(s):
        return '-c' in s

    def _contains_vowel_first(self, names):
        for n in names:
            if self._vowel_first(n):
                return True
        return False

    def _contains_consonant_first(self, names):
        for n in names:
            if self._consonant_first(n):
                return True
        return False

    def _allow_vowels(self, names):
        for n in names:
            if self._hates_previous_consonant(n) or not self._hates_previous_vowel(n):
                return True
        return False

    def _allow_consonants(self, names):
        for n in names:
            if self._hates_previous_vowel(n) or not self._hates_previous_consonant(n):
                return True
        return False
